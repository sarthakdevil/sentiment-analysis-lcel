import streamlit as st
from page_modules.chat import show_chat_page
from page_modules.sentiments import show_sentiments_page
from page_modules.streamlit_router import show_home_page, show_memory_page
from chatapp.memory.shorttermmemory import clear_memory
from chatapp.memory.summarymemory import clear_summaries

st.set_page_config(
    page_title="LangChain Sentiment Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("🤖 Sentiment Chatbot")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "💬 Chat", "📊 Mood Tracking", "🧠 Memory Viewer"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")
st.sidebar.success("✅ All agents loaded")
st.sidebar.info("💾 Memory available")

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
    clear_memory()
    clear_summaries()
    if 'chat_history' in st.session_state:
        st.session_state.chat_history = []
    st.sidebar.success("All data cleared!")
    st.rerun()

if page == "🏠 Home":
    show_home_page()
elif page == "💬 Chat":
    show_chat_page()
elif page == "📊 Mood Tracking":
    show_sentiments_page()
elif page == "🧠 Memory Viewer":
    show_memory_page()
