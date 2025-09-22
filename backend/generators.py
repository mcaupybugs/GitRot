import os
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils import TokenCalculator
from wrappers.rate_limitter import llm_rate_limiter

#TODO: Add a normalizer to create the right tags etc to the readme.
class Generators:

    def __init__(self, model_name: str):
        self.tokenizer = TokenCalculator(model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200,
            separators=["\nFile:", "\n\n", "\n", " ", ""] 
        )

    def recursive_map_reduce(self, llm, documents: list[Document], map_prompt: str, reduce_prompt: str) -> str:
        """Recursively splitting the text into chunks to process into a summary"""

        print(f"Starting the reducing using recursive method")
        summaries = []
        for document in documents:
            curr_prompt = map_prompt.replace('{text}', str(document))
            summaries.append(llm_rate_limiter.invoke(llm, curr_prompt))
        
        combined_summaries = '\n\n'.join(summaries)

        if not self.tokenizer.is_summary_within_size(combined_summaries):
            print("Size greater than min_input_tokens allowed, splitting again")
            combined_summary_chunks = self.text_splitter.split_text(combined_summaries)
            combined_summary_to_docs = [Document(page_content=chunk) for chunk in combined_summary_chunks]
            reduced_summary = self.recursive_map_reduce(llm, combined_summary_to_docs, map_prompt, reduce_prompt)
            return reduced_summary

        return combined_summaries
            

    def summarize_code(self, llm, code_text) -> str:
        """
        Summarize the code using Azure OpenAI and LangChain's summarize chain.
    
         Args:
            code_text: The text content of the code to summarize
        
        Returns:
            A summary of the code
        """  
        # Split the code text into chunks

        chunks = self.text_splitter.split_text(code_text)
        documents = [Document(page_content=chunk) for chunk in chunks]

        #TODO: Write better prompts, ensuring that the hardcoded words are not used
        map_prompt = "Summarize the code chunk in 200 words: \n\n{text}"
        reduce_prompt = "Combine the summaries into one approximately of 1500 tokens keeping all the main component and essense of the summaries: {text}"
        short_summary = self.recursive_map_reduce(llm, documents, map_prompt=map_prompt, reduce_prompt=reduce_prompt)
        return short_summary
    
    def generate_readme(self, llm, summary: str) -> str:

        # Ensure summary is a string
        if not isinstance(summary, str):
            print(f"Warning: summary is not a string, but {type(summary)}. Converting to string.")
            summary = str(summary)

        # This check is not required as we are ensuring this condition in summarize method,
        # but still keeping it here just in case
        if not self.tokenizer.is_summary_within_size(summary):
            print(f"Summary is large ({len(summary)} chars). Condensing first...")
            docs = [Document(page_content=summary)]

            split_docs = self.text_splitter.split_documents(docs)
            print(f"Split summary into {len(split_docs)} chunks")

            map_prompt = "This part of summary is more than expected size, condense it even further while keeping the essense and important concepts intact: {text}"

            reduce_prompt = "Take these part of condensed summaries, and make them better while maintaining the overall summary size {text}"

            # Get condensed summary
            condensed_result = self.recursive_map_reduce(llm, docs, map_prompt, reduce_prompt)
            condensed_summary = condensed_result if isinstance(condensed_result, str) else condensed_result.get('output_text', '')
            summary = condensed_summary
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

        return llm_rate_limiter.invoke(llm, prompt)

    # TODO: This method needs to be fixed after the basic one is robust. 
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