"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import {
  Github,
  Sparkles,
  ArrowRight,
  Copy,
  Download,
  CheckCircle,
  Settings,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { LoadingSpinner } from "@/components/loading-spinner";
import {
  getProvider,
  getAllProviderOptions,
  getModelOptions,
  getSelectedModel,
  getBackendModelPayload,
  DEFAULT_PROVIDER,
  DEFAULT_MODEL,
} from "@/lib/modelCatalog";

export default function HomePage() {
  const [githubUrl, setGithubUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(DEFAULT_PROVIDER);
  const [selectedModel, setSelectedModel] = useState(DEFAULT_MODEL);
  const [isMounted, setIsMounted] = useState(false);

  // Load persisted selection on mount
  useEffect(() => {
    setIsMounted(true);
    try {
      const stored = localStorage.getItem("gitrot:modelSelection");
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.provider && getProvider(parsed.provider)) {
          setSelectedProvider(parsed.provider);
          const provider = getProvider(parsed.provider);
          if (
            parsed.model &&
            provider?.models.some((m) => m.id === parsed.model)
          ) {
            setSelectedModel(parsed.model);
          } else if (provider) {
            setSelectedModel(provider.defaultModel);
          }
        }
      }
    } catch {
      // Ignore localStorage errors
    }
  }, []);

  // Persist selection changes (only after mounted)
  useEffect(() => {
    if (!isMounted) return;
    try {
      localStorage.setItem(
        "gitrot:modelSelection",
        JSON.stringify({
          provider: selectedProvider,
          model: selectedModel,
        })
      );
    } catch {
      // Ignore localStorage errors
    }
  }, [selectedProvider, selectedModel, isMounted]);

  // Update model when provider changes
  const handleProviderChange = (newProvider: string) => {
    setSelectedProvider(newProvider);
    const provider = getProvider(newProvider);
    if (provider) {
      setSelectedModel(provider.defaultModel);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!githubUrl) return;

    setIsLoading(true);

    try {
      // Use environment-based URL selection
      const apiUrl =
        typeof window !== "undefined" &&
        window.location.hostname === "localhost"
          ? "http://localhost:8000/generate-readme" // Local development
          : "/api/generate-readme"; // Production (through ingress)

      const backendPayload = getBackendModelPayload(
        selectedProvider,
        selectedModel
      );

      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: githubUrl,
          generation_method: "Standard README",
          ...backendPayload, // Spread the backend-compatible payload
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

                  {/* AI Model Selection */}
                  <div className="space-y-4 p-4 bg-stone-50 rounded-lg border border-stone-200">
                    <div className="flex items-center space-x-2">
                      <Settings className="h-4 w-4 text-stone-600" />
                      <h3 className="text-sm font-semibold text-stone-700">
                        AI Configuration
                      </h3>
                      <Badge
                        variant="secondary"
                        className="text-xs bg-stone-200 text-stone-600"
                      >
                        Advanced
                      </Badge>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Select
                          label="AI Provider"
                          options={getAllProviderOptions()}
                          value={selectedProvider}
                          onValueChange={handleProviderChange}
                          disabled={isLoading}
                          placeholder="Choose AI provider..."
                        />
                      </div>

                      <div>
                        <Select
                          label="Model"
                          options={getModelOptions(selectedProvider)}
                          value={selectedModel}
                          onValueChange={setSelectedModel}
                          disabled={isLoading}
                          placeholder="Choose model..."
                        />
                      </div>
                    </div>

                    {/* Model Performance Indicator */}
                    {(() => {
                      const currentModel = getSelectedModel(
                        selectedProvider,
                        selectedModel
                      );
                      return (
                        currentModel && (
                          <div className="flex items-center justify-between text-xs text-stone-600 pt-2 border-t border-stone-200">
                            <div className="flex items-center space-x-4">
                              <span className="flex items-center space-x-1">
                                <Zap className="h-3 w-3" />
                                <span>Speed: {currentModel.speed}</span>
                              </span>
                              <span>Cost: {currentModel.cost}</span>
                            </div>
                            {currentModel.recommended && (
                              <span className="flex items-center space-x-1 text-green-600">
                                <CheckCircle className="h-3 w-3" />
                                <span>Recommended</span>
                              </span>
                            )}
                          </div>
                        )
                      );
                    })()}
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
                        <span className="ml-2">
                          {isMounted ? (
                            <>
                              Generating with{" "}
                              {getProvider(selectedProvider)?.label}{" "}
                              {
                                getSelectedModel(
                                  selectedProvider,
                                  selectedModel
                                )?.label
                              }
                              ...
                            </>
                          ) : (
                            "Generating README..."
                          )}
                        </span>
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
                    <div className="flex items-center space-x-2 mb-1">
                      <h3 className="text-lg font-semibold text-stone-900">
                        Generated README
                      </h3>
                      <Badge
                        variant="secondary"
                        className="text-xs bg-green-100 text-green-700"
                      >
                        {isMounted ? getProvider(selectedProvider)?.icon : "🤖"}{" "}
                        {isMounted
                          ? getProvider(selectedProvider)?.label
                          : "AI"}
                      </Badge>
                      <Badge
                        variant="outline"
                        className="text-xs border-stone-200"
                      >
                        {isMounted
                          ? getSelectedModel(selectedProvider, selectedModel)
                              ?.label
                          : "Model"}
                      </Badge>
                    </div>
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
            Powered by{" "}
            {isMounted
              ? `${getProvider(selectedProvider)?.label} ${
                  getSelectedModel(selectedProvider, selectedModel)?.label
                }`
              : "AI"}{" "}
            • Made with ❤️ for developers
          </p>
        </div>
      </div>
    </div>
  );
}
