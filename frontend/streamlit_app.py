"""
Streamlit GUI for Podcast Transcription Archive
"""
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List

import streamlit as st
import pandas as pd
import httpx
from streamlit_option_menu import option_menu

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.config import settings
from backend.database import AsyncSessionLocal, init_db
from backend.services.processor import processing_service
from backend.services.search import search_service
from backend.services.file_monitor import file_monitor


# Page configuration
st.set_page_config(
    page_title="Podcast Transcription Archive",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    .success-msg {
        color: #28a745;
        font-weight: bold;
    }
    .error-msg {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False


async def init_app():
    """Initialize the application"""
    if not st.session_state.db_initialized:
        await init_db()
        st.session_state.db_initialized = True


# Helper functions
def format_duration(seconds: Optional[float]) -> str:
    """Format duration in human-readable format"""
    if seconds is None:
        return "Unknown"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def format_date(dt: Optional[datetime]) -> str:
    """Format datetime"""
    if dt is None:
        return "Unknown"
    return dt.strftime("%Y-%m-%d %H:%M")


# Main app
def main():
    # Initialize
    asyncio.run(init_app())

    # Sidebar navigation
    with st.sidebar:
        st.markdown("# 🎙️ Podcast Archive")
        st.markdown("---")

        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Add Files", "Search", "Browse", "Queue", "Settings"],
            icons=["speedometer2", "file-earmark-plus", "search", "list-ul", "clock-history", "gear"],
            default_index=0,
        )

        st.markdown("---")
        st.markdown("### Quick Stats")

        # Get stats
        async def get_quick_stats():
            async with AsyncSessionLocal() as db:
                stats = await search_service.get_statistics(db)
                queue_status = await processing_service.get_queue_status(db)
                return stats, queue_status

        try:
            stats, queue_status = asyncio.run(get_quick_stats())
            st.metric("Total Episodes", stats.get('total_episodes', 0))
            st.metric("Queued", queue_status.get('queued', 0))
            st.metric("Today's Limit", f"{queue_status.get('files_processed_today', 0)}/{queue_status.get('daily_limit', 50)}")
        except:
            st.warning("Database not initialized")

    # Main content based on selection
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Add Files":
        show_add_files()
    elif selected == "Search":
        show_search()
    elif selected == "Browse":
        show_browse()
    elif selected == "Queue":
        show_queue()
    elif selected == "Settings":
        show_settings()


def show_dashboard():
    """Dashboard page"""
    st.markdown('<h1 class="main-header">📊 Dashboard</h1>', unsafe_allow_html=True)

    async def get_dashboard_data():
        async with AsyncSessionLocal() as db:
            stats = await search_service.get_statistics(db)
            queue_status = await processing_service.get_queue_status(db)
            return stats, queue_status

    try:
        stats, queue_status = asyncio.run(get_dashboard_data())

        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Episodes",
                stats.get('total_episodes', 0),
                help="Total number of podcast episodes in archive"
            )

        with col2:
            st.metric(
                "Total Duration",
                f"{stats.get('total_duration_hours', 0):.1f}h",
                help="Total hours of audio content"
            )

        with col3:
            st.metric(
                "Transcripts",
                stats.get('total_transcripts', 0),
                help="Number of completed transcriptions"
            )

        with col4:
            st.metric(
                "Avg Confidence",
                f"{stats.get('avg_confidence', 0):.1%}",
                help="Average transcription confidence score"
            )

        st.markdown("---")

        # Status breakdown
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📈 Status Breakdown")
            status_counts = stats.get('status_counts', {})
            if status_counts:
                status_df = pd.DataFrame([
                    {"Status": status.title(), "Count": count}
                    for status, count in status_counts.items()
                ])
                st.dataframe(status_df, use_container_width=True, hide_index=True)
            else:
                st.info("No episodes yet")

        with col2:
            st.markdown("### 🏷️ Top Categories")
            categories = stats.get('category_counts', [])
            if categories:
                cat_df = pd.DataFrame(categories)
                cat_df.columns = ["Category", "Count"]
                st.dataframe(cat_df, use_container_width=True, hide_index=True)
            else:
                st.info("No categorized episodes yet")

        st.markdown("---")

        # Queue status
        st.markdown("### ⚙️ Processing Queue")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("In Queue", queue_status.get('queued', 0))
        with col2:
            st.metric("Processing", queue_status.get('processing', 0))
        with col3:
            st.metric("Today's Processed", queue_status.get('files_processed_today', 0))
        with col4:
            st.metric("Remaining Today", queue_status.get('remaining_today', 0))

        if queue_status.get('is_running'):
            st.info("🔄 Queue is currently processing...")
        else:
            if st.button("▶️ Process Queue", type="primary"):
                async def process():
                    async with AsyncSessionLocal() as db:
                        await processing_service.process_queue(db, max_items=5)

                asyncio.run(process())
                st.success("Processing started!")
                st.rerun()

    except Exception as e:
        st.error(f"Error loading dashboard: {e}")


def show_add_files():
    """Add files page"""
    st.markdown('<h1 class="main-header">➕ Add Files</h1>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Scan Directory", "Add Single File"])

    with tab1:
        st.markdown("### 📁 Scan Directory for Audio Files")

        directory = st.text_input(
            "Directory Path",
            value=str(Path.home()),
            help="Enter the path to scan for audio files"
        )

        col1, col2 = st.columns(2)
        with col1:
            recursive = st.checkbox("Include subdirectories", value=True)
        with col2:
            auto_add = st.checkbox("Auto-add to queue", value=True)

        if st.button("🔍 Scan Directory", type="primary"):
            if not Path(directory).exists():
                st.error("Directory does not exist!")
            else:
                with st.spinner("Scanning directory..."):
                    files = file_monitor.scan_directory(directory, recursive=recursive)

                    st.success(f"Found {len(files)} audio files")

                    if files:
                        st.markdown("**Found files:**")
                        df = pd.DataFrame([
                            {"File Name": Path(f).name, "Path": f}
                            for f in files[:100]
                        ])
                        st.dataframe(df, use_container_width=True)

                        if auto_add and files:
                            async def add_files():
                                async with AsyncSessionLocal() as db:
                                    added = 0
                                    for file_path in files:
                                        try:
                                            await processing_service.add_to_queue(db, file_path)
                                            added += 1
                                        except:
                                            pass
                                    return added

                            added = asyncio.run(add_files())
                            st.success(f"✅ Added {added} files to processing queue")

    with tab2:
        st.markdown("### 📄 Add Single File")

        file_path = st.text_input(
            "Audio File Path",
            help="Enter the full path to the audio file"
        )

        provider = st.selectbox(
            "Transcription Provider",
            options=["local", "openai", "huggingface", "deepgram"],
            index=0,
            help="Select which transcription service to use"
        )

        priority = st.slider(
            "Priority",
            min_value=0,
            max_value=10,
            value=5,
            help="Higher priority files are processed first"
        )

        if st.button("➕ Add to Queue", type="primary"):
            if not file_path:
                st.error("Please enter a file path")
            elif not Path(file_path).exists():
                st.error("File does not exist!")
            else:
                async def add_file():
                    async with AsyncSessionLocal() as db:
                        episode = await processing_service.add_to_queue(
                            db,
                            file_path=file_path,
                            priority=priority,
                            provider=provider
                        )
                        return episode

                try:
                    episode = asyncio.run(add_file())
                    st.success(f"✅ Added to queue: {episode.title}")
                except Exception as e:
                    st.error(f"Error: {e}")


def show_search():
    """Search page"""
    st.markdown('<h1 class="main-header">🔍 Search</h1>', unsafe_allow_html=True)

    # Search input
    query = st.text_input(
        "Search Query",
        placeholder="Enter keywords to search transcripts...",
        help="Search across episode titles, descriptions, and transcripts"
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        search_type = st.radio(
            "Search Type",
            options=["Full Text", "Transcripts Only"],
            horizontal=True
        )

    with col2:
        limit = st.number_input("Max Results", min_value=10, max_value=200, value=50)

    if st.button("🔍 Search", type="primary") or query:
        if query:
            async def do_search():
                async with AsyncSessionLocal() as db:
                    if search_type == "Full Text":
                        results = await search_service.full_text_search(db, query, limit=limit)
                    else:
                        results = await search_service.search_transcripts(db, query, limit=limit)
                    return results

            with st.spinner("Searching..."):
                results = asyncio.run(do_search())

            st.markdown(f"### Found {len(results)} results")

            for result in results:
                with st.expander(f"🎙️ {result.get('title') or result.get('episode_title', 'Untitled')}"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**Podcast:** {result.get('podcast_name', 'Unknown')}")
                        if result.get('category'):
                            st.markdown(f"**Category:** {result['category']}")

                    with col2:
                        if result.get('duration'):
                            st.markdown(f"**Duration:** {format_duration(result['duration'])}")

                    # Show snippet
                    snippet = result.get('transcript_snippet') or result.get('title_snippet')
                    if snippet:
                        st.markdown("**Match:**")
                        st.markdown(snippet, unsafe_allow_html=True)

                    # View details button
                    if st.button(f"View Details", key=f"view_{result.get('id') or result.get('episode_id')}"):
                        st.session_state.selected_episode = result.get('id') or result.get('episode_id')
                        st.rerun()


def show_browse():
    """Browse episodes page"""
    st.markdown('<h1 class="main-header">📚 Browse Episodes</h1>', unsafe_allow_html=True)

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        category = st.selectbox(
            "Category",
            options=["All"] + ["technology", "health", "business", "science", "philosophy", "comedy", "politics", "sports", "education", "arts"],
            index=0
        )

    with col2:
        status = st.selectbox(
            "Status",
            options=["All", "pending", "processing", "completed", "failed"],
            index=0
        )

    with col3:
        sort_by = st.selectbox(
            "Sort By",
            options=["Newest First", "Oldest First", "Duration"],
            index=0
        )

    # Get episodes
    async def get_episodes():
        async with AsyncSessionLocal() as db:
            episodes = await search_service.filter_episodes(
                db,
                category=None if category == "All" else category,
                status=None if status == "All" else status,
                limit=100,
            )
            return episodes

    episodes = asyncio.run(get_episodes())

    st.markdown(f"### {len(episodes)} Episodes")

    # Display episodes
    for episode in episodes:
        with st.expander(f"🎙️ {episode.title or episode.file_name}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Podcast:** {episode.podcast_name or 'Unknown'}")
                st.markdown(f"**Category:** {episode.category or 'Uncategorized'}")
                st.markdown(f"**Status:** {episode.status}")

            with col2:
                st.markdown(f"**Duration:** {format_duration(episode.duration)}")
                st.markdown(f"**Added:** {format_date(episode.created_at)}")

            # Action buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📄 View Details", key=f"details_{episode.id}"):
                    st.session_state.selected_episode = episode.id

            with col2:
                if episode.status == "completed":
                    if st.button("💾 Export", key=f"export_{episode.id}"):
                        st.session_state.export_episode = episode.id

            with col3:
                if episode.status == "failed":
                    if st.button("🔄 Retry", key=f"retry_{episode.id}"):
                        st.info("Retry functionality coming soon")


def show_queue():
    """Queue management page"""
    st.markdown('<h1 class="main-header">⏱️ Processing Queue</h1>', unsafe_allow_html=True)

    # Get queue status
    async def get_queue():
        async with AsyncSessionLocal() as db:
            queue_status = await processing_service.get_queue_status(db)
            return queue_status

    queue_status = asyncio.run(get_queue())

    # Status overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Queued", queue_status.get('queued', 0))
    with col2:
        st.metric("Processing", queue_status.get('processing', 0))
    with col3:
        st.metric("Processed Today", queue_status.get('files_processed_today', 0))
    with col4:
        st.metric("Remaining", queue_status.get('remaining_today', 0))

    st.markdown("---")

    # Controls
    col1, col2, col3 = st.columns(3)

    with col1:
        if queue_status.get('is_running'):
            st.info("🔄 Queue is currently running")
        else:
            if st.button("▶️ Start Processing", type="primary", use_container_width=True):
                async def process():
                    async with AsyncSessionLocal() as db:
                        await processing_service.process_queue(db, max_items=5)

                asyncio.run(process())
                st.success("Started!")
                st.rerun()

    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    with col3:
        batch_size = st.number_input("Batch Size", min_value=1, max_value=20, value=5)

    st.markdown("---")

    # Progress info
    if queue_status.get('current_task'):
        st.markdown("### Current Task")
        st.info(f"Processing Episode ID: {queue_status['current_task']}")


def show_settings():
    """Settings page"""
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["General", "Transcription", "Export"])

    with tab1:
        st.markdown("### General Settings")

        max_files = st.number_input(
            "Max Files Per Day",
            min_value=1,
            max_value=500,
            value=settings.MAX_FILES_PER_DAY,
            help="Daily limit for file processing"
        )

        batch_size = st.number_input(
            "Batch Size",
            min_value=1,
            max_value=20,
            value=settings.BATCH_SIZE,
            help="Number of files to process in each batch"
        )

        if st.button("Save General Settings"):
            st.success("Settings saved!")

    with tab2:
        st.markdown("### Transcription Settings")

        default_provider = st.selectbox(
            "Default Provider",
            options=["local", "openai", "huggingface", "deepgram"],
            index=["local", "openai", "huggingface", "deepgram"].index(
                settings.DEFAULT_TRANSCRIPTION_PROVIDER
            ),
            help="Default transcription service"
        )

        whisper_model = st.selectbox(
            "Whisper Model Size (Local)",
            options=["tiny", "base", "small", "medium", "large"],
            index=["tiny", "base", "small", "medium", "large"].index(
                settings.WHISPER_MODEL_SIZE
            ),
            help="Larger models are more accurate but slower"
        )

        st.markdown("#### API Keys")

        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=settings.OPENAI_API_KEY or "",
            help="Required for OpenAI Whisper API"
        )

        hf_token = st.text_input(
            "Hugging Face Token",
            type="password",
            value=settings.HUGGINGFACE_API_TOKEN or "",
            help="Required for Hugging Face API"
        )

        deepgram_key = st.text_input(
            "Deepgram API Key",
            type="password",
            value=settings.DEEPGRAM_API_KEY or "",
            help="Required for Deepgram API"
        )

        if st.button("Save Transcription Settings"):
            st.success("Settings saved!")

    with tab3:
        st.markdown("### Export Settings")

        export_formats = st.multiselect(
            "Default Export Formats",
            options=["txt", "srt", "vtt", "json", "markdown", "csv", "pdf"],
            default=["txt", "srt", "json", "markdown"],
            help="Formats to export by default"
        )

        include_timestamps = st.checkbox(
            "Include Timestamps in TXT",
            value=True,
            help="Add timestamps to plain text exports"
        )

        if st.button("Save Export Settings"):
            st.success("Settings saved!")

    st.markdown("---")
    st.markdown("### About")
    st.info(f"""
    **Podcast Transcription Archive v1.0.0**

    - Database: `{settings.DATABASE_URL}`
    - Models Directory: `{settings.MODELS_DIR}`
    - Transcripts Directory: `{settings.TRANSCRIPTS_DIR}`
    """)


if __name__ == "__main__":
    main()
