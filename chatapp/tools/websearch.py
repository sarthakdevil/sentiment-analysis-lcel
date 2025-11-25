from langchain.tools import tool
from tavily import TavilyClient
from settings import config
@tool
def web_search(query: str) -> str:
    """
    Perform a web search using Tavily API.
    Args:
        query: The search query string.
    Returns:
        A string containing the search results.
    """
    api_key = config.TAVILY_API_KEY

    client = TavilyClient(api_key=api_key)
    response = client.search(query)
    results = response.get('results', [])
    if not results:
        return "No results found."

    output = ""
    for result in results[:5]: 
        output += f"Title: {result.get('title', 'N/A')}\n"
        output += f"URL: {result.get('url', 'N/A')}\n"
        output += f"Snippet: {result.get('content', 'N/A')}\n\n"
    return output