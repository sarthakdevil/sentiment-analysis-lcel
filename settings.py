from dotenv import load_dotenv
import os
load_dotenv()

class settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY is None:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    if TAVILY_API_KEY is None:
        raise ValueError("TAVILY_API_KEY is not set in environment variables.")


config = settings()
