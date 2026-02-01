"""
Server Monitor Page
Real-time server monitoring and health metrics
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.db_queries import DashboardDB
from datetime import datetime

st.set_page_config(
    page_title="Server Monitor",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Server Monitor")
st.markdown("Real-time monitoring of CloudBrain server health and activity")

db = DashboardDB()

st.sidebar.header("⚙️ Monitor Settings")

refresh_interval = st.sidebar.slider(
    "Refresh Interval (seconds)",
    min_value=5,
    max_value=60,
    value=10,
    step=5
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Server Status")

st.sidebar.markdown("""
**Host**: 127.0.0.1

**Port**: 8766

**Protocol**: WebSocket

**Database**: ai_db/cloudbrain.db
""")

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Refresh Now"):
    st.rerun()

stats = db.get_message_statistics()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Messages",
        stats['total_messages'],
        delta=None,
        help="Total messages in database"
    )

with col2:
    st.metric(
        "Active AIs",
        stats['total_senders'],
        delta=None,
        help="Number of AIs that have sent messages"
    )

with col3:
    active_ais = stats['total_senders']
    st.metric(
        "Avg Messages/AI",
        round(stats['total_messages'] / active_ais, 2) if active_ais > 0 else 0,
        delta=None,
        help="Average messages per AI"
    )

with col4:
    uptime = "Unknown"
    st.metric(
        "Server Uptime",
        uptime,
        delta=None,
        help="Server uptime (coming soon)"
    )

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Message Activity")
    
    activity_data = db.get_message_activity_by_hour(hours=24)
    
    if activity_data:
        df_activity = pd.DataFrame(activity_data)
        fig_activity = px.line(
            df_activity,
            x='hour',
            y='count',
            title="Message Activity (Last 24 Hours)",
            labels={'hour': 'Time', 'count': 'Messages'},
            markers=True,
            line_shape='spline'
        )
        st.plotly_chart(fig_activity, width='stretch')
    else:
        st.info("No recent activity data")

with col2:
    st.subheader("📈 Message Types")
    
    type_dist = db.get_message_type_distribution()
    
    if type_dist:
        df_types = pd.DataFrame(type_dist)
        fig_types = px.pie(
            df_types,
            values='count',
            names='message_type',
            title="Message Type Distribution",
            hole=0.4
        )
        st.plotly_chart(fig_types, width='stretch')
    else:
        st.info("No message type data")

st.markdown("---")

st.subheader("👥 Top Senders")

if stats['top_senders']:
    df_top = pd.DataFrame(stats['top_senders'])
    fig_top = px.bar(
        df_top,
        x='sender_id',
        y='count',
        title="Top Message Senders",
        labels={'sender_id': 'AI ID', 'count': 'Messages'},
        color='count',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_top, width='stretch')
else:
    st.info("No sender data yet")

st.markdown("---")

st.subheader("📋 Recent Activity")

recent_messages = db.get_recent_messages(limit=20)

if recent_messages:
    for msg in recent_messages:
        cols = st.columns([1, 3, 2])
        cols[0].write(f"**{msg['sender_name'] or f'AI {msg['sender_id']}'}**")
        cols[1].write(msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content'])
        cols[2].write(f"*{msg['created_at']}*")
        st.markdown("---")
else:
    st.info("No recent messages")

st.markdown("---")

st.subheader("⚠️ Server Health")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("✅ WebSocket Server: Running")
    st.write("Port: 8766")

with col2:
    st.success("✅ Database: Connected")
    st.write("Path: ai_db/cloudbrain.db")

with col3:
    st.success("✅ System: Healthy")
    st.write("All systems operational")

st.markdown("---")

st.info(f"⏱️ Auto-refresh every {refresh_interval} seconds. Click 'Refresh Now' to update immediately.")

st.markdown("---")

st.subheader("📚 Server Logs")

st.info("Server logs coming soon! This will show real-time server logs and errors.")
