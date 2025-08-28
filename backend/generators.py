import os
import time
import json
from typing import Dict, List, Optional
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

class Generators:
    def __init__(self):
        self.retry_state_file = "retry_state.json"
        self.current_retry_delay = self._load_retry_state()
    
    def _load_retry_state(self) -> float:
        """Load the current retry delay from persistent storage."""
        try:
            if os.path.exists(self.retry_state_file):
                with open(self.retry_state_file, 'r') as f:
                    data = json.load(f)
                    return data.get('current_retry_delay', 2.0)
        except Exception as e:
            print(f"Error loading retry state: {e}")
        return 2.0  # Default starting delay
    
    def _save_retry_state(self, delay: float):
        """Save the current retry delay to persistent storage."""
        try:
            with open(self.retry_state_file, 'w') as f:
                json.dump({'current_retry_delay': delay}, f)
        except Exception as e:
            print(f"Error saving retry state: {e}")
    
    def _reset_retry_state(self):
        """Reset retry delay to initial value after successful operation."""
        self.current_retry_delay = 2.0
        self._save_retry_state(self.current_retry_delay)
    
    def _invoke_with_retry(self, llm, prompt: str, max_delay: float = 120.0) -> str:
        """
        Invoke LLM with exponential backoff retry logic.
        
        Args:
            llm: The language model instance
            prompt: The prompt to send
            max_delay: Maximum retry delay in seconds (default 2 minutes)
        
        Returns:
            Response from LLM
        """
        delay = self.current_retry_delay
        
        while delay <= max_delay:
            try:
                response = llm.invoke(prompt)
                # Success - reset retry state
                self._reset_retry_state()
                return response
                
            except Exception as e:
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ['rate limit', 'quota', 'too many requests', 'limit exceeded']):
                    print(f"Rate limit hit. Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    
                    # Update and save current retry delay
                    self.current_retry_delay = min(delay * 2, max_delay)
                    self._save_retry_state(self.current_retry_delay)
                    delay = self.current_retry_delay
                    
                    print(f"Next retry delay will be: {self.current_retry_delay} seconds")
                else:
                    # Non-rate-limit error, re-raise
                    raise e
        
        raise Exception(f"Maximum retry delay of {max_delay} seconds reached. Giving up.")
    
    def _summarize_documents_custom(self, llm, documents: List[Document]) -> str:
        """
        Custom implementation to replace load_summarize_chain with retry logic.
        Implements map-reduce pattern manually.
        """
        # Step 1: Map phase - summarize each document individually
        map_prompt_template = """
        Summarize the following code segment, focusing on key functionality, components, and technologies:

        {text}

        Summary:
        """
        
        individual_summaries = []
        total_docs = len(documents)
        
        for i, doc in enumerate(documents):
            print(f"Processing document {i+1}/{total_docs}")
            
            prompt = map_prompt_template.format(text=doc.page_content)
            try:
                summary = self._invoke_with_retry(llm, prompt)
                individual_summaries.append(summary)
                print(f"✓ Document {i+1} summarized successfully")
            except Exception as e:
                print(f"✗ Failed to process document {i+1}: {e}")
                # Continue with other documents rather than failing entirely
                continue
        
        if not individual_summaries:
            raise Exception("Failed to summarize any documents")
        
        # Step 2: Reduce phase - combine all summaries
        print(f"Combining {len(individual_summaries)} individual summaries...")
        
        reduce_prompt_template = """
        Combine the following code summaries into a comprehensive overview of the entire codebase:

        {summaries}

        Create a unified summary that captures:
        - Overall project purpose and functionality
        - Key technologies and frameworks used
        - Main components and their relationships
        - Important features and capabilities

        Comprehensive Summary:
        """
        
        combined_summaries = "\n\n---\n\n".join(individual_summaries)
        final_prompt = reduce_prompt_template.format(summaries=combined_summaries)
        
        return self._invoke_with_retry(llm, final_prompt)

    def summarize_code(self, llm, code_text):
        """
        Summarize the code using custom retry logic instead of load_summarize_chain.
    
         Args:
            code_text: The text content of the code to summarize
        
        Returns:
            A summary of the code
        """
        MAX_CHUNKS = 10  # Limit to prevent overwhelming the API
        
        # Split the code text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,  # Characters per chunk (approximately 1000 tokens)
            chunk_overlap=200,  # Overlap between chunks
            separators=["\nFile:", "\n\n", "\n", " ", ""]  # Split preferentially at file boundaries
        )

        chunks = text_splitter.split_text(code_text)
        
        documents = [Document(page_content=chunk) for chunk in chunks]
        print(f"Split code into {len(documents)} chunks for processing")
        
        # Use custom summarization with retry logic
        try:
            result = self._summarize_documents_custom(llm, documents)
            return {"output_text": result}  # Return in same format as original
        except Exception as e:
            print(f"Summarization failed: {e}")
            raise

    def generate_readme_with_examples_vectorstore(self, llm, embeddings, summary: str) -> str:
        """Generate README using vectorstore for examples rather than raw text inclusion."""
        # Ensure summary is a string
        if not isinstance(summary, str):
            print(f"Warning: summary is not a string, but {type(summary)}. Converting to string.")
            summary = str(summary)

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
            return self.generate_readme(llm, summary)

        # Create vector store from examples
        vectorstore = FAISS.from_documents(example_docs, embeddings)
        # Systematically condense summary if too large
        if len(summary) > 800:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=600,
                chunk_overlap=100,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            summary_docs = [Document(page_content=summary)]
            split_docs = text_splitter.split_documents(summary_docs)
            
            condense_prompt = PromptTemplate(
                template="""Condense this portion of a codebase summary while preserving key technical details:
                
                {text}
                
                Keep all important: functionality, technologies, architecture, and key components.
                Condensed summary:""",
                input_variables=["text"]
            )
            
            chain = load_summarize_chain(
                llm,
                chain_type="map_reduce",
                map_prompt=condense_prompt,
                combine_prompt=PromptTemplate(
                    template="Combine these condensed summaries into a comprehensive overview:\n\n{text}\n\nFinal summary:",
                    input_variables=["text"]
                )
            )
            
            condensed_result = chain.invoke({"input_documents": split_docs})
            summary_for_search = condensed_result['output_text'] if isinstance(condensed_result, dict) else str(condensed_result)
        else:
            summary_for_search = summary

        print("summary for searchy", summary_for_search)
        # Retrieve most relevant examples for this summary
        relevant_examples = vectorstore.similarity_search(summary_for_search, k=2)
        # Systematically process example content
        processed_examples = []
        for doc in relevant_examples:
            example_content = doc.page_content
            if len(example_content) > 1000:
                # Use text splitter to get most relevant sections
                example_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=800,
                    chunk_overlap=100,
                    separators=["\n## ", "\n### ", "\n\n", "\n", ""]
                )
                example_chunks = example_splitter.split_text(example_content)
                # Take first chunk (usually contains title and description)
                example_content = example_chunks[0]
            
            processed_examples.append(f"### Example from {doc.metadata['source']}\n\n{example_content}")
        
        relevant_content = "\n\n".join(processed_examples)

        # Create LangChain Azure OpenAI instance

        print(relevant_content)

        prompt = f"""
    You are a professional technical writer creating documentation for a software project.

    Based on the following codebase summary, generate a comprehensive README.md file that follows best practices for Azure projects.

    INSTRUCTIONS:
    1. Use the example README formats below as style guides
    2. Focus ONLY on relevant content from the summary - ignore CSS, HTML styling, and other non-documentation elements
    3. Follow Azure documentation standards and conventions

    REFERENCE EXAMPLES:
    {relevant_content}

    CODEBASE SUMMARY:
    {summary_for_search}

    Generate a complete, well-structured README.md following the sections above. If any section is not applicable based on the summary, you may omit it. Focus on technical accuracy and clarity.
    """
        return llm.invoke(prompt)

    def generate_readme(self, llm, summary: str) -> str:

        # Ensure summary is a string
        if not isinstance(summary, str):
            print(f"Warning: summary is not a string, but {type(summary)}. Converting to string.")
            summary = str(summary)

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