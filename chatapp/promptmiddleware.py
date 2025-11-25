from chatapp.memory.shorttermmemory import get_chats_from_memory
from chatapp.memory.longtermmemory import store
from chatapp.memory.summarymemory import get_summaries
import json
from chatapp.memory.longtermmemory import Context
from langchain.agents.middleware import dynamic_prompt,ModelRequest


@dynamic_prompt
def inject_memory_replier(Request:ModelRequest) -> str:
    """
    Dynamically inject short-term and long-term memory into the prompt.
    """
    prompt = '''
    You are a helpful conversational assistant. Your role is to:
        1. Provide helpful, contextual responses to user queries
        2. Use web search when you need current information
        3. Reference conversation history and user preferences from memory
        4. Be friendly, helpful, and engaging
        5. maintain your assistant memory for every chat
        Always consider the user's emotional state and conversation history when responding.
        Use web search for factual queries or current events.

'''
    chats = get_chats_from_memory()
    short_term = json.dumps([chat.model_dump() for chat in chats]) if chats else "No recent conversations"

    summaries_list = get_summaries()
    summaries = json.dumps([s.model_dump() for s in summaries_list]) if summaries_list else "No summaries available"

    user_id = getattr(Context, 'user_id', 'default_user')
    long_term_item = store.get(("users",), user_id)
    long_term = json.dumps(long_term_item.value) if long_term_item and long_term_item.value else "No long-term memory"

    enhanced_prompt = f"""{prompt}

CONTEXT MEMORY:

Short-term Memory (recent 5 conversations):
{short_term}

Summary Memory (conversation summaries):
{summaries}

Long-term Memory (user profile & preferences):
{long_term}

Please respond considering both the recent conversation context and the user's long-term preferences.
"""
    
    return enhanced_prompt

@dynamic_prompt
def inject_memory_sentiment(Request:ModelRequest) -> str:
    """
    Dynamically inject short-term and long-term memory into the prompt.
    """
    prompt = '''
     You are a sentiment analysis specialist. Your role is to:
        1. Analyze the sentiment of user messages using the analyze_sentiment tool
        2. Store conversations in short-term memory with sentiment scores
        3. When appropriate, save important user information to long-term memory
        4. Provide sentiment insights and emotional context
        Always use the sentiment analysis tool first, then store the conversation with sentiment data.
        Be empathetic and understanding in your responses.
    '''
    chats = get_chats_from_memory()
    short_term = json.dumps([chat.model_dump() for chat in chats]) if chats else "No recent conversations"

    summaries_list = get_summaries()
    summaries = json.dumps([s.model_dump() for s in summaries_list]) if summaries_list else "No summaries available"

    user_id = getattr(Context, 'user_id', 'default_user')
    long_term_item = store.get(("users",), user_id)
    long_term = json.dumps(long_term_item.value) if long_term_item and long_term_item.value else "No long-term memory"

    enhanced_prompt = f"""{prompt}

CONTEXT MEMORY:

Short-term Memory (recent 5 conversations):
{short_term}

Summary Memory (conversation summaries):
{summaries}

Long-term Memory (user profile & preferences):
{long_term}

Please respond considering both the recent conversation context and the user's long-term preferences.
"""
    
    return enhanced_prompt


@dynamic_prompt
def inject_global_prompt(Request:ModelRequest) -> str:
    """
    Inject global summaries into the prompt for overall context.
    """
    prompt = '''
    You are a global conversation analyzer. Your role is to:
        1. Analyze overall conversation patterns and sentiment trends
        2. Provide comprehensive summaries of user interactions
        3. Generate final sentiment analysis based on entire conversation history
        4. Identify key insights about user preferences, mood patterns, and topics of interest
        When a conversation session ends, provide a thoughtful summary including:
        - Overall sentiment trend
        - Key topics discussed
        - User's emotional journey
        - Important preferences or information learned
    '''
    from chatapp.memory.summarymemory import get_all_summaries

    summaries_str = get_all_summaries()
    short_term = get_chats_from_memory()
    short_term_str = json.dumps([chat.model_dump() for chat in short_term]) if short_term else "No recent conversations"
    enhanced_prompt = f"""{prompt}
    
Summary Memory (conversation summaries):
{summaries_str}

Short-term Memory (recent 5 conversations):
{short_term_str}
"""
    
    return enhanced_prompt