from config import app_config
from services.llm_service.groq_service.clients import AsyncGroqClient

async_groq_client = AsyncGroqClient(api_key=app_config.GROQ_API_KEY.get_secret_value())
