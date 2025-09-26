from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional, Union, Dict, Any
import os
from .model_config import ModelProvider, ModelType, ModelConfig, get_model_config
load_dotenv()

@dataclass
class AzureCredentials:
    """Azure OpenAI specific credentials and configurations."""
    api_key: str
    endpoint: str
    api_version: str
    deployment_name: str

    @classmethod
    def from_env(cls, model_name: str) -> 'AzureCredentials':

        model_env_name = model_name.upper().replace('-','_')
        return cls(
            api_key=os.getenv(f"AZURE_OPENAI_{model_env_name}_API_KEY"),
            endpoint=os.getenv(f"AZURE_OPENAI_{model_env_name}_ENDPOINT"),
            api_version=os.getenv(f"AZURE_OPENAI_{model_env_name}_API_VERSION"),
            deployment_name=os.getenv(f"AZURE_OPENAI_{model_env_name}_DEPLOYMENT")
        )
    
    def to_dict(self) -> Dict[str, str]:
        """Convert credentials to dictionary for LLM initialization."""
        return {
            'api_key': self.api_key,
            'azure_endpoint': self.endpoint,
            'api_version': self.api_version,
            'azure_deployment': self.deployment_name
        }
    
@dataclass
class GoogleCredentials:
    """Google AI specific credentials and configuration."""
    api_key: str

    @classmethod
    def from_env(cls, model_name: str) -> 'GoogleCredentials':
        model_env_name = model_name.upper().replace('-','_').replace('.','_')

        return cls(
            api_key=os.getenv(f"GOOGLE_{model_env_name}_API_KEY")
        )
    
    def to_dict(self) -> Dict[str, str]:
        """Convert credentials to dictionary for LLM initialization."""
        return {
            'google_api_key': self.api_key
        }
    
class ModelCredentialFactory:
    """Factory for creating model-specific LLM instances with lazy loading."""

    def __init__(self):
        self._azure_creds = {}
        self._google_creds = {}
        self._model_configs = {}

    def _get_azure_credentials(self, model_name: str) -> AzureCredentials:
        """Lazy loading azure credentials only when needed for specific model."""
        if model_name not in self._azure_creds:
            self._azure_creds[model_name]=AzureCredentials.from_env(model_name)
        return self._azure_creds[model_name]
    
    def _get_google_credentials(self, model_name: str) -> GoogleCredentials:
        """Lazy load Google credentials only when needed for specific model."""
        if model_name not in self._google_creds:
            self._google_creds[model_name] = GoogleCredentials.from_env(model_name)
        return self._google_creds[model_name]
    
    def _get_model_config_cached(self, model_name: str) -> Optional[ModelConfig]:
        """Get model configuration with caching."""
        if model_name not in self._model_configs:
            self._model_configs[model_name] = get_model_config(model_name)
        return self._model_configs[model_name]
    
    def calculate_estimated_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> Optional[float]:
        """Calculate estimated cost for using a specific model."""
        config = self._get_model_config_cached(model_name)
        if not config:
            return None
        
        input_cost = (input_tokens / 1000) * config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output
        return input_cost + output_cost
    
    def get_model_credentials(self, model_name: str) -> Dict[str, Any]:
        """
        Get credentials for a specific model as a dictionary.
        Returns credentials in format ready for LLM initialization.
        """
        model_config = self._get_model_config_cached(model_name)
        
        if not model_config:
            raise ValueError(f"Unsupported model: {model_name}")
        
        if model_config.provider == ModelProvider.AZURE_OPENAI:
            creds = self._get_azure_credentials(model_name)
            return creds.to_dict()
        
        elif model_config.provider == ModelProvider.GOOGLE:
            creds = self._get_google_credentials(model_name)
            return creds.to_dict()
        
        else:
            raise ValueError(f"Unsupported provider: {model_config.provider}")
    
model_credential_factory = ModelCredentialFactory()