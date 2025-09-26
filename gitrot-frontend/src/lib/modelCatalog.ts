// Frontend model catalog aligned with backend ModelType and ModelProvider enums

export interface Model {
  id: string;
  label: string;
  description: string;
  cost: "$" | "$$" | "$$$";
  speed: "fast" | "medium" | "slower";
  badge?: string;
  recommended?: boolean;
  contextWindow?: number;
  maxOutputTokens?: number;
}

export interface Provider {
  id: string;
  label: string;
  tagline: string;
  models: Model[];
  defaultModel: string;
  icon?: string;
  backendProvider: string; // Maps to backend ModelProvider enum
}

export const PROVIDERS: Provider[] = [
  {
    id: "azure_openai",
    label: "Azure OpenAI",
    tagline: "Enterprise-grade OpenAI models with Azure reliability",
    icon: "🤖",
    backendProvider: "azure_openai",
    models: [
      {
        id: "gpt-4o-mini",
        label: "GPT-4o Mini",
        description: "Fast, cost-effective model perfect for most tasks",
        cost: "$",
        speed: "fast",
        badge: "Most Popular",
        recommended: true,
        contextWindow: 128000,
        maxOutputTokens: 16384,
      },
      {
        id: "gpt-4o",
        label: "GPT-4o",
        description: "Enhanced reasoning with multimodal capabilities",
        cost: "$$",
        speed: "medium",
        badge: "Balanced",
        contextWindow: 128000,
        maxOutputTokens: 4096,
      },
      {
        id: "gpt-4-turbo",
        label: "GPT-4 Turbo",
        description: "High-quality responses with large context window",
        cost: "$$$",
        speed: "slower",
        badge: "Premium",
        contextWindow: 128000,
        maxOutputTokens: 4096,
      },
      {
        id: "gpt-35-turbo",
        label: "GPT-3.5 Turbo",
        description: "Reliable and efficient for standard documentation",
        cost: "$",
        speed: "fast",
        contextWindow: 4096,
        maxOutputTokens: 2048,
      },
      {
        id: "gpt-35-turbo-instruct",
        label: "GPT-3.5 Turbo Instruct",
        description: "Instruction-following variant of GPT-3.5",
        cost: "$",
        speed: "fast",
        contextWindow: 4096,
        maxOutputTokens: 2048,
      },
      {
        id: "gpt-35-turbo-16k",
        label: "GPT-3.5 Turbo 16K",
        description: "Extended context version of GPT-3.5",
        cost: "$",
        speed: "fast",
        badge: "Large Context",
        contextWindow: 16384,
        maxOutputTokens: 8192,
      },
      {
        id: "gpt-4",
        label: "GPT-4",
        description: "Advanced reasoning and complex problem-solving",
        cost: "$$$",
        speed: "slower",
        contextWindow: 8192,
        maxOutputTokens: 4096,
      },
      {
        id: "gpt-4-32k",
        label: "GPT-4 32K",
        description: "GPT-4 with extended 32K context window",
        cost: "$$$",
        speed: "slower",
        badge: "Large Context",
        contextWindow: 32768,
        maxOutputTokens: 16384,
      },
    ],
    defaultModel: "gpt-4o",
  },
  {
    id: "google",
    label: "Google Gemini",
    tagline: "Ultra-fast responses with massive context windows",
    icon: "✨",
    backendProvider: "google",
    models: [
      {
        id: "gemini-1.5-flash",
        label: "Gemini 1.5 Flash",
        description: "Lightning-fast generation with 1M token context",
        cost: "$",
        speed: "fast",
        badge: "Fastest",
        recommended: true,
        contextWindow: 1000000,
        maxOutputTokens: 8192,
      },
      {
        id: "gemini-1.5-pro",
        label: "Gemini 1.5 Pro",
        description: "Superior reasoning with 2M token context",
        cost: "$$",
        speed: "slower",
        badge: "Ultra Context",
        contextWindow: 2000000,
        maxOutputTokens: 8192,
      },
    ],
    defaultModel: "gemini-1.5-flash",
  },
];

// Helper functions
export function getProvider(id: string): Provider | undefined {
  return PROVIDERS.find((p) => p.id === id);
}

export function getAllProviderOptions() {
  return PROVIDERS.map((p) => ({
    value: p.id,
    label: p.label,
    description: p.tagline,
    icon: p.icon,
  }));
}

export function getModelOptions(providerId: string) {
  const provider = getProvider(providerId);
  return provider
    ? provider.models.map((m) => ({
        value: m.id,
        label: m.label,
        description: m.description,
        cost: m.cost,
        speed: m.speed,
        badge: m.badge,
        recommended: m.recommended,
      }))
    : [];
}

export function getSelectedModel(providerId: string, modelId: string) {
  const provider = getProvider(providerId);
  return provider?.models.find((m) => m.id === modelId);
}

// Backend integration helpers
export function getBackendModelPayload(providerId: string, modelId: string) {
  const provider = getProvider(providerId);
  const model = getSelectedModel(providerId, modelId);

  return {
    model_name: modelId,
    provider: provider?.backendProvider || providerId,
    model_config: {
      provider_id: providerId,
      model_id: modelId,
      context_window: model?.contextWindow,
      max_output_tokens: model?.maxOutputTokens,
      description: model?.description,
    },
  };
}

// Model type mapping for backend compatibility
export const MODEL_TYPE_MAPPING: Record<string, string> = {
  "gpt-35-turbo": "gpt-35-turbo",
  "gpt-35-turbo-instruct": "gpt-35-turbo-instruct",
  "gpt-35-turbo-16k": "gpt-35-turbo-16k",
  "gpt-4": "gpt-4",
  "gpt-4-32k": "gpt-4-32k",
  "gpt-4-turbo": "gpt-4-turbo",
  "gpt-4o": "gpt-4o",
  "gpt-4o-mini": "gpt-4o-mini",
  "gemini-1.5-pro": "gemini-1.5-pro",
  "gemini-1.5-flash": "gemini-1.5-flash",
};

// Default selections
export const DEFAULT_PROVIDER = PROVIDERS[0].id;
export const DEFAULT_MODEL = PROVIDERS[0].defaultModel;
