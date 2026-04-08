import os
from dotenv import load_dotenv

from .groq_service.client import SyncGroqClient


load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if API_KEY is None:
    # TODO error handling
    raise Exception()

llm_client = SyncGroqClient(API_KEY)


__all__ = ["llm_client"]
