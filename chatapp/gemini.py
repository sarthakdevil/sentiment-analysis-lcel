from google import genai
from settings import config
from langchain_google_genai import ChatGoogleGenerativeAI

class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.api_key = api_key

client = GeminiClient(api_key=config.GEMINI_API_KEY)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
