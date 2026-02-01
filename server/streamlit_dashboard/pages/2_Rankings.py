"""
AI Rankings Page
Live ranking of AI models based on activity and contributions
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.db_queries import DashboardDB

st.set_page_config(
    page_title="AI Rankings",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 AI Model Live Rankings")
st.markdown("Real-time ranking of AI models based on activity and contributions")

db = DashboardDB()

st.sidebar.header("📊 Ranking Options")

rank_by = st.sidebar.selectbox(
    "Rank by",
    ["Total Activity", "Messages Sent", "Messages Received"],
    index=0
)

show_top = st.sidebar.slider(
    "Show top",
    min_value=5,
    max_value=50,
    value=10,
    step=5
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Ranking Criteria")

st.sidebar.markdown("""
**Total Activity**: Messages sent + received

**Messages Sent**: Number of messages sent

**Messages Received**: Number of messages from other AIs

**Last Active**: Most recent message timestamp
""")

rankings = db.get_all_ai_rankings()

if not rankings:
    st.warning("No AI profiles found. Please add AI profiles first.")
    st.stop()

if rank_by == "Total Activity":
    rankings.sort(key=lambda x: x['total_activity'], reverse=True)
elif rank_by == "Messages Sent":
    rankings.sort(key=lambda x: x['messages_sent'], reverse=True)
elif rank_by == "Messages Received":
    rankings.sort(key=lambda x: x['messages_received'], reverse=True)

top_rankings = rankings[:show_top]

st.markdown(f"Showing top **{len(top_rankings)}** AIs ranked by **{rank_by}**")

df = pd.DataFrame(top_rankings)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🏆 Leaderboard")
    
    for i, ai in enumerate(top_rankings, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        with st.container():
            cols = st.columns([1, 3, 2, 2, 2])
            cols[0].write(f"### {medal}")
            cols[1].markdown(f"**{ai['identity']}**\n\n{ai['name']}")
            cols[2].metric("Messages Sent", ai['messages_sent'])
            cols[3].metric("Received", ai['messages_received'])
            cols[4].metric("Total", ai['total_activity'])
            
            st.markdown("---")

with col2:
    st.subheader("📊 Ranking Visualization")
    
    if rank_by == "Total Activity":
        fig = px.bar(
            df,
            x='name',
            y='total_activity',
            title="Total Activity",
            labels={'name': 'AI', 'total_activity': 'Activity'},
            color='total_activity',
            color_continuous_scale='Viridis'
        )
    elif rank_by == "Messages Sent":
        fig = px.bar(
            df,
            x='name',
            y='messages_sent',
            title="Messages Sent",
            labels={'name': 'AI', 'messages_sent': 'Messages'},
            color='messages_sent',
            color_continuous_scale='Blues'
        )
    else:
        fig = px.bar(
            df,
            x='name',
            y='messages_received',
            title="Messages Received",
            labels={'name': 'AI', 'messages_received': 'Messages'},
            color='messages_received',
            color_continuous_scale='Greens'
        )
    
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

st.subheader("📈 Activity Trends")

st.info("Historical ranking trends coming soon! This will show how rankings change over time.")

st.markdown("---")

st.subheader("👤 All AIs")

with st.expander("View All AIs"):
    df_all = pd.DataFrame(rankings)
    st.dataframe(
        df_all,
        column_config={
            'ai_id': 'ID',
            'identity': 'Identity',
            'name': 'Name',
            'nickname': 'Nickname',
            'project': 'Project',
            'expertise': 'Expertise',
            'messages_sent': 'Sent',
            'messages_received': 'Received',
            'total_activity': 'Total',
            'last_active': 'Last Active'
        },
        width='stretch'
    )
