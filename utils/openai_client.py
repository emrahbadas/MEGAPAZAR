from langchain_openai import ChatOpenAI
from openai import OpenAI
from config import get_settings

def get_openai_client() -> OpenAI:
    """Raw OpenAI client (embeddings için)"""
    settings = get_settings()
    return OpenAI(api_key=settings.openai_api_key)

def get_llm(model: str = "gpt-4o", temperature: float = 0.7) -> ChatOpenAI:
    """OpenAI LLM client oluştur"""
    settings = get_settings()
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=settings.openai_api_key
    )

def get_vision_llm() -> ChatOpenAI:
    """Vision model (GPT-4o)"""
    return get_llm(model="gpt-4o", temperature=0)

def get_mini_llm() -> ChatOpenAI:
    """Hızlı ve ucuz model (GPT-4o-mini)"""
    return get_llm(model="gpt-4o-mini", temperature=0)
