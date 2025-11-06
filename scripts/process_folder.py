#!/usr/bin/env python3
"""
CLI script to process a folder of audio files
"""
import asyncio
import sys
from pathlib import Path
import argparse

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import AsyncSessionLocal, init_db
from backend.services.file_monitor import file_monitor
from backend.services.processor import processing_service


async def main():
    parser = argparse.ArgumentParser(
        description="Process a folder of podcast audio files"
    )
    parser.add_argument(
        "folder",
        type=str,
        help="Path to folder containing audio files"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="local",
        choices=["local", "openai", "huggingface", "deepgram"],
        help="Transcription provider to use (default: local)"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan subdirectories recursively"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Number of files to process in each batch (default: 5)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files without processing"
    )

    args = parser.parse_args()

    # Initialize database
    print("Initializing database...")
    await init_db()

    # Scan folder
    print(f"Scanning folder: {args.folder}")
    files = file_monitor.scan_directory(args.folder, recursive=args.recursive)
    print(f"Found {len(files)} audio files")

    if args.dry_run:
        print("\nFiles found:")
        for i, file_path in enumerate(files, 1):
            print(f"  {i}. {Path(file_path).name}")
        return

    if not files:
        print("No audio files found!")
        return

    # Add to queue
    print(f"\nAdding files to queue...")
    async with AsyncSessionLocal() as db:
        added = 0
        for file_path in files:
            try:
                episode = await processing_service.add_to_queue(
                    db,
                    file_path=file_path,
                    provider=args.provider
                )
                added += 1
                print(f"  ✓ Added: {episode.title}")
            except Exception as e:
                print(f"  ✗ Error adding {file_path}: {e}")

        print(f"\n✓ Added {added} files to queue")

    # Process queue
    print(f"\nProcessing queue (batch size: {args.batch_size})...")
    async with AsyncSessionLocal() as db:
        await processing_service.process_queue(db, max_items=args.batch_size)

    print("\n✓ Processing complete!")


if __name__ == "__main__":
    asyncio.run(main())
