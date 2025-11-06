"""
Processing service for managing transcription queue
"""
import asyncio
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import (
    Episode,
    Transcript,
    Summary,
    SearchIndex,
    ProcessingQueue,
    Statistics,
)
from backend.services.transcription import transcription_service, TranscriptionResult
from backend.services.nlp import nlp_service
from backend.services.export import export_service
from backend.services.file_monitor import file_monitor
from backend.core.config import settings


class ProcessingService:
    """Service for processing audio files through the transcription pipeline"""

    def __init__(self):
        self.is_running = False
        self.current_task: Optional[int] = None
        self.queue_lock = asyncio.Lock()

    async def add_to_queue(
        self,
        db: AsyncSession,
        file_path: str,
        priority: int = 0,
        provider: Optional[str] = None,
    ) -> Episode:
        """
        Add a file to the processing queue

        Args:
            db: Database session
            file_path: Path to audio file
            priority: Queue priority (higher = more urgent)
            provider: Transcription provider to use

        Returns:
            Created Episode record
        """
        # Check if file already exists
        existing_stmt = select(Episode).where(Episode.file_path == file_path)
        result = await db.execute(existing_stmt)
        existing = result.scalar_one_or_none()

        if existing:
            print(f"File already in database: {file_path}")
            return existing

        # Get file metadata
        metadata = file_monitor.get_audio_metadata(file_path)

        # Create episode record
        episode = Episode(
            file_path=file_path,
            file_name=metadata['file_name'],
            file_size=metadata['file_size'],
            duration=metadata['duration'],
            format=metadata['format'],
            title=metadata.get('title') or metadata['file_name'],
            podcast_name=metadata.get('artist'),
            description=None,
            status='pending',
        )

        db.add(episode)
        await db.flush()

        # Create queue entry
        queue_entry = ProcessingQueue(
            episode_id=episode.id,
            priority=priority,
            status='queued',
            provider=provider or settings.DEFAULT_TRANSCRIPTION_PROVIDER,
        )

        db.add(queue_entry)
        await db.commit()
        await db.refresh(episode)

        print(f"Added to queue: {file_path}")
        return episode

    async def check_daily_limit(self, db: AsyncSession) -> bool:
        """
        Check if daily processing limit has been reached

        Returns:
            True if can process more files, False if limit reached
        """
        today = date.today()

        # Get today's statistics
        stmt = select(Statistics).where(
            Statistics.date >= datetime.combine(today, datetime.min.time())
        )
        result = await db.execute(stmt)
        stats = result.scalar_one_or_none()

        if not stats:
            return True

        return stats.files_processed < settings.MAX_FILES_PER_DAY

    async def update_daily_stats(
        self,
        db: AsyncSession,
        success: bool,
        duration: float = 0,
        processing_time: float = 0,
        provider: str = 'local',
    ):
        """Update daily statistics"""
        today = datetime.combine(date.today(), datetime.min.time())

        # Get or create today's stats
        stmt = select(Statistics).where(Statistics.date == today)
        result = await db.execute(stmt)
        stats = result.scalar_one_or_none()

        if not stats:
            stats = Statistics(date=today)
            db.add(stats)

        # Update counts
        if success:
            stats.files_processed += 1
        else:
            stats.files_failed += 1

        stats.total_duration += duration
        stats.total_processing_time += processing_time

        # Update API call counts
        if provider == 'openai':
            stats.api_calls_openai += 1
        elif provider == 'huggingface':
            stats.api_calls_huggingface += 1
        elif provider == 'deepgram':
            stats.api_calls_deepgram += 1

        await db.commit()

    async def process_episode(
        self,
        db: AsyncSession,
        episode_id: int,
        queue_entry: ProcessingQueue,
    ) -> bool:
        """
        Process a single episode through the pipeline

        Args:
            db: Database session
            episode_id: Episode ID to process
            queue_entry: Queue entry

        Returns:
            True if successful, False otherwise
        """
        # Get episode
        stmt = select(Episode).where(Episode.id == episode_id)
        result = await db.execute(stmt)
        episode = result.scalar_one_or_none()

        if not episode:
            return False

        try:
            # Update status
            episode.status = 'processing'
            queue_entry.status = 'processing'
            queue_entry.started_at = datetime.utcnow()
            queue_entry.progress = 10
            await db.commit()

            print(f"Processing episode: {episode.title}")

            # Step 1: Transcribe
            print(f"  Transcribing with {queue_entry.provider}...")
            transcription_result = await transcription_service.transcribe_audio(
                episode.file_path,
                provider_name=queue_entry.provider,
            )
            queue_entry.progress = 50
            await db.commit()

            # Step 2: Save transcript
            print(f"  Saving transcript...")
            transcript = Transcript(
                episode_id=episode.id,
                full_text=transcription_result.text,
                segments=[s.to_dict() for s in transcription_result.segments],
                language=transcription_result.language,
                confidence_score=transcription_result.confidence,
                provider=transcription_result.provider,
                model=transcription_result.model,
                processing_time=transcription_result.processing_time,
                word_count=transcription_result.word_count,
                format='json',
            )
            db.add(transcript)
            await db.flush()

            # Export in multiple formats
            output_dir = settings.TRANSCRIPTS_DIR / f"episode_{episode.id}"
            output_dir.mkdir(parents=True, exist_ok=True)

            for fmt in ['txt', 'srt', 'vtt', 'json', 'markdown']:
                output_path = output_dir / f"transcript.{fmt}"
                export_service.export(
                    transcription_result,
                    format=fmt,
                    output_path=str(output_path),
                    title=episode.title,
                    metadata={
                        'podcast': episode.podcast_name,
                        'duration': f"{episode.duration:.1f}s" if episode.duration else None,
                        'file': episode.file_name,
                    },
                )

            queue_entry.progress = 70
            await db.commit()

            # Step 3: NLP Analysis
            print(f"  Analyzing content...")
            analysis = nlp_service.analyze_transcript(
                transcription_result.text,
                segments=[s.to_dict() for s in transcription_result.segments],
            )

            # Determine category
            categories = analysis['categories']
            primary_category = categories[0][0] if categories else 'general'

            # Create summary
            summary = Summary(
                episode_id=episode.id,
                short_summary=analysis['short_summary'],
                full_summary=analysis['full_summary'],
                key_points=analysis['keywords'][:10],
                topics=[{'id': t['id'], 'words': t['words']} for t in analysis['topics']],
                keywords=analysis['keywords'],
                highlights=analysis['highlights'],
                speakers=analysis['speakers'],
                mentioned_people=analysis['named_entities'].get('people', []),
                mentioned_organizations=analysis['named_entities'].get('organizations', []),
                mentioned_locations=analysis['named_entities'].get('locations', []),
                model='nltk+sklearn',
                confidence_score=0.8,
            )
            db.add(summary)

            # Update episode with category and tags
            episode.category = primary_category
            episode.tags = analysis['keywords'][:20]

            queue_entry.progress = 90
            await db.commit()

            # Step 4: Create search index
            print(f"  Indexing for search...")
            search_text = f"{episode.title} {episode.description or ''} {transcription_result.text}"

            search_index = SearchIndex(
                episode_id=episode.id,
                searchable_text=search_text,
                embedding=None,  # TODO: Add embedding generation
                tfidf_vector=None,
            )
            db.add(search_index)

            # Mark as completed
            episode.status = 'completed'
            episode.processed_at = datetime.utcnow()
            queue_entry.status = 'completed'
            queue_entry.completed_at = datetime.utcnow()
            queue_entry.progress = 100

            await db.commit()

            # Update statistics
            await self.update_daily_stats(
                db,
                success=True,
                duration=episode.duration or 0,
                processing_time=transcription_result.processing_time,
                provider=queue_entry.provider,
            )

            print(f"  ✓ Completed: {episode.title}")
            return True

        except Exception as e:
            print(f"  ✗ Error processing episode: {e}")

            # Update error status
            episode.status = 'failed'
            episode.error_message = str(e)
            queue_entry.status = 'failed'
            queue_entry.error_message = str(e)
            queue_entry.retry_count += 1

            await db.commit()

            # Update statistics
            await self.update_daily_stats(
                db,
                success=False,
                provider=queue_entry.provider,
            )

            return False

    async def process_queue(self, db: AsyncSession, max_items: int = 5):
        """
        Process items from the queue

        Args:
            db: Database session
            max_items: Maximum number of items to process in this batch
        """
        async with self.queue_lock:
            if self.is_running:
                print("Queue processing already running")
                return

            self.is_running = True

        try:
            # Check daily limit
            if not await self.check_daily_limit(db):
                print("Daily processing limit reached")
                return

            # Get queued items
            stmt = (
                select(ProcessingQueue, Episode)
                .join(Episode, ProcessingQueue.episode_id == Episode.id)
                .where(ProcessingQueue.status == 'queued')
                .order_by(ProcessingQueue.priority.desc(), ProcessingQueue.queued_at)
                .limit(max_items)
            )

            result = await db.execute(stmt)
            items = result.all()

            if not items:
                print("Queue is empty")
                return

            print(f"Processing {len(items)} items from queue...")

            for queue_entry, episode in items:
                # Check daily limit before each item
                if not await self.check_daily_limit(db):
                    print("Daily limit reached, stopping queue processing")
                    break

                self.current_task = episode.id
                await self.process_episode(db, episode.id, queue_entry)
                self.current_task = None

        finally:
            async with self.queue_lock:
                self.is_running = False

    async def get_queue_status(self, db: AsyncSession) -> Dict[str, Any]:
        """Get current queue status"""
        # Count by status
        queued_stmt = select(ProcessingQueue).where(ProcessingQueue.status == 'queued')
        queued_result = await db.execute(queued_stmt)
        queued_count = len(queued_result.scalars().all())

        processing_stmt = select(ProcessingQueue).where(
            ProcessingQueue.status == 'processing'
        )
        processing_result = await db.execute(processing_stmt)
        processing_count = len(processing_result.scalars().all())

        # Get daily stats
        today = datetime.combine(date.today(), datetime.min.time())
        stats_stmt = select(Statistics).where(Statistics.date == today)
        stats_result = await db.execute(stats_stmt)
        stats = stats_result.scalar_one_or_none()

        files_processed_today = stats.files_processed if stats else 0

        return {
            'queued': queued_count,
            'processing': processing_count,
            'is_running': self.is_running,
            'current_task': self.current_task,
            'files_processed_today': files_processed_today,
            'daily_limit': settings.MAX_FILES_PER_DAY,
            'remaining_today': max(0, settings.MAX_FILES_PER_DAY - files_processed_today),
        }


# Global processing service
processing_service = ProcessingService()
