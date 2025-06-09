from dotenv import load_dotenv
from langchain_openai import OpenAI as LangchainOpenAI
from langchain_openai import AzureOpenAI as LangchainAzureOpenAI
from langchain_openai import AzureOpenAIEmbeddings
import os

load_dotenv()
class GitrotBrain:
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://mcaupybugs-ai.openai.azure.com/")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo-instruct")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
        
    def getLLM(self, max_tokens:int = 1000, temperature: float = 0.3 ) -> LangchainAzureOpenAI:
        return LangchainAzureOpenAI(
            azure_deployment = self.deployment_name,
            api_version = self.api_version,
            azure_endpoint = self.azure_endpoint,
            api_key = self.api_key,
            temperature = temperature,
            max_tokens = max_tokens
        )
    
    def getEmbeddingModel(self):
        return AzureOpenAIEmbeddings(
            azure_deployment = self.embedding_deployment,
            azure_endpoint = self.azure_endpoint,
            api_key = self.api_key,
            api_version = self.api_version,
        )