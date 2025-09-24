export interface Model {
  id: string;
  label: string;
  description: string;
  cost: "$" | "$$" | "$$$";
  speed: "fast" | "medium" | "slower";
  badge?: string;
  recommended?: boolean;
}

export interface Provider {
  id: string;
  label: string;
  tagline: string;
  models: Model[];
  defaultModel: string;
  icon?: string;
}

export const PROVIDERS: Provider[] = [
  {
    id: "openai",
    label: "OpenAI",
    tagline: "Industry-leading reasoning & versatility",
    icon: "🤖",
    models: [
      {
        id: "gpt-4o-mini",
        label: "GPT-4o Mini",
        description: "Fast, cost-effective model perfect for most tasks",
        cost: "$",
        speed: "fast",
        badge: "Most Popular",
        recommended: true,
      },
      {
        id: "gpt-4o",
        label: "GPT-4o",
        description: "Enhanced reasoning with multimodal capabilities",
        cost: "$$",
        speed: "medium",
        badge: "Balanced",
      },
      {
        id: "gpt-3.5-turbo",
        label: "GPT-3.5 Turbo",
        description: "Reliable and efficient for standard documentation",
        cost: "$",
        speed: "fast",
      },
    ],
    defaultModel: "gpt-4o-mini",
  },
  {
    id: "gemini",
    label: "Google Gemini",
    tagline: "Ultra-fast responses with advanced multimodal AI",
    icon: "✨",
    models: [
      {
        id: "gemini-1.5-flash",
        label: "Gemini 1.5 Flash",
        description: "Lightning-fast generation with excellent quality",
        cost: "$",
        speed: "fast",
        badge: "Fastest",
      },
      {
        id: "gemini-1.5-pro",
        label: "Gemini 1.5 Pro",
        description: "Superior reasoning for complex documentation",
        cost: "$$",
        speed: "slower",
        badge: "Advanced",
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

// Default selections
export const DEFAULT_PROVIDER = PROVIDERS[0].id;
export const DEFAULT_MODEL = PROVIDERS[0].defaultModel;
