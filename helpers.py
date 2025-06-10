import os
import shutil
from git import Repo

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
        if os.path.exists(folder_name):
            print(f"Folder '{folder_name}' already exists. Skipping clone.")
        else:
            Repo.clone_from(github_url, folder_name)
            print(f"Repository cloned into '{folder_name}'")
        return folder_name
    
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