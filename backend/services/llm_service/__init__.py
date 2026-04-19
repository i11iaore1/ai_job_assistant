from services.llm_service.groq_service.client_singletone import async_groq_client
from services.llm_service.llm_service import AsyncLLMClient

# SyncLLMClient | AsyncLLMClient
llm_client: AsyncLLMClient = async_groq_client

__all__ = ["llm_client"]
