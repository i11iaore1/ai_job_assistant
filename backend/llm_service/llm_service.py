from abc import ABC, abstractmethod

from llm_service.types import ReviewResult


class SyncLLMClient(ABC):
    @abstractmethod
    def evaluate_vacancy(
        self, resume_text: str, context: str, vacancy_description: str
    ) -> ReviewResult:
        pass
