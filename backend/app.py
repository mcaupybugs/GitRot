from gitrot_brain import GitrotBrain
from helpers import Helper
from generators import Generators
import os

class ReadmeGeneratorApp:
    def __init__(self):
        self.brain = GitrotBrain()
        self.helper = Helper()
        self.generator = Generators()
        self.llm = self.brain.get_gemini_llm()
        self.embeddings = self.brain.getEmbeddingModel()

    def generate_readme_from_repo_url(self, github_url: str, generator_method: str = "Standard README"):
        repo_name = github_url.rstrip('/').split('/')[-1]
        local_path = self.helper.clone_repo(github_url, repo_name)
        code_text = self.helper.extract_code_from_repo(local_path)
        summary = self.generator.summarize_code(self.llm, code_text)
        ## For readme without examples.
        if generator_method == "Standard README":
            readme_content = self.generator.generate_readme(self.llm, summary)
        elif generator_method == "README with Examples":
            readme_content = self.generator.generate_readme_with_examples_vectorstore(self.llm, self.embeddings, summary)   
        # For readme with examples.
        #readme_content = generate_readme_with_examples_vectorstore(summary)

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