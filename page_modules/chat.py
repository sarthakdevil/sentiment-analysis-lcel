import streamlit as st
from chatapp.agents import sentiment_agent, replier_agent, global_analyzer_agent
from chatapp.models import Context
from chatapp.memory.shorttermmemory import clear_mood_shifts
import random
from langsmith import traceable, Client
from langsmith.run_helpers import get_current_run_tree
from datetime import datetime

try:
    ls_client = Client()
    LANGSMITH_ENABLED = True
except Exception as e:
    st.warning(f"LangSmith not configured: {e}")
    LANGSMITH_ENABLED = False

def get_sentiment_emoji(sentiment_type: str) -> str:
    """Get emoji based on sentiment type."""
    emoji_map = {
        "POSITIVE": "😊",
        "NEGATIVE": "😢",
        "NEUTRAL": "😐"
    }
    return emoji_map.get(sentiment_type, "😐")

def get_sentiment_color(sentiment_type: str) -> str:
    """Get color based on sentiment type."""
    color_map = {
        "POSITIVE": "#28a745",
        "NEGATIVE": "#dc3545",
        "NEUTRAL": "#ffc107"
    }
    return color_map.get(sentiment_type, "#6c757d")

@traceable(name="sentiment_analysis", run_type="chain")
def analyze_sentiment_with_tracking(prompt: str, user_id: str):
    """Analyze sentiment with LangSmith tracking."""
    try:
        sentiment_result = st.session_state.sentiment_agent.invoke({
            "messages": [{"role": "user", "content": f"Analyze the sentiment of this message and store it in memory: {prompt}"}]
        },
        {'context': {"user_id": user_id}}
        )
        
        sentiment_type = "NEUTRAL"
        sentiment_score = 0.5
        
        if isinstance(sentiment_result, dict) and 'output' in sentiment_result:
            output = sentiment_result['output']
            try:
                if isinstance(output, str) and 'POSITIVE' in output:
                    sentiment_type = "POSITIVE"
                    import re
                    score_match = re.search(r"'score':\s*(-?\d+\.?\d*)", output)
                    if score_match:
                        sentiment_score = abs(float(score_match.group(1)))
                    else:
                        sentiment_score = 0.8
                elif isinstance(output, str) and 'NEGATIVE' in output:
                    sentiment_type = "NEGATIVE"
                    import re
                    score_match = re.search(r"'score':\s*(-?\d+\.?\d*)", output)
                    if score_match:
                        sentiment_score = abs(float(score_match.group(1)))
                    else:
                        sentiment_score = 0.8
                elif isinstance(output, dict):
                    sentiment_type = output.get('label', 'NEUTRAL').upper()
                    sentiment_score = abs(output.get('score', 0.5))
            except Exception:
                if 'POSITIVE' in str(output):
                    sentiment_type = "POSITIVE"
                    sentiment_score = 0.8
                elif 'NEGATIVE' in str(output):
                    sentiment_type = "NEGATIVE"
                    sentiment_score = 0.8

        if LANGSMITH_ENABLED:
            run_tree = get_current_run_tree()
            if run_tree:
                run_tree.add_metadata({
                    "sentiment_type": sentiment_type,
                    "sentiment_score": sentiment_score,
                    "user_id": user_id
                })
        
        return sentiment_type, sentiment_score
    
    except Exception as e:
        st.error(f"Sentiment analysis failed: {e}")
        return "NEUTRAL", 0.5

@traceable(name="response_generation", run_type="chain")
def generate_response_with_tracking(prompt: str, sentiment_type: str, sentiment_score: float):
    """Generate response with LangSmith tracking."""
    try:
        response_result = st.session_state.replier_agent.invoke({
            "messages": [{"role": "user", "content": f"Generate a response to this message and store it in memory: {prompt}"}]
        })
        
        response_text = "I apologize, but I couldn't generate a response."
        if isinstance(response_result, dict):
            if 'messages' in response_result:
                for msg in reversed(response_result['messages']):
                    if hasattr(msg, 'type') and msg.type == 'ai':
                        if hasattr(msg, 'content'):
                            if isinstance(msg.content, list):
                                text_parts = []
                                for content_block in msg.content:
                                    if isinstance(content_block, dict) and 'text' in content_block:
                                        text_parts.append(content_block['text'])
                                response_text = ''.join(text_parts)
                            else:
                                response_text = str(msg.content)
                        break
                    elif hasattr(msg, 'role') and msg.role == 'assistant':
                        if hasattr(msg, 'content'):
                            if isinstance(msg.content, list):
                                text_parts = []
                                for content_block in msg.content:
                                    if isinstance(content_block, dict) and 'text' in content_block:
                                        text_parts.append(content_block['text'])
                                response_text = ''.join(text_parts)
                            else:
                                response_text = str(msg.content)
                        break
            elif 'output' in response_result:
                response_text = response_result['output']

        if LANGSMITH_ENABLED:
            run_tree = get_current_run_tree()
            if run_tree:
                run_tree.add_metadata({
                    "input_sentiment": sentiment_type,
                    "input_sentiment_score": sentiment_score,
                    "response_length": len(response_text)
                })
        
        return response_text
    
    except Exception as e:
        st.error(f"Failed to generate response: {e}")
        return "I apologize, but I couldn't generate a response."

@traceable(name="conversation_analysis", run_type="chain")
def analyze_conversation_with_tracking(analysis_type: str):
    """Analyze conversation with LangSmith tracking."""
    try:
        prompt = ""
        if analysis_type == "finish":
            prompt = "Please analyze this conversation session and provide insights about the overall sentiment trends, key topics discussed, user's emotional journey, and any important patterns or preferences that emerged."
        else:
            prompt = "Please provide a comprehensive summary of this conversation session including overall sentiment trends, key topics, and user's emotional journey."
        
        analysis_result = st.session_state.global_analyzer.invoke({
            "messages": [{"role": "user", "content": prompt}]
        })
        
        analysis_text = "Unable to generate analysis."
        if isinstance(analysis_result, dict):
            if 'messages' in analysis_result:
                for msg in reversed(analysis_result['messages']):
                    if hasattr(msg, 'type') and msg.type == 'ai':
                        if hasattr(msg, 'content'):
                            if isinstance(msg.content, list):
                                text_parts = []
                                for content_block in msg.content:
                                    if isinstance(content_block, dict) and 'text' in content_block:
                                        text_parts.append(content_block['text'])
                                analysis_text = ''.join(text_parts)
                            else:
                                analysis_text = str(msg.content)
                        break
                    elif hasattr(msg, 'role') and msg.role == 'assistant':
                        if hasattr(msg, 'content'):
                            if isinstance(msg.content, list):
                                text_parts = []
                                for content_block in msg.content:
                                    if isinstance(content_block, dict) and 'text' in content_block:
                                        text_parts.append(content_block['text'])
                                analysis_text = ''.join(text_parts)
                            else:
                                analysis_text = str(msg.content)
                        break
            elif 'output' in analysis_result:
                analysis_text = analysis_result['output']
        
        # Log to LangSmith
        if LANGSMITH_ENABLED:
            run_tree = get_current_run_tree()
            if run_tree:
                run_tree.add_metadata({
                    "analysis_type": analysis_type,
                    "total_messages": len(st.session_state.chat_history),
                    "session_id": st.session_state.context.user_id
                })
        
        return analysis_text
    
    except Exception as e:
        raise e

def log_session_metrics():
    """Log session-level metrics to LangSmith."""
    if not LANGSMITH_ENABLED:
        return
    
    try:
        # Calculate session metrics
        user_messages = [msg for msg in st.session_state.chat_history if msg['role'] == 'user']
        sentiments = [msg.get('sentiment_type', 'NEUTRAL') for msg in st.session_state.chat_history if 'sentiment_type' in msg]
        
        positive_count = sentiments.count('POSITIVE')
        negative_count = sentiments.count('NEGATIVE')
        neutral_count = sentiments.count('NEUTRAL')
        
        # Create a dataset example for this session
        ls_client.create_example(
            inputs={
                "session_id": st.session_state.context.user_id,
                "total_messages": len(st.session_state.chat_history),
                "user_messages": len(user_messages)
            },
            outputs={
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count
                }
            },
            dataset_name="chat_sessions",
            created_at=datetime.now()
        )
    except Exception as e:
        st.warning(f"Failed to log session metrics: {e}")

def show_chat_page():
    """Render the main chat interface page with real-time sentiment analysis."""
    st.title("💬 Chat with Sentiment Analysis")
    
    # LangSmith status indicator
    if LANGSMITH_ENABLED:
        st.sidebar.success("🔬 LangSmith Tracking: Active")
    else:
        st.sidebar.warning("🔬 LangSmith Tracking: Disabled")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'context' not in st.session_state:
        user = random.randint(1000,9999)
        st.session_state.context = Context(user_id=str(user))
        clear_mood_shifts()
        
        # Log session start to LangSmith
        if LANGSMITH_ENABLED:
            try:
                ls_client.create_run(
                    name="chat_session_start",
                    run_type="chain",
                    inputs={"user_id": str(user)},
                    extra={"session_start": datetime.now().isoformat()}
                )
            except Exception:
                pass
    
    if 'agents_initialized' not in st.session_state:
        with st.spinner("Initializing agents..."):
            st.session_state.sentiment_agent = sentiment_agent
            st.session_state.replier_agent = replier_agent
            st.session_state.global_analyzer = global_analyzer_agent
            st.session_state.agents_initialized = True
    
    with st.sidebar:
        st.markdown("### 📊 Current Session")
        st.metric("Session ID", st.session_state.context.user_id)
        st.metric("Messages", len(st.session_state.chat_history))
        
        # Sentiment distribution
        if st.session_state.chat_history:
            sentiments = [msg.get('sentiment_type', 'NEUTRAL') for msg in st.session_state.chat_history if 'sentiment_type' in msg]
            if sentiments:
                st.markdown("### 📈 Sentiment Distribution")
                col1, col2, col3 = st.columns(3)
                col1.metric("😊", sentiments.count('POSITIVE'))
                col2.metric("😐", sentiments.count('NEUTRAL'))
                col3.metric("😢", sentiments.count('NEGATIVE'))
        
        st.markdown("---")
        
        if st.button("🎯 Finish Conversation", type="secondary", use_container_width=True):
            with st.spinner("Analyzing conversation..."):
                try:
                    analysis_text = analyze_conversation_with_tracking("finish")
                    st.success("Conversation Analysis")
                    st.write(analysis_text)
                except Exception as e:
                    st.error(f"Failed to analyze conversation: {e}")
        
        if st.button("🏁 End Session", type="primary", use_container_width=True):
            with st.spinner("Generating session summary..."):
                try:
                    summary_text = analyze_conversation_with_tracking("summary")
                    
                    # Log final session metrics
                    log_session_metrics()
                    
                    st.success("Session Summary")
                    st.write(summary_text)
                    
                    if LANGSMITH_ENABLED:
                        st.info("📊 Session data logged to LangSmith for analysis")
                    
                except Exception as e:
                    st.error(f"Failed to generate summary: {e}")
    
    # Display chat history
    for message in st.session_state.chat_history:
        role = message['role']
        content = message['content']
        
        with st.chat_message(role):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(content)
            with col2:
                if role == 'user' and 'sentiment_type' in message:
                    emoji = get_sentiment_emoji(message['sentiment_type'])
                    st.markdown(
                        f"<div style='text-align: center; font-size: 24px;'>{emoji}</div>",
                        unsafe_allow_html=True
                    )
            
            if role == 'user' and 'sentiment_score' in message:
                st.caption(f"Sentiment: {message['sentiment_type']} ({message['sentiment_score']:.2f})")
    
    # Handle new messages
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.chat_history.append({
            'role': 'user',
            'content': prompt
        })
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Analyze sentiment with tracking
        with st.spinner("Analyzing sentiment..."):
            sentiment_type, sentiment_score = analyze_sentiment_with_tracking(
                prompt, 
                st.session_state.context.user_id
            )
        
        # Generate response with tracking
        with st.spinner("Generating response..."):
            response_text = generate_response_with_tracking(
                prompt, 
                sentiment_type, 
                sentiment_score
            )
            
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response_text,
                'sentiment_type': sentiment_type,
                'sentiment_score': sentiment_score
            })
            
            with st.chat_message("assistant"):
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.write(response_text)
                with col2:
                    emoji = get_sentiment_emoji(sentiment_type)
                    st.markdown(
                        f"<div style='text-align: center; font-size: 24px;'>{emoji}</div>",
                        unsafe_allow_html=True
                    )
                st.caption(f"Sentiment: {sentiment_type} ({sentiment_score:.2f})")
        
        st.rerun()