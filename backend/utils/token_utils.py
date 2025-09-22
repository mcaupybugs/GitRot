import tiktoken
from config.model_config import ModelConfig, get_model_config
from typing import Optional

class TokenCalculator:
    """Utility class for token calculations and validation."""
    def __init__(self, model_name):
        self.model_name = model_name
        self.model_config = get_model_config(model_name)
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.model_name)
        except:
            #TODO:  Check what default value should be added instead of this.
            self.tokenizer = tiktoken.get_encoding('cl100k_base')

    def count_token(self, text: str) -> str:
        """Count exact tokens in text"""
        try:
            return len(self.tokenizer.encode(text))
        except Exception:
            return len(text)//4 # Fallback estimation
        
    def get_max_input_tokens_for_readme(self, buffer_percentage: float = 0.10) -> int:
        """
        Get maximum input tokens for README generation with safety buffer.
        
        Args:
            buffer_percentage: Percentage of context window to reserve as safety buffer
                              (default 10% = 0.10)
        
        Returns:
            Maximum safe input tokens for README generation
        """
        if not self.model_config:
            return 2000
        
        context_window = self.model_config.context_window
        max_output_tokens = 700 # Keeping 700 as output token buffer as do not need readme more than this

        buffer_tokens = int(context_window * buffer_percentage)

        max_input_tokens = context_window - max_output_tokens - buffer_tokens

        min_input_tokens = 500
        max_input_tokens = max(max_input_tokens, min_input_tokens)
        
        return max_input_tokens
    
    def is_summary_within_size(self, text: str, buffer_percentage: float = 0.10) -> bool:
        return self.count_token(text) < self.get_max_input_tokens_for_readme(buffer_percentage)