from langchain.agents import create_agent
from chatapp.promptmiddleware import inject_global_prompt,inject_memory_replier,inject_memory_sentiment
from langchain.agents.middleware import ModelCallLimitMiddleware,ToolCallLimitMiddleware
from chatapp.tools.index import sentiment_tools,replier_tools
from chatapp.memory.longtermmemory import store
from chatapp.gemini import llm

llm_sentiment = llm.bind_tools(sentiment_tools)

sentiment_agent = create_agent(
        model=llm_sentiment,
        tools=sentiment_tools,
        middleware=[inject_memory_sentiment,ModelCallLimitMiddleware(thread_limit=5),ToolCallLimitMiddleware(thread_limit=5)],
        store =store
    )

llm_replier = llm.bind_tools(replier_tools)

replier_agent = create_agent(
        model=llm_replier,
        tools=replier_tools,
        middleware=[inject_memory_replier,ModelCallLimitMiddleware(thread_limit=5),ToolCallLimitMiddleware(thread_limit=5)],
    )

global_analyzer_agent = create_agent(
        model=llm,
        middleware=[inject_global_prompt]
    )