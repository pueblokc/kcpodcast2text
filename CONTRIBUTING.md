# Contributing to Podcast Transcription Archive

First off, thank you for considering contributing! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Error messages and logs**

### Suggesting Features

Feature suggestions are welcome! Please provide:

- **Clear description** of the feature
- **Use case** - why is it needed?
- **Examples** of how it would work
- **Alternatives considered**

### Pull Requests

1. **Fork** the repo
2. **Create a branch** from `main`
   ```bash
   git checkout -b feature/my-feature
   ```
3. **Make changes** with clear commits
4. **Add tests** if applicable
5. **Update documentation**
6. **Run tests** and linting
   ```bash
   pytest
   black .
   flake8
   ```
7. **Submit PR** with description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/podcast-transcription-archive.git
cd podcast-transcription-archive

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## Code Style

- Follow **PEP 8**
- Use **type hints**
- Write **docstrings** for functions/classes
- Keep functions **focused and small**
- Use **meaningful variable names**

### Example:

```python
async def transcribe_audio(
    self,
    audio_path: str,
    provider_name: Optional[str] = None
) -> TranscriptionResult:
    """
    Transcribe an audio file using specified provider

    Args:
        audio_path: Path to audio file
        provider_name: Provider to use (local, openai, etc.)

    Returns:
        TranscriptionResult with text and segments

    Raises:
        ValueError: If provider is not available
    """
    # Implementation...
```

## Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for >80% coverage

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test
pytest tests/test_transcription.py -v
```

## Documentation

- Update README for new features
- Add docstrings to new functions
- Update API docs if endpoints change
- Include examples where helpful

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add support for Deepgram API
fix: resolve database locking issue
docs: update installation instructions
test: add tests for export service
refactor: simplify search query logic
```

## Project Structure

```
backend/
├── api/           # API endpoints
├── core/          # Configuration
├── database/      # Models and DB operations
├── services/      # Business logic
│   ├── transcription.py
│   ├── nlp.py
│   ├── search.py
│   └── ...
└── main.py

frontend/
└── streamlit_app.py

tests/
├── test_transcription.py
├── test_search.py
└── ...
```

## Areas That Need Help

- [ ] Additional transcription providers
- [ ] Improved speaker diarization
- [ ] Multi-language support
- [ ] Performance optimizations
- [ ] Mobile-responsive UI
- [ ] Additional export formats
- [ ] Better error handling
- [ ] More comprehensive tests

## Questions?

- Open an issue with the "question" label
- Join our discussions
- Email the maintainers

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- No harassment or discrimination

## Recognition

Contributors will be acknowledged in:
- README contributors section
- Release notes
- Project documentation

Thank you for contributing! 🙌
