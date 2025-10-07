const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const IS_PRODUCTION = process.env.NODE_ENV === "production";

const API_PREFIX = IS_PRODUCTION ? "/api" : "";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL, apiPrefix: string = API_PREFIX) {
    this.baseUrl = baseUrl;
    this.apiPrefix = apiPrefix;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const fullEndpoint = `${this.apiPrefix}${endpoint}`;
    const url = `${this.baseUrl}${fullEndpoint}`;
    console.log("Emitting url", url);
    const config: RequestInit = {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(
          error.message || `HTTP error: Status ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.log(`API request failed with endpoint: ${endpoint}`, error);
      throw error;
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: "DELETE",
      body: data ? JSON.stringify(data) : undefined,
    });
  }
}

export const apiClient = new ApiClient();
