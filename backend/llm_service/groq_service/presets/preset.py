from typing import Callable

from pydantic import BaseModel
from groq.types.shared_params.function_definition import FunctionDefinition


class Preset(BaseModel):
    # preset for chat completion parameters
    tool_function_definition: FunctionDefinition
    get_system_message_content: Callable[..., str]
    get_user_message_content: Callable[..., str]
