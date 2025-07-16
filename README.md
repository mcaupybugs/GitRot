# GitRot - AI-Powered README Generator

GitRot is an intelligent, full-stack application designed to transform your GitHub repositories into professional, comprehensive documentation automatically. By leveraging Azure OpenAI's advanced AI capabilities, GitRot analyzes your codebase and generates high-quality README files, significantly streamlining the documentation process for developers.

## ✨ Features

*   **AI-Powered README Generation**: Automatically creates detailed READMEs from GitHub repository URLs.
*   **Code Analysis & Summarization**: Intelligently processes and summarizes repository code to inform README content.
*   **Standard & Example-Rich READMEs**: Option to generate a standard README or one that includes code examples.
*   **User-Friendly Web Interface**: A modern and intuitive frontend built with Next.js allows for easy input and result management.
*   **FastAPI Backend**: Robust and scalable API to handle repository cloning, code processing, and AI interactions.
*   **Azure Optimized**: Designed for seamless deployment and operation on Azure App Services, utilizing Azure OpenAI.
*   **Copy & Download**: Easily copy the generated README content or download it as a Markdown file.

## 🛠️ Tech Stack

### Backend

*   **Python**: Primary language for backend logic.
*   **FastAPI**: A modern, fast (high-performance) web framework for building APIs.
*   **Langchain**: Used for integrating with large language models and managing AI workflows.
*   **GitPython**: For programmatically interacting with Git repositories (cloning, etc.).

### Frontend

*   **Next.js**: React framework for building the user interface.
*   **React**: JavaScript library for building interactive UIs.
*   **Tailwind CSS**: A utility-first CSS framework for rapid UI development.
*   **Shadcn/ui**: Components for building beautiful user interfaces.

### AI / Machine Learning

*   **Azure OpenAI**: Utilizes Azure-hosted OpenAI models (e.g., GPT-3.5 Turbo Instruct, text-embedding-ada-002) for code summarization and README generation.

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed:

*   Python 3.9+ (`python --version`)
*   Node.js 18.18+ (`node --version`)
*   npm (`npm --version`)
*   Git (`git --version`)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/mcaupybugs/GitRot.git # Replace with actual repo URL
    cd GitRot
    ```

2.  **Set up Python Backend:**

    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows, use `.\venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set up Node.js Frontend:**

    ```bash
    cd gitrot-frontend
    npm install
    cd ..
    ```

### Running Locally

To start both the backend and frontend in development mode, run the `start-dev.sh` script from the project root:

```bash
./start-dev.sh
```

This will start:
*   FastAPI backend on `http://localhost:8000`
*   Next.js frontend on `http://localhost:3000`

You can access the API documentation at `http://localhost:8000/api/docs`.

### Environment Variables

Create a `.env` file in the project root with your Azure OpenAI credentials:

```dotenv
AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
AZURE_OPENAI_ENDPOINT="your_azure_openai_endpoint" # e.g., https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT="gpt-35-turbo-instruct" # Or your specific deployment name
AZURE_OPENAI_API_VERSION="2024-12-01-preview"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002" # Or your specific embedding deployment name
```

## ☁️ Deployment

The project includes scripts for deployment to Azure App Services:

*   `startup_fastapi.sh`: For deploying only the FastAPI backend.
*   `startup-azure.sh`: For deploying the FastAPI backend and building the Next.js frontend during deployment.
*   `startup-azure-fullstack.sh`: Comprehensive script for full-stack deployment on Azure, handling both backend and frontend setup.

## 🤝 Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` for details on how to contribute to this project.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details. 