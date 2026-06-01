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

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token!);
    }
  });
  failedQueue = [];
}

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<{ message: string; code: string }>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise<typeof originalRequest>((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              resolve(apiClient(originalRequest));
            },
            reject,
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem("refresh_token");

      if (!refreshToken) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
        if (typeof window !== "undefined") {
          window.location.href = "/auth/login";
        }
        return Promise.reject(error);
      }

      try {
        const response = await axios.post<ApiResponse<{ access_token: string; refresh_token: string }>>(
          `${API_BASE_URL}/v1/auth/refresh`,
          { refresh_token: refreshToken }
        );

        const { access_token, refresh_token: newRefreshToken } = response.data.data;
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", newRefreshToken);

        processQueue(null, access_token);

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
        if (typeof window !== "undefined") {
          window.location.href = "/auth/login";
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    const message =
      error.response?.data?.message || error.message || "An unexpected error occurred";
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
      const refreshToken = localStorage.getItem("refresh_token");
      await apiClient.post("/v1/auth/logout", { refresh_token: refreshToken });
    },
    me: async () => {
      const response = await apiClient.get<ApiResponse<{ user: import("@/types").User }>>("/v1/auth/me");
      return response.data.data;
    },
    refreshToken: async (refreshToken: string) => {
      const response = await apiClient.post<ApiResponse<AuthResponse["tokens"]>>("/v1/auth/refresh", {
        refresh_token: refreshToken,
      });
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