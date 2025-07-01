import os
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

class Generators:

    def summarize_code(self, llm, code_text):
        """
        Summarize the code using Azure OpenAI and LangChain's summarize chain.
    
         Args:
            code_text: The text content of the code to summarize
        
        Returns:
            A summary of the code
        """

        # Split the code text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,  # Characters per chunk (approximately 1000 tokens)
            chunk_overlap=200,  # Overlap between chunks
            separators=["\nFile:", "\n\n", "\n", " ", ""]  # Split preferentially at file boundaries
        )

        chunks = text_splitter.split_text(code_text)
        documents = [Document(page_content=chunk) for chunk in chunks]
    #     document = Document(
    #     page_content=chunk,
    #     metadata={
    #         "chunk_id": i,
    #         "chunk_size": len(chunk),
    #         "source_type": "code_repository",
    #         "processing_timestamp": datetime.now().isoformat(),
    #         "file_path": file_info.get("file_path", "unknown"),
    #         "file_extension": file_info.get("extension", "unknown"),
    #         "language": detect_language(file_info.get("extension", "")),
    #         "chunk_total": len(chunks),
    #         "has_functions": "def " in chunk or "function " in chunk,
    #         "has_classes": "class " in chunk,
    #         "line_count": chunk.count('\n'),
    #         "estimated_tokens": len(chunk) // 4,  # Rough estimate
    #     }
    # )

        print(f"Split code into {len(documents)} chunks for processing")
        # Create and run the summarize chain
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        return chain.invoke({"input_documents": documents})
    
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
    {summary_truncated}

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