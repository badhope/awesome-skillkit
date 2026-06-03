import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import type {
  ApiResponse,
  AuthResponse,
  Category,
  Composition,
  DashboardStats,
  LoginRequest,
  PaginatedResponse,
  PopularSkill,
  RegisterRequest,
  SearchParams,
  Skill,
  SkillCreateRequest,
  SkillUpdateRequest,
  SkillReview,
  ReviewCreateRequest,
  SkillVersion,
  UsageRecord,
  UsageTrend,
  CategoryDistribution,
  CompositionCreateRequest,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api";

// HttpOnly cookies carry the auth now. We MUST include credentials on
// every request or the browser will drop the cookies. The old code
// stored tokens in `localStorage` and forwarded them as `Authorization:
// Bearer` headers, which is XSS-vulnerable.
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
  timeout: 15000,
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<{ detail?: string; message?: string; code?: string }>) => {
    // The server is now the source of truth for cookie lifetime; when
    // a 401 comes back, we hard-logout (the access cookie is gone or
    // rejected) and bounce to the login page. No more client-side
    // refresh-token queue — the server sets a new pair on every
    // successful 200 from /auth/refresh.
    if (error.response?.status === 401 && typeof window !== "undefined") {
      // Avoid infinite loops if /auth/login itself 401s.
      const url = error.config?.url ?? "";
      if (url.includes("/auth/")) {
        return Promise.reject(error);
      }
      // Make sure any cached user state is gone — the cookie is the
      // source of truth now.
      try {
        localStorage.removeItem("user");
      } catch {
        // localStorage may be disabled (private mode); ignore.
      }
      if (window.location.pathname !== "/auth/login") {
        const next = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/auth/login?next=${next}`;
      }
    }

    const message =
      // FastAPI's HTTPException serializes to `{ "detail": "..." }` (and our
      // `localized_http_exception` follows the same shape). The legacy
      // `message` field is kept as a fallback for handlers that opt into
      // the `ApiResponse` envelope.
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "An unexpected error occurred";
    return Promise.reject(new Error(message));
  }
);

export const api = {
  auth: {
    login: async (data: LoginRequest): Promise<AuthResponse> => {
      const response = await apiClient.post<ApiResponse<AuthResponse>>("/v1/auth/login", data);
      return response.data.data;
    },
    register: async (data: RegisterRequest): Promise<AuthResponse> => {
      const response = await apiClient.post<ApiResponse<AuthResponse>>("/v1/auth/register", data);
      return response.data.data;
    },
    logout: async (): Promise<void> => {
      await apiClient.post("/v1/auth/logout");
    },
    me: async () => {
      const response = await apiClient.get<ApiResponse<{ user: import("@/types").User }>>("/v1/auth/me");
      return response.data.data;
    },
    refreshToken: async () => {
      // The refresh cookie is HttpOnly and gets sent automatically.
      // Just hit the endpoint; on success the server sets a new pair.
      const response = await apiClient.post<ApiResponse<AuthResponse["tokens"]>>(
        "/v1/auth/refresh",
        {}
      );
      return response.data.data;
    },
  },

  skills: {
    list: async (params?: Partial<SearchParams>): Promise<PaginatedResponse<Skill>> => {
      const response = await apiClient.get<ApiResponse<PaginatedResponse<Skill>>>("/v1/skills", { params });
      return response.data.data;
    },
    search: async (params: SearchParams): Promise<PaginatedResponse<Skill>> => {
      const response = await apiClient.get<ApiResponse<PaginatedResponse<Skill>>>("/v1/skills/search", {
        params,
      });
      return response.data.data;
    },
    get: async (slug: string): Promise<Skill> => {
      const response = await apiClient.get<ApiResponse<Skill>>(`/v1/skills/${slug}`);
      return response.data.data;
    },
    create: async (data: SkillCreateRequest): Promise<Skill> => {
      const response = await apiClient.post<ApiResponse<Skill>>("/v1/skills", data);
      return response.data.data;
    },
    update: async (slug: string, data: SkillUpdateRequest): Promise<Skill> => {
      const response = await apiClient.patch<ApiResponse<Skill>>(`/v1/skills/${slug}`, data);
      return response.data.data;
    },
    delete: async (slug: string): Promise<void> => {
      await apiClient.delete(`/v1/skills/${slug}`);
    },
    getVersions: async (slug: string): Promise<SkillVersion[]> => {
      const response = await apiClient.get<ApiResponse<SkillVersion[]>>(`/v1/skills/${slug}/versions`);
      return response.data.data;
    },
    getDependencies: async (slug: string): Promise<Skill[]> => {
      const response = await apiClient.get<ApiResponse<Skill[]>>(`/v1/skills/${slug}/dependencies`);
      return response.data.data;
    },
    getReviews: async (slug: string, page = 1): Promise<PaginatedResponse<SkillReview>> => {
      const response = await apiClient.get<ApiResponse<PaginatedResponse<SkillReview>>>(
        `/v1/skills/${slug}/reviews`,
        { params: { page } }
      );
      return response.data.data;
    },
    addReview: async (slug: string, data: ReviewCreateRequest): Promise<SkillReview> => {
      const response = await apiClient.post<ApiResponse<SkillReview>>(`/v1/skills/${slug}/reviews`, data);
      return response.data.data;
    },
    getSimilar: async (slug: string): Promise<Skill[]> => {
      const response = await apiClient.get<ApiResponse<Skill[]>>(`/v1/skills/${slug}/similar`);
      return response.data.data;
    },
    getTrending: async (limit = 10): Promise<Skill[]> => {
      const response = await apiClient.get<ApiResponse<Skill[]>>("/v1/skills/trending", {
        params: { limit },
      });
      return response.data.data;
    },
    getFeatured: async (): Promise<Skill[]> => {
      const response = await apiClient.get<ApiResponse<Skill[]>>("/v1/skills/featured");
      return response.data.data;
    },
    download: async (slug: string, version?: string): Promise<Blob> => {
      const response = await apiClient.get(`/v1/skills/${slug}/download`, {
        params: version ? { version } : {},
        responseType: "blob",
      });
      return response.data;
    },
  },

  categories: {
    list: async (): Promise<Category[]> => {
      const response = await apiClient.get<ApiResponse<Category[]>>("/v1/categories");
      return response.data.data;
    },
    tree: async (): Promise<Category[]> => {
      const response = await apiClient.get<ApiResponse<Category[]>>("/v1/categories/tree");
      return response.data.data;
    },
    get: async (slug: string): Promise<Category> => {
      const response = await apiClient.get<ApiResponse<Category>>(`/v1/categories/${slug}`);
      return response.data.data;
    },
    getSkills: async (slug: string, params?: Partial<SearchParams>): Promise<PaginatedResponse<Skill>> => {
      const response = await apiClient.get<ApiResponse<PaginatedResponse<Skill>>>(
        `/v1/categories/${slug}/skills`,
        { params }
      );
      return response.data.data;
    },
  },

  compositions: {
    list: async (params?: Partial<SearchParams>): Promise<PaginatedResponse<Composition>> => {
      const response = await apiClient.get<ApiResponse<PaginatedResponse<Composition>>>("/v1/compositions", {
        params,
      });
      return response.data.data;
    },
    get: async (slug: string): Promise<Composition> => {
      const response = await apiClient.get<ApiResponse<Composition>>(`/v1/compositions/${slug}`);
      return response.data.data;
    },
    create: async (data: CompositionCreateRequest): Promise<Composition> => {
      const response = await apiClient.post<ApiResponse<Composition>>("/v1/compositions", data);
      return response.data.data;
    },
    delete: async (slug: string): Promise<void> => {
      await apiClient.delete(`/v1/compositions/${slug}`);
    },
  },

  dashboard: {
    stats: async (): Promise<DashboardStats> => {
      const response = await apiClient.get<ApiResponse<DashboardStats>>("/v1/dashboard/stats");
      return response.data.data;
    },
    usageTrends: async (days = 30): Promise<UsageTrend[]> => {
      const response = await apiClient.get<ApiResponse<UsageTrend[]>>("/v1/dashboard/usage-trends", {
        params: { days },
      });
      return response.data.data;
    },
    categoryDistribution: async (): Promise<CategoryDistribution[]> => {
      const response = await apiClient.get<ApiResponse<CategoryDistribution[]>>(
        "/v1/dashboard/category-distribution"
      );
      return response.data.data;
    },
    popularSkills: async (limit = 10): Promise<PopularSkill[]> => {
      const response = await apiClient.get<ApiResponse<PopularSkill[]>>("/v1/dashboard/popular-skills", {
        params: { limit },
      });
      return response.data.data;
    },
    recentUsage: async (limit = 20): Promise<UsageRecord[]> => {
      const response = await apiClient.get<ApiResponse<UsageRecord[]>>("/v1/dashboard/recent-usage", {
        params: { limit },
      });
      return response.data.data;
    },
  },

  tags: {
    list: async (): Promise<import("@/types").Tag[]> => {
      const response = await apiClient.get<ApiResponse<import("@/types").Tag[]>>("/v1/tags");
      return response.data.data;
    },
    search: async (q: string): Promise<import("@/types").Tag[]> => {
      const response = await apiClient.get<ApiResponse<import("@/types").Tag[]>>("/v1/tags/search", {
        params: { q },
      });
      return response.data.data;
    },
  },
};

export default api;
