from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

class ModelProvider(Enum):
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"
    OPENAI = "openai"

class ModelType(Enum):
    GPT_35_TURBO = "gpt-35-turbo"
    GPT_35_TURBO_INSTRUCT = "gpt-35-turbo-instruct"
    GPT_35_TURBO_16K = "gpt-35-turbo-16k"
    GPT_4 = "gpt-4"
    GPT_4_32K = "gpt-4-32k"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GEMINI_15_PRO = "gemini-1.5-pro"
    GEMINI_15_FLASH = "gemini-1.5-flash"

@dataclass
class ModelConfig:
    """Configuration for AI models."""
    name: str
    provider: ModelProvider
    context_window: int
    max_output_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    supports_functions: bool = True
    supports_streaming: bool = True
    
    @property
    def max_input_tokens(self) -> int:
        """Calculate maximum input tokens."""
        return self.context_window - self.max_output_tokens
    
    @property
    def recommended_chunk_size(self) -> int:
        """Recommended chunk size for processing."""
        return min(3000, self.max_input_tokens // 4)

# Model Registry
MODEL_REGISTRY: Dict[ModelType, ModelConfig] = {
    # Azure OpenAI Models
    ModelType.GPT_35_TURBO: ModelConfig(
        name="gpt-35-turbo",
        provider=ModelProvider.AZURE_OPENAI,
        context_window=4096,
        max_output_tokens=2048,
        cost_per_1k_input=0.0015,
        cost_per_1k_output=0.002
    ),
    
    ModelType.GPT_35_TURBO_INSTRUCT: ModelConfig(
        name="gpt-35-turbo-instruct",
        provider=ModelProvider.AZURE_OPENAI,
        context_window=4096,
        max_output_tokens=2048,
        cost_per_1k_input=0.0015,
        cost_per_1k_output=0.002
    ),
    
    ModelType.GPT_35_TURBO_16K: ModelConfig(
        name="gpt-35-turbo-16k",
        provider=ModelProvider.AZURE_OPENAI,
        context_window=16384,
        max_output_tokens=8192,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.004
    ),
    
    ModelType.GPT_4: ModelConfig(
        name="gpt-4",
        provider=ModelProvider.AZURE_OPENAI,
        context_window=8192,
        max_output_tokens=4096,
        cost_per_1k_input=0.03,
        cost_per_1k_output=0.06
    ),
    
    ModelType.GPT_4_32K: ModelConfig(
        name="gpt-4-32k",
        provider=ModelProvider.AZURE_OPENAI,
        context_window=32768,
        max_output_tokens=16384,
        cost_per_1k_input=0.06,
        cost_per_1k_output=0.12
    ),
    
    ModelType.GPT_4_TURBO: ModelConfig(
        name="gpt-4-turbo",
        provider=ModelProvider.AZURE_OPENAI,
        context_window=128000,
        max_output_tokens=4096,
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.03
    ),
    
    ModelType.GPT_4O: ModelConfig(
        name="gpt-4o",
        provider=ModelProvider.AZURE_OPENAI,
        context_window=128000,
        max_output_tokens=4096,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015
    ),
    
    ModelType.GPT_4O_MINI: ModelConfig(
        name="gpt-4o-mini",
        provider=ModelProvider.AZURE_OPENAI,
        context_window=128000,
        max_output_tokens=16384,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006
    ),
    
    # Google Models
    ModelType.GEMINI_15_PRO: ModelConfig(
        name="gemini-1.5-pro",
        provider=ModelProvider.GOOGLE,
        context_window=2000000,
        max_output_tokens=8192,
        cost_per_1k_input=0.0035,
        cost_per_1k_output=0.0105
    ),
    
    ModelType.GEMINI_15_FLASH: ModelConfig(
        name="gemini-1.5-flash",
        provider=ModelProvider.GOOGLE,
        context_window=1000000,
        max_output_tokens=8192,
        cost_per_1k_input=0.00035,
        cost_per_1k_output=0.00105
    ),
}

def get_model_config(model_name: str) -> Optional[ModelConfig]:
    """Get model configuration by name."""
    for model_type, config in MODEL_REGISTRY.items():
        if config.name == model_name:
            return config
    return None

def get_available_models(provider: Optional[ModelProvider] = None) -> Dict[str, ModelConfig]:
    """Get available models, optionally filtered by provider."""
    if provider:
        return {config.name: config for config in MODEL_REGISTRY.values() 
                if config.provider == provider}
    return {config.name: config for config in MODEL_REGISTRY.values()}

def get_recommended_models_by_use_case():
    """Get recommended models for different use cases."""
    return {
        "development": ModelType.GPT_35_TURBO,
        "production": ModelType.GPT_4O,
        "large_context": ModelType.GEMINI_15_FLASH,
        "cost_effective": ModelType.GPT_4O_MINI,
        "high_quality": ModelType.GPT_4_TURBO
    }
