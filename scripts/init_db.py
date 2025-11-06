#!/usr/bin/env python3
"""
Initialize the database
"""
import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import init_db


async def main():
    print("Initializing database...")
    await init_db()
    print("✓ Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(main())
