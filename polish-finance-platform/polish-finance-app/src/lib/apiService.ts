/**
 * API Service - Production-ready API client
 * Handles all API communication with proper error handling and retries
 */

const API_TIMEOUT = 10000; // 10 seconds
const MAX_RETRIES = 3;

interface ApiConfig {
  baseUrl: string;
  timeout?: number;
  retries?: number;
}

class ApiService {
  private config: Required<ApiConfig>;

  constructor(config: ApiConfig) {
    this.config = {
      baseUrl: config.baseUrl,
      timeout: config.timeout || API_TIMEOUT,
      retries: config.retries || MAX_RETRIES,
    };
  }

  private async fetchWithTimeout(url: string, options: RequestInit = {}): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }

  async get<T>(endpoint: string, retries = this.config.retries): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await this.fetchWithTimeout(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        return data as T;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        if (attempt < retries) {
          // Exponential backoff
          await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
      }
    }

    throw new Error(`API request failed after ${retries} attempts: ${lastError?.message || 'Unknown error'}`);
  }

  async post<T>(endpoint: string, body: any, retries = this.config.retries): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await this.fetchWithTimeout(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(body),
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        return data as T;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        if (attempt < retries) {
          await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
      }
    }

    throw new Error(`API request failed after ${retries} attempts: ${lastError?.message || 'Unknown error'}`);
  }
}

// Create API service instances
export const backendApi = new ApiService({
  baseUrl: import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000'),
});

export const analysisApi = new ApiService({
  baseUrl: import.meta.env.VITE_ANALYSIS_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8001'),
});


