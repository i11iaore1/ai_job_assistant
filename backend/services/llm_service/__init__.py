from services.llm_service.base import AsyncLLMClient
from services.llm_service.groq_service.client_singletone import async_groq_client

# SyncLLMClient | AsyncLLMClient
llm_client: AsyncLLMClient = async_groq_client

__all__ = ["llm_client"]
