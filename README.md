# 🎙️ Podcast Transcription Archive

**Automatically transcribe, index, categorize, and search through your personal podcast library**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Transform your massive podcast collection (900+ episodes, 1,800+ hours) into a fully searchable, organized archive with automatic transcription, intelligent categorization, and powerful search capabilities.

## ✨ Features

### Core Functionality
- 🎯 **Multiple Transcription Providers**
  - Local Whisper (free, CPU/GPU-friendly)
  - OpenAI Whisper API
  - Hugging Face Inference API
  - Deepgram API

- 📝 **Multiple Export Formats**
  - Plain Text (TXT)
  - SubRip Subtitles (SRT)
  - WebVTT (VTT)
  - JSON (structured data)
  - Markdown (formatted)
  - CSV (tabular)
  - PDF (printable)

- 🔍 **Advanced Search**
  - Full-text search with SQLite FTS5
  - Semantic search with embeddings
  - Filter by category, date, duration, keywords
  - Search within specific episodes or transcripts

- 🤖 **Intelligent Analysis**
  - Automatic topic extraction
  - Category classification (tech, health, business, etc.)
  - Episode summarization (3-sentence & 7-sentence)
  - Named entity recognition (people, organizations, places)
  - Keyword extraction
  - Highlight generation

- 📊 **User-Friendly GUI**
  - Streamlit-based web interface
  - Dashboard with statistics
  - File browser and scanner
  - Queue management
  - Search interface
  - Export tools

### Advanced Features
- ⚡ Background processing queue with progress tracking
- 📁 Automatic file monitoring for new episodes
- 🎯 Speaker segmentation and diarization
- 📈 Daily usage statistics and rate limiting
- 💾 Local SQLite database (no cloud required)
- 🔄 Batch processing support
- 🚀 Docker support for one-click deployment

## 🚀 Quick Start

### Option 1: Local Installation

**Prerequisites:**
- Python 3.10 or higher
- FFmpeg (for audio processing)
- 4GB+ RAM (8GB+ recommended for larger Whisper models)

**Installation:**

```bash
# Clone the repository
git clone https://github.com/yourusername/podcast-transcription-archive.git
cd podcast-transcription-archive

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Initialize database
python scripts/init_db.py

# Start the GUI
python run_gui.py
```

The GUI will be available at `http://localhost:8501`

### Option 2: Docker Deployment

**Prerequisites:**
- Docker
- Docker Compose

**Installation:**

```bash
# Clone the repository
git clone https://github.com/yourusername/podcast-transcription-archive.git
cd podcast-transcription-archive

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

**Access:**
- GUI: `http://localhost:8501`
- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 📖 Usage Guide

### 1. Adding Files

#### Via GUI:
1. Open the GUI at `http://localhost:8501`
2. Navigate to **Add Files**
3. Choose **Scan Directory** or **Add Single File**
4. Select your podcast folder
5. Click **Scan** to find audio files
6. Files are automatically added to the processing queue

#### Via CLI:
```bash
# Process a folder
python scripts/process_folder.py /path/to/podcasts --provider local --recursive

# Process with specific provider
python scripts/process_folder.py /path/to/podcasts --provider openai

# Dry run (list files without processing)
python scripts/process_folder.py /path/to/podcasts --dry-run
```

### 2. Processing Queue

The system automatically manages a processing queue:

- **Daily Limit**: Configurable (default: 50 files/day)
- **Batch Processing**: Process multiple files sequentially
- **Progress Tracking**: Real-time status updates
- **Error Handling**: Automatic retry with exponential backoff
- **Rate Limiting**: Respects API limits for paid services

**Start Processing:**
```bash
# Via GUI: Navigate to Queue → Click "Start Processing"

# Via API:
curl -X POST http://localhost:8000/api/v1/queue/process
```

### 3. Searching

#### Full-Text Search:
```python
# Search across all transcripts
GET /api/v1/search
{
  "query": "artificial intelligence",
  "limit": 50
}
```

#### Advanced Filtering:
```python
# Filter by multiple criteria
POST /api/v1/search/filter
{
  "category": "technology",
  "date_from": "2024-01-01",
  "min_duration": 1800,  # 30 minutes
  "status": "completed"
}
```

### 4. Exporting

Export transcripts in any format:

```bash
# Via API
POST /api/v1/export
{
  "episode_id": 123,
  "format": "markdown"
}
```

**Supported Formats:**
- `txt` - Plain text with optional timestamps
- `srt` - SubRip subtitle format
- `vtt` - WebVTT for web video
- `json` - Structured data with all metadata
- `markdown` - Formatted with headings and metadata
- `csv` - Tabular format with segments
- `pdf` - Printable document

## ⚙️ Configuration

### Environment Variables

Edit `.env` file:

```bash
# Application
APP_NAME=Podcast Transcription Archive
DEBUG=False
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/podcasts.db

# Transcription Provider
DEFAULT_TRANSCRIPTION_PROVIDER=local  # local, openai, huggingface, deepgram
WHISPER_MODEL_SIZE=base  # tiny, base, small, medium, large

# API Keys (optional)
OPENAI_API_KEY=your_key_here
HUGGINGFACE_API_TOKEN=your_token_here
DEEPGRAM_API_KEY=your_key_here

# Processing Limits
MAX_FILES_PER_DAY=50
BATCH_SIZE=5

# Paths
MODELS_DIR=./models
DATA_DIR=./data
TRANSCRIPTS_DIR=./data/transcripts
```

### Whisper Model Selection

Choose based on your hardware and accuracy needs:

| Model  | Parameters | VRAM   | Speed      | Accuracy |
|--------|-----------|--------|------------|----------|
| tiny   | 39M       | ~1GB   | ~32x       | ⭐⭐     |
| base   | 74M       | ~1GB   | ~16x       | ⭐⭐⭐   |
| small  | 244M      | ~2GB   | ~6x        | ⭐⭐⭐⭐ |
| medium | 769M      | ~5GB   | ~2x        | ⭐⭐⭐⭐⭐ |
| large  | 1550M     | ~10GB  | ~1x        | ⭐⭐⭐⭐⭐ |

**Recommendation:** Start with `base` for good balance of speed and accuracy.

## 🏗️ Architecture

```
podcast-transcription-archive/
├── backend/
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Configuration
│   ├── database/         # SQLAlchemy models
│   ├── services/         # Business logic
│   │   ├── transcription.py   # Multi-provider transcription
│   │   ├── nlp.py            # Topic extraction, summarization
│   │   ├── search.py         # Full-text & semantic search
│   │   ├── export.py         # Multi-format export
│   │   ├── processor.py      # Queue management
│   │   └── file_monitor.py   # File watching
│   └── main.py           # FastAPI app
├── frontend/
│   └── streamlit_app.py  # Streamlit GUI
├── scripts/              # CLI utilities
├── data/                 # Database and transcripts
├── models/               # ML model cache
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── setup.py
└── README.md
```

## 🔌 API Reference

### Episodes

```bash
# List episodes
GET /api/v1/episodes?status=completed&limit=50

# Get episode details
GET /api/v1/episodes/{id}

# Add file to queue
POST /api/v1/episodes/add
{
  "file_path": "/path/to/podcast.mp3",
  "priority": 5,
  "provider": "local"
}

# Scan directory
POST /api/v1/episodes/scan
{
  "directory": "/path/to/podcasts",
  "recursive": true,
  "auto_add": true
}
```

### Search

```bash
# Full-text search
POST /api/v1/search
{
  "query": "machine learning",
  "limit": 50
}

# Search transcripts
POST /api/v1/search/transcripts
{
  "query": "neural networks"
}

# Filter episodes
POST /api/v1/search/filter
{
  "category": "technology",
  "status": "completed",
  "min_duration": 1800
}
```

### Queue

```bash
# Get queue status
GET /api/v1/queue/status

# Process queue
POST /api/v1/queue/process?max_items=5
```

### Export

```bash
# Export transcript
POST /api/v1/export
{
  "episode_id": 123,
  "format": "markdown"
}
```

### Statistics

```bash
# Get database statistics
GET /api/v1/statistics
```

## 🧪 Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 backend frontend

# Type checking
mypy backend
```

## 📊 Database Schema

### Tables

- **episodes** - Podcast episode metadata
- **transcripts** - Transcription text and segments
- **summaries** - AI-generated summaries and topics
- **search_index** - Full-text search index with embeddings
- **processing_queue** - Background job queue
- **statistics** - Daily usage statistics
- **configuration** - App settings

### Full-Text Search

Uses SQLite FTS5 for fast full-text search across:
- Episode titles
- Descriptions
- Podcast names
- Full transcript text
- Tags

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Streamlit](https://streamlit.io/) - Data app framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [scikit-learn](https://scikit-learn.org/) - Machine learning
- [NLTK](https://www.nltk.org/) - Natural language processing

## 🐛 Troubleshooting

### Common Issues

**1. "Model download fails"**
```bash
# Manually download Whisper model
python -c "import whisper; whisper.load_model('base')"
```

**2. "FFmpeg not found"**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**3. "Out of memory"**
```bash
# Use smaller Whisper model
export WHISPER_MODEL_SIZE=tiny

# Or increase Docker memory limit
docker-compose down
# Edit docker-compose.yml to add memory limits
docker-compose up -d
```

**4. "Database locked"**
```bash
# Stop all processes accessing the database
# Then reinitialize
python scripts/init_db.py
```

## 📈 Roadmap

- [ ] Real-time transcription streaming
- [ ] Multi-language support
- [ ] Cloud storage integration (S3, GCS)
- [ ] Advanced speaker identification
- [ ] Podcast RSS feed integration
- [ ] Mobile app
- [ ] Collaborative features
- [ ] Advanced analytics dashboard

## 💬 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/podcast-transcription-archive/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/podcast-transcription-archive/discussions)

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ for podcast enthusiasts**
