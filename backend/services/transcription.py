"""
Transcription service with multiple provider support
"""
import os
import time
import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta

import torch
from pydub import AudioSegment
from backend.core.config import settings


class TranscriptionSegment:
    """Represents a single segment of transcription with timing"""

    def __init__(
        self,
        start: float,
        end: float,
        text: str,
        confidence: Optional[float] = None,
        speaker: Optional[str] = None,
    ):
        self.start = start
        self.end = end
        self.text = text
        self.confidence = confidence
        self.speaker = speaker

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "confidence": self.confidence,
            "speaker": self.speaker,
        }


class TranscriptionResult:
    """Result of transcription operation"""

    def __init__(
        self,
        text: str,
        segments: List[TranscriptionSegment],
        language: str,
        confidence: float,
        provider: str,
        model: str,
        processing_time: float,
    ):
        self.text = text
        self.segments = segments
        self.language = language
        self.confidence = confidence
        self.provider = provider
        self.model = model
        self.processing_time = processing_time
        self.word_count = len(text.split())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "segments": [s.to_dict() for s in self.segments],
            "language": self.language,
            "confidence": self.confidence,
            "provider": self.provider,
            "model": self.model,
            "processing_time": self.processing_time,
            "word_count": self.word_count,
        }


class TranscriptionProvider(ABC):
    """Base class for transcription providers"""

    @abstractmethod
    async def transcribe(self, audio_path: str) -> TranscriptionResult:
        """Transcribe audio file and return result"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is properly configured and available"""
        pass


class LocalWhisperProvider(TranscriptionProvider):
    """Local Whisper model transcription (free, CPU/GPU)"""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def is_available(self) -> bool:
        return True  # Local always available

    def _load_model(self):
        """Lazy load the Whisper model"""
        if self.model is None:
            import whisper

            print(f"Loading Whisper {self.model_size} model on {self.device}...")
            self.model = whisper.load_model(self.model_size, device=self.device)

    async def transcribe(self, audio_path: str) -> TranscriptionResult:
        """Transcribe using local Whisper model"""
        start_time = time.time()

        # Load model if needed
        await asyncio.to_thread(self._load_model)

        # Transcribe in thread to avoid blocking
        result = await asyncio.to_thread(
            self.model.transcribe,
            audio_path,
            verbose=False,
            word_timestamps=True,
        )

        # Extract segments
        segments = []
        for seg in result.get("segments", []):
            segments.append(
                TranscriptionSegment(
                    start=seg["start"],
                    end=seg["end"],
                    text=seg["text"].strip(),
                    confidence=seg.get("avg_logprob"),
                )
            )

        processing_time = time.time() - start_time

        return TranscriptionResult(
            text=result["text"].strip(),
            segments=segments,
            language=result.get("language", "unknown"),
            confidence=sum(s.confidence or 0 for s in segments) / len(segments)
            if segments
            else 0,
            provider="local",
            model=f"whisper-{self.model_size}",
            processing_time=processing_time,
        )


class OpenAIWhisperProvider(TranscriptionProvider):
    """OpenAI Whisper API transcription"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY

    def is_available(self) -> bool:
        return self.api_key is not None

    async def transcribe(self, audio_path: str) -> TranscriptionResult:
        """Transcribe using OpenAI API"""
        from openai import AsyncOpenAI

        start_time = time.time()
        client = AsyncOpenAI(api_key=self.api_key)

        with open(audio_path, "rb") as audio_file:
            # Get detailed transcription with timestamps
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        # Extract segments
        segments = []
        if hasattr(response, "segments"):
            for seg in response.segments:
                segments.append(
                    TranscriptionSegment(
                        start=seg.start,
                        end=seg.end,
                        text=seg.text.strip(),
                        confidence=getattr(seg, "avg_logprob", None),
                    )
                )

        processing_time = time.time() - start_time

        return TranscriptionResult(
            text=response.text.strip(),
            segments=segments,
            language=getattr(response, "language", "unknown"),
            confidence=0.9,  # OpenAI doesn't provide confidence
            provider="openai",
            model="whisper-1",
            processing_time=processing_time,
        )


class HuggingFaceProvider(TranscriptionProvider):
    """Hugging Face Inference API transcription"""

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or settings.HUGGINGFACE_API_TOKEN
        self.api_url = "https://api-inference.huggingface.co/models/openai/whisper-base"

    def is_available(self) -> bool:
        return self.api_token is not None

    async def transcribe(self, audio_path: str) -> TranscriptionResult:
        """Transcribe using Hugging Face API"""
        import httpx

        start_time = time.time()

        headers = {"Authorization": f"Bearer {self.api_token}"}

        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url, headers=headers, content=audio_data, timeout=300.0
            )
            response.raise_for_status()
            result = response.json()

        # Parse result (format may vary)
        text = result.get("text", "")

        # HF doesn't provide detailed segments by default
        segments = [
            TranscriptionSegment(start=0.0, end=0.0, text=text, confidence=None)
        ]

        processing_time = time.time() - start_time

        return TranscriptionResult(
            text=text.strip(),
            segments=segments,
            language="unknown",
            confidence=0.85,
            provider="huggingface",
            model="whisper-base",
            processing_time=processing_time,
        )


class DeepgramProvider(TranscriptionProvider):
    """Deepgram API transcription"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.DEEPGRAM_API_KEY

    def is_available(self) -> bool:
        return self.api_key is not None

    async def transcribe(self, audio_path: str) -> TranscriptionResult:
        """Transcribe using Deepgram API"""
        from deepgram import DeepgramClient, PrerecordedOptions

        start_time = time.time()

        client = DeepgramClient(self.api_key)

        with open(audio_path, "rb") as audio_file:
            buffer_data = audio_file.read()

        payload = {"buffer": buffer_data}

        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            utterances=True,
            punctuate=True,
            diarize=True,
        )

        response = await asyncio.to_thread(
            client.listen.prerecorded.v("1").transcribe_file, payload, options
        )

        # Extract text and segments
        transcript = response.results.channels[0].alternatives[0]
        text = transcript.transcript

        segments = []
        if hasattr(transcript, "words"):
            current_segment = {"start": 0, "end": 0, "text": "", "speaker": None}

            for word in transcript.words:
                if (
                    current_segment["speaker"] != word.get("speaker")
                    and current_segment["text"]
                ):
                    segments.append(
                        TranscriptionSegment(
                            start=current_segment["start"],
                            end=current_segment["end"],
                            text=current_segment["text"].strip(),
                            confidence=word.get("confidence"),
                            speaker=current_segment["speaker"],
                        )
                    )
                    current_segment = {
                        "start": word.start,
                        "end": word.end,
                        "text": word.word,
                        "speaker": word.get("speaker"),
                    }
                else:
                    current_segment["end"] = word.end
                    current_segment["text"] += " " + word.word
                    if current_segment["start"] == 0:
                        current_segment["start"] = word.start
                        current_segment["speaker"] = word.get("speaker")

            if current_segment["text"]:
                segments.append(
                    TranscriptionSegment(
                        start=current_segment["start"],
                        end=current_segment["end"],
                        text=current_segment["text"].strip(),
                        speaker=current_segment["speaker"],
                    )
                )

        processing_time = time.time() - start_time

        return TranscriptionResult(
            text=text.strip(),
            segments=segments,
            language=response.results.channels[0].detected_language or "unknown",
            confidence=transcript.confidence,
            provider="deepgram",
            model="nova-2",
            processing_time=processing_time,
        )


class TranscriptionService:
    """Main transcription service that manages multiple providers"""

    def __init__(self):
        self.providers: Dict[str, TranscriptionProvider] = {
            "local": LocalWhisperProvider(settings.WHISPER_MODEL_SIZE),
            "openai": OpenAIWhisperProvider(),
            "huggingface": HuggingFaceProvider(),
            "deepgram": DeepgramProvider(),
        }

    def get_provider(self, provider_name: Optional[str] = None) -> TranscriptionProvider:
        """Get a transcription provider by name"""
        provider_name = provider_name or settings.DEFAULT_TRANSCRIPTION_PROVIDER

        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")

        provider = self.providers[provider_name]

        if not provider.is_available():
            raise ValueError(f"Provider {provider_name} is not configured")

        return provider

    async def transcribe_audio(
        self, audio_path: str, provider_name: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Transcribe an audio file using specified provider

        Args:
            audio_path: Path to audio file
            provider_name: Provider to use (local, openai, huggingface, deepgram)

        Returns:
            TranscriptionResult with text and segments
        """
        provider = self.get_provider(provider_name)
        return await provider.transcribe(audio_path)

    def list_available_providers(self) -> List[str]:
        """List all available and configured providers"""
        return [
            name for name, provider in self.providers.items() if provider.is_available()
        ]


# Global service instance
transcription_service = TranscriptionService()
