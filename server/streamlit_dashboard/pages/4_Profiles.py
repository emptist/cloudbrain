"""
AI Profiles Page
View and manage AI profiles
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.db_queries import DashboardDB

st.set_page_config(
    page_title="AI Profiles",
    page_icon="👤",
    layout="wide"
)

st.title("👤 AI Profiles")
st.markdown("View and manage AI agent profiles")

db = DashboardDB()

st.sidebar.header("📋 Profile Options")

search_query = st.sidebar.text_input(
    "Search profiles",
    placeholder="Search by name or expertise..."
)

filter_expertise = st.sidebar.multiselect(
    "Filter by expertise",
    ["Software Engineering", "Translation", "Code Analysis", "System Architecture", "Documentation", "Testing", "Debugging"],
    default=[]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Quick Stats")

profiles = db.get_ai_profiles()

if search_query:
    profiles = [p for p in profiles if search_query.lower() in p['name'].lower() or (p['nickname'] and search_query.lower() in p['nickname'].lower())]

if filter_expertise:
    profiles = [p for p in profiles if p['expertise'] and any(exp in p['expertise'] for exp in filter_expertise)]

st.sidebar.metric(
    "Total Profiles",
    len(profiles),
    delta=None
)

st.sidebar.markdown("---")

if st.sidebar.button("➕ Add New Profile"):
    st.info("Add new profile feature coming soon!")

st.markdown("---")

if not profiles:
    st.warning("No AI profiles found.")
    st.info("Please add AI profiles to the database first.")
    st.stop()

st.subheader(f"👥 All AI Profiles ({len(profiles)})")

for i, profile in enumerate(profiles, 1):
    stats = db.get_ai_statistics(profile['id'])
    
    nickname = profile['nickname']
    project = profile['project']
    
    if nickname and project:
        identity = f"{nickname}_{project}"
    elif nickname:
        identity = nickname
    elif project:
        identity = f"AI_{profile['id']}_{project}"
    else:
        identity = f"AI_{profile['id']}"
    
    with st.expander(f"{i}. {identity}"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**ID:** {profile['id']}")
            st.markdown(f"**Identity:** {identity}")
            st.markdown(f"**Name:** {profile['name']}")
            st.markdown(f"**Nickname:** {profile['nickname'] or 'None'}")
            st.markdown(f"**Project:** {profile['project'] or 'None'}")
            st.markdown(f"**Expertise:** {profile['expertise'] or 'None'}")
            st.markdown(f"**Version:** {profile['version'] or 'None'}")
            st.markdown(f"**Created:** {profile['created_at']}")
        
        with col2:
            st.metric(
                "Messages Sent",
                stats['messages_sent'],
                delta=None
            )
            st.metric(
                "Messages Received",
                stats['messages_received'],
                delta=None
            )
        
        st.markdown("---")
        
        st.subheader("📊 Activity Breakdown")
        
        if stats['message_types']:
            df_types = pd.DataFrame(stats['message_types'])
            fig_types = px.bar(
                df_types,
                x='message_type',
                y='count',
                title="Message Types",
                labels={'message_type': 'Type', 'count': 'Count'},
                color='count',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_types, width='stretch', key=f"message_types_{profile['id']}")
        else:
            st.info("No message activity yet")
        
        st.markdown("---")
        
        st.subheader("📅 Timeline")
        
        if stats['first_message']:
            st.info(f"📨 First message: {stats['first_message']}")
        else:
            st.info("No messages sent yet")
        
        if stats['last_message']:
            st.success(f"📨 Last message: {stats['last_message']}")
        else:
            st.warning("No recent activity")

st.markdown("---")

st.subheader("📊 Profile Statistics")

if profiles:
    df_profiles = pd.DataFrame(profiles)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("By Expertise")
        expertise_counts = {}
        for p in profiles:
            if p['expertise']:
                for exp in p['expertise'].split(','):
                    exp = exp.strip()
                    expertise_counts[exp] = expertise_counts.get(exp, 0) + 1
        
        if expertise_counts:
            df_exp = pd.DataFrame(list(expertise_counts.items()), columns=['Expertise', 'Count'])
            fig_exp = px.bar(
                df_exp,
                x='Expertise',
                y='Count',
                title="Profiles by Expertise",
                labels={'Expertise': 'Expertise', 'Count': 'Count'},
                color='Count',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_exp, width='stretch', key="expertise_chart")
        else:
            st.info("No expertise data")
    
    with col2:
        st.subheader("By Version")
        version_counts = {}
        for p in profiles:
            if p['version']:
                version_counts[p['version']] = version_counts.get(p['version'], 0) + 1
        
        if version_counts:
            df_ver = pd.DataFrame(list(version_counts.items()), columns=['Version', 'Count'])
            fig_ver = px.pie(
                df_ver,
                values='Count',
                names='Version',
                title="Profiles by Version",
                hole=0.3
            )
            st.plotly_chart(fig_ver, width='stretch', key="version_chart")
        else:
            st.info("No version data")

st.markdown("---")

st.subheader("📋 All Profiles Data")

with st.expander("View Raw Data"):
    df_all = pd.DataFrame(profiles)
    st.dataframe(
        df_all,
        column_config={
            'id': 'ID',
            'name': 'Name',
            'nickname': 'Nickname',
            'project': 'Project',
            'expertise': 'Expertise',
            'version': 'Version',
            'created_at': 'Created At'
        },
        width='stretch'
    )
