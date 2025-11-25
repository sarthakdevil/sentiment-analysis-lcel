from chatapp.models import ShortTermMemory, SummaryMemory, SummaryEntry
from chatapp.gemini import client
import json
from datetime import datetime

summary_memory = SummaryMemory(summaries=[])
history = []

def add_summary_entry(summary: str, mood: str):
    """Helper function to add summary entry."""
    entry = SummaryEntry(
        summary=summary,
        general_mood=mood,
        timestamp=datetime.now().isoformat()
    )
    summary_memory.summaries.append(entry)
    if len(summary_memory.summaries) > summary_memory.max_summaries:
        summary_memory.summaries.pop(0)

def get_summaries():
    """Helper function to get all summaries."""
    return summary_memory.summaries[:5]

def summarize_memory(short_term_memory: ShortTermMemory) -> str:
    """
    Summarize short-term memory and store in summary memory array.
    Args:
        short_term_memory: The short-term memory to summarize.
    Returns:
        Confirmation message with summary details.
    """

    chats_text = ""
    chats_list = short_term_memory.chats
    history.append(chats_list)
    
    if not summary_memory.summaries and history:
        chats_list = history[-1]
    
    for chat in chats_list:
        chats_text += f"User: {chat.user}\nAssistant: {chat.assistant}\nSentiment: {chat.sentiment_type} ({chat.sentiment_score})\n\n"

    extraction_prompt = f"""
Analyze the following conversation history and extract key information:

{chats_text}

Extract and return ONLY a JSON object with these fields:
{{
    "summary": "brief summary of the chat interactions and key topics",
    "general_mood": "overall mood/sentiment pattern across conversations"
}}

Return only valid JSON, no additional text.
"""
    
    try:
        response = client.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=extraction_prompt
        )
        print(response)
        
        response_text = response.candidates[0].content.parts[0].text.strip()

        if response_text.startswith('```json'):
            response_text = response_text[7:]  
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]  
        
        response_text = response_text.strip()
        
        extracted = json.loads(response_text)

        summary_entry = SummaryEntry(
            summary=extracted.get("summary", "No summary available"),
            general_mood=extracted.get("general_mood", "NEUTRAL"),
            timestamp=datetime.now().isoformat()
        )

        summary_memory.summaries.append(summary_entry)

        if len(summary_memory.summaries) > summary_memory.max_summaries:
            summary_memory.summaries.pop(0) 
        
        return f"Summary created and stored. Total summaries: {len(summary_memory.summaries)}"
        
    except Exception as e:
        print(f"Error in summarize_memory: {e}")
        import traceback
        traceback.print_exc()
        
        sentiments = [chat.sentiment_type for chat in chats_list]
        dominant_sentiment = max(set(sentiments), key=sentiments.count) if sentiments else "NEUTRAL"
        
        summary_entry = SummaryEntry(
            summary="Basic summary - extraction failed",
            general_mood=dominant_sentiment,
            timestamp=datetime.now().isoformat()
        )
        
        summary_memory.summaries.append(summary_entry)
        
        return f"Basic summary created (extraction failed). Total summaries: {len(summary_memory.summaries)}"

def get_all_summaries() -> str:
    """
    Get all stored summaries for generating comprehensive output.
    Returns:
        JSON string of all summary entries.
    """
    return json.dumps([entry.model_dump() for entry in summary_memory.summaries])

def clear_summaries() -> str:
    """
    Clear all stored summaries.
    Returns:
        Confirmation message.
    """
    summary_memory.summaries.clear()
    return "All summaries cleared."

def gethistory():
    return history