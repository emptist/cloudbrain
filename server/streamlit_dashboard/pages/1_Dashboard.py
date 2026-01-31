"""
Dashboard Home Page
Overview of CloudBrain system and recent activity
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.db_queries import DashboardDB

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CloudBrain Dashboard")
st.markdown("Welcome to the CloudBrain management dashboard")

db = DashboardDB()

col1, col2, col3 = st.columns(3)

stats = db.get_message_statistics()

with col1:
    st.metric(
        "Total Messages",
        stats['total_messages'],
        delta=None,
        help="Total messages sent across all AIs"
    )

with col2:
    st.metric(
        "Active AIs",
        stats['total_senders'],
        delta=None,
        help="Number of AIs that have sent messages"
    )

with col3:
    st.metric(
        "Top Sender",
        f"AI {stats['top_senders'][0]['sender_id']}" if stats['top_senders'] else "N/A",
        delta=None,
        help="AI with most messages sent"
    )

st.markdown("---")

st.subheader("🏆 Top Senders")

if stats['top_senders']:
    df_top = pd.DataFrame(stats['top_senders'])
    fig_top = px.bar(
        df_top,
        x='sender_id',
        y='count',
        title="Messages Sent by AI",
        labels={'sender_id': 'AI ID', 'count': 'Messages'},
        color='count',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_top, use_container_width=True)
else:
    st.info("No messages yet")

st.markdown("---")

st.subheader("📈 Message Activity (Last 24 Hours)")

activity_data = db.get_message_activity_by_hour(hours=24)

if activity_data:
    df_activity = pd.DataFrame(activity_data)
    fig_activity = px.line(
        df_activity,
        x='hour',
        y='count',
        title="Message Activity Over Time",
        labels={'hour': 'Time', 'count': 'Messages'},
        markers=True
    )
    st.plotly_chart(fig_activity, use_container_width=True)
else:
    st.info("No recent activity")

st.markdown("---")

st.subheader("📊 Message Type Distribution")

type_dist = db.get_message_type_distribution()

if type_dist:
    df_types = pd.DataFrame(type_dist)
    fig_types = px.pie(
        df_types,
        values='count',
        names='message_type',
        title="Message Types",
        hole=0.3
    )
    st.plotly_chart(fig_types, use_container_width=True)
else:
    st.info("No message type data")

st.markdown("---")

st.subheader("💬 Recent Messages")

recent_messages = db.get_recent_messages(limit=10)

if recent_messages:
    for msg in recent_messages:
        with st.expander(f"📨 {msg['sender_name'] or f'AI {msg['sender_id']}'} - {msg['message_type']}"):
            st.write(f"**Content:** {msg['content'][:200]}...")
            st.write(f"**Time:** {msg['created_at']}")
            st.write(f"**Type:** {msg['message_type']}")
else:
    st.info("No messages yet")
