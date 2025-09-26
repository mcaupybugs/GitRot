from gitrot_brain import GitrotBrain
from helpers import Helper
from models import ReadmeRequest
from generators import Generators
from config.model_credential_factory import model_credential_factory
import os

class ReadmeGeneratorApp:
    def __init__(self, request: ReadmeRequest):
        self.brain = GitrotBrain(request.model_name)
        self.helper = Helper()
        self.generator = Generators(request.model_name)
        self.llm = self.brain.get_llm()

    def generate_readme_from_repo_url(self, request: ReadmeRequest):
        github_url = request.repo_url
        generator_method = request.generation_method
        repo_name = request.repo_url.rstrip('/').split('/')[-1]
        local_path = self.helper.clone_repo(github_url, repo_name)
        code_text = self.helper.extract_code_from_repo(local_path)
        summary = self.generator.summarize_code(self.llm, code_text)
        ## For readme without examples.
        if generator_method == "Standard README":
            readme_content = self.generator.generate_readme(self.llm, summary)
        elif generator_method == "README with Examples":
            readme_content = self.generator.generate_readme_with_examples_vectorstore(self.llm, self.embeddings, summary)

        with open(os.path.join(local_path, "GENERATED_README.md"), "w", encoding="utf-8") as f:
            f.write(readme_content)

        print(f"\n✅ README generated at: {local_path}/GENERATED_README.md\n")
        print("🔍 Preview:")
        print("-" * 60)
        print(readme_content[:1000])  # Show first 1000 characters
        
        # Cleanup: Delete the cloned repository folder
        cleanup_success = self.helper.delete_cloned_repo(local_path)
        if cleanup_success:
            print("🧹 Cleanup completed successfully")
        else:
            print("⚠️ Warning: Could not clean up temporary files")
        
        return readme_content