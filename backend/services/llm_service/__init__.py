from services.llm_service.groq_service.client_singletone import async_groq_client

llm_client = async_groq_client

__all__ = ["llm_client"]
