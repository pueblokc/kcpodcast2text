"""
Database models for podcast transcription archive
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, Boolean,
    ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs

Base = declarative_base()


class Episode(AsyncAttrs, Base):
    """Podcast episode metadata"""
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(500), unique=True, nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)  # in bytes
    duration = Column(Float)  # in seconds
    format = Column(String(10))  # mp3, wav, m4a, etc.

    # Metadata
    title = Column(String(500))
    podcast_name = Column(String(255), index=True)
    episode_number = Column(Integer)
    season_number = Column(Integer)
    publish_date = Column(DateTime)
    description = Column(Text)

    # Categorization
    category = Column(String(100), index=True)
    tags = Column(JSON)  # List of tags

    # Processing status
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)

    # Relationships
    transcripts = relationship("Transcript", back_populates="episode", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="episode", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_episode_status_created', 'status', 'created_at'),
        Index('idx_episode_category_date', 'category', 'publish_date'),
    )


class Transcript(AsyncAttrs, Base):
    """Episode transcription with timestamps"""
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Transcript data
    full_text = Column(Text, nullable=False)
    segments = Column(JSON)  # List of segments with timestamps
    language = Column(String(10))
    confidence_score = Column(Float)  # Average confidence

    # Provider information
    provider = Column(String(50))  # local, openai, huggingface, deepgram
    model = Column(String(100))  # whisper-base, whisper-large, etc.

    # Format and storage
    format = Column(String(20))  # txt, srt, vtt, json, markdown
    file_path = Column(String(500))  # Path to saved transcript file

    # Processing metadata
    processing_time = Column(Float)  # in seconds
    word_count = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    episode = relationship("Episode", back_populates="transcripts")

    # Indexes
    __table_args__ = (
        Index('idx_transcript_episode', 'episode_id'),
    )


class Summary(AsyncAttrs, Base):
    """Episode summaries and highlights"""
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Summary content
    short_summary = Column(Text)  # 2-3 sentences
    full_summary = Column(Text)  # 5-7 sentences
    key_points = Column(JSON)  # List of key points

    # Topics and themes
    topics = Column(JSON)  # List of extracted topics with confidence scores
    keywords = Column(JSON)  # List of keywords

    # Highlights
    highlights = Column(JSON)  # List of {timestamp, text, reason}

    # Named entities
    speakers = Column(JSON)  # List of detected speakers
    mentioned_people = Column(JSON)  # Names mentioned
    mentioned_organizations = Column(JSON)
    mentioned_locations = Column(JSON)

    # Generation metadata
    model = Column(String(100))
    confidence_score = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    episode = relationship("Episode", back_populates="summaries")


class SearchIndex(AsyncAttrs, Base):
    """Full-text search index with embeddings"""
    __tablename__ = "search_index"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Search content
    searchable_text = Column(Text, nullable=False)  # Combined text for FTS
    embedding = Column(JSON)  # Vector embedding for semantic search

    # TF-IDF features
    tfidf_vector = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_search_episode', 'episode_id'),
    )


class ProcessingQueue(AsyncAttrs, Base):
    """Queue for managing transcription jobs"""
    __tablename__ = "processing_queue"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Queue metadata
    priority = Column(Integer, default=0)  # Higher = more urgent
    status = Column(String(50), default="queued", index=True)  # queued, processing, completed, failed, paused
    progress = Column(Float, default=0.0)  # 0-100%

    # Processing details
    provider = Column(String(50))
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text)

    # Timing
    queued_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion = Column(DateTime)

    # Indexes
    __table_args__ = (
        Index('idx_queue_status_priority', 'status', 'priority'),
        Index('idx_queue_episode', 'episode_id'),
    )


class Configuration(AsyncAttrs, Base):
    """Application configuration storage"""
    __tablename__ = "configuration"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON)
    description = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Statistics(AsyncAttrs, Base):
    """Daily usage statistics for rate limiting"""
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)

    # Counters
    files_processed = Column(Integer, default=0)
    files_failed = Column(Integer, default=0)
    total_duration = Column(Float, default=0.0)  # Total audio duration processed
    total_processing_time = Column(Float, default=0.0)  # Total CPU time used

    # API usage
    api_calls_openai = Column(Integer, default=0)
    api_calls_huggingface = Column(Integer, default=0)
    api_calls_deepgram = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
