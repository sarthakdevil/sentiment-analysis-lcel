import streamlit as st
import json
from chatapp.memory.shorttermmemory import get_chats_from_memory, clear_memory, get_mood_shifts
from chatapp.memory.longtermmemory import store
from chatapp.memory.summarymemory import get_summaries, clear_summaries

def show_home_page():
    """Render the home dashboard page."""
    st.title("🏠 Welcome to Sentiment Analysis Chatbot")
    st.markdown("""
    A powerful AI chatbot with real-time sentiment analysis, memory management, and mood tracking.
    """)
    
    st.markdown("---")
    
    st.header("📊 Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    chats = get_chats_from_memory()
    summaries = get_summaries()
    mood_shifts = get_mood_shifts()
    
    with col1:
        st.metric("Current Session Messages", len(chats))
    with col2:
        st.metric("Total Summaries", len(summaries))
    with col3:
        st.metric("Mood Shifts Detected", len(mood_shifts))
    with col4:
        st.metric("Status", "🟢 Active")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 System Status")
        st.success("✅ Sentiment Agent: Active")
        st.success("✅ Replier Agent: Active")
        st.success("✅ Global Analyzer: Active")
        st.info("💾 Memory System: Operational")
        st.info("🔍 Web Search: Enabled")
    
    with col2:
        st.subheader("📈 Recent Activity")
        if chats:
            st.write(f"**Last message:** {len(chats)} chats in current session")
            latest_chat = chats[-1]
            st.caption(f"Latest sentiment: {latest_chat.sentiment_type} ({latest_chat.sentiment_score:.2f})")
        else:
            st.write("No recent activity")
        
        if summaries:
            latest_summary = summaries[-1]
            st.write(f"**Latest summary mood:** {latest_summary.general_mood}")
            st.caption(f"Time: {latest_summary.timestamp}")
    
    st.markdown("---")
    
    st.header("🚀 Getting Started")
    
    with st.expander("📖 How to Use This Chatbot", expanded=True):
        st.markdown("""
        1. **💬 Chat**: Have natural conversations with sentiment analysis
        2. **📊 Mood Tracking**: Visualize sentiment trends and mood shifts
        3. **🧠 Memory Viewer**: Explore short-term, long-term, and summary memories
        
        - Click **Chat** to start a conversation
        - Navigate to **Mood Tracking** to see analytics
        - Visit **Memory Viewer** to explore stored data
        - Use the sidebar to switch between pages
        
        - The chatbot analyzes sentiment in real-time
        - Mood shifts are automatically detected (>0.35 score change)
        - After 5 messages, conversations are automatically summarized
        - You can end a session anytime to get comprehensive insights
        """)
    
    st.markdown("---")
    st.header("📝 Recent Summaries")
    
    if summaries:
        for summary in list(reversed(summaries))[:3]:
            with st.container():
                st.markdown(f"**{summary.general_mood}** - {summary.timestamp}")
                st.caption(summary.summary)
                st.markdown("---")
    else:
        st.info("No summaries yet. Start chatting to generate summaries!")
    
    st.markdown("---")
    
    with st.container():
        if st.button("🗑️ Clear History", use_container_width=True, type="secondary"):
            clear_memory()
            clear_summaries()
            st.success("History cleared!")
            st.rerun()


def show_memory_page():
    """Render the memory viewer page."""
    st.title("🧠 Memory Viewer")
    st.markdown("Explore and manage different types of memory")
    
    tab1, tab2, tab3 = st.tabs(["📝 Short-Term", "💾 Long-Term", "📚 Summaries"])
    
    with tab1:
        st.header("Short-Term Memory")
        st.caption("Stores the last 5 conversations")
        
        chats = get_chats_from_memory()
        
        if chats:
            capacity = len(chats)
            max_capacity = 5
            progress = capacity / max_capacity
            st.progress(progress, text=f"Memory Usage: {capacity}/{max_capacity} slots")
            
            st.markdown("---")
            
            for i, chat in enumerate(chats):
                with st.container():
                    col1, col2 = st.columns([0.7, 0.3])
                    
                    with col1:
                        st.markdown(f"**Message {i+1}**")
                        st.info(f"👤 **User:** {chat.user}")
                        st.success(f"🤖 **Assistant:** {chat.assistant}")
                    
                    with col2:
                        sentiment_color = {
                            'POSITIVE': 'green',
                            'NEGATIVE': 'red',
                            'NEUTRAL': 'orange'
                        }.get(chat.sentiment_type, 'gray')
                        
                        st.markdown("**Sentiment**")
                        st.markdown(f":{sentiment_color}[{chat.sentiment_type}]")
                        st.markdown(f"**Score:** {chat.sentiment_score:.2f}")
                    
                    st.markdown("---")
            
            if st.button("🗑️ Clear Short-Term Memory", type="secondary"):
                clear_memory()
                st.success("Short-term memory cleared!")
                st.rerun()
        else:
            st.info("Short-term memory is empty. Start chatting to fill it!")
    
    with tab2:
        st.header("Long-Term Memory")
        st.caption("Persistent user profile and preferences")
        
        try:
            user_data = store.get(("users",), "default_user")
            
            if user_data and user_data.value:
                st.success("✅ User profile found")
                
                st.subheader("User Profile")
                
                for key, value in user_data.value.items():
                    col1, col2 = st.columns([0.3, 0.7])
                    with col1:
                        st.markdown(f"**{key.replace('_', ' ').title()}:**")
                    with col2:
                        st.markdown(value)
                
                st.markdown("---")
                
                if st.button("📥 Export Profile as JSON"):
                    json_str = json.dumps(user_data.value, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name="user_profile.json",
                        mime="application/json"
                    )
            else:
                st.info("No long-term memory stored yet. Continue conversations to build your profile!")
        except Exception as e:
            st.warning(f"Could not access long-term memory: {e}")
    
    with tab3:
        st.header("Conversation Summaries")
        st.caption("Historical conversation summaries and insights")
        
        summaries = get_summaries()
        
        if summaries:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Summaries", len(summaries))
            with col2:
                moods = [s.general_mood for s in summaries]
                mood_counts = {mood: moods.count(mood) for mood in set(moods)}
                dominant_mood = max(mood_counts, key=mood_counts.get)
                st.metric("Dominant Mood", dominant_mood)
            
            st.markdown("---")
            
            filter_mood = st.selectbox(
                "Filter by Mood",
                ["All"] + list(set(s.general_mood for s in summaries))
            )
            
            filtered_summaries = summaries if filter_mood == "All" else [
                s for s in summaries if s.general_mood == filter_mood
            ]
            
            st.subheader(f"Summaries ({len(filtered_summaries)})")
            
            for i, summary in enumerate(reversed(filtered_summaries)):
                with st.expander(
                    f"Summary {len(filtered_summaries)-i}: {summary.general_mood}",
                    expanded=False
                ):
                    st.markdown("**Summary:**")
                    st.write(summary.summary)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Mood:** {summary.general_mood}")
                    with col2:
                        st.markdown(f"**Timestamp:** {summary.timestamp}")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Export All Summaries"):
                    export_data = [s.model_dump() for s in summaries]
                    json_str = json.dumps(export_data, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name="summaries.json",
                        mime="application/json"
                    )
            
            with col2:
                if st.button("🗑️ Clear All Summaries", type="secondary"):
                    clear_summaries()
                    st.success("All summaries cleared!")
                    st.rerun()
        else:
            st.info("No summaries available yet. Complete conversations to generate summaries!")
