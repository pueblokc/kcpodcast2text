"""
Search service with full-text search and semantic search capabilities
"""
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy import select, text, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.database.models import Episode, Transcript, Summary, SearchIndex


class SearchService:
    """Service for searching transcripts"""

    async def full_text_search(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Full-text search using SQLite FTS5

        Args:
            db: Database session
            query: Search query
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of matching episodes with highlights
        """
        # Search using FTS5
        fts_query = text("""
            SELECT
                e.*,
                snippet(episodes_fts, 0, '<mark>', '</mark>', '...', 32) as title_snippet,
                snippet(episodes_fts, 2, '<mark>', '</mark>', '...', 64) as transcript_snippet,
                rank
            FROM episodes_fts
            JOIN episodes e ON episodes_fts.episode_id = e.id
            WHERE episodes_fts MATCH :query
            ORDER BY rank
            LIMIT :limit OFFSET :offset
        """)

        result = await db.execute(
            fts_query,
            {"query": query, "limit": limit, "offset": offset}
        )

        rows = result.fetchall()
        episodes = []

        for row in rows:
            episodes.append({
                "id": row.id,
                "title": row.title,
                "podcast_name": row.podcast_name,
                "file_name": row.file_name,
                "duration": row.duration,
                "category": row.category,
                "publish_date": row.publish_date,
                "title_snippet": getattr(row, 'title_snippet', None),
                "transcript_snippet": getattr(row, 'transcript_snippet', None),
                "rank": getattr(row, 'rank', 0),
            })

        return episodes

    async def filter_episodes(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        podcast_name: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        min_duration: Optional[float] = None,
        max_duration: Optional[float] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Episode]:
        """
        Filter episodes by various criteria

        Args:
            db: Database session
            category: Filter by category
            podcast_name: Filter by podcast name
            date_from: Start date
            date_to: End date
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds
            status: Processing status
            tags: List of tags (ANY match)
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of matching episodes
        """
        query = select(Episode)

        # Build filters
        filters = []

        if category:
            filters.append(Episode.category == category)

        if podcast_name:
            filters.append(Episode.podcast_name.ilike(f"%{podcast_name}%"))

        if date_from:
            filters.append(Episode.publish_date >= date_from)

        if date_to:
            filters.append(Episode.publish_date <= date_to)

        if min_duration:
            filters.append(Episode.duration >= min_duration)

        if max_duration:
            filters.append(Episode.duration <= max_duration)

        if status:
            filters.append(Episode.status == status)

        # Apply filters
        if filters:
            query = query.where(and_(*filters))

        # Order by date
        query = query.order_by(Episode.publish_date.desc())

        # Pagination
        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        return result.scalars().all()

    async def search_transcripts(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search within transcript text

        Args:
            db: Database session
            query: Search query
            limit: Maximum results

        Returns:
            List of matching transcript segments
        """
        # Search in transcript full_text
        stmt = select(Transcript, Episode).join(
            Episode, Transcript.episode_id == Episode.id
        ).where(
            Transcript.full_text.ilike(f"%{query}%")
        ).limit(limit)

        result = await db.execute(stmt)
        rows = result.all()

        matches = []
        for transcript, episode in rows:
            # Find matching segments
            matching_segments = []
            if transcript.segments:
                for segment in transcript.segments:
                    if query.lower() in segment.get('text', '').lower():
                        matching_segments.append(segment)

            matches.append({
                "episode_id": episode.id,
                "episode_title": episode.title,
                "podcast_name": episode.podcast_name,
                "transcript_id": transcript.id,
                "matching_segments": matching_segments[:5],  # Top 5 segments
            })

        return matches

    async def semantic_search(
        self,
        db: AsyncSession,
        query_embedding: List[float],
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using embeddings (cosine similarity)

        Args:
            db: Database session
            query_embedding: Query vector embedding
            limit: Maximum results

        Returns:
            List of episodes ranked by similarity
        """
        # Get all search indices with embeddings
        stmt = select(SearchIndex, Episode).join(
            Episode, SearchIndex.episode_id == Episode.id
        ).where(
            SearchIndex.embedding.isnot(None)
        )

        result = await db.execute(stmt)
        rows = result.all()

        # Calculate cosine similarity
        query_vec = np.array(query_embedding)
        similarities = []

        for search_idx, episode in rows:
            if search_idx.embedding:
                doc_vec = np.array(search_idx.embedding)

                # Cosine similarity
                similarity = np.dot(query_vec, doc_vec) / (
                    np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
                )

                similarities.append({
                    "episode_id": episode.id,
                    "title": episode.title,
                    "podcast_name": episode.podcast_name,
                    "category": episode.category,
                    "similarity": float(similarity),
                })

        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)

        return similarities[:limit]

    async def get_episode_with_transcript(
        self,
        db: AsyncSession,
        episode_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Get episode with its transcript and summary

        Args:
            db: Database session
            episode_id: Episode ID

        Returns:
            Episode data with transcript and summary
        """
        # Get episode
        episode_stmt = select(Episode).where(Episode.id == episode_id)
        episode_result = await db.execute(episode_stmt)
        episode = episode_result.scalar_one_or_none()

        if not episode:
            return None

        # Get transcript
        transcript_stmt = select(Transcript).where(
            Transcript.episode_id == episode_id
        ).order_by(Transcript.created_at.desc())
        transcript_result = await db.execute(transcript_stmt)
        transcript = transcript_result.scalar_one_or_none()

        # Get summary
        summary_stmt = select(Summary).where(
            Summary.episode_id == episode_id
        ).order_by(Summary.created_at.desc())
        summary_result = await db.execute(summary_stmt)
        summary = summary_result.scalar_one_or_none()

        return {
            "episode": episode,
            "transcript": transcript,
            "summary": summary,
        }

    async def get_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Statistics about the database
        """
        # Count episodes by status
        status_query = text("""
            SELECT status, COUNT(*) as count
            FROM episodes
            GROUP BY status
        """)
        status_result = await db.execute(status_query)
        status_counts = {row.status: row.count for row in status_result}

        # Count episodes by category
        category_query = text("""
            SELECT category, COUNT(*) as count
            FROM episodes
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
            LIMIT 10
        """)
        category_result = await db.execute(category_query)
        category_counts = [
            {"category": row.category, "count": row.count}
            for row in category_result
        ]

        # Total duration
        duration_query = text("""
            SELECT
                COUNT(*) as total_episodes,
                SUM(duration) as total_duration,
                AVG(duration) as avg_duration
            FROM episodes
            WHERE duration IS NOT NULL
        """)
        duration_result = await db.execute(duration_query)
        duration_stats = duration_result.fetchone()

        # Transcription stats
        transcript_query = text("""
            SELECT
                COUNT(*) as total_transcripts,
                AVG(word_count) as avg_words,
                AVG(confidence_score) as avg_confidence
            FROM transcripts
        """)
        transcript_result = await db.execute(transcript_query)
        transcript_stats = transcript_result.fetchone()

        return {
            "status_counts": status_counts,
            "category_counts": category_counts,
            "total_episodes": duration_stats.total_episodes if duration_stats else 0,
            "total_duration_hours": (duration_stats.total_duration or 0) / 3600,
            "avg_duration_minutes": (duration_stats.avg_duration or 0) / 60,
            "total_transcripts": transcript_stats.total_transcripts if transcript_stats else 0,
            "avg_words_per_transcript": transcript_stats.avg_words if transcript_stats else 0,
            "avg_confidence": transcript_stats.avg_confidence if transcript_stats else 0,
        }


# Global search service instance
search_service = SearchService()
