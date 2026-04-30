from typing import Any

from groq.types.shared_params.function_definition import FunctionDefinition

from services.llm_service.constants import NOT_MENTIONED
from services.llm_service.groq_service.config import MODEL
from services.llm_service.groq_service.presets.preset import PresetSchema
from services.llm_service.groq_service.schemas import RawReviewSchema

function_definition: FunctionDefinition = {
    "name": "save_review",
    "description": "Saves job review including: position, company_name, advantages, disadvantages, questions",
    "parameters": RawReviewSchema.model_json_schema(),
}


def system_message_content_template(language: str) -> str:
    return f"You are helping user with review of vacancy, they are thinking of applying for. Analyze provided <resume>, <context>, and <vacancy>. Output review ONLY via {function_definition['name']}.\nInterpretation:\n- advantages: non-trivial benefits and strong matches between candidate and role.\n- disadvantages: poor job conditions, skill/experience mismatches, potential red flags.\n- questions: details missing from vacancy that applicant should clarify.\nRules:\n- if position or company_name is missing, use '{NOT_MENTIONED}'.\n- be highly critical. ONLY return empty list if no RELEVANT points exist after thorough consideration.\n- all text values MUST be in {language}."


def user_message_content_template(
    resume_text: str, context: str, vacancy_description: str
) -> str:
    context_block = f"<context>{context}</context>" if context else None
    resume_block = f"<resume>{resume_text}</resume>"
    vacancy_block = f"<vacancy>{vacancy_description}</vacancy>"
    blocks = (context_block, resume_block, vacancy_block)

    return "\n".join(block for block in blocks if block is not None)


review_preset = PresetSchema(
    tool_function_definition=function_definition,
    get_system_message_content=system_message_content_template,
    get_user_message_content=user_message_content_template,
)


def get_review_completion_params(
    resume_text: str,
    context: str,
    vacancy_description: str,
    language: str,
) -> dict[str, Any]:
    return {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": review_preset.get_system_message_content(language=language),
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
        "tools": [
            {
                "type": "function",
                "function": review_preset.tool_function_definition,
            }
        ],
        "tool_choice": {
            "type": "function",
            "function": {"name": review_preset.tool_function_definition["name"]},
        },
    }
