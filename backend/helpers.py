import os
import shutil
from git import Repo
import subprocess
import logging
import uuid
import time

# Azure best practice: Configure logging for deployment monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
def configure_git_for_azure():
    """Configure Git for Azure App Service deployment."""
    try:
        # Azure best practice: Set Git environment variables
        os.environ['GIT_PYTHON_REFRESH'] = 'quiet'
        
        # Check if git is available
        try:
            git_path = subprocess.check_output(['which', 'git'], text=True).strip()
            os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = git_path
            logger.info(f"✅ Azure: Git found at {git_path}")
            
            # Verify git version
            git_version = subprocess.check_output(['git', '--version'], text=True).strip()
            logger.info(f"✅ Azure: {git_version}")
            
        except subprocess.CalledProcessError:
            logger.warning("⚠️ Azure: Git not found in PATH")
            
            # Azure fallback: Try common Git paths
            common_git_paths = [
                '/usr/bin/git',
                '/usr/local/bin/git',
                '/opt/git/bin/git',
                '/home/site/wwwroot/.venv/bin/git'
            ]
            for git_path in common_git_paths:
                if os.path.exists(git_path):
                    os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = git_path
                    logger.info(f"✅ Azure: Git configured at {git_path}")
                    break
            else:
                logger.error("❌ Azure: Git executable not found")
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"❌ Azure Git configuration error: {str(e)}")
        return False

# Azure deployment: Configure Git before imports
git_configured = configure_git_for_azure()


class Helper:
    def extract_code_from_repo(self, folder_name: str)-> str:
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
    
    def clone_repo(self, github_url: str, folder_name: str="cloned_repo")-> str:
        # Create projects directory if it doesn't exist
        projects_dir = "projects"
        if not os.path.exists(projects_dir):
            os.makedirs(projects_dir)
            print(f"Created '{projects_dir}' directory")
        
        # Create full path inside projects folder
        unique_suffix = str(uuid.uuid4())[:8]
        timestamp = str(int(time.time()))
        unique_folder_name = f"{folder_name}_{timestamp}_{unique_suffix}"

        full_path = os.path.join(projects_dir, unique_folder_name)

        retry_count = 0
        while os.path.exists(full_path) and retry_count < 5:
            print(f"⚠️ Folder '{full_path}' exists, trying another name...")
            retry_count += 1
            unique_suffix = str(uuid.uuid4())[:8]
            unique_folder_name = f"{folder_name}_{timestamp}_{retry_count}_{unique_suffix}"
            full_path = os.path.join(projects_dir, unique_folder_name)
        
        try:
            print(f"🔄 Cloning {github_url} into '{full_path}'...")
            Repo.clone_from(github_url, full_path)
            print(f"✅ Repository cloned successfully into '{full_path}'")
            return full_path
            
        except Exception as e:
            print(f"❌ Error cloning repository: {e}")
            
            # Cleanup partial clone if it exists
            if os.path.exists(full_path):
                try:
                    shutil.rmtree(full_path, ignore_errors=True)
                    print(f"🧹 Cleaned up partial clone: {full_path}")
                except:
                    pass
            
            raise
    
    def delete_cloned_repo(self, folder_path: str) -> bool:
        """
        Delete the cloned repository folder for cleanup after processing.
        
        Args:
            folder_path (str): Path to the folder to be deleted
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            if os.path.exists(folder_path):
                # Use shutil.rmtree to remove the entire directory tree
                shutil.rmtree(folder_path)
                print(f"✅ Successfully deleted folder: {folder_path}")
                return True
            else:
                print(f"⚠️ Folder not found: {folder_path}")
                return False
        except PermissionError as e:
            print(f"❌ Permission denied when deleting {folder_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error deleting folder {folder_path}: {e}")
            return False