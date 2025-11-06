"""
FastAPI routes for the application
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.database import get_db, Episode, Transcript, Summary
from backend.services.processor import processing_service
from backend.services.search import search_service
from backend.services.file_monitor import file_monitor
from backend.services.export import export_service
from backend.core.config import settings

router = APIRouter()


# Pydantic models for request/response
class EpisodeResponse(BaseModel):
    id: int
    title: Optional[str]
    podcast_name: Optional[str]
    file_name: str
    duration: Optional[float]
    category: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AddFileRequest(BaseModel):
    file_path: str
    priority: int = 0
    provider: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 50
    offset: int = 0


class FilterRequest(BaseModel):
    category: Optional[str] = None
    podcast_name: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    status: Optional[str] = None
    limit: int = 50
    offset: int = 0


class ExportRequest(BaseModel):
    episode_id: int
    format: str  # txt, srt, vtt, json, markdown, csv, pdf


# Episodes
@router.get("/episodes", response_model=List[EpisodeResponse])
async def list_episodes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all episodes with optional filtering"""
    episodes = await search_service.filter_episodes(
        db,
        status=status,
        category=category,
        limit=limit,
        offset=skip,
    )
    return episodes


@router.get("/episodes/{episode_id}")
async def get_episode(
    episode_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get episode details with transcript and summary"""
    result = await search_service.get_episode_with_transcript(db, episode_id)

    if not result:
        raise HTTPException(status_code=404, detail="Episode not found")

    return {
        "episode": result["episode"],
        "transcript": result["transcript"],
        "summary": result["summary"],
    }


@router.post("/episodes/add")
async def add_episode(
    request: AddFileRequest,
    db: AsyncSession = Depends(get_db),
):
    """Add a file to the processing queue"""
    if not Path(request.file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")

    episode = await processing_service.add_to_queue(
        db,
        file_path=request.file_path,
        priority=request.priority,
        provider=request.provider,
    )

    return {"episode_id": episode.id, "status": "added to queue"}


@router.post("/episodes/scan")
async def scan_directory(
    directory: str,
    recursive: bool = True,
    auto_add: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Scan a directory for audio files"""
    if not Path(directory).exists():
        raise HTTPException(status_code=404, detail="Directory not found")

    files = file_monitor.scan_directory(directory, recursive=recursive)

    added = []
    if auto_add:
        for file_path in files:
            try:
                episode = await processing_service.add_to_queue(db, file_path)
                added.append(episode.id)
            except Exception as e:
                print(f"Error adding {file_path}: {e}")

    return {
        "total_files": len(files),
        "files": files[:100],  # Return first 100
        "added_to_queue": len(added),
    }


# Search
@router.post("/search")
async def search(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Full-text search across episodes"""
    results = await search_service.full_text_search(
        db,
        query=request.query,
        limit=request.limit,
        offset=request.offset,
    )
    return {"results": results, "count": len(results)}


@router.post("/search/transcripts")
async def search_transcripts(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Search within transcript text"""
    results = await search_service.search_transcripts(
        db,
        query=request.query,
        limit=request.limit,
    )
    return {"results": results, "count": len(results)}


@router.post("/search/filter")
async def filter_episodes(
    request: FilterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Filter episodes by various criteria"""
    episodes = await search_service.filter_episodes(
        db,
        category=request.category,
        podcast_name=request.podcast_name,
        date_from=request.date_from,
        date_to=request.date_to,
        min_duration=request.min_duration,
        max_duration=request.max_duration,
        status=request.status,
        limit=request.limit,
        offset=request.offset,
    )
    return {"results": episodes, "count": len(episodes)}


# Processing Queue
@router.get("/queue/status")
async def queue_status(db: AsyncSession = Depends(get_db)):
    """Get current queue status"""
    status = await processing_service.get_queue_status(db)
    return status


@router.post("/queue/process")
async def process_queue(
    max_items: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Trigger queue processing"""
    await processing_service.process_queue(db, max_items=max_items)
    return {"status": "processing started"}


# Export
@router.post("/export")
async def export_transcript(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Export transcript in specified format"""
    result = await search_service.get_episode_with_transcript(db, request.episode_id)

    if not result or not result["transcript"]:
        raise HTTPException(status_code=404, detail="Transcript not found")

    episode = result["episode"]
    transcript = result["transcript"]

    # Convert to TranscriptionResult
    from backend.services.transcription import TranscriptionResult, TranscriptionSegment

    segments = [
        TranscriptionSegment(
            start=s.get("start", 0),
            end=s.get("end", 0),
            text=s.get("text", ""),
            confidence=s.get("confidence"),
            speaker=s.get("speaker"),
        )
        for s in transcript.segments or []
    ]

    transcription_result = TranscriptionResult(
        text=transcript.full_text,
        segments=segments,
        language=transcript.language,
        confidence=transcript.confidence_score or 0,
        provider=transcript.provider,
        model=transcript.model,
        processing_time=transcript.processing_time or 0,
    )

    # Export
    output_dir = settings.TRANSCRIPTS_DIR / f"episode_{episode.id}"
    output_path = output_dir / f"transcript.{request.format}"

    content = export_service.export(
        transcription_result,
        format=request.format,
        output_path=str(output_path),
        title=episode.title,
        metadata={
            "podcast": episode.podcast_name,
            "duration": f"{episode.duration:.1f}s" if episode.duration else None,
            "category": episode.category,
        },
    )

    return {
        "file_path": str(output_path),
        "format": request.format,
        "size": len(content) if isinstance(content, str) else 0,
    }


# Statistics
@router.get("/statistics")
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """Get database statistics"""
    stats = await search_service.get_statistics(db)
    return stats


# Configuration
@router.get("/config/providers")
async def list_providers():
    """List available transcription providers"""
    from backend.services.transcription import transcription_service

    available = transcription_service.list_available_providers()
    return {
        "providers": available,
        "default": settings.DEFAULT_TRANSCRIPTION_PROVIDER,
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}
