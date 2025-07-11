"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Github,
  Sparkles,
  ArrowRight,
  Copy,
  Download,
  CheckCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { LoadingSpinner } from "@/components/loading-spinner";

export default function HomePage() {
  const [githubUrl, setGithubUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!githubUrl) return;

    setIsLoading(true);

    try {
      // Get API URL from environment variable
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      // Call your FastAPI backend
      const response = await fetch(`${apiUrl}/api/generate-readme`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: githubUrl,
          generation_method: "Standard README",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setResult(data.readme_content);
      } else {
        setResult(
          `# Error\n\nFailed to generate README: ${data.error_message}`
        );
      }
    } catch (error) {
      console.error("Error generating README:", error);
      setResult(
        `# Error\n\nFailed to generate README. Please check if the repository URL is correct and the backend server is running.\n\n**Error details:** ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async () => {
    if (result) {
      try {
        await navigator.clipboard.writeText(result);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      } catch (err) {
        console.error("Failed to copy to clipboard:", err);
      }
    }
  };

  const downloadReadme = () => {
    if (result) {
      const blob = new Blob([result], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "README.md";
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 to-stone-100">
      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-2 mb-6">
            <div className="h-8 w-8 bg-stone-900 rounded-lg flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-stone-900">GitRot</h1>
            <Badge variant="secondary" className="bg-stone-200 text-stone-700">
              AI-Powered
            </Badge>
          </div>

          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-stone-900 mb-6 leading-tight">
            Turn chaos into <span className="text-stone-600">clarity.</span>
          </h2>

          <p className="text-lg text-stone-600 mb-12 max-w-2xl mx-auto">
            GitRot is the intelligent companion that helps you transform your
            GitHub repositories into professional, comprehensive documentation.
          </p>
        </div>

        {/* Main Interface */}
        <div className="max-w-4xl mx-auto">
          {!result ? (
            <Card className="border-stone-200 shadow-sm">
              <CardContent className="p-8">
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="space-y-2">
                    <label
                      htmlFor="github-url"
                      className="text-sm font-medium text-stone-700"
                    >
                      GitHub Repository URL
                    </label>
                    <div className="relative">
                      <Github className="absolute left-3 top-1/2 transform -translate-y-1/2 text-stone-400 h-4 w-4" />
                      <Input
                        id="github-url"
                        type="url"
                        value={githubUrl}
                        onChange={(e) => setGithubUrl(e.target.value)}
                        placeholder="https://github.com/username/repository"
                        className="pl-10 h-12 border-stone-200 focus:border-stone-400 focus:ring-stone-400"
                        required
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  <Button
                    type="submit"
                    disabled={isLoading || !githubUrl}
                    className={cn(
                      "w-full h-12 bg-stone-900 hover:bg-stone-800 text-white",
                      "disabled:opacity-50 disabled:cursor-not-allowed"
                    )}
                  >
                    {isLoading ? (
                      <>
                        <LoadingSpinner />
                        <span className="ml-2">Generating README...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Generate README
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </>
                    )}
                  </Button>
                </form>

                {/* Try it out section */}
                <div className="mt-8 pt-6 border-t border-stone-200">
                  <p className="text-sm text-stone-500 text-center mb-4">
                    New to GitRot? Try these popular repositories:
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {[
                      "facebook/react",
                      "microsoft/vscode",
                      "vercel/next.js",
                    ].map((repo) => (
                      <Button
                        key={repo}
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          setGithubUrl(`https://github.com/${repo}`)
                        }
                        className="text-stone-600 border-stone-200 hover:bg-stone-50"
                        disabled={isLoading}
                      >
                        {repo}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="border-stone-200 shadow-sm">
              <CardContent className="p-8">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-semibold text-stone-900">
                      Generated README
                    </h3>
                    <p className="text-sm text-stone-600">
                      Your AI-generated documentation is ready
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={copyToClipboard}
                      className="border-stone-200 hover:bg-stone-50"
                    >
                      {copySuccess ? (
                        <>
                          <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="h-4 w-4 mr-2" />
                          Copy
                        </>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={downloadReadme}
                      className="border-stone-200 hover:bg-stone-50"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>

                <div className="bg-stone-50 rounded-lg p-6 border border-stone-200">
                  <div className="prose prose-stone max-w-none text-sm text-stone-700">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {result}
                    </ReactMarkdown>
                  </div>
                </div>

                <div className="mt-6 text-center">
                  <Button
                    onClick={() => {
                      setResult(null);
                      setGithubUrl("");
                    }}
                    variant="outline"
                    className="border-stone-200 hover:bg-stone-50"
                  >
                    Generate Another README
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-16">
          <p className="text-sm text-stone-500">
            Powered by Azure OpenAI • Made with ❤️ for developers
          </p>
        </div>
      </div>
    </div>
  );
}
