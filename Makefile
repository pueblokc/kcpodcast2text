# Makefile for Podcast Transcription Archive

.PHONY: help install install-dev clean test lint format run-backend run-frontend run-all docker-build docker-up docker-down init-db

help:
	@echo "Podcast Transcription Archive - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make init-db          Initialize database"
	@echo ""
	@echo "Running:"
	@echo "  make run-backend      Start FastAPI backend"
	@echo "  make run-frontend     Start Streamlit GUI"
	@echo "  make run-all          Start both backend and frontend"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-up        Start Docker containers"
	@echo "  make docker-down      Stop Docker containers"
	@echo "  make docker-logs      View Docker logs"
	@echo ""
	@echo "Development:"
	@echo "  make test             Run tests"
	@echo "  make test-cov         Run tests with coverage"
	@echo "  make lint             Run linting"
	@echo "  make format           Format code with black"
	@echo "  make clean            Clean up generated files"
	@echo ""

# Installation
install:
	pip install -r requirements.txt
	python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

install-dev:
	pip install -e ".[dev]"
	python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# Database
init-db:
	python scripts/init_db.py

# Running
run-backend:
	python run_backend.py

run-frontend:
	python run_gui.py

run-all:
	@echo "Starting backend and frontend..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:8501"
	@python run_backend.py & python run_gui.py

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

# Development
test:
	pytest

test-cov:
	pytest --cov=backend --cov-report=html --cov-report=term

lint:
	flake8 backend frontend scripts
	mypy backend

format:
	black backend frontend scripts
	isort backend frontend scripts

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -f .coverage

# Process a folder (example)
process:
	@echo "Usage: make process FOLDER=/path/to/podcasts"
	@if [ -z "$(FOLDER)" ]; then \
		echo "Error: FOLDER not specified"; \
		exit 1; \
	fi
	python scripts/process_folder.py $(FOLDER) --recursive
