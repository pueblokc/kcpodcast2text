"""
Basic tests for the application
"""
import pytest
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.config import settings
from backend.services.export import export_service
from backend.services.nlp import nlp_service


def test_settings():
    """Test that settings are loaded correctly"""
    assert settings.APP_NAME == "Podcast Transcription Archive"
    assert settings.MAX_FILES_PER_DAY > 0
    assert settings.WHISPER_MODEL_SIZE in ["tiny", "base", "small", "medium", "large"]


def test_export_formats():
    """Test export format generation"""
    from backend.services.transcription import TranscriptionResult, TranscriptionSegment

    # Create sample transcription
    segments = [
        TranscriptionSegment(
            start=0.0,
            end=5.0,
            text="This is a test transcript.",
            confidence=0.95,
        ),
        TranscriptionSegment(
            start=5.0,
            end=10.0,
            text="Testing the export functionality.",
            confidence=0.92,
        ),
    ]

    result = TranscriptionResult(
        text="This is a test transcript. Testing the export functionality.",
        segments=segments,
        language="en",
        confidence=0.93,
        provider="test",
        model="test-model",
        processing_time=1.5,
    )

    # Test TXT export
    txt = export_service.to_txt(result)
    assert "This is a test transcript" in txt
    assert "Testing the export functionality" in txt

    # Test JSON export
    json_str = export_service.to_json(result)
    assert '"text"' in json_str
    assert '"segments"' in json_str

    # Test SRT export
    srt = export_service.to_srt(result)
    assert "1" in srt
    assert "-->" in srt

    # Test VTT export
    vtt = export_service.to_vtt(result)
    assert "WEBVTT" in vtt
    assert "-->" in vtt

    # Test Markdown export
    md = export_service.to_markdown(result, title="Test Episode")
    assert "# Test Episode" in md
    assert "## Transcription Details" in md


def test_nlp_keyword_extraction():
    """Test NLP keyword extraction"""
    text = """
    Machine learning is a subset of artificial intelligence that focuses on
    building systems that can learn from data. Deep learning, neural networks,
    and natural language processing are important topics in machine learning.
    """

    keywords = nlp_service.extract_keywords(text, top_n=5)
    assert len(keywords) > 0
    assert all(isinstance(kw, tuple) for kw in keywords)
    assert all(len(kw) == 2 for kw in keywords)


def test_nlp_categorization():
    """Test content categorization"""
    tech_text = "Python programming, software development, artificial intelligence, machine learning"
    categories = nlp_service.categorize(tech_text)

    assert len(categories) > 0
    # Should detect technology category
    category_names = [cat for cat, score in categories]
    assert 'technology' in category_names


def test_nlp_summary():
    """Test text summarization"""
    text = """
    Artificial intelligence is transforming many industries. Machine learning
    algorithms can analyze vast amounts of data and make predictions. Deep learning
    uses neural networks with multiple layers. Natural language processing enables
    computers to understand human language. Computer vision allows machines to
    interpret visual information. These technologies are being applied in healthcare,
    finance, transportation, and many other fields.
    """

    summary = nlp_service.generate_summary(text, num_sentences=3)
    assert len(summary) > 0
    assert len(summary) < len(text)


@pytest.mark.asyncio
async def test_database_init():
    """Test database initialization"""
    from backend.database import init_db, close_db

    # This should not raise an exception
    await init_db()
    await close_db()


def test_file_formats():
    """Test supported audio formats"""
    from backend.services.file_monitor import SUPPORTED_AUDIO_FORMATS

    assert '.mp3' in SUPPORTED_AUDIO_FORMATS
    assert '.wav' in SUPPORTED_AUDIO_FORMATS
    assert '.m4a' in SUPPORTED_AUDIO_FORMATS
    assert '.flac' in SUPPORTED_AUDIO_FORMATS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
