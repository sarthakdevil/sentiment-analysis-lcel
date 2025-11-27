```
uv sync
uv run poe main (runs ui version)
uv run poe dev (runs cli version)
```
Link https://github.com/sarthakdevil/sentiment-analysis-lcel
# Summary
### This is a sentiment analysis workflow using LCEL (LangChain Expression Language) agents, which act as a replacement for ReAct agents.

## Tools Used
- **GEMINI** – for the entire workflow and summary memory  
- **LangChain agents** – for the agentic workflow  
- **Finetuned BERT** – for Tier 2 message-level sentiment tracking  
- **Ruff** – for validations and linting (combined via Poe)

## Workflow
### The workflow consists of 3 agents:
1. **Sentiment Agent**
2. **Replier Agent**
3. **Global Summarization Agent**

### Sentiment Agent
- Uses BERT for sentiment analysis  
- Adds short-term and long-term memory messages  

### Replier Agent
- Can use web search for gathering information  
- Replies to the user  

### Global Summarizer
- Summarizes the entire chat to produce the final sentiment analysis overview  

## Architecture
- When the user sends a message, it is stored in short-term memory along with its sentiment.  
- If there are more than 5 messages, they are summarized and stored as summary memory.  
- If a mood swing is detected (sudden change in sentiment), it is added to sentiment memory.  
- Dominant memory is the memory which…

### Tier 1 completed  
### Tier 2 completed  
### Additional features — mood graph, dominant mood, mood change  
