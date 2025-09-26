from pydantic import BaseModel
from typing import Optional

class ReadmeRequest(BaseModel):
    repo_url: str
    generation_method: str = "Standard README"
    model_name: str = "gpt-35-turbo-instruct"
    provider: str
    max_tokens: int = 1000
    temperature: float = 0.3

class ReadmeResponse(BaseModel):
    success: bool
    readme_content: str = ""
    error_message: str = ""
    generation_timestamp: str
    repo_url: str
    generation_method: str