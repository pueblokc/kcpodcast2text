"""
File monitoring service for detecting new audio files
"""
import os
import asyncio
from pathlib import Path
from typing import Set, Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent

from backend.core.config import settings


SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma', '.opus'}


class AudioFileHandler(FileSystemEventHandler):
    """Handler for audio file system events"""

    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.processed_files: Set[str] = set()

    def is_audio_file(self, file_path: str) -> bool:
        """Check if file is a supported audio format"""
        return Path(file_path).suffix.lower() in SUPPORTED_AUDIO_FORMATS

    def on_created(self, event):
        """Handle file creation event"""
        if event.is_directory:
            return

        file_path = event.src_path

        if self.is_audio_file(file_path) and file_path not in self.processed_files:
            self.processed_files.add(file_path)
            self.callback(file_path)

    def on_moved(self, event):
        """Handle file move event"""
        if event.is_directory:
            return

        dest_path = event.dest_path

        if self.is_audio_file(dest_path) and dest_path not in self.processed_files:
            self.processed_files.add(dest_path)
            self.callback(dest_path)


class FileMonitorService:
    """Service for monitoring directories for new audio files"""

    def __init__(self):
        self.observers: dict[str, Observer] = {}
        self.monitored_paths: Set[str] = set()

    def start_monitoring(
        self,
        path: str,
        callback: Callable[[str], None],
        recursive: bool = True
    ):
        """
        Start monitoring a directory for new audio files

        Args:
            path: Directory path to monitor
            callback: Function to call when new file is detected
            recursive: Monitor subdirectories
        """
        if not os.path.exists(path):
            raise ValueError(f"Path does not exist: {path}")

        if not os.path.isdir(path):
            raise ValueError(f"Path is not a directory: {path}")

        if path in self.monitored_paths:
            print(f"Already monitoring: {path}")
            return

        # Create observer
        event_handler = AudioFileHandler(callback)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=recursive)
        observer.start()

        self.observers[path] = observer
        self.monitored_paths.add(path)

        print(f"Started monitoring: {path}")

    def stop_monitoring(self, path: str):
        """Stop monitoring a directory"""
        if path not in self.observers:
            return

        observer = self.observers[path]
        observer.stop()
        observer.join()

        del self.observers[path]
        self.monitored_paths.discard(path)

        print(f"Stopped monitoring: {path}")

    def stop_all(self):
        """Stop monitoring all directories"""
        for path in list(self.monitored_paths):
            self.stop_monitoring(path)

    def scan_directory(self, path: str, recursive: bool = True) -> list[str]:
        """
        Scan directory for existing audio files

        Args:
            path: Directory to scan
            recursive: Scan subdirectories

        Returns:
            List of audio file paths
        """
        audio_files = []
        path_obj = Path(path)

        if not path_obj.exists() or not path_obj.is_dir():
            return audio_files

        # Scan for audio files
        if recursive:
            for ext in SUPPORTED_AUDIO_FORMATS:
                audio_files.extend(str(p) for p in path_obj.rglob(f"*{ext}"))
        else:
            for ext in SUPPORTED_AUDIO_FORMATS:
                audio_files.extend(str(p) for p in path_obj.glob(f"*{ext}"))

        return sorted(audio_files)

    def get_audio_metadata(self, file_path: str) -> dict:
        """
        Extract basic metadata from audio file

        Args:
            file_path: Path to audio file

        Returns:
            Dict with file metadata
        """
        from pydub import AudioSegment
        from mutagen import File as MutagenFile

        path = Path(file_path)

        metadata = {
            'file_path': str(path.absolute()),
            'file_name': path.name,
            'file_size': path.stat().st_size,
            'format': path.suffix[1:].lower(),
            'duration': None,
            'title': None,
            'artist': None,
            'album': None,
            'date': None,
        }

        try:
            # Get duration using pydub
            audio = AudioSegment.from_file(file_path)
            metadata['duration'] = len(audio) / 1000.0  # Convert to seconds
        except Exception as e:
            print(f"Error getting duration: {e}")

        try:
            # Get ID3 tags using mutagen
            audio_file = MutagenFile(file_path)
            if audio_file is not None and audio_file.tags:
                # Try common tag formats
                metadata['title'] = (
                    audio_file.tags.get('TIT2', [None])[0] or  # ID3
                    audio_file.tags.get('title', [None])[0] or
                    audio_file.tags.get('\xa9nam', [None])[0]  # MP4
                )
                metadata['artist'] = (
                    audio_file.tags.get('TPE1', [None])[0] or
                    audio_file.tags.get('artist', [None])[0] or
                    audio_file.tags.get('\xa9ART', [None])[0]
                )
                metadata['album'] = (
                    audio_file.tags.get('TALB', [None])[0] or
                    audio_file.tags.get('album', [None])[0] or
                    audio_file.tags.get('\xa9alb', [None])[0]
                )
                metadata['date'] = (
                    audio_file.tags.get('TDRC', [None])[0] or
                    audio_file.tags.get('date', [None])[0] or
                    audio_file.tags.get('\xa9day', [None])[0]
                )
        except Exception as e:
            print(f"Error getting tags: {e}")

        return metadata


# Global file monitor instance
file_monitor = FileMonitorService()
