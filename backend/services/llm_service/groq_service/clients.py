from abc import ABC

from groq import AsyncGroq, Groq
from groq.types.chat.chat_completion import ChatCompletion
from pydantic import ValidationError

from exceptions.llm_service import LLMRequestProcessedIncorrectly
from services.llm_service.groq_service.presets.review_preset import (
    get_review_completion_params,
)
from services.llm_service.groq_service.schemas import RawReviewSchema, ReviewSchema


class ProcessCompletionBase(ABC):
    def process_completion(self, chat_completion: ChatCompletion) -> ReviewSchema:
        message = chat_completion.choices[0].message
        if not message.tool_calls:
            raise LLMRequestProcessedIncorrectly()
        try:
            return RawReviewSchema.model_validate_json(
                message.tool_calls[0].function.arguments
            ).process()
        except ValidationError:
            raise LLMRequestProcessedIncorrectly()


class SyncGroqClient(ProcessCompletionBase):
    def __init__(self, api_key: str) -> None:
        self._client = Groq(api_key=api_key)

    def evaluate_vacancy(
        self,
        resume_text: str,
        context: str,
        vacancy_description: str,
        language: str = "english",
    ) -> ReviewSchema:
        chat_completion: ChatCompletion = self._client.chat.completions.create(
            **get_review_completion_params(
                resume_text=resume_text,
                context=context,
                vacancy_description=vacancy_description,
                language=language,
            )
        )
        return self.process_completion(chat_completion)


class AsyncGroqClient(ProcessCompletionBase):
    def __init__(self, api_key: str) -> None:
        self._client = AsyncGroq(api_key=api_key)

    async def evaluate_vacancy(
        self,
        resume_text: str,
        context: str,
        vacancy_description: str,
        language: str = "english",
    ) -> ReviewSchema:
        chat_completion: ChatCompletion = await self._client.chat.completions.create(
            **get_review_completion_params(
                resume_text=resume_text,
                context=context,
                vacancy_description=vacancy_description,
                language=language,
            )
        )
        return self.process_completion(chat_completion)
