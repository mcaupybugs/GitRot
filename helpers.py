import os
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