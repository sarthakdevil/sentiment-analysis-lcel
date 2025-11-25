from langchain.tools import tool
from chatapp.models import ShortTermMemory, ChatMemory, moodshift, local
import json
import os

MOOD_SHIFTS_FILE = "mood_shifts.json"

def load_mood_shifts():
    if os.path.exists(MOOD_SHIFTS_FILE):
        try:
            with open(MOOD_SHIFTS_FILE, 'r') as f:
                data = json.load(f)
                return [moodshift(moodshift=local(chat=[ChatMemory(**c) for c in item['moodshift']['chat']])) for item in data]
        except Exception:
            return []
    return []

def save_mood_shifts():
    data = [shift.model_dump() for shift in mood_shifts]
    with open(MOOD_SHIFTS_FILE, 'w') as f:
        json.dump(data, f)

short_term_memory = ShortTermMemory(chats=[], max_chats=5)
mood_shifts = load_mood_shifts()

def add_chat_to_memory(user: str, sentiment_score: float, sentiment_type: str):
    """Helper function to add chat to memory."""
    chat = ChatMemory(user=user, sentiment_score=sentiment_score, sentiment_type=sentiment_type)

    if short_term_memory.chats:
        prev_chat = short_term_memory.chats[-1]
        if (prev_chat.sentiment_type == 'POS' and sentiment_type == 'NEG') or (prev_chat.sentiment_type == 'NEG' and sentiment_type == 'POS'):
            mood_shift_data = local(
                chat=[prev_chat, chat]
            )
            mood_shift_record = moodshift(moodshift=mood_shift_data)

            mood_shifts.append(mood_shift_record)
            save_mood_shifts()
    
    short_term_memory.chats.append(chat)
    if len(short_term_memory.chats) > short_term_memory.max_chats:
        short_term_memory.chats.pop(0)


def get_chats_from_memory():
    """Helper function to get chats from memory."""
    return short_term_memory.chats

def clear_memory():
    """Helper function to clear memory."""
    short_term_memory.chats.clear()

@tool
def add_to_short_term_memory(user: str, assistant: str, sentiment_score: float, sentiment_type: str) -> str:
    """
    Add a chat to short-term memory.
    Args:
        user: The user's message.
        assistant: The assistant's response.
        sentiment_score: The sentiment score (e.g., 0.95).
        sentiment_type: The sentiment type (e.g., 'POSITIVE').
    Returns:
        Confirmation message.
    """
    add_chat_to_memory(user, sentiment_score, sentiment_type)

    if len(short_term_memory.chats) >= 5:
        from chatapp.memory.summarymemory import summarize_memory
        extracted_memory = summarize_memory(short_term_memory)
        clear_memory()
        return f"Memory full! Summarized and stored: {extracted_memory}. Short-term memory cleared."
    
    return f"Added chat to memory. Current chats: {len(short_term_memory.chats)}"

@tool
def get_short_term_memory() -> str:
    """
    Get the current short-term memory chats.
    Returns:
        JSON string of the chats.
    """
    chats = get_chats_from_memory()
    return json.dumps([chat.model_dump() for chat in chats])

def clear_mood_shifts():
    """Helper function to clear mood shifts."""
    global mood_shifts
    mood_shifts.clear()
    if os.path.exists(MOOD_SHIFTS_FILE):
        os.remove(MOOD_SHIFTS_FILE)

def get_mood_shifts():
    return mood_shifts

def add_assistant_to_memory(user: str, assistant: str):
    """Helper function to add assistant reply to the last chat in memory."""
    if short_term_memory.chats and short_term_memory.chats[-1].user == user and short_term_memory.chats[-1].assistant is None:
        short_term_memory.chats[-1].assistant = assistant
    else:
        add_chat_to_memory(user, assistant, 0.5, "NEUTRAL")

@tool
def add_assistant_reply_to_short_term_memory(user: str, assistant: str) -> str:
    """
    Add an assistant reply to short-term memory.
    Args:
        user: The user's message.
        assistant: The assistant's response.
    Returns:
        Confirmation message.
    """
    add_assistant_to_memory(user, assistant)
    return "Added assistant reply to memory."