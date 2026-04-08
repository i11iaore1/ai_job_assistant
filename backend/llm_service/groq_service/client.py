import json

from groq import Groq

from llm_service.constants import NOT_MENTIONED
from errors.llm_service import LLMServiceException
from llm_service.llm_service import SyncLLMClient
from llm_service.types import ReviewResult
from llm_service.groq_service.presets.review_preset import review_preset
from llm_service.groq_service.config import MODEL


class SyncGroqClient(SyncLLMClient):
    def __init__(self, api_key: str) -> None:
        self._client = Groq(
            api_key=api_key,
        )

    def evaluate_vacancy(
        self, resume_text: str, context: str, vacancy_description: str
    ) -> ReviewResult:
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

        # TODO manage "not mentioned"
        if arguments["company_name"] == NOT_MENTIONED:
            arguments["company_name"] = None

        # TODO manage validation error
        return ReviewResult(**arguments)
