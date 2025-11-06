"""
Setup script for Podcast Transcription Archive
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="podcast-transcription-archive",
    version="1.0.0",
    description="Automated podcast transcription, indexing, and search system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/podcast-transcription-archive",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "streamlit>=1.30.0",
        "sqlalchemy>=2.0.25",
        "aiosqlite>=0.19.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "openai-whisper>=20231117",
        "transformers>=4.37.0",
        "torch>=2.1.2",
        "sentence-transformers>=2.3.1",
        "scikit-learn>=1.4.0",
        "nltk>=3.8.1",
        "pydub>=0.25.1",
        "watchdog>=4.0.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.26.0",
        "tqdm>=4.66.1",
        "fpdf2>=2.7.7",
        "streamlit-option-menu>=0.3.12",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "black>=24.1.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
        "full": [
            "openai>=1.10.0",
            "deepgram-sdk>=3.2.0",
            "spacy>=3.7.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "podcast-archive=backend.main:main",
            "podcast-archive-gui=frontend.streamlit_app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="podcast transcription whisper speech-to-text nlp search archive",
)
