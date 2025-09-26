from dotenv import load_dotenv
from langchain_openai import OpenAI as LangchainOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from config.model_config import get_model_config, ModelProvider
from config.model_credential_factory import model_credential_factory
import os
import time

load_dotenv()
class GitrotBrain:
    def __init__(self, model_name: str):
        self.model_credentials = model_credential_factory.get_model_credentials(model_name=model_name)
        self.model_config = get_model_config(model_name=model_name)
        
    def get_llm(self):
        if self.model_config.provider == ModelProvider.AZURE_OPENAI:
            return AzureChatOpenAI(
                max_tokens=self.model_config.max_output_tokens,
                **self.model_credentials  # Unpack credentials dictionary
            )

        elif self.model_config.provider == ModelProvider.GOOGLE:
            return ChatGoogleGenerativeAI(
                model=self.model_config.name,  # Use actual model name
                max_output_tokens=self.model_config.max_tokens,
                convert_system_message_to_human=True,
                **self.model_credentials  # Unpack credentials dictionary
            )

    def getEmbeddingModel(self):
        return AzureOpenAIEmbeddings(
            azure_deployment = self.embedding_deployment,
            azure_endpoint = self.azure_endpoint,
            api_key = self.api_key,
            api_version = self.api_version,
        )