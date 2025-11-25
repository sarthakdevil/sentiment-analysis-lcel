```
uv sync
uv run poe main (runs ui version)
uv run poe dev (runs cli version)
```
#### poe combines ruff check with it
# Summary
### This is a sentiment analysis workflow with LCEL (langchain expression language) agents which are a replacement to react agents

## Tools used 
#### GEMINI (for whole workflow and summary memory)
#### Langchain agents (for agentic workflow)
#### Finetuned bert (for teir2 each message sentiment tracking)
#### Ruff (for validations and linting)

## Workflow
### workflow consist of 3 agents (Sentiment agent,Replier agent,Global summarization agent)

### sentiment agent :- 
#### uses bert for sentiment analysis
#### adds short/long term memory messages

### Replier agents :-
#### can use web search for searching and repling
#### replies to user

### Global summarizer :-
#### summarizes whole chat to make a final senmtiment analysis view

## Architecture
#### when user enters messages it gets stored in short term memory along with sentiment if more than 5 memory it is summarized and stored as summary memory
#### if anytime a moodswing is detected sudden change in sentiment it is stored in sentiment memory
#### dominant memory is memory which 

#### Teir1 completed 
#### Teir2 completed 
#### additional feature- mood graph,dominant mood,mood change