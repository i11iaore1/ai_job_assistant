import json

from groq import AsyncGroq, Groq

from errors.llm_service import LLMServiceException
from llm_service.groq_service.config import MODEL
from llm_service.groq_service.presets.review_preset import review_preset
from llm_service.llm_service import AsyncLLMClient, SyncLLMClient
from llm_service.schemas import RawReviewSchema, ReviewSchema


class SyncGroqClient(SyncLLMClient):
    def __init__(self, api_key: str) -> None:
        self._client = Groq(
            api_key=api_key,
        )

    def evaluate_vacancy(
        self, resume_text: str, context: str, vacancy_description: str
    ) -> ReviewSchema:
        chat_response = self._client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": review_preset.get_system_message_content(
                        language="ukrainian"  # TODO develop language choice logic
                    ),
                },
                {
                    "role": "user",
                    "content": review_preset.get_user_message_content(
                        resume_text=resume_text,
                        context=context,
                        vacancy_description=vacancy_description,
                    ),
                },
            ],
            tools=[
                {
                    "type": "function",
                    "function": review_preset.tool_function_definition,
                }
            ],
            tool_choice={
                "type": "function",
                "function": {"name": review_preset.tool_function_definition["name"]},
            },
        )

        ####### response processing
        message = chat_response.choices[0].message
        if not message.tool_calls:
            print(message)
            raise LLMServiceException

        arguments = json.loads(message.tool_calls[0].function.arguments)

        # TODO manage validation error
        return RawReviewSchema(**arguments).process()


class AsyncGroqClient(AsyncLLMClient):
    def __init__(self, api_key: str) -> None:
        self._client = AsyncGroq(
            api_key=api_key,
        )

    async def evaluate_vacancy(
        self, resume_text: str, context: str, vacancy_description: str
    ) -> ReviewSchema:
        chat_response = await self._client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": review_preset.get_system_message_content(
                        language="ukrainian"  # TODO develop language choice logic
                    ),
                },
                {
                    "role": "user",
                    "content": review_preset.get_user_message_content(
                        resume_text=resume_text,
                        context=context,
                        vacancy_description=vacancy_description,
                    ),
                },
            ],
            tools=[
                {
                    "type": "function",
                    "function": review_preset.tool_function_definition,
                }
            ],
            tool_choice={
                "type": "function",
                "function": {"name": review_preset.tool_function_definition["name"]},
            },
        )

        ####### response processing
        message = chat_response.choices[0].message
        if not message.tool_calls:
            print(message)
            raise LLMServiceException

        arguments = json.loads(message.tool_calls[0].function.arguments)

        # TODO manage validation error
        return RawReviewSchema(**arguments).process()
