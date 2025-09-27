import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { AlertCircle, Settings, Crown, Wallet } from "lucide-react";

interface CustomCredentials {
  azure_api_key?: string;
  azure_endpoint?: string;
  azure_api_version?: string;
  azure_deployment?: string;
  google_api_key?: string;
  openai_api_key?: string;
}

interface ConfigurationPanelProps {
  selectedProvider: string;
  selectedModel: string;
  useHostedService: boolean;
  customCredentials: CustomCredentials;
  onUseHostedServiceChange: (value: boolean) => void;
  onCustomCredentialsChange: (credentials: CustomCredentials) => void;
  onProviderChange: (provider: string) => void;
  onModelChange: (model: string) => void;
}

export default function ConfigurationPanel({
  selectedProvider,
  selectedModel,
  useHostedService,
  customCredentials,
  onUseHostedServiceChange,
  onCustomCredentialsChange,
  onProviderChange,
  onModelChange,
}: ConfigurationPanelProps) {
  const updateCredential = (key: keyof CustomCredentials, value: string) => {
    onCustomCredentialsChange({
      ...customCredentials,
      [key]: value || undefined,
    });
  };

  const handleSelectPaid = () => {
    onUseHostedServiceChange(true);
  };

  const handleSelectFree = () => {
    onUseHostedServiceChange(false);
  };

  const isConfigComplete = () => {
    if (useHostedService) return true;

    if (selectedProvider === "azure_openai") {
      return !!(
        customCredentials.azure_api_key &&
        customCredentials.azure_endpoint &&
        customCredentials.azure_deployment
      );
    }

    if (selectedProvider === "google") {
      return !!customCredentials.google_api_key;
    }

    return false;
  };

  const getModelOptions = () => {
    if (selectedProvider === "azure_openai") {
      return [
        { value: "gpt-4o", label: "GPT-4o (Latest)" },
        { value: "gpt-4o-mini", label: "GPT-4o Mini (Fast & Cost-Effective)" },
        { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
        { value: "gpt-35-turbo", label: "GPT-3.5 Turbo" },
      ];
    } else if (selectedProvider === "google") {
      return [
        { value: "gemini-1.5-pro", label: "Gemini 1.5 Pro (Best Performance)" },
        { value: "gemini-1.5-flash", label: "Gemini 1.5 Flash (Fast)" },
        { value: "gemini-pro", label: "Gemini Pro" },
      ];
    }
    return [];
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          AI Model Configuration
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Model Selection */}
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Select
                label="AI Provider"
                options={[
                  { value: "azure_openai", label: "Azure OpenAI" },
                  { value: "google", label: "Google Gemini" },
                ]}
                value={selectedProvider}
                onValueChange={onProviderChange}
                placeholder="Select AI Provider"
              />
            </div>

            <div className="space-y-2">
              <Select
                label="Model"
                options={getModelOptions()}
                value={selectedModel}
                onValueChange={onModelChange}
                disabled={!selectedProvider}
                placeholder="Select Model"
              />
            </div>
          </div>
        </div>

        {/* Service Type Selection */}
        <div className="space-y-3">
          <div className="text-base font-medium">Choose Your Plan</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Paid Version - Hosted Service */}
            <div
              className={
                useHostedService
                  ? "p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md hover:scale-[1.02] border-gray-300 bg-white shadow-sm"
                  : "p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md hover:scale-[1.02] border-gray-300 hover:border-blue-400 bg-white hover:bg-gray-50"
              }
              onClick={handleSelectPaid}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div
                    className={
                      useHostedService
                        ? "w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors border-blue-600 bg-blue-600 shadow-sm"
                        : "w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors border-gray-400 bg-white hover:border-blue-400"
                    }
                  >
                    {useHostedService && (
                      <div className="w-3 h-3 rounded-full bg-white" />
                    )}
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Crown className="h-4 w-4 text-amber-600" />
                    <h3 className="font-semibold text-gray-900">GitRot Pro</h3>
                    <Badge
                      variant="default"
                      className="bg-amber-500 hover:bg-amber-600 text-xs font-medium"
                    >
                      PAID
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-3 font-medium">
                    Premium service with enterprise features & support.
                  </p>
                  <ul className="text-xs text-gray-500 space-y-1">
                    <li>• Unlimited usage</li>
                    <li>• Premium model access</li>
                    <li>• Priority support</li>
                    <li>• No API key management</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Free Version - Bring Your Own Keys */}
            <div
              className={
                !useHostedService
                  ? "p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md hover:scale-[1.02] border-gray-300 bg-white shadow-sm"
                  : "p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md hover:scale-[1.02] border-gray-300 hover:border-blue-400 bg-white hover:bg-gray-50"
              }
              onClick={handleSelectFree}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div
                    className={
                      !useHostedService
                        ? "w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors border-blue-600 bg-blue-600 shadow-sm"
                        : "w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors border-gray-400 bg-white hover:border-blue-400"
                    }
                  >
                    {!useHostedService && (
                      <div className="w-3 h-3 rounded-full bg-white" />
                    )}
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Wallet className="h-4 w-4 text-green-600" />
                    <h3 className="font-semibold text-gray-900">GitRot Free</h3>
                    <Badge
                      variant="secondary"
                      className="bg-green-100 text-green-700 text-xs font-medium"
                    >
                      FREE
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-3 font-medium">
                    Use your own AI service credits. Pay providers directly.
                  </p>
                  <ul className="text-xs text-gray-500 space-y-1">
                    <li>• Bring your own API keys</li>
                    <li>• Pay AI providers directly</li>
                    <li>• Full control over usage</li>
                    <li>• Enterprise compliance</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Custom Credentials Form */}
        {!useHostedService && (
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg border">
            <div className="flex items-center gap-2 mb-3">
              <AlertCircle className="h-4 w-4 text-orange-500" />
              <span className="text-sm font-medium text-gray-700">
                API Credentials Required
              </span>
            </div>

            {selectedProvider === "azure_openai" && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="azure-api-key">
                      API Key <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="azure-api-key"
                      type="password"
                      placeholder="Your Azure OpenAI API key"
                      value={customCredentials.azure_api_key || ""}
                      onChange={(e) =>
                        updateCredential("azure_api_key", e.target.value)
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="azure-endpoint">
                      Endpoint <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="azure-endpoint"
                      placeholder="https://your-resource.openai.azure.com/"
                      value={customCredentials.azure_endpoint || ""}
                      onChange={(e) =>
                        updateCredential("azure_endpoint", e.target.value)
                      }
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="azure-deployment">
                      Deployment Name <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="azure-deployment"
                      placeholder={selectedModel}
                      value={
                        customCredentials.azure_deployment || selectedModel
                      }
                      onChange={(e) =>
                        updateCredential("azure_deployment", e.target.value)
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="azure-api-version">API Version</Label>
                    <Input
                      id="azure-api-version"
                      placeholder="2024-12-01-preview"
                      value={
                        customCredentials.azure_api_version ||
                        "2024-12-01-preview"
                      }
                      onChange={(e) =>
                        updateCredential("azure_api_version", e.target.value)
                      }
                    />
                  </div>
                </div>
              </div>
            )}

            {selectedProvider === "google" && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="google-api-key">
                    Google Gemini API Key{" "}
                    <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="google-api-key"
                    type="password"
                    placeholder="Your Google Gemini API key"
                    value={customCredentials.google_api_key || ""}
                    onChange={(e) =>
                      updateCredential("google_api_key", e.target.value)
                    }
                  />
                </div>

                <div className="text-xs text-gray-600">
                  Get your API key from{" "}
                  <a
                    href="https://makersuite.google.com/app/apikey"
                    target="_blank"
                    className="text-blue-600 hover:underline"
                    rel="noopener noreferrer"
                  >
                    Google AI Studio
                  </a>
                </div>
              </div>
            )}

            <div className="mt-4">
              <Badge
                variant={isConfigComplete() ? "default" : "destructive"}
                className="mb-2"
              >
                {isConfigComplete()
                  ? "✓ Configuration Complete"
                  : "⚠ Missing Required Fields"}
              </Badge>

              {!isConfigComplete() && (
                <p className="text-xs text-gray-500">
                  Please fill in all required fields marked with *
                </p>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
