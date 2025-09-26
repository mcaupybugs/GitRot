import pytest
import os
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Import the modules we're testing
from backend.config.model_credential_factory import (
    AzureCredentials,
    GoogleCredentials,
    ModelCredentialFactory,
    model_credential_factory
)
from backend.config.model_config import ModelProvider, ModelType, ModelConfig


class TestAzureCredentials:
    """Test suite for AzureCredentials class."""
    
    def test_azure_credentials_initialization(self):
        """Test that AzureCredentials can be initialized with all required fields."""
        creds = AzureCredentials(
            api_key="test_key",
            endpoint="https://test.openai.azure.com",
            api_version="2023-12-01-preview",
            deployment_name="test-deployment"
        )
        
        assert creds.api_key == "test_key"
        assert creds.endpoint == "https://test.openai.azure.com"
        assert creds.api_version == "2023-12-01-preview"
        assert creds.deployment_name == "test-deployment"
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_GPT_4O_MINI_API_KEY': 'test_azure_key',
        'AZURE_OPENAI_GPT_4O_MINI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_GPT_4O_MINI_API_VERSION': '2023-12-01-preview',
        'AZURE_OPENAI_GPT_4O_MINI_DEPLOYMENT': 'gpt-4o-mini-deployment'
    })
    def test_azure_credentials_from_env_success(self):
        """Test successful creation of AzureCredentials from environment variables."""
        creds = AzureCredentials.from_env("gpt-4o-mini")
        
        assert creds.api_key == "test_azure_key"
        assert creds.endpoint == "https://test.openai.azure.com"
        assert creds.api_version == "2023-12-01-preview"
        assert creds.deployment_name == "gpt-4o-mini-deployment"
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_GPT_35_TURBO_API_KEY': 'test_gpt35_key',
        'AZURE_OPENAI_GPT_35_TURBO_ENDPOINT': 'https://gpt35.openai.azure.com',
        'AZURE_OPENAI_GPT_35_TURBO_API_VERSION': '2023-05-15',
        'AZURE_OPENAI_GPT_35_TURBO_DEPLOYMENT': 'gpt-35-turbo-deployment'
    })
    def test_azure_credentials_from_env_with_hyphen_conversion(self):
        """Test that model names with hyphens are properly converted to underscores for env vars."""
        creds = AzureCredentials.from_env("gpt-35-turbo")
        
        assert creds.api_key == "test_gpt35_key"
        assert creds.endpoint == "https://gpt35.openai.azure.com"
        assert creds.api_version == "2023-05-15"
        assert creds.deployment_name == "gpt-35-turbo-deployment"
    
    def test_azure_credentials_from_env_missing_vars(self):
        """Test AzureCredentials.from_env when environment variables are missing."""
        with patch.dict(os.environ, {}, clear=True):
            creds = AzureCredentials.from_env("missing-model")
            
            assert creds.api_key is None
            assert creds.endpoint is None
            assert creds.api_version is None
            assert creds.deployment_name is None
    
    def test_azure_credentials_to_dict(self):
        """Test that AzureCredentials.to_dict returns the correct format."""
        creds = AzureCredentials(
            api_key="test_key",
            endpoint="https://test.openai.azure.com",
            api_version="2023-12-01-preview",
            deployment_name="test-deployment"
        )
        
        result = creds.to_dict()
        expected = {
            'api_key': 'test_key',
            'azure_endpoint': 'https://test.openai.azure.com',
            'api_version': '2023-12-01-preview',
            'azure_deployment': 'test-deployment'
        }
        
        assert result == expected


class TestGoogleCredentials:
    """Test suite for GoogleCredentials class."""
    
    def test_google_credentials_initialization(self):
        """Test that GoogleCredentials can be initialized with required fields."""
        creds = GoogleCredentials(api_key="test_google_key")
        assert creds.api_key == "test_google_key"
    
    @patch.dict(os.environ, {
        'GOOGLE_GEMINI_1_5_PRO_API_KEY': 'test_gemini_key'
    })
    def test_google_credentials_from_env_success(self):
        """Test successful creation of GoogleCredentials from environment variables."""
        creds = GoogleCredentials.from_env("gemini-1.5-pro")
        assert creds.api_key == "test_gemini_key"
    
    @patch.dict(os.environ, {
        'GOOGLE_GEMINI_1_5_FLASH_API_KEY': 'test_flash_key'
    })
    def test_google_credentials_from_env_with_hyphen_conversion(self):
        """Test that model names with hyphens and dots are properly converted."""
        creds = GoogleCredentials.from_env("gemini-1.5-flash")
        assert creds.api_key == "test_flash_key"
    
    def test_google_credentials_from_env_missing_vars(self):
        """Test GoogleCredentials.from_env when environment variables are missing."""
        with patch.dict(os.environ, {}, clear=True):
            creds = GoogleCredentials.from_env("missing-model")
            assert creds.api_key is None
    
    def test_google_credentials_to_dict(self):
        """Test that GoogleCredentials.to_dict returns the correct format."""
        creds = GoogleCredentials(api_key="test_google_key")
        result = creds.to_dict()
        expected = {'google_api_key': 'test_google_key'}
        assert result == expected


class TestModelCredentialFactory:
    """Test suite for ModelCredentialFactory class."""
    
    def setup_method(self):
        """Set up fresh factory instance for each test."""
        self.factory = ModelCredentialFactory()
    
    def test_initialization(self):
        """Test that ModelCredentialFactory initializes with empty caches."""
        assert self.factory._azure_creds == {}
        assert self.factory._google_creds == {}
        assert self.factory._model_configs == {}
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_GPT_4O_MINI_API_KEY': 'test_azure_key',
        'AZURE_OPENAI_GPT_4O_MINI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_GPT_4O_MINI_API_VERSION': '2023-12-01-preview',
        'AZURE_OPENAI_GPT_4O_MINI_DEPLOYMENT': 'gpt-4o-mini-deployment'
    })
    def test_get_azure_credentials_lazy_loading(self):
        """Test that Azure credentials are lazy loaded and cached."""
        model_name = "gpt-4o-mini"
        
        # First call should create and cache
        creds1 = self.factory._get_azure_credentials(model_name)
        assert model_name in self.factory._azure_creds
        assert creds1.api_key == "test_azure_key"
        
        # Second call should return cached instance
        creds2 = self.factory._get_azure_credentials(model_name)
        assert creds1 is creds2  # Same object reference
    
    @patch.dict(os.environ, {
        'GOOGLE_GEMINI_1_5_PRO_API_KEY': 'test_gemini_key'
    })
    def test_get_google_credentials_lazy_loading(self):
        """Test that Google credentials are lazy loaded and cached."""
        model_name = "gemini-1.5-pro"
        
        # First call should create and cache
        creds1 = self.factory._get_google_credentials(model_name)
        assert model_name in self.factory._google_creds
        assert creds1.api_key == "test_gemini_key"
        
        # Second call should return cached instance
        creds2 = self.factory._get_google_credentials(model_name)
        assert creds1 is creds2  # Same object reference
    
    @patch('backend.config.model_credential_factory.get_model_config')
    def test_get_model_config_cached_lazy_loading(self, mock_get_model_config):
        """Test that model configs are lazy loaded and cached."""
        model_name = "gpt-4o-mini"
        mock_config = ModelConfig(
            name=model_name,
            provider=ModelProvider.AZURE_OPENAI,
            context_window=128000,
            max_output_tokens=4096,
            cost_per_1k_input=0.00015,
            cost_per_1k_output=0.0006
        )
        mock_get_model_config.return_value = mock_config
        
        # First call should create and cache
        config1 = self.factory._get_model_config_cached(model_name)
        assert model_name in self.factory._model_configs
        assert config1 == mock_config
        assert mock_get_model_config.call_count == 1
        
        # Second call should return cached instance
        config2 = self.factory._get_model_config_cached(model_name)
        assert config1 is config2
        assert mock_get_model_config.call_count == 1  # No additional calls
    
    @patch('backend.config.model_credential_factory.get_model_config')
    def test_calculate_estimated_cost_success(self, mock_get_model_config):
        """Test successful cost calculation."""
        mock_config = ModelConfig(
            name="gpt-4o-mini",
            provider=ModelProvider.AZURE_OPENAI,
            context_window=128000,
            max_output_tokens=4096,
            cost_per_1k_input=0.00015,
            cost_per_1k_output=0.0006
        )
        mock_get_model_config.return_value = mock_config
        
        # Test with specific token counts
        input_tokens = 1000
        output_tokens = 500
        
        cost = self.factory.calculate_estimated_cost("gpt-4o-mini", input_tokens, output_tokens)
        
        expected_input_cost = (input_tokens / 1000) * 0.00015  # $0.00015
        expected_output_cost = (output_tokens / 1000) * 0.0006  # $0.0003
        expected_total = expected_input_cost + expected_output_cost  # $0.00045
        
        assert cost == expected_total
        assert cost == 0.00045
    
    @patch('backend.config.model_credential_factory.get_model_config')
    def test_calculate_estimated_cost_no_config(self, mock_get_model_config):
        """Test cost calculation when model config is not found."""
        mock_get_model_config.return_value = None
        
        cost = self.factory.calculate_estimated_cost("unknown-model", 1000, 500)
        assert cost is None
    
    @patch('backend.config.model_credential_factory.get_model_config')
    @patch.dict(os.environ, {
        'AZURE_OPENAI_GPT_4O_MINI_API_KEY': 'test_azure_key',
        'AZURE_OPENAI_GPT_4O_MINI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_GPT_4O_MINI_API_VERSION': '2023-12-01-preview',
        'AZURE_OPENAI_GPT_4O_MINI_DEPLOYMENT': 'gpt-4o-mini-deployment'
    })
    def test_get_model_credentials_azure_success(self, mock_get_model_config):
        """Test successful retrieval of Azure model credentials."""
        mock_config = ModelConfig(
            name="gpt-4o-mini",
            provider=ModelProvider.AZURE_OPENAI,
            context_window=128000,
            max_output_tokens=4096,
            cost_per_1k_input=0.00015,
            cost_per_1k_output=0.0006
        )
        mock_get_model_config.return_value = mock_config
        
        credentials = self.factory.get_model_credentials("gpt-4o-mini")
        
        expected = {
            'api_key': 'test_azure_key',
            'azure_endpoint': 'https://test.openai.azure.com',
            'api_version': '2023-12-01-preview',
            'azure_deployment': 'gpt-4o-mini-deployment'
        }
        
        assert credentials == expected
    
    @patch('backend.config.model_credential_factory.get_model_config')
    @patch.dict(os.environ, {
        'GOOGLE_GEMINI_1_5_PRO_API_KEY': 'test_gemini_key'
    })
    def test_get_model_credentials_google_success(self, mock_get_model_config):
        """Test successful retrieval of Google model credentials."""
        mock_config = ModelConfig(
            name="gemini-1.5-pro",
            provider=ModelProvider.GOOGLE,
            context_window=1048576,
            max_output_tokens=8192,
            cost_per_1k_input=0.00125,
            cost_per_1k_output=0.00375
        )
        mock_get_model_config.return_value = mock_config
        
        credentials = self.factory.get_model_credentials("gemini-1.5-pro")
        
        expected = {'google_api_key': 'test_gemini_key'}
        assert credentials == expected
    
    @patch('backend.config.model_credential_factory.get_model_config')
    def test_get_model_credentials_unsupported_model(self, mock_get_model_config):
        """Test error when requesting credentials for unsupported model."""
        mock_get_model_config.return_value = None
        
        with pytest.raises(ValueError, match="Unsupported model: unknown-model"):
            self.factory.get_model_credentials("unknown-model")
    
    @patch('backend.config.model_credential_factory.get_model_config')
    def test_get_model_credentials_unsupported_provider(self, mock_get_model_config):
        """Test error when model has unsupported provider."""
        mock_config = ModelConfig(
            name="test-model",
            provider=ModelProvider.OPENAI,  # Unsupported provider
            context_window=4096,
            max_output_tokens=1024,
            cost_per_1k_input=0.001,
            cost_per_1k_output=0.002
        )
        mock_get_model_config.return_value = mock_config
        
        with pytest.raises(ValueError, match="Unsupported provider: ModelProvider.OPENAI"):
            self.factory.get_model_credentials("test-model")


class TestModuleGlobals:
    """Test suite for module-level globals."""
    
    def test_model_credential_factory_singleton_exists(self):
        """Test that the module provides a global factory instance."""
        assert model_credential_factory is not None
        assert isinstance(model_credential_factory, ModelCredentialFactory)


class TestIntegration:
    """Integration tests that test multiple components together."""
    
    @patch('backend.config.model_credential_factory.get_model_config')
    @patch.dict(os.environ, {
        'AZURE_OPENAI_GPT_4O_MINI_API_KEY': 'integration_azure_key',
        'AZURE_OPENAI_GPT_4O_MINI_ENDPOINT': 'https://integration.openai.azure.com',
        'AZURE_OPENAI_GPT_4O_MINI_API_VERSION': '2023-12-01-preview',
        'AZURE_OPENAI_GPT_4O_MINI_DEPLOYMENT': 'integration-deployment',
        'GOOGLE_GEMINI_15_PRO_API_KEY': 'integration_gemini_key'
    })
    def test_end_to_end_azure_workflow(self, mock_get_model_config):
        """Test complete workflow for Azure model from config to credentials."""
        mock_config = ModelConfig(
            name="gpt-4o-mini",
            provider=ModelProvider.AZURE_OPENAI,
            context_window=128000,
            max_output_tokens=4096,
            cost_per_1k_input=0.00015,
            cost_per_1k_output=0.0006
        )
        mock_get_model_config.return_value = mock_config
        
        factory = ModelCredentialFactory()
        
        # Test cost calculation
        cost = factory.calculate_estimated_cost("gpt-4o-mini", 2000, 1000)
        expected_cost = (2000 / 1000) * 0.00015 + (1000 / 1000) * 0.0006  # $0.0009
        assert cost == expected_cost
        
        # Test credential retrieval
        credentials = factory.get_model_credentials("gpt-4o-mini")
        expected_creds = {
            'api_key': 'integration_azure_key',
            'azure_endpoint': 'https://integration.openai.azure.com',
            'api_version': '2023-12-01-preview',
            'azure_deployment': 'integration-deployment'
        }
        assert credentials == expected_creds
        
        # Verify caching worked
        assert "gpt-4o-mini" in factory._azure_creds
        assert "gpt-4o-mini" in factory._model_configs
    
    @patch('backend.config.model_credential_factory.get_model_config')
    @patch.dict(os.environ, {
        'GOOGLE_GEMINI_1_5_FLASH_API_KEY': 'integration_flash_key'
    })
    def test_end_to_end_google_workflow(self, mock_get_model_config):
        """Test complete workflow for Google model from config to credentials."""
        mock_config = ModelConfig(
            name="gemini-1.5-flash",
            provider=ModelProvider.GOOGLE,
            context_window=1048576,
            max_output_tokens=8192,
            cost_per_1k_input=0.000075,
            cost_per_1k_output=0.0003
        )
        mock_get_model_config.return_value = mock_config
        
        factory = ModelCredentialFactory()
        
        # Test cost calculation
        cost = factory.calculate_estimated_cost("gemini-1.5-flash", 4000, 2000)
        expected_cost = (4000 / 1000) * 0.000075 + (2000 / 1000) * 0.0003  # $0.0009
        assert cost == expected_cost
        
        # Test credential retrieval
        credentials = factory.get_model_credentials("gemini-1.5-flash")
        expected_creds = {'google_api_key': 'integration_flash_key'}
        assert credentials == expected_creds
        
        # Verify caching worked
        assert "gemini-1.5-flash" in factory._google_creds
        assert "gemini-1.5-flash" in factory._model_configs