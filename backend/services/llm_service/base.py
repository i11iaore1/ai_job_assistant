from abc import ABC, abstractmethod

from services.llm_service.groq_service.schemas import ReviewSchema


class SyncLLMClient(ABC):
    @abstractmethod
    def evaluate_vacancy(
        self, resume_text: str, context: str, vacancy_description: str
    ) -> ReviewSchema:
        pass


class AsyncLLMClient(ABC):
    @abstractmethod
    async def evaluate_vacancy(
        self, resume_text: str, context: str, vacancy_description: str
    ) -> ReviewSchema:
        pass
