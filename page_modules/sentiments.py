import streamlit as st
import pandas as pd
import plotly.express as px
from chatapp.memory.shorttermmemory import get_chats_from_memory
from chatapp.memory.summarymemory import gethistory, get_summaries

def show_sentiments_page():
    """Render the mood tracking and sentiment analytics page."""
    st.title("📊 Mood Tracking & Sentiment Analysis")
    st.markdown("Visualize sentiment trends and mood shifts across conversations")
    
    tab1, tab2, tab3 = st.tabs(["📈 Current Session", "🔄 Mood Shifts", "📜 Historical Trends"])
    
    with tab1:
        st.header("All Conversations Analysis")
        
        history = gethistory()
        all_chats = []
        for session in history:
            all_chats.extend(session)
        
        current_chats = get_chats_from_memory()
        all_chats.extend(current_chats)
        
        if all_chats:
            col1, col2, col3 = st.columns(3)
            
            total_messages = len(all_chats)
            avg_sentiment = sum(chat.sentiment_score for chat in all_chats) / total_messages
            sentiment_types = [chat.sentiment_type for chat in all_chats]
            dominant_sentiment = max(set(sentiment_types), key=sentiment_types.count)
            
            with col1:
                st.metric("Total Messages", total_messages)
            with col2:
                st.metric("Average Sentiment model confidence", f"{avg_sentiment:.2f}")
            with col3:
                st.metric("Dominant Sentiment", dominant_sentiment)
            
            st.markdown("---")
            
            st.subheader("Sentiment Trend Over Time (All Conversations)")
            sentiment_data = pd.DataFrame([
                {"Message": i+1, "Sentiment Value": 1 if chat.sentiment_type in ['POSITIVE', 'POS'] else (-1 if chat.sentiment_type in ['NEGATIVE', 'NEG'] else 0)}
                for i, chat in enumerate(all_chats)
            ])
            fig_line = px.line(sentiment_data, x="Message", y="Sentiment Value", 
                              markers=True, title="Sentiment Trend")
            fig_line.update_yaxes(range=[-1, 1])
            st.plotly_chart(fig_line, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Sentiment Distribution")
                sentiment_counts = pd.Series(sentiment_types).value_counts()
                fig_bar = px.bar(x=sentiment_counts.index, y=sentiment_counts.values,
                                labels={'x': 'Sentiment Type', 'y': 'Count'},
                                color=sentiment_counts.index,
                                color_discrete_map={
                                    'POSITIVE': '#00FF00',  # Green for POS
                                    'POS': '#00FF00',       # Green for POS
                                    'NEGATIVE': '#00FFFF',  # Teal/Cyan for NEG  
                                    'NEG': '#00FFFF',       # Teal/Cyan for NEG
                                    'NEUTRAL': '#FF0000',   # Red for NEU
                                    'NEU': '#FF0000'        # Red for NEU
                                })
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                st.subheader("Sentiment Pie Chart")
                fig_pie = px.pie(values=sentiment_counts.values, names=sentiment_counts.index,
                                color=sentiment_counts.index,
                                color_discrete_map={
                                    'POSITIVE': '#00FF00',  # Green for POS
                                    'POS': '#00FF00',       # Green for POS
                                    'NEGATIVE': '#00FFFF',  # Teal/Cyan for NEG
                                    'NEG': '#00FFFF',       # Teal/Cyan for NEG
                                    'NEUTRAL': '#FF0000',   # Red for NEU
                                    'NEU': '#FF0000'        # Red for NEU
                                })
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("---")
            st.subheader("All Conversations")
            for i, chat in enumerate(reversed(all_chats[-20:])):
                with st.expander(f"Message {len(all_chats)-i} - {chat.sentiment_type}"):
                    col1, col2 = st.columns([0.7, 0.3])
                    with col1:
                        st.markdown(f"**User:** {chat.user}")
                        st.markdown(f"**Assistant:** {chat.assistant}")
                    with col2:
                        sentiment_emoji = {
                            'POSITIVE': '😊',
                            'NEGATIVE': '😔',
                            'NEUTRAL': '😐'
                        }.get(chat.sentiment_type, '❓')
                        st.markdown(f"**Sentiment:** {sentiment_emoji} {chat.sentiment_type}")
                        st.markdown(f"**Score:** {chat.sentiment_score:.2f}")
        else:
            st.info("No conversations in current session. Start chatting to see analytics!")
    
    with tab2:
        st.header("Mood Shift Analysis (All History)")
        
        all_historical_chats = []
        history = gethistory()
        for session in history:
            all_historical_chats.extend(session)
        current_chats = get_chats_from_memory()
        all_historical_chats.extend(current_chats)
        
        from chatapp.memory.shorttermmemory import get_mood_shifts
        mood_shifts = get_mood_shifts()
        
        if mood_shifts:
            col1, col2, col3 = st.columns(3)
            
            total_shifts = len(mood_shifts)
            
            with col1:
                st.metric("Total Mood Shifts", total_shifts)
            with col2:
                st.metric("Shifts Detected", "POS ↔ NEG")
            with col3:
                st.metric("Detection Method", "Sentiment Type Change")
            
            st.markdown("---")
            
            st.markdown("---")
            st.subheader("Mood Shift Details")
            
            for i, shift in enumerate(mood_shifts):
                if len(shift.moodshift.chat) >= 2:
                    before = shift.moodshift.chat[0]
                    after = shift.moodshift.chat[1]
                    with st.expander(f"Shift {i+1}: {before.sentiment_type} → {after.sentiment_type}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Before**")
                            st.info(f"_{before.user}_")
                            st.markdown(f"**Sentiment:** {before.sentiment_type}")
                            st.markdown(f"**Score:** {before.sentiment_score:.2f}")
                        
                        with col2:
                            st.markdown("**After**")
                            st.success(f"_{after.user}_")
                            st.markdown(f"**Sentiment:** {after.sentiment_type}")
                            st.markdown(f"**Score:** {after.sentiment_score:.2f}")
        else:
            st.info("No mood shifts detected yet. Continue chatting to track mood changes!")
    
    with tab3:
        st.header("Historical Trends")
        
        summaries = get_summaries()
        history = gethistory()
        
        if history:
            st.subheader("📜 All Historical Chats")
            st.markdown(f"Total conversation sessions: **{len(history)}**")
            
            for session_idx, session_chats in enumerate(history):
                with st.expander(f"Session {session_idx + 1} - {len(session_chats)} messages", expanded=False):
                    for chat_idx, chat in enumerate(session_chats):
                        col1, col2 = st.columns([0.8, 0.2])
                        
                        with col1:
                            st.markdown(f"**#{chat_idx + 1} User:** {chat.user}")
                            st.markdown(f"**Assistant:** {chat.assistant}")
                        
                        with col2:
                            sentiment_emoji = {
                                'POSITIVE': '😊',
                                'NEGATIVE': '😔',
                                'NEUTRAL': '😐'
                            }.get(chat.sentiment_type, '❓')
                            st.markdown(f"{sentiment_emoji} **{chat.sentiment_type}**")
                            st.markdown(f"Score: {chat.sentiment_score:.2f}")
                        
                        if chat_idx < len(session_chats) - 1:
                            st.markdown("---")
            
            st.markdown("---")
        
        if summaries:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Sessions", len(summaries))
            with col2:
                moods = [s.general_mood for s in summaries]
                dominant_mood = max(set(moods), key=moods.count)
                st.metric("Most Common Mood", dominant_mood)
            
            st.markdown("---")
            
            st.subheader("Mood Distribution Across Sessions")
            mood_counts = pd.Series(moods).value_counts()
            fig_bar = px.bar(x=mood_counts.index, y=mood_counts.values,
                            labels={'x': 'Mood', 'y': 'Count'},
                            color=mood_counts.index,
                            color_discrete_map={
                                'POSITIVE': '#00FF00',  # Green for POS
                                'POS': '#00FF00',       # Green for POS
                                'NEGATIVE': '#00FFFF',  # Teal/Cyan for NEG
                                'NEG': '#00FFFF',       # Teal/Cyan for NEG
                                'NEUTRAL': '#FF0000',   # Red for NEU
                                'NEU': '#FF0000'        # Red for NEU
                            })
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown("---")
            st.subheader("Session Timeline")
            
            for i, summary in enumerate(reversed(summaries)):
                with st.expander(f"Session {len(summaries)-i} - {summary.general_mood}", expanded=False):
                    col1, col2 = st.columns([0.7, 0.3])
                    with col1:
                        st.markdown(f"**Summary:** {summary.summary}")
                    with col2:
                        st.markdown(f"**Mood:** {summary.general_mood}")
                        st.caption(f"**Time:** {summary.timestamp}")
        else:
            st.info("No historical data yet. Complete conversations to build history!")
