import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the project root and backend directories to the Python path
import sys
project_root = os.path.dirname(os.path.dirname(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, project_root)
sys.path.insert(0, backend_path)

# Now try importing the required modules
try:
    from backend.app import ReadmeGeneratorApp
    from backend.models import ReadmeRequest
except ImportError:
    # Fallback to direct imports if the above fails
    import app as app_module
    import models as models_module
    ReadmeGeneratorApp = app_module.ReadmeGeneratorApp
    ReadmeRequest = models_module.ReadmeRequest


class TestReadmeGeneratorE2E:
    
    @patch('backend.app.GitrotBrain')
    @patch('backend.app.Helper')
    @patch('backend.app.Generators')
    def test_end_to_end_readme_generation(self, mock_generators, mock_helper, mock_gitrot_brain):
        """
        Complete end-to-end test that mocks all external dependencies and tests
        the full flow from ReadmeGeneratorApp creation to README generation.
        """
        # Mock GitHub repository data
        mock_github_url = "https://github.com/test-user/test-repo.git"
        mock_repo_name = "test-repo.git"  # This is what app.py actually extracts
        mock_local_path = "/tmp/test-repo"
        mock_code_content = """
        # Python Flask Application
        from flask import Flask
        
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return "Hello World"
            
        if __name__ == '__main__':
            app.run(debug=True)
        """
        
        mock_code_summary = """
        This is a simple Flask web application that serves a "Hello World" message.
        The application uses Python Flask framework and includes a single route
        that responds to HTTP GET requests at the root path.
        """
        
        mock_readme_content = """
        # Test Repo
        
        ## Description
        This is a simple Flask web application that serves a "Hello World" message.
        
        ## Prerequisites
        - Python 3.8+
        - Flask
        
        ## Installation
        1. Clone the repository
        2. Install dependencies: `pip install flask`
        3. Run the application: `python app.py`
        
        ## Usage
        Navigate to http://localhost:5000 to see the "Hello World" message.
        
        ## License
        MIT License
        """
        
        # Set up mocks for GitrotBrain
        mock_brain_instance = Mock()
        mock_llm = Mock()
        mock_embeddings = Mock()
        mock_brain_instance.get_llm.return_value = mock_llm
        mock_brain_instance.getEmbeddingModel.return_value = mock_embeddings
        mock_gitrot_brain.return_value = mock_brain_instance
        
        # Set up mocks for Helper
        mock_helper_instance = Mock()
        mock_helper_instance.clone_repo.return_value = mock_local_path
        mock_helper_instance.extract_code_from_repo.return_value = mock_code_content
        mock_helper_instance.delete_cloned_repo.return_value = True
        mock_helper.return_value = mock_helper_instance
        
        # Set up mocks for Generators
        mock_generator_instance = Mock()
        mock_generator_instance.summarize_code.return_value = mock_code_summary
        mock_generator_instance.generate_readme.return_value = mock_readme_content
        mock_generators.return_value = mock_generator_instance
        
        # Create the request object
        request = ReadmeRequest(
            repo_url=mock_github_url,
            generation_method="Standard README",
            model_name="gpt-35-turbo-instruct",
            provider="azure_openai",
            max_tokens=1000,
            temperature=0.3
        )
        
        # Mock file writing
        mock_open = MagicMock()
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        with patch('builtins.open', mock_open), \
             patch('os.path.join', return_value=f"{mock_local_path}/GENERATED_README.md"):
            
            # Create the ReadmeGeneratorApp instance
            app = ReadmeGeneratorApp(request)
            
            # Execute the end-to-end flow
            result = app.generate_readme_from_repo_url(request)
        
        # Verify all the steps were executed in the correct order
        
        # 1. Brain initialization with correct model
        mock_gitrot_brain.assert_called_once_with("gpt-35-turbo-instruct")
        mock_brain_instance.get_llm.assert_called_once()
        mock_brain_instance.getEmbeddingModel.assert_called_once()
        
        # 2. Helper operations
        mock_helper_instance.clone_repo.assert_called_once_with(mock_github_url, mock_repo_name)
        mock_helper_instance.extract_code_from_repo.assert_called_once_with(mock_local_path)
        
        # 3. Generator operations
        mock_generator_instance.summarize_code.assert_called_once_with(mock_llm, mock_code_content)
        mock_generator_instance.generate_readme.assert_called_once_with(mock_llm, mock_code_summary)
        
        # 4. File operations
        mock_open.assert_called_once_with(f"{mock_local_path}/GENERATED_README.md", "w", encoding="utf-8")
        mock_file.write.assert_called_once_with(mock_readme_content)
        
        # 5. Cleanup
        mock_helper_instance.delete_cloned_repo.assert_called_once_with(mock_local_path)
        
        # 6. Verify the final result
        assert result == mock_readme_content
        assert isinstance(result, str)
        assert "# Test Repo" in result
        assert "Description" in result
        assert "Prerequisites" in result
        
        print("✅ End-to-end test passed successfully!")


if __name__ == "__main__":
    test_instance = TestReadmeGeneratorE2E()
    test_instance.test_end_to_end_readme_generation()