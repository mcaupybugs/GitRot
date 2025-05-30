import os
import tempfile
from openai import AzureOpenAI
from langchain_openai import AzureOpenAI as LangchainAzureOpenAI
from langchain_openai import OpenAI as LangchainOpenAI
from langchain_core.documents import Document
from langchain.chains.summarize import load_summarize_chain
from dotenv import load_dotenv
from git import Repo
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
if not api_key:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set.")
def clone_repo(github_url: str, folder_name: str="cloned_repo")-> str:
    if os.path.exists(folder_name):
        print(f"Folder '{folder_name}' already exists. Skipping clone.")
    else:
        Repo.clone_from(github_url, folder_name)
        print(f"Repository cloned into '{folder_name}'")
    return folder_name

def extract_code_from_repo(folder_name: str)-> str:
    code_text = ""
    for root, dirs, files in os.walk(folder_name):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                # Check if the file has a typical text file extension
                text_extensions = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.csv', '.ini', '.cfg', '.xml', '.html', '.js', '.css', '.java', '.c', '.cpp', '.ts', '.go', '.rs', '.rb', '.php', '.sh', '.bat'}
                _, ext = os.path.splitext(file)
                if ext.lower() not in text_extensions:
                    continue
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    code_text += f"File: {file_path}\n{content}\n\n"
            except Exception as e:
                print(f"Error reading file {file}: {e}")
    return code_text

def summarize_code(code_text: str) -> str:
    """
    Summarize the code using Azure OpenAI and LangChain's summarize chain.
    
    Args:
        code_text: The text content of the code to summarize
        
    Returns:
        A summary of the code
    """
    # Get configuration from environment variables with fallbacks
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://mcaupybugs-ai.openai.azure.com/")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo-instruct") # Use your actual Azure deployment name
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    # Create the LangChain Azure OpenAI instance
    llm = LangchainAzureOpenAI(
        azure_deployment=deployment_name,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        temperature=0,
    )
    
    # Split the code text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,  # Characters per chunk (approximately 1000 tokens)
        chunk_overlap=200,  # Overlap between chunks
        separators=["\nFile:", "\n\n", "\n", " ", ""]  # Split preferentially at file boundaries
    )

    chunks = text_splitter.split_text(code_text)
    documents = [Document(page_content=chunk) for chunk in chunks]
    
    print(f"Split code into {len(documents)} chunks for processing")
    # Create and run the summarize chain
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    return chain.invoke({"input_documents": documents})

def generate_readme(summary: str) -> str:
    prompt = f"""
You are a professional technical writer. Based on the following codebase summary, generate a complete README.md file. 
Include: 
- Project Title
- Description
- Installation
- Usage
- Features (if applicable)
- License (if applicable)

Summary:
{summary}
"""
    llm = LangchainAzureOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo-instruct"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://mcaupybugs-ai.openai.azure.com/"),
        api_key=api_key,
        temperature=0.3
    )
    return llm.invoke(prompt)

def generate_readme_from_repo_url(github_url: str):
    repo_name = github_url.rstrip('/').split('/')[-1]
    local_path = clone_repo(github_url, repo_name)
    code_text = extract_code_from_repo(local_path)
    summary = summarize_code(code_text)
    readme_content = generate_readme(summary)
    with open(os.path.join(local_path, "GENERATED_README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"\n✅ README generated at: {local_path}/GENERATED_README.md\n")
    print("🔍 Preview:")
    print("-" * 60)
    print(readme_content[:1000])  # Show first 1000 characters

# ---- Example Usage ----
if __name__ == "__main__":
    repo_url = input("Enter GitHub repository URL: ")
    generate_readme_from_repo_url(repo_url)

def interactive_chat():
    # Get Azure OpenAI configuration from environment variables
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set.")
    
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://mcaupybugs-ai.openai.azure.com/")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo-instruct")  # Use your actual deployment name
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=azure_endpoint,
        api_key=api_key,
    )

    chat_prompt = [
        {
            "role": "system",
            "content": "You are an AI assistant that helps people find information."
        }
    ]

    # Include speech result if speech is enabled
    messages = chat_prompt

    completion = client.chat.completions.create(
        model=deployment,  # Use the deployment name from environment variables
        messages=messages,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )

    # Process the response
    if completion.choices:
        response = completion.choices[0].message.content
        print("Response:", response)
    else:
        print("No response received from the model.")