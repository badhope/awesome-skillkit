import type {
  AnalyticsDashboardDict,
  CategoryDict,
  ClientConfig,
  CompositionDict,
  PaginatedResult,
  SkillDependencyDict,
  SkillDict,
  SkillRatingResponse,
  SkillSearchResultDict,
  SkillSimilarDict,
  SkillUsageResponse,
  SkillUsageTrendResponse,
  SkillVersionDict,
  TagDict,
  TokenDict,
  UserDict,
} from "./types";
import {
  SkillLibraryError,
  ConnectionError,
  APIError,
  RateLimitError,
  createErrorFromStatus,
} from "./errors";

type QueryParams = Record<string, string | number | boolean | undefined | null>;
type JsonBody = Record<string, unknown> | unknown[];

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

class SkillsAPI {
  constructor(private client: SkillLibraryClient) {}

  async list(params?: {
    category_slug?: string;
    tag?: string;
    search?: string;
    complexity?: string;
    status?: string;
    sort_by?: string;
    sort_order?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResult<SkillDict>> {
    const data = await this.client.request<PaginatedResult<SkillDict>>("GET", "/skills", params as QueryParams);
    return data;
  }

  async search(
    q: string,
    limit: number = 10,
    category_id?: string,
  ): Promise<SkillSearchResultDict[]> {
    const params: QueryParams = { q, limit };
    if (category_id) params.category_id = category_id;
    return this.client.request<SkillSearchResultDict[]>("GET", "/skills/search", params);
  }

  async get(slug: string): Promise<SkillDict> {
    return this.client.request<SkillDict>("GET", `/skills/${slug}`);
  }

  async create(skillData: Record<string, unknown>): Promise<SkillDict> {
    return this.client.request<SkillDict>("POST", "/skills", undefined, skillData as JsonBody);
  }

  async update(slug: string, skillData: Record<string, unknown>): Promise<SkillDict> {
    return this.client.request<SkillDict>("PUT", `/skills/${slug}`, undefined, skillData as JsonBody);
  }

  async delete(slug: string): Promise<void> {
    await this.client.request<void>("DELETE", `/skills/${slug}`);
  }

  async getFeatured(limit: number = 10): Promise<SkillDict[]> {
    return this.client.request<SkillDict[]>("GET", "/skills/featured", { limit });
  }

  async getPopular(limit: number = 10): Promise<SkillDict[]> {
    return this.client.request<SkillDict[]>("GET", "/skills/popular", { limit });
  }

  async getTrending(limit: number = 10): Promise<SkillDict[]> {
    return this.client.request<SkillDict[]>("GET", "/skills/trending", { limit });
  }

  async getVersions(slug: string): Promise<SkillVersionDict[]> {
    return this.client.request<SkillVersionDict[]>("GET", `/skills/${slug}/versions`);
  }

  async createVersion(slug: string, versionData: Record<string, unknown>): Promise<SkillVersionDict> {
    return this.client.request<SkillVersionDict>("POST", `/skills/${slug}/versions`, undefined, versionData as JsonBody);
  }

  async getDependencies(slug: string): Promise<SkillDependencyDict[]> {
    return this.client.request<SkillDependencyDict[]>("GET", `/skills/${slug}/dependencies`);
  }

  async addDependency(slug: string, dependencyData: Record<string, unknown>): Promise<SkillDependencyDict> {
    return this.client.request<SkillDependencyDict>(
      "POST",
      `/skills/${slug}/dependencies`,
      undefined,
      dependencyData as JsonBody,
    );
  }

  async removeDependency(slug: string, depId: string): Promise<void> {
    await this.client.request<void>("DELETE", `/skills/${slug}/dependencies/${depId}`);
  }

  async getSimilar(slug: string, limit: number = 10): Promise<SkillSimilarDict[]> {
    return this.client.request<SkillSimilarDict[]>("GET", `/skills/${slug}/similar`, { limit });
  }

  async rate(slug: string, rating: number, comment?: string): Promise<SkillRatingResponse> {
    const body: Record<string, unknown> = { rating };
    if (comment) body.comment = comment;
    return this.client.request<SkillRatingResponse>("POST", `/skills/${slug}/rate`, undefined, body);
  }

  async logUsage(slug: string, action: string = "download"): Promise<SkillUsageResponse> {
    return this.client.request<SkillUsageResponse>("POST", `/skills/${slug}/use`, undefined, { action });
  }
}

class CategoriesAPI {
  constructor(private client: SkillLibraryClient) {}

  async list(flat: boolean = false, parentId?: string): Promise<CategoryDict[]> {
    const params: QueryParams = { flat };
    if (parentId) params.parent_id = parentId;
    return this.client.request<CategoryDict[]>("GET", "/categories", params);
  }

  async tree(): Promise<CategoryDict[]> {
    return this.client.request<CategoryDict[]>("GET", "/categories/tree");
  }

  async get(slug: string): Promise<CategoryDict> {
    return this.client.request<CategoryDict>("GET", `/categories/${slug}`);
  }
}

class TagsAPI {
  constructor(private client: SkillLibraryClient) {}

  async list(params?: {
    search?: string;
    sort_by?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResult<TagDict>> {
    return this.client.request<PaginatedResult<TagDict>>("GET", "/tags", params as QueryParams);
  }

  async popular(limit: number = 20): Promise<TagDict[]> {
    return this.client.request<TagDict[]>("GET", "/tags/popular", { limit });
  }
}

class AuthAPI {
  constructor(private client: SkillLibraryClient) {}

  async login(username: string, password: string): Promise<TokenDict> {
    const data = await this.client.request<TokenDict>("POST", "/auth/login", undefined, { username, password });
    this.client.setToken(data.access_token);
    return data;
  }

  async register(
    email: string,
    username: string,
    password: string,
    fullName?: string,
  ): Promise<UserDict> {
    const body: Record<string, unknown> = { email, username, password };
    if (fullName) body.full_name = fullName;
    return this.client.request<UserDict>("POST", "/auth/register", undefined, body);
  }

  async refresh(refreshToken: string): Promise<TokenDict> {
    const data = await this.client.request<TokenDict>("POST", "/auth/refresh", undefined, { refresh_token: refreshToken });
    this.client.setToken(data.access_token);
    return data;
  }

  async me(): Promise<UserDict> {
    return this.client.request<UserDict>("GET", "/auth/me");
  }
}

class AnalyticsAPI {
  constructor(private client: SkillLibraryClient) {}

  async dashboard(): Promise<AnalyticsDashboardDict> {
    return this.client.request<AnalyticsDashboardDict>("GET", "/analytics/dashboard");
  }

  async skillUsage(days: number = 30): Promise<SkillUsageTrendResponse> {
    return this.client.request<SkillUsageTrendResponse>("GET", "/analytics/skills/usage", { days });
  }

  async popularSkills(limit: number = 10): Promise<Record<string, unknown>[]> {
    return this.client.request<Record<string, unknown>[]>("GET", "/analytics/skills/popular", { limit });
  }
}

class CompositionsAPI {
  constructor(private client: SkillLibraryClient) {}

  async list(params?: {
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResult<CompositionDict>> {
    return this.client.request<PaginatedResult<CompositionDict>>("GET", "/compositions", params as QueryParams);
  }

  async get(slug: string): Promise<CompositionDict> {
    return this.client.request<CompositionDict>("GET", `/compositions/${slug}`);
  }

  async create(compositionData: Record<string, unknown>): Promise<CompositionDict> {
    return this.client.request<CompositionDict>("POST", "/compositions", undefined, compositionData as JsonBody);
  }
}

export class SkillLibraryClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeout: number;
  private maxRetries: number;
  private retryDelay: number;
  private accessToken: string | null = null;

  public skills: SkillsAPI;
  public categories: CategoriesAPI;
  public tags: TagsAPI;
  public auth: AuthAPI;
  public analytics: AnalyticsAPI;
  public compositions: CompositionsAPI;

  constructor(config: ClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, "");
    this.apiKey = config.apiKey;
    this.timeout = config.timeout ?? 30;
    this.maxRetries = config.maxRetries ?? 3;
    this.retryDelay = config.retryDelay ?? 1.0;

    this.skills = new SkillsAPI(this);
    this.categories = new CategoriesAPI(this);
    this.tags = new TagsAPI(this);
    this.auth = new AuthAPI(this);
    this.analytics = new AnalyticsAPI(this);
    this.compositions = new CompositionsAPI(this);
  }

  setToken(token: string): void {
    this.accessToken = token;
  }

  clearToken(): void {
    this.accessToken = null;
  }

  async request<T>(
    method: string,
    path: string,
    params?: QueryParams,
    body?: JsonBody,
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}/api/v1${path}`);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.set(key, String(value));
        }
      });
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "Accept": "application/json",
    };

    if (this.accessToken) {
      headers["Authorization"] = `Bearer ${this.accessToken}`;
    }
    if (this.apiKey) {
      headers["X-API-Key"] = this.apiKey;
    }

    const signal = AbortSignal.timeout(this.timeout * 1000);

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const fetchOptions: RequestInit = {
          method,
          headers,
          signal,
        };

        if (body && method !== "GET" && method !== "HEAD") {
          fetchOptions.body = JSON.stringify(body);
        }

        const response = await fetch(url.toString(), fetchOptions);

        if (response.status === 204) {
          return undefined as unknown as T;
        }

        let responseData: unknown;
        const contentType = response.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
          responseData = await response.json();
        } else {
          responseData = await response.text();
        }

        if (!response.ok) {
          const errorMessage =
            typeof responseData === "object" && responseData !== null && "detail" in responseData
              ? String((responseData as Record<string, unknown>).detail)
              : typeof responseData === "string"
                ? responseData
                : "Unknown error";

          if (response.status === 429) {
            const retryAfter = response.headers.get("Retry-After");
            throw new RateLimitError(
              errorMessage,
              response.status,
              responseData,
              retryAfter ? parseInt(retryAfter, 10) : null,
            );
          }

          throw createErrorFromStatus(response.status, errorMessage, responseData);
        }

        return responseData as T;
      } catch (error: unknown) {
        if (error instanceof SkillLibraryError) {
          if (error instanceof RateLimitError && attempt < this.maxRetries) {
            const delay = error.retryAfter
              ? error.retryAfter * 1000
              : this.retryDelay * Math.pow(2, attempt) * 1000;
            await sleep(delay);
            continue;
          }
          throw error;
        }

        if (error instanceof DOMException && error.name === "TimeoutError") {
          lastError = new ConnectionError(`Request timed out: ${error.message}`);
        } else if (error instanceof TypeError && error.message.includes("fetch")) {
          lastError = new ConnectionError(`Connection failed: ${error.message}`);
        } else {
          lastError = new APIError(
            `Unexpected error: ${error instanceof Error ? error.message : String(error)}`,
          );
        }

        if (attempt < this.maxRetries) {
          await sleep(this.retryDelay * Math.pow(2, attempt) * 1000);
        }
      }
    }

    throw lastError || new APIError("Request failed after retries");
  }
}