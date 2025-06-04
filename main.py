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
from langchain.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
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

def generate_readme_with_examples(summary: str) -> str:
    
    example_text = ""
    # First collect all examples
    for root, dirs, files in os.walk("examples"):
        for file in files:
            if file.endswith(('.md')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        example_text += f"### Example from {file_path}\n\n{content}\n\n"
                except Exception as e:
                    print(f"Error reading example file {file}: {e}")
    
    # Get Azure OpenAI configuration
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://mcaupybugs-ai.openai.azure.com/")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo-instruct")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    
    # Create LangChain Azure OpenAI instance
    llm = LangchainAzureOpenAI(
        azure_deployment=deployment_name,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        temperature=0.3,
        max_tokens=1000  # Control the response length
    )

    
def generate_readme_with_examples_vectorstore(summary: str) -> str:
    """Generate README using vectorstore for examples rather than raw text inclusion."""
    # Ensure summary is a string
    if not isinstance(summary, str):
        print(f"Warning: summary is not a string, but {type(summary)}. Converting to string.")
        summary = str(summary)
    
    # Get Azure OpenAI configuration
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://mcaupybugs-ai.openai.azure.com/")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo-instruct")
    embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    
    # Initialize Azure OpenAI embeddings
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=embedding_deployment,
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version=api_version,
    )
    
    # Collect example files
    example_docs = []
    for root, dirs, files in os.walk("examples"):
        for file in files:
            if file.endswith(('.md')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        example_docs.append(Document(
                            page_content=content,
                            metadata={"source": file_path, "type": "example"}
                        ))
                except Exception as e:
                    print(f"Error reading example file {file}: {e}")
    
    if not example_docs:
        print("No example files found. Using standard README generation.")
        return generate_readme(summary)
    
    # Create vector store from examples
    vectorstore = FAISS.from_documents(example_docs, embeddings)
    
    # Truncate summary to reasonable size
    summary_truncated = summary[:800] if len(summary) > 800 else summary
    
    # Retrieve most relevant examples for this summary
    relevant_examples = vectorstore.similarity_search(summary_truncated, k=2)
    relevant_content = "\n\n".join([f"### Example from {doc.metadata['source']}\n\n{doc.page_content}" 
                                  for doc in relevant_examples])
    
    # Truncate if still too large
    if len(relevant_content) > 2000:
        relevant_content = relevant_content[:2000] + "...(truncated)"
    
    # Create LangChain Azure OpenAI instance
    llm = LangchainAzureOpenAI(
        azure_deployment=deployment_name,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        temperature=0.3,
        max_tokens=1000
    )
    print(relevant_content)
     
    prompt = f"""
You are a professional technical writer creating documentation for a software project.

Based on the following codebase summary, generate a comprehensive README.md file that follows best practices for Azure projects.

INSTRUCTIONS:
1. Use the example README formats below as style guides
2. Focus ONLY on relevant content from the summary - ignore CSS, HTML styling, and other non-documentation elements
3. Follow Azure documentation standards and conventions

The README MUST include these sections:
- Project Title: Clear and descriptive
- Description: Overview of what the project does and its purpose
- Architecture: How the components work together (if applicable)
- Prerequisites: Required software, accounts, and configurations
- Installation: Step-by-step setup instructions
- Configuration: Environment variables, settings, and Azure-specific configurations
- Usage: How to use the software with examples
- API Reference: If the project exposes APIs (if applicable)
- Development: Instructions for contributors (if applicable)
- Deployment: How to deploy to Azure (if applicable)
- Security: Security considerations and best practices
- Troubleshooting: Common issues and solutions
- License: Project license information

REFERENCE EXAMPLES:
{relevant_content}

CODEBASE SUMMARY:
{summary_truncated}

Generate a complete, well-structured README.md following the sections above. If any section is not applicable based on the summary, you may omit it. Focus on technical accuracy and clarity.
"""
    return llm.invoke(prompt)

def generate_readme(summary: str) -> str:

    # Ensure summary is a string
    if not isinstance(summary, str):
        print(f"Warning: summary is not a string, but {type(summary)}. Converting to string.")
        summary = str(summary)
    llm = LangchainAzureOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo-instruct"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://mcaupybugs-ai.openai.azure.com/"),
        api_key=api_key,
        temperature=0.3,
        max_tokens=1000
    )

    docs = [Document(page_content=summary)]
    map_template = """
    Analyze this portion of a codebase summary and extract the most important information:
    
    {text}
    
    KEY POINTS:
    """
    map_prompt = PromptTemplate(template=map_template, input_variables=["text"])

    combine_template = """
    Based on these key points from a codebase analysis, create a concise summary that captures the essence of the project:
    
    {text}
    
    CONCISE SUMMARY:
    """
    combine_prompt = PromptTemplate(template=combine_template, input_variables=["text"])
    if len(summary) > 2000:
        print(f"Summary is large ({len(summary)} chars). Condensing first...")
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(docs)
        print(f"Split summary into {len(split_docs)} chunks")
        
        # Use map_reduce to condense the summary
        chain = load_summarize_chain(
            llm, 
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            verbose=True
        )
        
        # Get condensed summary
        condensed_result = chain.invoke({"input_documents": split_docs})
        condensed_summary = condensed_result if isinstance(condensed_result, str) else condensed_result.get('output_text', '')
        print(f"Condensed summary from {len(summary)} to {len(condensed_summary)} chars")
    else:
        condensed_summary = summary

    prompt = f"""
    You are a professional technical writer. Based on the following codebase summary, generate a complete README.md file. 
    Include: 
    - Project Title: Clear and descriptive
    - Description: Overview of what the project does and its purpose
    - Architecture: How the components work together (if applicable)
    - Prerequisites: Required software, accounts, and configurations
    - Installation: Step-by-step setup instructions
    - Configuration: Environment variables, settings, and Azure-specific configurations
    - Usage: How to use the software with examples
    - API Reference: If the project exposes APIs (if applicable)
    - Development: Instructions for contributors (if applicable)
    - Deployment: How to deploy to Azure (if applicable)
    - Security: Security considerations and best practices
    - Troubleshooting: Common issues and solutions
    - License: Project license information

    Summary:
    {condensed_summary}
    """

    try:
        return llm.invoke(prompt)
    except Exception as e:
        if "maximum context length" in str(e):
            # If still hitting token limits, use an even more aggressive approach
            print("Still hitting token limits. Using more aggressive summarization.")
            
            # Use more aggressive summarization
            from langchain.chains import LLMChain
            
            final_prompt = PromptTemplate(template="""
            Create an extremely concise summary (maximum 500 words) of this codebase:
            
            {text}
            
            FOCUS ONLY on core functionality, main components, and technologies used.
            """, input_variables=["text"])
            
            chain = LLMChain(llm=llm, prompt=final_prompt)
            ultra_condensed = chain.invoke({"text": condensed_summary[:3000]})
            
            if isinstance(ultra_condensed, dict):
                ultra_condensed = ultra_condensed.get('text', '')
            
            # Final attempt with ultra-condensed summary
            minimal_prompt = f"""
            Create a README.md for this project. Include only essential sections:
            
            Summary: {ultra_condensed}
            """
            return llm.invoke(minimal_prompt)
        else:
            raise

def generate_readme_from_repo_url(github_url: str):
    repo_name = github_url.rstrip('/').split('/')[-1]
    local_path = clone_repo(github_url, repo_name)
    code_text = extract_code_from_repo(local_path)
    summary = summarize_code(code_text)

    ## For readme without examples.
    readme_content = generate_readme(summary)

    # For readme with examples.
    #readme_content = generate_readme_with_examples_vectorstore(summary)

    with open(os.path.join(local_path, "GENERATED_README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"\n✅ README generated at: {local_path}/GENERATED_README.md\n")
    print("🔍 Preview:")
    print("-" * 60)
    print(readme_content[:1000])  # Show first 1000 characters
    return readme_content

# ---- Example Usage ----
if __name__ == "__main__":
    repo_url = input("Enter GitHub repository URL: ")
    generate_readme_from_repo_url(repo_url)    # Get Azure OpenAI configuration from environment variables