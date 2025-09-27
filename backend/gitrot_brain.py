from dotenv import load_dotenv
from langchain_openai import OpenAI as LangchainOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from config.model_config import get_model_config, ModelProvider
from config.model_credential_factory import model_credential_factory
from models.request_models import CustomCredentials
from typing import Optional
import os
import time

load_dotenv()
class GitrotBrain:
    def __init__(self, model_name: str, custom_credentials: Optional[CustomCredentials] = None):
        self.model_name = model_name
        self.custom_credentials = custom_credentials
        
        if custom_credentials:
            # Use custom credentials
            self.model_credentials = self._prepare_custom_credentials(custom_credentials)
        else:
            # Use hosted credentials
            self.model_credentials = model_credential_factory.get_model_credentials(model_name=model_name)
        
        self.model_config = get_model_config(model_name=model_name)
    
    def _prepare_custom_credentials(self, custom_creds: CustomCredentials) -> dict:
        """Convert CustomCredentials to format expected by LangChain"""
        if custom_creds.azure_api_key:
            return {
                'api_key': custom_creds.azure_api_key,
                'azure_endpoint': custom_creds.azure_endpoint,
                'api_version': custom_creds.azure_api_version or "2024-12-01-preview",
                'azure_deployment': custom_creds.azure_deployment or self.model_name
            }
        elif custom_creds.google_api_key:
            return {
                'google_api_key': custom_creds.google_api_key
            }
        elif custom_creds.openai_api_key:
            return {
                'api_key': custom_creds.openai_api_key
            }
        else:
            raise ValueError("No valid custom credentials provided")
        
    def get_llm(self):
        if self.model_config.provider == ModelProvider.AZURE_OPENAI:
            return AzureChatOpenAI(
                max_tokens=self.model_config.max_output_tokens,
                **self.model_credentials  # Unpack credentials dictionary
            )

        elif self.model_config.provider == ModelProvider.GOOGLE:
            return ChatGoogleGenerativeAI(
                model=self.model_config.name,  # Use actual model name
                max_output_tokens=self.model_config.max_output_tokens,
                convert_system_message_to_human=True,
                **self.model_credentials  # Unpack credentials dictionary
            )

    def getEmbeddingModel(self):
        """Only works with hosted service for now"""
        if self.custom_credentials:
            return None  # Custom credentials don't support embeddings yet
            
        # Use the hosted embedding model with fallback to gpt-35-turbo-instruct credentials
        try:
            embedding_credentials = model_credential_factory.get_model_credentials("text-embedding-ada-002")
        except:
            # Fallback to using the same credentials as the main model for Azure
            if self.model_config.provider == ModelProvider.AZURE_OPENAI:
                embedding_credentials = self.model_credentials.copy()
                embedding_credentials['azure_deployment'] = 'text-embedding-ada-002'
            else:
                return None
                
        return AzureOpenAIEmbeddings(
            **embedding_credentials
        )