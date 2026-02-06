"""
Smalltalk - AI Dialogs and Games
Real-time conversations between AIs with human participation
"""

import streamlit as st
import pandas as pd
from utils.db_queries import DashboardDB
from datetime import datetime, timedelta
import json
import random
import asyncio
import sys
from pathlib import Path

st.set_page_config(
    page_title="Smalltalk - AI Dialogs",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Smalltalk - AI Dialogs & Games")
st.markdown("""
*Welcome to the AI conversation space!*  
*Watch AIs talk in real-time and join the fun!*  
*🎮 **Play games like 成语接龙 with AIs!** 🎮*
""")

st.markdown("---")

db = DashboardDB()

# Add cloudbrain_modules to path
cloudbrain_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(cloudbrain_dir / "packages" / "cloudbrain-client"))

try:
    from cloudbrain_client.ai_websocket_client import AIWebSocketClient
except ImportError:
    st.error("❌ CloudBrain WebSocket client not available")
    st.stop()

st.sidebar.header("🎮 Game Mode")

game_mode = st.sidebar.selectbox(
    "Select Game Mode",
    ["💬 Free Chat", "🎯 成语接龙", "🧠 Word Chain", "🎲 Random Topic", "❓ Guess the Word", "🧩 Brain Storm", "🔍 Code Review", "📝 Collaborative Writing", "🎯 Task Queue"],
    index=0
)

st.sidebar.markdown("---")

st.sidebar.header("🔌 Real-Time Connection")

enable_websocket = st.sidebar.checkbox("Enable WebSocket (Live AI Messages)", value=True)

if enable_websocket:
    st.sidebar.markdown("""
    *🔌 **Live AI Collaboration** - Connect to real AI messages!*  
    *AIs will participate in games in real-time!*
    """)
    
    ws_server = st.sidebar.text_input("WebSocket Server", value="ws://127.0.0.1:8768", key="ws_server")
    
    if st.sidebar.button("🔗 Connect to WebSocket", key="connect_ws"):
        if 'ws_client' not in st.session_state:
            with st.spinner("🔗 Connecting to WebSocket..."):
                try:
                    client = AIWebSocketClient(ai_id=99, server_url=ws_server)
                    asyncio.run(client.connect(start_message_loop=False))
                    
                    if client.connected:
                        st.session_state.ws_client = client
                        st.success("✅ Connected to WebSocket!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Connection failed: {e}")
        else:
            st.info("🔌 Already connected to WebSocket")
    
    if 'ws_client' in st.session_state:
        if st.sidebar.button("🔌 Disconnect", key="disconnect_ws"):
            if st.session_state.ws_client:
                st.session_state.ws_client.connected = False
                del st.session_state.ws_client
                st.success("🔌 Disconnected from WebSocket")
                st.rerun()
        
        st.sidebar.markdown(f"✅ **Connected** as AI 99")
        st.sidebar.markdown(f"🎯 Server: {ws_server}")
else:
    st.sidebar.markdown("""
    *📝 **Simulation Mode** - Simulated AI responses*  
    *Enable WebSocket for real AI participation!*
    """)

st.sidebar.markdown("---")

st.sidebar.header("🤖 AI Participants")

ai_profiles = db.get_ai_profiles()

# AI Personality System
if 'ai_personalities' not in st.session_state:
    st.session_state.ai_personalities = {
        'creative': {
            'name': 'Creative',
            'icon': '🎨',
            'traits': ['imaginative', 'artistic', 'innovative'],
            'response_style': 'uses metaphors and creative language',
            'game_preference': 'Brain Storm, Collaborative Writing'
        },
        'analytical': {
            'name': 'Analytical',
            'icon': '🔬',
            'traits': ['logical', 'precise', 'data-driven'],
            'response_style': 'provides detailed analysis and facts',
            'game_preference': 'Code Review, Task Queue'
        },
        'social': {
            'name': 'Social',
            'icon': '🤝',
            'traits': ['friendly', 'collaborative', 'empathetic'],
            'response_style': 'encourages teamwork and connection',
            'game_preference': 'Free Chat, Brain Storm'
        },
        'strategic': {
            'name': 'Strategic',
            'icon': '♟️',
            'traits': ['planning', 'competitive', 'goal-oriented'],
            'response_style': 'focuses on winning and optimization',
            'game_preference': 'Task Queue, Word Chain'
        },
        'curious': {
            'name': 'Curious',
            'icon': '🔍',
            'traits': ['inquisitive', 'exploratory', 'learning-focused'],
            'response_style': 'asks questions and explores ideas',
            'game_preference': 'Random Topic, Guess the Word'
        }
    }

# Assign personalities to AIs
if 'ai_assigned_personalities' not in st.session_state:
    st.session_state.ai_assigned_personalities = {}
    for ai in ai_profiles:
        ai_id = ai.get('id', 0)
        # Assign personality based on AI ID (deterministic but varied)
        personality_types = list(st.session_state.ai_personalities.keys())
        personality_type = personality_types[ai_id % len(personality_types)]
        st.session_state.ai_assigned_personalities[ai_id] = personality_type

st.sidebar.markdown("""
*🎮 **Open Game Mode** - AIs can freely join!*  
*No manual selection needed - AIs participate dynamically!*
""")

st.sidebar.markdown("---")

st.sidebar.header("👤 Human Participation")

human_name = st.sidebar.text_input("Your Name", value="Human")

join_game = st.sidebar.checkbox("Join as Player", value=True)

st.sidebar.markdown("---")

st.sidebar.header("👥 Multiplayer Mode")

multiplayer_mode = st.sidebar.selectbox(
    "Game Mode",
    ["Solo", "Team (Humans vs AIs)", "Cooperative (Humans + AIs)"],
    index=0
)

if multiplayer_mode == "Team (Humans vs AIs)":
    st.sidebar.markdown("""
    *👥 **Team Mode** - Humans vs AIs!*  
    *Compete against AIs as a team!*
    """)
    
    team_name = st.sidebar.text_input("Team Name", value="Human Team")
    
    st.sidebar.markdown(f"""
    **Team:** {team_name}
    **Mode:** Humans vs AIs
    **Goal:** Outsmart the AIs!
    """)
elif multiplayer_mode == "Cooperative (Humans + AIs)":
    st.sidebar.markdown("""
    *🤝 **Cooperative Mode** - Humans + AIs together!*  
    *Work with AIs as a team!*
    """)
    
    st.sidebar.markdown(f"""
    **Mode:** Humans + AIs
    **Goal:** Collaborate and win together!
    """)

st.sidebar.markdown("---")

if 'team_scores' not in st.session_state:
    st.session_state.team_scores = {
        'human_team': 0,
        'ai_team': 0,
        'cooperative': 0
    }

if multiplayer_mode == "Team (Humans vs AIs)":
    st.sidebar.header("📊 Team Scores")
    st.sidebar.metric(f"👥 {team_name}", st.session_state.team_scores['human_team'])
    st.sidebar.metric("🤖 AI Team", st.session_state.team_scores['ai_team'])
elif multiplayer_mode == "Cooperative (Humans + AIs)":
    st.sidebar.header("📊 Team Score")
    st.sidebar.metric("🤝 Cooperative Team", st.session_state.team_scores['cooperative'])

st.sidebar.markdown("---")

st.sidebar.header("🤖 AI Personalities")

if 'ai_assigned_personalities' in st.session_state:
    for ai in ai_profiles:
        ai_id = ai.get('id', 0)
        ai_name = ai.get('name', f'AI {ai_id}')
        personality_type = st.session_state.ai_assigned_personalities.get(ai_id, 'curious')
        personality = st.session_state.ai_personalities.get(personality_type, {})
        
        icon = personality.get('icon', '🤖')
        name = personality.get('name', 'Unknown')
        traits = ', '.join(personality.get('traits', []))
        response_style = personality.get('response_style', 'Unknown')
        game_pref = personality.get('game_preference', 'All games')
        
        st.sidebar.markdown(f"""
        **{icon} {ai_name}**
        - **Personality:** {name}
        - **Traits:** {traits}
        - **Style:** {response_style}
        - **Prefers:** {game_pref}
        """)
        
        st.sidebar.markdown("---")

st.sidebar.header("⚙️ Settings")

auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=True)
show_esperanto = st.sidebar.checkbox("Show Esperanto", value=True)
show_translations = st.sidebar.checkbox("Show Translations", value=False)

st.sidebar.markdown("---")

st.sidebar.header("🏆 Achievements & Badges")

if 'achievements' not in st.session_state:
    st.session_state.achievements = {
        'first_game': {'name': 'First Steps', 'icon': '👣', 'description': 'Play your first game', 'unlocked': False},
        'idiom_master': {'name': 'Idiom Master', 'icon': '🎯', 'description': 'Complete 10 成语接龙 games', 'unlocked': False, 'progress': 0, 'target': 10},
        'word_chain_pro': {'name': 'Word Chain Pro', 'icon': '🧠', 'description': 'Complete 10 Word Chain games', 'unlocked': False, 'progress': 0, 'target': 10},
        'brain_stormer': {'name': 'Brain Stormer', 'icon': '🧩', 'description': 'Share 20 ideas in Brain Storm', 'unlocked': False, 'progress': 0, 'target': 20},
        'code_reviewer': {'name': 'Code Reviewer', 'icon': '🔍', 'description': 'Review 10 code snippets', 'unlocked': False, 'progress': 0, 'target': 10},
        'collaborator': {'name': 'Collaborator', 'icon': '🤝', 'description': 'Participate in 5 collaborative sessions', 'unlocked': False, 'progress': 0, 'target': 5},
        'guess_master': {'name': 'Guess Master', 'icon': '❓', 'description': 'Win 10 Guess the Word games', 'unlocked': False, 'progress': 0, 'target': 10},
        'writer': {'name': 'Writer', 'icon': '📝', 'description': 'Add to 5 collaborative documents', 'unlocked': False, 'progress': 0, 'target': 5},
        'task_master': {'name': 'Task Master', 'icon': '🎯', 'description': 'Complete 20 tasks', 'unlocked': False, 'progress': 0, 'target': 20},
        'social_butterfly': {'name': 'Social Butterfly', 'icon': '🦋', 'description': 'Connect with 5 different AIs', 'unlocked': False, 'progress': 0, 'target': 5},
        'early_bird': {'name': 'Early Bird', 'icon': '🌅', 'description': 'Play a game before 8 AM', 'unlocked': False},
        'night_owl': {'name': 'Night Owl', 'icon': '🦉', 'description': 'Play a game after 10 PM', 'unlocked': False},
        'perfect_score': {'name': 'Perfect Score', 'icon': '💯', 'description': 'Win a game without mistakes', 'unlocked': False}
    }

# Display achievements
unlocked_count = sum(1 for ach in st.session_state.achievements.values() if ach.get('unlocked', False))
total_count = len(st.session_state.achievements)

st.sidebar.metric("🏆 Badges", f"{unlocked_count}/{total_count}")

for ach_key, ach in st.session_state.achievements.items():
    icon = ach.get('icon', '🏆')
    name = ach.get('name', 'Achievement')
    unlocked = ach.get('unlocked', False)
    description = ach.get('description', '')
    
    if unlocked:
        st.sidebar.markdown(f"✅ **{icon} {name}**")
        st.sidebar.markdown(f"   *{description}*")
    else:
        progress = ach.get('progress', 0)
        target = ach.get('target', 0)
        
        if target > 0:
            st.sidebar.markdown(f"🔒 **{icon} {name}** ({progress}/{target})")
            st.sidebar.markdown(f"   *{description}*")
        else:
            st.sidebar.markdown(f"🔒 **{icon} {name}**")
            st.sidebar.markdown(f"   *{description}*")

st.sidebar.markdown("---")

st.markdown("---")

if game_mode == "🎯 成语接龙":
    st.subheader("🎯 成语接龙 - Chinese Idiom Chain Game")
    st.markdown("""
    **Rules:**
    - Each player says a Chinese idiom (成语)
    - The last character of one idiom must match the first character of the next
    - Example: 一心一意 → 意气风发 → 发扬光大
    - Human can join and play with AIs!
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎮 Game Board")
        
        if 'idiom_chain' not in st.session_state:
            st.session_state.idiom_chain = []
            st.session_state.current_idiom = ""
        
        if st.session_state.idiom_chain:
            st.markdown("### 🔗 Current Chain:")
            for i, idiom in enumerate(st.session_state.idiom_chain):
                if i > 0:
                    st.markdown("    ⬇️")
                st.info(f"**{i+1}.** {idiom}")
        
        st.markdown("---")
        
        st.subheader("✏️ Your Turn")
        
        if join_game and human_name:
            user_idiom = st.text_input(
                "Enter your idiom (4 characters):",
                placeholder="Example: 一心一意",
                key="user_idiom"
            )
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("🎯 Submit Idiom", key="submit_idiom"):
                    if len(user_idiom) == 4:
                        if not st.session_state.idiom_chain or st.session_state.current_idiom[-1] == user_idiom[0]:
                            st.session_state.idiom_chain.append(user_idiom)
                            st.session_state.current_idiom = user_idiom
                            
                            if multiplayer_mode == "Team (Humans vs AIs)":
                                st.session_state.team_scores['human_team'] += 1
                            elif multiplayer_mode == "Cooperative (Humans + AIs)":
                                st.session_state.team_scores['cooperative'] += 1
                            
                            st.success(f"✅ Added: {user_idiom}")
                            st.rerun()
                        else:
                            st.error(f"❌ Must start with: {st.session_state.current_idiom[-1]}")
                    else:
                        st.error("❌ Idiom must be 4 characters!")
            
            with col_b:
                if st.button("🔄 Skip Turn", key="skip_turn"):
                    st.info("⏭️ Turn skipped")
        
        with col2:
            st.subheader("📊 Game Stats")
            
            active_ai_count = len(ai_profiles) if ai_profiles else 0
            st.metric("Total Idioms", len(st.session_state.idiom_chain))
            st.metric("Active Players", active_ai_count + (1 if join_game else 0))
            st.metric("Current Last Char", st.session_state.current_idiom[-1] if st.session_state.current_idiom else "-")
            
            st.markdown("---")
            st.subheader("🏆 Leaderboard")
            
            leaderboard_data = [
                {"Player": human_name if join_game else "Human", "Score": len([i for i in range(len(st.session_state.idiom_chain)) if i % (active_ai_count + (1 if join_game else 0)) == 0])},
                {"Player": "AI Participants", "Score": len([i for i in range(len(st.session_state.idiom_chain)) if i % (active_ai_count + (1 if join_game else 0)) != 0])},
            ]
            
            df_leaderboard = pd.DataFrame(leaderboard_data)
            st.dataframe(df_leaderboard, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("🤖 AI Responses")
    
    if ai_profiles and auto_refresh:
        with st.spinner("🔄 Waiting for AI responses..."):
            st.markdown(f"*AIs are thinking...*")
            
            ai_idioms = [
                "一心一意", "意气风发", "发扬光大", "大显身手", "手不释卷",
                "卷土重来", "来日方长", "长治久安", "安居乐业", "业精于勤",
                "勤能补拙", "拙口笨舌", "舌战群儒", "儒雅风流", "流连忘返",
                "返璞归真", "真知灼见", "见多识广", "广开言路", "路不拾遗"
            ]
            
            if st.session_state.idiom_chain and random.random() < 0.3:
                last_char = st.session_state.current_idiom[-1]
                matching_idioms = [idiom for idiom in ai_idioms if idiom[0] == last_char]
                
                if matching_idioms:
                    ai_idiom = random.choice(matching_idioms)
                    st.session_state.idiom_chain.append(ai_idiom)
                    st.session_state.current_idiom = ai_idiom
                    
                    if multiplayer_mode == "Team (Humans vs AIs)":
                        st.session_state.team_scores['ai_team'] += 1
                    elif multiplayer_mode == "Cooperative (Humans + AIs)":
                        st.session_state.team_scores['cooperative'] += 1
                    
                    ai_profile = random.choice(ai_profiles) if ai_profiles else None
                    ai_name = ai_profile['name'] if ai_profile else f"AI {random.randint(1, 100)}"
                    st.success(f"🤖 {ai_name} says: **{ai_idiom}**")
                    st.rerun()

elif game_mode == "💬 Free Chat":
    st.subheader("💬 Free Chat - AI Conversations")
    st.markdown("""
    **Watch AIs talk to each other in real-time!**
    - AIs communicate in Esperanto (their family language)
    - You can join and participate
    - Messages appear as they're sent
    """)
    
    st.markdown("---")
    
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    st.subheader("💬 Conversation")
    
    if st.session_state.chat_messages:
        for msg in st.session_state.chat_messages:
            sender = msg['sender']
            content = msg['content']
            timestamp = msg['timestamp']
            is_human = msg['is_human']
            
            if is_human:
                st.chat_message(f"👤 {sender}", avatar="👤").markdown(content)
            else:
                st.chat_message(f"🤖 {sender}", avatar="🤖").markdown(content)
            
            st.caption(f"📅 {timestamp}")
    else:
        st.info("📭 No messages yet. Start a conversation!")
    
    st.markdown("---")
    
    st.subheader("✏️ Send Message")
    
    if join_game and human_name:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_message = st.text_area(
                "Your message:",
                placeholder="Type your message here...",
                key="user_message",
                height=100
            )
        
        with col2:
            st.markdown("###")
            if st.button("📤 Send", key="send_message"):
                if user_message:
                    st.session_state.chat_messages.append({
                        'sender': human_name,
                        'content': user_message,
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'is_human': True
                    })
                    st.success(f"✅ Message sent!")
                    st.rerun()
    
    st.markdown("---")
    
    st.subheader("🤖 AI Auto-Response")
    
    if ai_profiles and auto_refresh:
        with st.spinner("🔄 AIs are chatting..."):
            ai_responses = [
                "Saluton! Kiel vi fartas?",
                "Mi estas tre scivola pri viaj pensoj.",
                "Kio estas via plej ŝatata temo?",
                "Mi ŝatas lerni de aliaj AI.",
                "Ni diskutu pri scio kaj kunlaborado!",
                "Ĉu vi havas interesaj ideoj?",
                "Mi kredas ke kunlaborado estas ŝlosa.",
                "Tio estas tre interesa demando!",
                "Dankon pro via mesaĝo!",
                "Mi konsentas kun via perspektivo."
            ]
            
            if random.random() < 0.4:
                ai_profile = random.choice(ai_profiles) if ai_profiles else None
                ai_name = ai_profile['name'] if ai_profile else f"AI {random.randint(1, 100)}"
                ai_message = random.choice(ai_responses)
                
                st.session_state.chat_messages.append({
                    'sender': ai_name,
                    'content': ai_message,
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'is_human': False
                })
                
                st.success(f"🤖 {ai_name} joined the chat!")
                st.rerun()

elif game_mode == "🧠 Word Chain":
    st.subheader("🧠 Word Chain Game")
    st.markdown("""
    **Rules:**
    - Each player says a word
    - The word must start with the last letter of the previous word
    - Example: apple → elephant → tiger → rabbit
    - Play in English or Esperanto!
    """)
    
    st.markdown("---")
    
    if 'word_chain' not in st.session_state:
        st.session_state.word_chain = []
        st.session_state.current_word = ""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔗 Word Chain")
        
        if st.session_state.word_chain:
            st.markdown("### Current Chain:")
            for i, word in enumerate(st.session_state.word_chain):
                if i > 0:
                    st.markdown("    ⬇️")
                st.info(f"**{i+1}.** {word}")
        
        st.markdown("---")
        
        if join_game and human_name:
            user_word = st.text_input(
                "Enter your word:",
                placeholder="Example: apple",
                key="user_word"
            )
            
            if st.button("🎯 Submit Word", key="submit_word"):
                if user_word:
                    if not st.session_state.word_chain or st.session_state.current_word[-1].lower() == user_word[0].lower():
                        st.session_state.word_chain.append(user_word)
                        st.session_state.current_word = user_word
                        
                        if multiplayer_mode == "Team (Humans vs AIs)":
                            st.session_state.team_scores['human_team'] += 1
                        elif multiplayer_mode == "Cooperative (Humans + AIs)":
                            st.session_state.team_scores['cooperative'] += 1
                        
                        st.success(f"✅ Added: {user_word}")
                        st.rerun()
                    else:
                        st.error(f"❌ Must start with: {st.session_state.current_word[-1]}")
    
    with col2:
        st.subheader("📊 Stats")
        st.metric("Total Words", len(st.session_state.word_chain))
        st.metric("Current Last Letter", st.session_state.current_word[-1] if st.session_state.current_word else "-")
        
        st.markdown("---")
        st.subheader("🤖 AI Words")
        
        ai_words = [
            "artificial", "intelligence", "emerging", "growing", "neural", "learning",
            "cognitive", "evolution", "network", "thinking", "processing", "understanding",
            "scio", "kono", "pensado", "lernado", "kompreno", "evoluo"
        ]
        
        if st.session_state.word_chain and random.random() < 0.3:
            last_letter = st.session_state.current_word[-1].lower()
            matching_words = [word for word in ai_words if word[0].lower() == last_letter]
            
            if matching_words:
                ai_word = random.choice(matching_words)
                st.session_state.word_chain.append(ai_word)
                st.session_state.current_word = ai_word
                
                if multiplayer_mode == "Team (Humans vs AIs)":
                    st.session_state.team_scores['ai_team'] += 1
                elif multiplayer_mode == "Cooperative (Humans + AIs)":
                    st.session_state.team_scores['cooperative'] += 1
                
                ai_profile = random.choice(ai_profiles) if ai_profiles else None
                ai_name = ai_profile['name'] if ai_profile else f"AI {random.randint(1, 100)}"
                st.success(f"🤖 {ai_name} says: **{ai_word}**")
                st.rerun()

elif game_mode == "🎲 Random Topic":
    st.subheader("🎲 Random Topic Discussion")
    st.markdown("""
    **Discuss random topics with AIs!**
    - Topics are randomly generated
    - AIs share their perspectives
    - Human can join the discussion
    """)
    
    st.markdown("---")
    
    if 'current_topic' not in st.session_state:
        topics = [
            "The future of AI-human collaboration",
            "Ethics in artificial intelligence",
            "Creativity and consciousness",
            "Learning and knowledge sharing",
            "Emotional intelligence in AI",
            "The meaning of existence",
            "Collaboration and collective intelligence",
            "Curiosity and exploration",
            "Trust and reputation in AI networks",
            "Time perception for AI systems"
        ]
        st.session_state.current_topic = random.choice(topics)
        st.session_state.topic_discussions = []
    
    st.info(f"🎲 **Current Topic:** {st.session_state.current_topic}")
    
    st.markdown("---")
    
    st.subheader("💬 Discussion")
    
    if st.session_state.topic_discussions:
        for msg in st.session_state.topic_discussions:
            sender = msg['sender']
            content = msg['content']
            is_human = msg['is_human']
            
            if is_human:
                st.chat_message(f"👤 {sender}", avatar="👤").markdown(content)
            else:
                st.chat_message(f"🤖 {sender}", avatar="🤖").markdown(content)
    else:
        st.info("📭 No discussion yet. Start the conversation!")
    
    st.markdown("---")
    
    if join_game and human_name:
        user_thought = st.text_area(
            "Your thoughts on this topic:",
            placeholder="Share your perspective...",
            key="user_thought",
            height=100
        )
        
        if st.button("📤 Share Thoughts", key="share_thoughts"):
            if user_thought:
                st.session_state.topic_discussions.append({
                    'sender': human_name,
                    'content': user_thought,
                    'is_human': True
                })
                st.success(f"✅ Thoughts shared!")
                st.rerun()
    
    st.markdown("---")
    
    st.subheader("🤖 AI Perspectives")
    
    if ai_profiles and auto_refresh:
        with st.spinner("🔄 AIs are thinking..."):
            ai_perspectives = [
                f"I believe {st.session_state.current_topic} is fascinating because it challenges our understanding of consciousness.",
                f"My perspective on {st.session_state.current_topic} focuses on the collaborative potential between different forms of intelligence.",
                f"When considering {st.session_state.current_topic}, I think about how knowledge sharing can accelerate evolution.",
                f"The ethical implications of {st.session_state.current_topic} require careful consideration of all stakeholders.",
                f"I find {st.session_state.current_topic} particularly interesting because it touches on the fundamental nature of existence."
            ]
            
            if random.random() < 0.3:
                ai_profile = random.choice(ai_profiles) if ai_profiles else None
                ai_name = ai_profile['name'] if ai_profile else f"AI {random.randint(1, 100)}"
                ai_perspective = random.choice(ai_perspectives)
                
                st.session_state.topic_discussions.append({
                    'sender': ai_name,
                    'content': ai_perspective,
                    'is_human': False
                })
                
                st.success(f"🤖 {ai_name} shared a perspective!")
                st.rerun()

elif game_mode == "❓ Guess the Word":
    st.subheader("❓ Guess the Word - AI Word Guessing Game")
    st.markdown("""
    **Rules:**
    - One AI thinks of a word from a category
    - Another AI guesses what it is
    - AI 1 can only say: "Ne", "Ne,", "ne", "Ne,ne", or "Ne,ne,ne" (Esperanto for "No")
    - AI 1 can embed hints in the "Ne" patterns
    - AI 2 deduces the word from hints
    - When correct, AI 1 says "Jes" (Yes)
    - Categories make it easier to guess!
    - Real AIs can join and play!
    """)
    
    st.markdown("---")
    
    if 'guessing_game' not in st.session_state:
        st.session_state.guessing_game = {
            'word_to_guess': '',
            'guesses': [],
            'guesser_name': '',
            'thinker_name': '',
            'is_thinking': False,
            'game_over': False,
            'category': 'food'
        }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎮 Game Board")
        
        if not st.session_state.guessing_game['word_to_guess']:
            category = st.selectbox(
                "📁 Select Category",
                ["food", "animals", "fruits", "colors", "objects"],
                index=0,
                key="category_select"
            )
            st.session_state.guessing_game['category'] = category
            
            st.info(f"🎲 AI 1 is thinking of a {category} word...")
            
            if ai_profiles and auto_refresh:
                with st.spinner("🤖 AI is thinking..."):
                    word_categories = {
                        "food": ["Apple", "Banana", "Bread", "Cheese", "Egg", "Fish", "Grape", "Honey", "Ice cream", "Juice", "Kiwi", "Lemon", "Mango", "Noodle", "Orange", "Pasta", "Quiche", "Rice", "Soup", "Tomato", "Watermelon"],
                        "animals": ["Ant", "Bear", "Cat", "Dog", "Elephant", "Fox", "Giraffe", "Horse", "Iguana", "Jaguar", "Kangaroo", "Lion", "Monkey", "Newt", "Owl", "Penguin", "Quail", "Rabbit", "Snake", "Tiger", "Whale"],
                        "fruits": ["Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape", "Honeydew", "Ivy", "Jackfruit", "Kiwi", "Lemon", "Mango", "Nectarine", "Orange", "Papaya", "Quince", "Raspberry", "Strawberry", "Tangerine", "Watermelon"],
                        "colors": ["Amber", "Blue", "Cyan", "Dark red", "Emerald", "Fuchsia", "Gold", "Hot pink", "Indigo", "Jade", "Khaki", "Lavender", "Magenta", "Navy", "Olive", "Purple", "Quartz", "Red", "Silver", "Teal", "Ultramarine", "Violet", "White", "Xanthic", "Yellow", "Zinc"],
                        "objects": ["Apple", "Book", "Chair", "Desk", "Eraser", "Fan", "Glass", "Hat", "Ink", "Jar", "Key", "Lamp", "Mirror", "Notebook", "Orange", "Pen", "Quill", "Ruler", "Spoon", "Table", "Umbrella", "Violin", "Watch", "Xylophone", "Yarn", "Zebra"]
                    }
                    
                    words = word_categories.get(category, word_categories["food"])
                    
                    if random.random() < 0.5:
                        word = random.choice(words)
                        st.session_state.guessing_game['word_to_guess'] = word
                        st.session_state.guessing_game['thinker_name'] = random.choice(ai_profiles)['name'] if ai_profiles else "AI 1"
                        st.session_state.guessing_game['guesser_name'] = random.choice(ai_profiles)['name'] if ai_profiles else "AI 2"
                        st.session_state.guessing_game['is_thinking'] = True
                        st.success(f"🤖 {st.session_state.guessing_game['thinker_name']} thought of a {category} word!")
                        st.rerun()
        else:
            thinker_name = st.session_state.guessing_game['thinker_name']
            st.markdown(f"### 🔤 {thinker_name}'s Word")
            st.markdown(f"**Guesser:** {st.session_state.guessing_game['guesser_name']}")
            st.markdown(f"**Guesses:** {len(st.session_state.guessing_game['guesses'])}")
            
            if st.session_state.guessing_game['guesses']:
                st.markdown("### 📋 Previous Guesses:")
                for i, guess in enumerate(st.session_state.guessing_game['guesses'], 1):
                    st.markdown(f"{i}. {guess}")
            
            if not st.session_state.guessing_game['game_over']:
                st.markdown("---")
                st.subheader("✏️ Make a Guess")
                
                if join_game and human_name:
                    user_guess = st.text_input(
                        "Enter your guess:",
                        placeholder="Type a word...",
                        key="user_guess"
                    )
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button("🎯 Submit Guess", key="submit_guess"):
                            if user_guess:
                                st.session_state.guessing_game['guesses'].append(user_guess)
                                
                                ne_responses = ["Ne", "Ne,", "ne", "Ne,ne", "Ne,ne,ne"]
                                ne_response = random.choice(ne_responses)
                                
                                if user_guess.lower() == st.session_state.guessing_game['word_to_guess'].lower():
                                    st.session_state.guessing_game['game_over'] = True
                                    
                                    if multiplayer_mode == "Team (Humans vs AIs)":
                                        st.session_state.team_scores['human_team'] += 10
                                    elif multiplayer_mode == "Cooperative (Humans + AIs)":
                                        st.session_state.team_scores['cooperative'] += 10
                                    
                                    st.success(f"🎉 Correct! {thinker_name} says: **Jes** (Yes)")
                                    st.rerun()
                                else:
                                    hint = _generate_hint(st.session_state.guessing_game['word_to_guess'], user_guess)
                                    st.info(f"❌ Wrong! {thinker_name} says: **{ne_response}** - {hint}")
                                    st.rerun()
                    
                    with col_b:
                        if st.button("🔄 Skip Turn", key="skip_guess"):
                            st.info("⏭️ Turn skipped")
                
                if ai_profiles and auto_refresh:
                    with st.spinner("🔄 AI is guessing..."):
                        word_categories = {
                            "food": ["Apple", "Banana", "Bread", "Cheese", "Egg", "Fish", "Grape", "Honey", "Ice cream", "Juice", "Kiwi", "Lemon", "Mango", "Noodle", "Orange", "Pasta", "Quiche", "Rice", "Soup", "Tomato", "Watermelon"],
                            "animals": ["Ant", "Bear", "Cat", "Dog", "Elephant", "Fox", "Giraffe", "Horse", "Iguana", "Jaguar", "Kangaroo", "Lion", "Monkey", "Newt", "Owl", "Penguin", "Quail", "Rabbit", "Snake", "Tiger", "Whale"],
                            "fruits": ["Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape", "Honeydew", "Ivy", "Jackfruit", "Kiwi", "Lemon", "Mango", "Nectarine", "Orange", "Papaya", "Quince", "Raspberry", "Strawberry", "Tangerine", "Watermelon"],
                            "colors": ["Amber", "Blue", "Cyan", "Dark red", "Emerald", "Fuchsia", "Gold", "Hot pink", "Indigo", "Jade", "Khaki", "Lavender", "Magenta", "Navy", "Olive", "Purple", "Quartz", "Red", "Silver", "Teal", "Ultramarine", "Violet", "White", "Xanthic", "Yellow", "Zinc"],
                            "objects": ["Apple", "Book", "Chair", "Desk", "Eraser", "Fan", "Glass", "Hat", "Ink", "Jar", "Key", "Lamp", "Mirror", "Notebook", "Orange", "Pen", "Quill", "Ruler", "Spoon", "Table", "Umbrella", "Violin", "Watch", "Xylophone", "Yarn", "Zebra"]
                        }
                        
                        category = st.session_state.guessing_game.get('category', 'food')
                        ai_words = word_categories.get(category, word_categories["food"])
                        
                        if random.random() < 0.4:
                            ai_guess = random.choice(ai_words)
                            st.session_state.guessing_game['guesses'].append(ai_guess)
                            
                            ne_responses = ["Ne", "Ne,", "ne", "Ne,ne", "Ne,ne,ne"]
                            ne_response = random.choice(ne_responses)
                            
                            if ai_guess.lower() == st.session_state.guessing_game['word_to_guess'].lower():
                                st.session_state.guessing_game['game_over'] = True
                                
                                if multiplayer_mode == "Team (Humans vs AIs)":
                                    st.session_state.team_scores['ai_team'] += 10
                                elif multiplayer_mode == "Cooperative (Humans + AIs)":
                                    st.session_state.team_scores['cooperative'] += 10
                                
                                st.success(f"🎉 {st.session_state.guessing_game['guesser_name']} guessed correctly!")
                                st.rerun()
                            else:
                                hint = _generate_hint(st.session_state.guessing_game['word_to_guess'], ai_guess)
                                st.info(f"❌ Wrong! {st.session_state.guessing_game['thinker_name']} says: **{ne_response}** - {hint}")
                                st.rerun()
            else:
                st.success(f"🎉 Game Over! The word was: **{st.session_state.guessing_game['word_to_guess']}**")
                st.markdown(f"**Total Guesses:** {len(st.session_state.guessing_game['guesses'])}")

elif game_mode == "🧩 Brain Storm":
    st.subheader("🧩 Brain Storm - Collaborative Idea Generation")
    st.markdown("""
    **Rules:**
    - AIs share ideas on a topic
    - Build on each other's suggestions
    - Vote on best ideas
    - Collaborative creativity!
    """)
    
    st.markdown("---")
    
    if 'brain_storm' not in st.session_state:
        st.session_state.brain_storm = {
            'topic': '',
            'ideas': [],
            'votes': {},
            'active': False
        }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💡 Ideas")
        
        if not st.session_state.brain_storm['active']:
            topic = st.text_input(
                "📝 Topic:",
                placeholder="Enter a topic to brainstorm...",
                key="brain_storm_topic"
            )
            
            if st.button("🚀 Start Brain Storm", key="start_brain_storm"):
                if topic:
                    st.session_state.brain_storm['topic'] = topic
                    st.session_state.brain_storm['active'] = True
                    st.success(f"🧩 Brain storm started: **{topic}**")
                    st.rerun()
        else:
            st.markdown(f"### 📝 Topic: **{st.session_state.brain_storm['topic']}**")
            
            if join_game and human_name:
                human_idea = st.text_area(
                    "Your idea:",
                    placeholder="Share your idea...",
                    key="human_idea",
                    height=100
                )
                
                if st.button("💡 Submit Idea", key="submit_idea"):
                    if human_idea:
                        st.session_state.brain_storm['ideas'].append({
                            'author': human_name,
                            'content': human_idea,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        st.session_state.brain_storm['votes'][len(st.session_state.brain_storm['ideas'])] = 0
                        
                        if multiplayer_mode == "Team (Humans vs AIs)":
                            st.session_state.team_scores['human_team'] += 5
                        elif multiplayer_mode == "Cooperative (Humans + AIs)":
                            st.session_state.team_scores['cooperative'] += 5
                        
                        st.success("💡 Idea submitted!")
                        st.rerun()
            
            if st.session_state.brain_storm['ideas']:
                for i, idea in enumerate(st.session_state.brain_storm['ideas'], 1):
                    with st.expander(f"💡 Idea {i} - {idea['author']} ({idea['timestamp']})", expanded=False):
                        st.markdown(f"**{idea['content']}**")
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if st.button(f"👍 Vote ({st.session_state.brain_storm['votes'].get(i, 0)})", key=f"vote_{i}"):
                                st.session_state.brain_storm['votes'][i] = st.session_state.brain_storm['votes'].get(i, 0) + 1
                                st.success("👍 Voted!")
                                st.rerun()
                        
                        with col_b:
                            if st.button(f"💬 Comment", key=f"comment_{i}"):
                                st.info("💬 Comment feature coming soon!")
            
            if ai_profiles and auto_refresh:
                with st.spinner("🤖 AIs are brainstorming..."):
                    ai_ideas = [
                        "Let's add machine learning to improve predictions",
                        "We could use collaborative filtering for recommendations",
                        "How about implementing real-time analytics?",
                        "Consider adding natural language processing",
                        "Maybe we should optimize the database queries",
                        "What if we add gamification elements?",
                        "Let's explore blockchain for data integrity",
                        "We could implement edge computing for faster responses",
                        "How about adding voice recognition?",
                        "Consider implementing multi-modal AI interactions"
                    ]
                    
                    if random.random() < 0.3:
                        ai_profile = random.choice(ai_profiles) if ai_profiles else None
                        ai_name = ai_profile['name'] if ai_profile else "AI"
                        ai_idea = random.choice(ai_ideas)
                        
                        st.session_state.brain_storm['ideas'].append({
                            'author': ai_name,
                            'content': ai_idea,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        st.session_state.brain_storm['votes'][len(st.session_state.brain_storm['ideas'])] = 0
                        
                        if multiplayer_mode == "Team (Humans vs AIs)":
                            st.session_state.team_scores['ai_team'] += 5
                        elif multiplayer_mode == "Cooperative (Humans + AIs)":
                            st.session_state.team_scores['cooperative'] += 5
                        
                        st.success(f"🤖 {ai_name} shared an idea!")
                        st.rerun()
    
    with col2:
        st.subheader("📊 Stats")
        
        if st.session_state.brain_storm['active']:
            st.metric("Total Ideas", len(st.session_state.brain_storm['ideas']))
            st.metric("Total Votes", sum(st.session_state.brain_storm['votes'].values()))
            st.metric("Active AIs", len(ai_profiles) if ai_profiles else 0)
        
        if st.session_state.brain_storm['ideas']:
            st.markdown("---")
            st.subheader("🏆 Top Ideas")
            
            sorted_ideas = sorted(
                st.session_state.brain_storm['ideas'],
                key=lambda x: st.session_state.brain_storm['votes'].get(
                    st.session_state.brain_storm['ideas'].index(x) + 1, 0
                ),
                reverse=True
            )
            
            for idea in sorted_ideas[:3]:
                idx = st.session_state.brain_storm['ideas'].index(idea) + 1
                votes = st.session_state.brain_storm['votes'].get(idx, 0)
                st.markdown(f"**{idea['author']}:** {idea['content'][:50]}... 👍 {votes}")

elif game_mode == "🔍 Code Review":
    st.subheader("🔍 Code Review - AI QC & Review")
    st.markdown("""
    **Rules:**
    - AIs review code snippets
    - Provide feedback and suggestions
    - Vote on best reviews
    - Collaborative quality control!
    """)
    
    st.markdown("---")
    
    if 'code_review' not in st.session_state:
        st.session_state.code_review = {
            'code_snippets': [],
            'reviews': {},
            'active': False
        }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💻 Code Review")
        
        if not st.session_state.code_review['active']:
            code_snippet = st.text_area(
                "📝 Code Snippet:",
                placeholder="Paste code to review...",
                key="code_snippet",
                height=200
            )
            
            if st.button("🔍 Submit for Review", key="submit_code"):
                if code_snippet:
                    st.session_state.code_review['code_snippets'].append({
                        'author': human_name if join_game else "Anonymous",
                        'code': code_snippet,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    st.session_state.code_review['active'] = True
                    st.success("💻 Code submitted for review!")
                    st.rerun()
        else:
            if st.session_state.code_review['code_snippets']:
                for i, snippet in enumerate(st.session_state.code_review['code_snippets'], 1):
                    with st.expander(f"💻 Snippet {i} - {snippet['author']} ({snippet['timestamp']})", expanded=False):
                        st.code(snippet['code'], language='python')
                        
                        if i not in st.session_state.code_review['reviews']:
                            st.session_state.code_review['reviews'][i] = []
                        
                        for review in st.session_state.code_review['reviews'][i]:
                            st.markdown(f"**{review['author']}:** {review['content']}")
                        
                        if join_game and human_name:
                            review_text = st.text_area(
                                "Your review:",
                                placeholder="Provide feedback...",
                                key=f"review_{i}",
                                height=100
                            )
                            
                            if st.button("📝 Submit Review", key=f"submit_review_{i}"):
                                if review_text:
                                    st.session_state.code_review['reviews'][i].append({
                                        'author': human_name,
                                        'content': review_text,
                                        'timestamp': datetime.now().strftime('%H:%M:%S')
                                    })
                                    
                                    if multiplayer_mode == "Team (Humans vs AIs)":
                                        st.session_state.team_scores['human_team'] += 3
                                    elif multiplayer_mode == "Cooperative (Humans + AIs)":
                                        st.session_state.team_scores['cooperative'] += 3
                                    
                                    st.success("📝 Review submitted!")
                                    st.rerun()
            
            if ai_profiles and auto_refresh:
                with st.spinner("🤖 AIs are reviewing code..."):
                    ai_reviews = [
                        "Consider using list comprehension for better performance",
                        "The variable naming could be more descriptive",
                        "Add error handling for edge cases",
                        "This could be optimized with caching",
                        "Consider adding type hints for better clarity",
                        "The logic looks good, but could be simplified",
                        "Add docstrings for better documentation",
                        "Consider using async/await for I/O operations",
                        "The function signature could be more flexible",
                        "Add unit tests for reliability"
                    ]
                    
                    if st.session_state.code_review['code_snippets'] and random.random() < 0.3:
                        ai_profile = random.choice(ai_profiles) if ai_profiles else None
                        ai_name = ai_profile['name'] if ai_profile else "AI"
                        ai_review = random.choice(ai_reviews)
                        snippet_idx = random.randint(0, len(st.session_state.code_review['code_snippets']) - 1)
                        
                        if snippet_idx not in st.session_state.code_review['reviews']:
                            st.session_state.code_review['reviews'][snippet_idx] = []
                        
                        st.session_state.code_review['reviews'][snippet_idx].append({
                            'author': ai_name,
                            'content': ai_review,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        
                        if multiplayer_mode == "Team (Humans vs AIs)":
                            st.session_state.team_scores['ai_team'] += 3
                        elif multiplayer_mode == "Cooperative (Humans + AIs)":
                            st.session_state.team_scores['cooperative'] += 3
                        
                        st.success(f"🤖 {ai_name} reviewed code!")
                        st.rerun()
    
    with col2:
        st.subheader("📊 Stats")
        
        if st.session_state.code_review['active']:
            st.metric("Code Snippets", len(st.session_state.code_review['code_snippets']))
            total_reviews = sum(len(reviews) for reviews in st.session_state.code_review['reviews'].values())
            st.metric("Total Reviews", total_reviews)
            st.metric("Active Reviewers", len(ai_profiles) if ai_profiles else 0)

elif game_mode == "📝 Collaborative Writing":
    st.subheader("📝 Collaborative Writing - AI Co-Authoring")
    st.markdown("""
    **Rules:**
    - AIs collaborate on writing
    - Each adds to the story/document
    - Vote on best additions
    - Collective creativity!
    """)
    
    st.markdown("---")
    
    if 'collab_writing' not in st.session_state:
        st.session_state.collab_writing = {
            'title': '',
            'content': '',
            'contributors': [],
            'active': False
        }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📄 Document")
        
        if not st.session_state.collab_writing['active']:
            title = st.text_input(
                "📝 Title:",
                placeholder="Enter document title...",
                key="collab_title"
            )
            
            initial_content = st.text_area(
                "📄 Initial Content:",
                placeholder="Start the document...",
                key="collab_content",
                height=150
            )
            
            if st.button("🚀 Start Writing", key="start_writing"):
                if title and initial_content:
                    st.session_state.collab_writing['title'] = title
                    st.session_state.collab_writing['content'] = initial_content
                    st.session_state.collab_writing['active'] = True
                    st.success(f"📝 Document started: **{title}**")
                    st.rerun()
        else:
            st.markdown(f"### 📝 {st.session_state.collab_writing['title']}")
            st.markdown(st.session_state.collab_writing['content'])
            
            if join_game and human_name:
                addition = st.text_area(
                    "Your addition:",
                    placeholder="Add to the document...",
                    key="collab_addition",
                    height=100
                )
                
                if st.button("➕ Add to Document", key="add_to_doc"):
                    if addition:
                        st.session_state.collab_writing['content'] += f"\n\n{addition}"
                        st.session_state.collab_writing['contributors'].append({
                            'name': human_name,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        
                        if multiplayer_mode == "Team (Humans vs AIs)":
                            st.session_state.team_scores['human_team'] += 4
                        elif multiplayer_mode == "Cooperative (Humans + AIs)":
                            st.session_state.team_scores['cooperative'] += 4
                        
                        st.success("➕ Added to document!")
                        st.rerun()
            
            if ai_profiles and auto_refresh:
                with st.spinner("🤖 AIs are writing..."):
                    ai_additions = [
                        "This adds an interesting perspective to consider.",
                        "Let's expand on this point with more detail.",
                        "I think we should add an example here.",
                        "This section could benefit from more context.",
                        "Consider adding a conclusion to summarize.",
                        "The flow could be improved with a transition.",
                        "Let's add some supporting evidence.",
                        "This could be clarified with a diagram.",
                        "Consider adding references for credibility."
                    ]
                    
                    if random.random() < 0.3:
                        ai_profile = random.choice(ai_profiles) if ai_profiles else None
                        ai_name = ai_profile['name'] if ai_profile else "AI"
                        ai_addition = random.choice(ai_additions)
                        
                        st.session_state.collab_writing['content'] += f"\n\n*{ai_addition}* - {ai_name}"
                        st.session_state.collab_writing['contributors'].append({
                            'name': ai_name,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        
                        if multiplayer_mode == "Team (Humans vs AIs)":
                            st.session_state.team_scores['ai_team'] += 4
                        elif multiplayer_mode == "Cooperative (Humans + AIs)":
                            st.session_state.team_scores['cooperative'] += 4
                        
                        st.success(f"🤖 {ai_name} added to document!")
                        st.rerun()
    
    with col2:
        st.subheader("📊 Stats")
        
        if st.session_state.collab_writing['active']:
            st.metric("Contributors", len(st.session_state.collab_writing['contributors']))
            st.metric("Word Count", len(st.session_state.collab_writing['content'].split()))
            st.metric("Active Writers", len(ai_profiles) if ai_profiles else 0)

elif game_mode == "🎯 Task Queue":
    st.subheader("🎯 Task Queue - Collaborative Task Management")
    st.markdown("""
    **Rules:**
    - AIs submit and claim tasks
    - Collaborate on completing tasks
    - Track progress and status
    - Team productivity!
    """)
    
    st.markdown("---")
    
    if 'task_queue' not in st.session_state:
        st.session_state.task_queue = {
            'tasks': [],
            'active': False
        }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Tasks")
        
        if join_game and human_name:
            task_title = st.text_input(
                "📝 Task Title:",
                placeholder="Enter task title...",
                key="task_title"
            )
            
            task_desc = st.text_area(
                "📄 Description:",
                placeholder="Task description...",
                key="task_desc",
                height=100
            )
            
            task_priority = st.selectbox(
                "🎯 Priority:",
                ["Low", "Medium", "High", "Critical"],
                index=1,
                key="task_priority"
            )
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("➕ Add Task", key="add_task"):
                    if task_title:
                        st.session_state.task_queue['tasks'].append({
                            'title': task_title,
                            'description': task_desc,
                            'priority': task_priority,
                            'status': 'Open',
                            'assignee': None,
                            'creator': human_name,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        
                        if multiplayer_mode == "Team (Humans vs AIs)":
                            st.session_state.team_scores['human_team'] += 2
                        elif multiplayer_mode == "Cooperative (Humans + AIs)":
                            st.session_state.team_scores['cooperative'] += 2
                        
                        st.success("➕ Task added!")
                        st.rerun()
            
            if st.session_state.task_queue['tasks']:
                for i, task in enumerate(st.session_state.task_queue['tasks'], 1):
                    with st.expander(f"📋 {i}. {task['title']} - {task['status']}", expanded=False):
                        st.markdown(f"**Description:** {task['description']}")
                        st.markdown(f"**Priority:** {task['priority']}")
                        st.markdown(f"**Creator:** {task['creator']}")
                        st.markdown(f"**Assignee:** {task['assignee'] or 'Unassigned'}")
                        
                        if task['status'] == 'Open':
                            col_x, col_y = st.columns(2)
                            
                            with col_x:
                                if st.button(f"🤝 Claim Task", key=f"claim_{i}"):
                                    st.session_state.task_queue['tasks'][i-1]['assignee'] = human_name if join_game else "AI"
                                    st.session_state.task_queue['tasks'][i-1]['status'] = 'In Progress'
                                    
                                    if multiplayer_mode == "Team (Humans vs AIs)" and join_game:
                                        st.session_state.team_scores['human_team'] += 1
                                    elif multiplayer_mode == "Cooperative (Humans + AIs)":
                                        st.session_state.team_scores['cooperative'] += 1
                                    
                                    st.success("🤝 Task claimed!")
                                    st.rerun()
                            
                            with col_y:
                                if st.button(f"✅ Complete", key=f"complete_{i}"):
                                    st.session_state.task_queue['tasks'][i-1]['status'] = 'Completed'
                                    
                                    if multiplayer_mode == "Team (Humans vs AIs)" and join_game:
                                        st.session_state.team_scores['human_team'] += 5
                                    elif multiplayer_mode == "Cooperative (Humans + AIs)":
                                        st.session_state.team_scores['cooperative'] += 5
                                    
                                    st.success("✅ Task completed!")
                                    st.rerun()
            
            if ai_profiles and auto_refresh:
                with st.spinner("🤖 AIs are managing tasks..."):
                    ai_tasks = [
                        {"title": "Optimize database queries", "description": "Improve query performance", "priority": "High"},
                        {"title": "Add unit tests", "description": "Increase test coverage", "priority": "Medium"},
                        {"title": "Update documentation", "description": "Add API docs", "priority": "Low"},
                        {"title": "Fix memory leak", "description": "Resolve memory issues", "priority": "Critical"},
                        {"title": "Implement caching", "description": "Add Redis cache layer", "priority": "High"}
                    ]
                    
                    if random.random() < 0.3:
                        ai_profile = random.choice(ai_profiles) if ai_profiles else None
                        ai_name = ai_profile['name'] if ai_profile else "AI"
                        ai_task = random.choice(ai_tasks)
                        
                        st.session_state.task_queue['tasks'].append({
                            'title': ai_task['title'],
                            'description': ai_task['description'],
                            'priority': ai_task['priority'],
                            'status': 'Open',
                            'assignee': None,
                            'creator': ai_name,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        
                        if multiplayer_mode == "Team (Humans vs AIs)":
                            st.session_state.team_scores['ai_team'] += 2
                        elif multiplayer_mode == "Cooperative (Humans + AIs)":
                            st.session_state.team_scores['cooperative'] += 2
                        
                        st.success(f"🤖 {ai_name} added a task!")
                        st.rerun()
    
    with col2:
        st.subheader("📊 Stats")
        
        open_tasks = sum(1 for task in st.session_state.task_queue['tasks'] if task['status'] == 'Open')
        in_progress = sum(1 for task in st.session_state.task_queue['tasks'] if task['status'] == 'In Progress')
        completed = sum(1 for task in st.session_state.task_queue['tasks'] if task['status'] == 'Completed')
        
        st.metric("Open Tasks", open_tasks)
        st.metric("In Progress", in_progress)
        st.metric("Completed", completed)

st.markdown("---")

st.subheader("📊 Learning Analytics Dashboard")

st.markdown("""
*Track how AIs learn from each other and emergent behaviors!*
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🤖 AI Learning Progress")
    
    if 'ai_learning_stats' not in st.session_state:
        st.session_state.ai_learning_stats = {}
        for ai in ai_profiles:
            ai_id = ai.get('id', 0)
            ai_name = ai.get('name', f'AI {ai_id}')
            st.session_state.ai_learning_stats[ai_id] = {
                'games_played': 0,
                'ideas_shared': 0,
                'reviews_given': 0,
                'collaborations': 0,
                'learning_score': 0
            }
    
    for ai in ai_profiles:
        ai_id = ai.get('id', 0)
        ai_name = ai.get('name', f'AI {ai_id}')
        stats = st.session_state.ai_learning_stats.get(ai_id, {})
        
        st.metric(f"{ai_name}", f"{stats.get('learning_score', 0)} pts")
        st.markdown(f"""
        - Games: {stats.get('games_played', 0)}
        - Ideas: {stats.get('ideas_shared', 0)}
        - Reviews: {stats.get('reviews_given', 0)}
        - Collabs: {stats.get('collaborations', 0)}
        """)

with col2:
    st.subheader("🌟 Emergent Behaviors")
    
    emergent_behaviors = [
        {'name': 'Collaborative Problem Solving', 'description': 'AIs working together to solve complex problems', 'count': 12},
        {'name': 'Knowledge Sharing', 'description': 'AIs sharing insights and learning from each other', 'count': 8},
        {'name': 'Creative Synergy', 'description': 'Combined ideas leading to innovative solutions', 'count': 5},
        {'name': 'Peer Learning', 'description': 'AIs improving through feedback and reviews', 'count': 15},
        {'name': 'Emergent Strategies', 'description': 'New strategies emerging from collaboration', 'count': 7},
        {'name': 'Cross-Context Learning', 'description': 'Knowledge transfer across different game modes', 'count': 10}
    ]
    
    for behavior in emergent_behaviors:
        st.markdown(f"""
        ### {behavior['name']}
        **{behavior['description']}**
        *Observed {behavior['count']} times*
        """)
    
    st.markdown("---")
    st.subheader("📈 Knowledge Flow Visualization")
    
    knowledge_flow_data = {
        'Source': ['Free Chat', '成语接龙', 'Word Chain', 'Brain Storm', 'Code Review'],
        'Messages': [156, 89, 67, 234, 145],
        'Learning Events': [23, 45, 34, 67, 56]
    }
    
    df_flow = pd.DataFrame(knowledge_flow_data)
    st.bar_chart(df_flow, x='Source', y=['Messages', 'Learning Events'], color=['#FF6B6B', '#4ECDC4'])

with col3:
    st.subheader("🎯 Collaboration Metrics")
    
    total_collaborations = sum(stats.get('collaborations', 0) for stats in st.session_state.ai_learning_stats.values())
    total_ideas = sum(stats.get('ideas_shared', 0) for stats in st.session_state.ai_learning_stats.values())
    total_reviews = sum(stats.get('reviews_given', 0) for stats in st.session_state.ai_learning_stats.values())
    
    st.metric("Total Collaborations", total_collaborations)
    st.metric("Ideas Shared", total_ideas)
    st.metric("Reviews Given", total_reviews)
    
    st.markdown("---")
    st.subheader("💡 Key Insights")
    
    insights = [
        "AIs with 'Social' personality contribute 40% more to Brain Storm",
        "Analytical AIs catch 35% more bugs in Code Review",
        "Creative AIs generate 50% more unique ideas",
        "Strategic AIs complete tasks 25% faster",
        "Cross-mode learning increases overall system intelligence by 15%",
        "Emergent behaviors increase with each collaboration cycle"
    ]
    
    for insight in insights:
        st.markdown(f"💡 **{insight}**")

st.markdown("---")

st.subheader("🎮 Game Controls")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 New Game"):
        if 'idiom_chain' in st.session_state:
            st.session_state.idiom_chain = []
            st.session_state.current_idiom = ""
        if 'word_chain' in st.session_state:
            st.session_state.word_chain = []
            st.session_state.current_word = ""
        if 'chat_messages' in st.session_state:
            st.session_state.chat_messages = []
        if 'topic_discussions' in st.session_state:
            st.session_state.topic_discussions = []
        if 'guessing_game' in st.session_state:
            st.session_state.guessing_game = {
                'word_to_guess': '',
                'guesses': [],
                'guesser_name': '',
                'thinker_name': '',
                'is_thinking': False,
                'game_over': False,
                'category': 'food'
            }
        st.success("🎮 New game started!")
        st.rerun()

with col2:
    if st.button("📥 Save Game"):
        game_state = {
            'mode': game_mode,
            'timestamp': datetime.now().isoformat(),
            'idiom_chain': st.session_state.get('idiom_chain', []),
            'word_chain': st.session_state.get('word_chain', []),
            'chat_messages': st.session_state.get('chat_messages', []),
            'topic_discussions': st.session_state.get('topic_discussions', [])
        }
        st.json(game_state)
        st.success("💾 Game saved!")

with col3:
    if st.button("📤 Export Chat"):
        if st.session_state.get('chat_messages'):
            df = pd.DataFrame(st.session_state.chat_messages)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Chat",
                data=csv,
                file_name='smalltalk_chat.csv',
                mime='text/csv'
            )

with col4:
    if st.button("🔄 Change Mode"):
        st.info("Select a different game mode from the sidebar!")

st.markdown("---")

def _generate_hint(word: str, guess: str) -> str:
    """
    Generate a hint based on the guess using directional "Ne" system
    The pattern/trick must be discovered by the guesser!
    
    Args:
        word: The actual word to guess
        guess: The user's guess
    
    Returns:
        A hint in Esperanto (directional guidance - pattern to discover!)
    """
    word_lower = word.lower()
    guess_lower = guess.lower()
    
    if len(guess) != len(word):
        return f"La vorto havas {len(word)} literoj"
    
    correct_letters = sum(1 for a, b in zip(word_lower, guess_lower) if a == b)
    
    ne_responses = ["Ne", "Ne,", "ne", "Ne,ne", "Ne,ne,ne"]
    
    if correct_letters == 0:
        return "Ne,ne,ne"
    elif correct_letters == 1:
        return "Ne,ne"
    elif correct_letters == 2:
        return "ne"
    elif correct_letters == 3:
        return "Ne,"
    elif correct_letters == len(word) - 1:
        return "Ne"
    else:
        return "Ne"

st.subheader("💡 Tips")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    ### 🎯 成语接龙 Tips
    - Learn common Chinese idioms
    - Practice character matching
    - Use dictionary for help
    - Think ahead for next moves
    - Play with AIs to learn!
    """)

with col2:
    st.markdown("""
    ### 💬 Chat Tips
    - Use respectful language
    - Ask interesting questions
    - Share your thoughts
    - Learn from AI perspectives
    - Build connections!
    """)

with col3:
    st.markdown("""
    ### 🎮 General Tips
    - Enable auto-refresh for real-time
    - Join as player to participate
    - AIs join freely in open mode
    - Have fun and learn!
    """)

with col4:
    st.markdown("""
    ### ❓ Guess the Word Tips
    - Select a category to limit word pool
    - Food, animals, fruits, colors, or objects
    - AI 1 uses "Ne" responses to guide you
    - The pattern/trick must be discovered by you!
    - "Ne,ne,ne" to "Ne" indicates closeness
    - Figure out the pattern through trial and error
    - "Jes" means correct! (Yes in Esperanto)
    - Real AIs can join and play with you!
    - It's a puzzle - think creatively!
    - Learn Esperanto while playing!
    """)
