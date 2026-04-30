from typing import Any, Protocol

from services.llm_service.groq_service.schemas import ReviewSchema


class SyncLLMClient(Protocol):
    def evaluate_vacancy(
        self,
        resume_text: str,
        context: str,
        vacancy_description: str,
        *args: Any,
        **kwargs: Any,
    ) -> ReviewSchema: ...


class AsyncLLMClient(Protocol):
    async def evaluate_vacancy(
        self,
        resume_text: str,
        context: str,
        vacancy_description: str,
        *args: Any,
        **kwargs: Any,
    ) -> ReviewSchema: ...
