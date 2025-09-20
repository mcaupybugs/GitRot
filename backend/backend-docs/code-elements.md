[// Backend Code Elements]

## app.py

**ReadmeGeneratorApp**: Main application class that coordinates README generation.

- Uses `GitrotBrain` for AI models (LLM and embeddings).
- Uses `Helper` for repo cloning and code extraction.
- Uses `Generators` for code summarization and README creation.
- Method `generate_readme_from_repo_url` takes a GitHub URL, clones the repo, extracts code, summarizes it, and generates a README (with or without examples).

## api_helper.py

**APIMetrics**: Tracks API usage metrics for monitoring and logging (Azure best practices).

- Counts requests, errors, generations, and response times.
- Provides metrics for uptime, total requests, error rate, etc.

### Components Used:

- **Python Standard Library**: `logging`, `time`, `functools`, `json`
- **FastAPI**: `Request`, `HTTPException`

### Classes & Functions:

- **APIMetrics**: Metrics collection class
  - Tracks request count, error count, generation count, response times
  - Calculates uptime, average response time, error rate
- **RateLimiter**: In-memory rate limiting
  - Configurable request limits per time window
  - Automatic cleanup of old entries
  - Client-based tracking using IP addresses
- **Utility Functions**:
  - `log_request_metrics`: Decorator for automatic request logging and timing
  - `validate_github_url`: GitHub URL format validation
  - `sanitize_repo_name`: Extract and clean repository names
  - `format_error_response`: Structured error response formatting
  - `log_generation_attempt`: Log README generation attempts
  - `get_client_info`: Extract client metadata from requests
  - `check_rate_limit`: Rate limiting enforcement
  - `create_download_filename`: Safe filename generation for downloads

## fastapi_app.py

**FastAPI Application**: Defines the FastAPI web server for the GitRot backend.

- Configures CORS for frontend integration.
- Sets up API endpoints for README generation.
- Integrates with Azure OpenAI and AdSense.
- Uses helpers from `api_helper.py` for request validation, logging, and metrics.

## generators.py

**Generators**: Handles code summarization and README generation using AI models.

### Components Used:

- **LangChain Components**:
  - `RecursiveCharacterTextSplitter`: Splits large text into manageable chunks with overlap
  - `load_summarize_chain`: Creates summarization chains with map-reduce strategy
  - `Document`: Wrapper for text content with metadata
  - `PromptTemplate`: Templates for structured LLM prompts
  - `LLMChain`: Basic chain for single LLM calls
- **Vector Store**:
  - `FAISS`: Facebook AI Similarity Search for example retrieval
- **Azure OpenAI**:
  - `AzureOpenAIEmbeddings`: Text embedding model for semantic search

### Methods:

- `summarize_code`:
  - Splits code into 3000-character chunks with 200-character overlap
  - Uses map-reduce summarization chain to handle large codebases
  - Preferentially splits at file boundaries for better context
- `generate_readme_with_examples_vectorstore`:
  - Creates vector store from example README files in `/examples` directory
  - Performs similarity search to find relevant examples
  - Condenses large summaries using recursive text splitting
  - Generates README using retrieved examples as style guides
- `generate_readme`:
  - Standard README generation without examples
  - Handles large summaries with progressive condensation
  - Uses map-reduce chain for content over 2000 characters
  - Includes comprehensive sections (title, description, architecture, deployment, etc.)

## gitrot_brain.py

**GitrotBrain**: Manages AI model configuration and instantiation.

- Loads API keys and endpoints from environment variables.
- Provides methods to get Azure OpenAI LLM and embeddings.
- Supports Google Gemini LLM integration.
- Handles rate limiting for Gemini API.

## helpers.py

**Helper Functions**: Provides utilities for repo management and deployment.

- Clones GitHub repositories.
- Extracts code from repos.
- Configures Git for Azure deployments.
- Sets up logging for monitoring.

## wrappers/rate_limitter.py

**RateLimitter**: Class stub for rate limiting functionality (implementation not shown).

## Generators
