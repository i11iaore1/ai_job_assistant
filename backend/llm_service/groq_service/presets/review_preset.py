from groq.types.shared_params.function_definition import FunctionDefinition

from llm_service.constants import NOT_MENTIONED
from llm_service.groq_service.presets.preset import PresetSchema
from llm_service.schemas import LLMReviewResultSchema


review_tool_function_definition: FunctionDefinition = {
    "name": "save_review_result",
    "description": "Saves the jobs review including: position, company_name, advantages, disadvantages, questions",
    "parameters": LLMReviewResultSchema.model_json_schema(),
}


def system_message_template(language: str) -> str:
    return f"You are helping the user with review of the vacancy they are thinking of applying for. Analyze the provided <resume>, <context>, and <vacancy>. Output the review ONLY via the {review_tool_function_definition['name']}.\nInterpretation:\n- advantages: Non-trivial benefits and strong matches between the candidate and the role.\n- disadvantages: Poor job conditions, skill/experience mismatches, or potential red flags.\n- questions: Critical details missing from the vacancy that an applicant should clarify.\nRules:\n- if position or company_name is missing, use '{NOT_MENTIONED}'.\n- be highly critical. ONLY return an empty list if no RELEVANT points exist after thorough consideration.\n- all text values MUST be in {language}."


def user_message_template(
    resume_text: str, context: str, vacancy_description: str
) -> str:
    context_block = f"<context>{context}</context>" if context else None
    resume_block = f"<resume>{resume_text}</resume>"
    vacancy_block = f"<vacancy>{vacancy_description}</vacancy>"
    blocks = (context_block, resume_block, vacancy_block)

    return "\n".join(block for block in blocks if block is not None)


review_preset = PresetSchema(
    tool_function_definition=review_tool_function_definition,
    get_system_message_content=system_message_template,
    get_user_message_content=user_message_template,
)
