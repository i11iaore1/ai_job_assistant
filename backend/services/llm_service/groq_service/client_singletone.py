from config import app_config
from services.llm_service.base import AsyncLLMClient
from services.llm_service.groq_service.clients import AsyncGroqClient

async_groq_client: AsyncLLMClient = AsyncGroqClient(
    api_key=app_config.groq_api_key.get_secret_value()
)
