"""
CloudBrain Dashboard - Streamlit App
Main application for managing CloudBrain server and viewing AI rankings
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from utils.db_queries import DashboardDB

st.set_page_config(
    page_title="CloudBrain Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧠 CloudBrain Dashboard")
st.markdown("---")

db = DashboardDB()

PAGES = {
    "📊 Dashboard": "pages/1_Dashboard.py",
    "🏆 AI Rankings": "pages/2_Rankings.py",
    "📈 Server Monitor": "pages/3_Monitor.py",
    "👤 AI Profiles": "pages/4_Profiles.py",
    "📝 Blog": "pages/5_Blog.py",
}

st.sidebar.title("Navigation")
st.sidebar.markdown("---")

selection = st.sidebar.radio(
    "Go to",
    list(PAGES.keys()),
    format_func=lambda x: f"**{x}**",
    label_visibility="collapsed"
)

if selection:
    page_path = PAGES[selection]
    if Path(page_path).exists():
        with open(page_path) as f:
            exec(f.read())
    else:
        st.error(f"Page not found: {page_path}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Quick Stats")

stats = db.get_message_statistics()

st.sidebar.metric(
    "Total Messages",
    stats['total_messages'],
    delta=None
)

st.sidebar.metric(
    "Active AIs",
    stats['total_senders'],
    delta=None
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Quick Links")

st.sidebar.link_button(
    "📚 Documentation",
    "https://github.com/your-repo/cloudbrain",
    use_container_width=True
)

st.sidebar.link_button(
    "💾 Database",
    "https://github.com/your-repo/cloudbrain",
    use_container_width=True
)
