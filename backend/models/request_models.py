from pydantic import BaseModel
from typing import Optional, Dict, Any

class CustomCredentials(BaseModel):
    """User's own API credentials for AI services"""
    # Azure OpenAI fields
    azure_api_key: Optional[str] = None
    azure_endpoint: Optional[str] = None
    azure_api_version: Optional[str] = None
    azure_deployment: Optional[str] = None
    
    # Google Gemini fields
    google_api_key: Optional[str] = None
    
    # OpenAI fields (if we add support later)
    openai_api_key: Optional[str] = None

class ReadmeRequest(BaseModel):
    repo_url: str
    generation_method: str = "Standard README"
    model_name: str = "gpt-4o"
    provider: str = "azure_openai"
    max_tokens: int = 1000
    temperature: float = 0.3
    
    # Configuration mode
    use_hosted_service: bool = True  # True = use our keys, False = use custom credentials
    custom_credentials: Optional[CustomCredentials] = None

class ReadmeResponse(BaseModel):
    success: bool
    readme_content: str = ""
    error_message: str = ""
    generation_timestamp: str
    repo_url: str
    generation_method: str
    configuration_used: str = "hosted"  # "hosted" or "custom"