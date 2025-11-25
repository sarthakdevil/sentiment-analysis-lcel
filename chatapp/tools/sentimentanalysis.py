from langchain.tools import tool
from transformers import pipeline
from typing import List, Dict

@tool
def analyze_sentiment(text: str) -> List[Dict]:
    """
    Analyze the sentiment of the given text using a pre-trained model.
    Args:
        text: The input text to analyze.
    Returns:
    
        A dictionary containing the sentiment analysis results.
        example: {"label": "POSITIVE", "score": 0.998}
    """
    specific_model = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")
    result = specific_model(text)
    if result:
        result = result[0]
    if result['label'] == 'NEGATIVE':
        result['score'] = -result['score']

    print(result)
    return result