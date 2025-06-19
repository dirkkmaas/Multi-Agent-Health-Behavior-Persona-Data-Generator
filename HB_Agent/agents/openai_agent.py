from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY


class OpenAIAgent:
    """OpenAI agent class to allow OpenAI models to be used for experts"""
    def __init__(self, model_name="gpt-4.1"):
        api_key = OPENAI_API_KEY 
        if not api_key:
            raise ValueError("Missing OpenAI API Key. Set OPENAI_API_KEY in .env file.")
        
        self.llm = ChatOpenAI(model=model_name, api_key=api_key, temperature=0.2)
    
    def query(self, messages) -> str:
        return self.llm.invoke(messages)

