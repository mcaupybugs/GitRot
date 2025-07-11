from dotenv import load_dotenv
from langchain_openai import OpenAI as LangchainOpenAI
from langchain_openai import AzureOpenAI as LangchainAzureOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os

load_dotenv()
class GitrotBrain:
    def __init__(self):
        # Azure OpenAI configuration
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://mcaupybugs-ai.openai.azure.com/")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo-instruct")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
        
        # Google Gemini configuration
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.gemini_embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")

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
    
    def getGeminiLLM(self, max_tokens: int = 1000, temperature: float = 0.3) -> ChatGoogleGenerativeAI:
        """
        Get Google Gemini LLM using LangChain
        
        Args:
            max_tokens: Maximum tokens for the response
            temperature: Temperature for randomness (0.0 to 1.0)
            
        Returns:
            ChatGoogleGenerativeAI instance
        """
        return ChatGoogleGenerativeAI(
            model=self.gemini_model,
            google_api_key=self.google_api_key,
            temperature=temperature,
            max_output_tokens=max_tokens,
            convert_system_message_to_human=True  # Gemini-specific setting
        )
    
    def getGeminiEmbeddingModel(self):
        """
        Get Google Gemini Embedding Model using LangChain
        
        Returns:
            GoogleGenerativeAIEmbeddings instance
        """
        return GoogleGenerativeAIEmbeddings(
            model=self.gemini_embedding_model,
            google_api_key=self.google_api_key
        )