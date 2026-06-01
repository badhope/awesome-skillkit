"use client";

import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import api from "@/lib/api";
import type {
  Skill,
  SearchParams,
  PaginatedResponse,
  SkillCreateRequest,
  SkillUpdateRequest,
  SkillReview,
  ReviewCreateRequest,
  SkillVersion,
} from "@/types";

export function useSkills(params?: Partial<SearchParams>) {
  return useQuery({
    queryKey: ["skills", params],
    queryFn: () => api.skills.list(params),
    placeholderData: (previousData) => previousData,
    staleTime: 2 * 60 * 1000,
  });
}

export function useInfiniteSkills(params?: Partial<SearchParams>) {
  return useInfiniteQuery({
    queryKey: ["skills", "infinite", params],
    queryFn: ({ pageParam = 1 }) =>
      api.skills.list({ ...params, page: pageParam as number }),
    initialPageParam: 1,
    getNextPageParam: (lastPage: PaginatedResponse<Skill>) => {
      if (lastPage.page < lastPage.total_pages) return lastPage.page + 1;
      return undefined;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function useSkill(slug: string) {
  return useQuery({
    queryKey: ["skill", slug],
    queryFn: () => api.skills.get(slug),
    enabled: !!slug,
    placeholderData: (previousData) => previousData,
    staleTime: 3 * 60 * 1000,
  });
}

export function useFeaturedSkills() {
  return useQuery({
    queryKey: ["skills", "featured"],
    queryFn: () => api.skills.getFeatured(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useTrendingSkills(limit = 10) {
  return useQuery({
    queryKey: ["skills", "trending", limit],
    queryFn: () => api.skills.getTrending(limit),
    staleTime: 3 * 60 * 1000,
  });
}

export function useSearchSkills(params: SearchParams) {
  return useQuery({
    queryKey: ["skills", "search", params],
    queryFn: () => api.skills.search(params),
    enabled: !!params.q && params.q.length >= 2,
    placeholderData: (previousData) => previousData,
    staleTime: 1 * 60 * 1000,
  });
}

export function useSimilarSkills(slug: string) {
  return useQuery({
    queryKey: ["skills", slug, "similar"],
    queryFn: () => api.skills.getSimilar(slug),
    enabled: !!slug,
    staleTime: 5 * 60 * 1000,
  });
}

export function useSkillVersions(slug: string) {
  return useQuery({
    queryKey: ["skills", slug, "versions"],
    queryFn: () => api.skills.getVersions(slug),
    enabled: !!slug,
  });
}

export function useSkillDependencies(slug: string) {
  return useQuery({
    queryKey: ["skills", slug, "dependencies"],
    queryFn: () => api.skills.getDependencies(slug),
    enabled: !!slug,
  });
}

export function useSkillReviews(slug: string, page = 1) {
  return useQuery({
    queryKey: ["skills", slug, "reviews", page],
    queryFn: () => api.skills.getReviews(slug, page),
    enabled: !!slug,
  });
}

export function useCreateSkill() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SkillCreateRequest) => api.skills.create(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["skills"] });
      toast.success(`Skill "${data.name}" created successfully!`);
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to create skill");
    },
  });
}

export function useUpdateSkill() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ slug, data }: { slug: string; data: SkillUpdateRequest }) =>
      api.skills.update(slug, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["skills"] });
      queryClient.invalidateQueries({ queryKey: ["skill", variables.slug] });
      toast.success("Skill updated successfully!");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to update skill");
    },
  });
}

export function useDeleteSkill() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (slug: string) => api.skills.delete(slug),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["skills"] });
      toast.success("Skill deleted successfully!");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to delete skill");
    },
  });
}

export function useAddReview(slug: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ReviewCreateRequest) => api.skills.addReview(slug, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["skills", slug, "reviews"] });
      queryClient.invalidateQueries({ queryKey: ["skill", slug] });
      toast.success("Review submitted successfully!");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to submit review");
    },
  });
}

export function useDownloadSkill() {
  return useMutation({
    mutationFn: ({ slug, version }: { slug: string; version?: string }) =>
      api.skills.download(slug, version),
    onSuccess: (blob, variables) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${variables.slug}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("Download started!");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to download skill");
    },
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: () => api.categories.list(),
    staleTime: 10 * 60 * 1000,
  });
}

export function useCategoryTree() {
  return useQuery({
    queryKey: ["categories", "tree"],
    queryFn: () => api.categories.tree(),
    placeholderData: (previousData) => previousData,
    staleTime: 10 * 60 * 1000,
  });
}

export function useCategory(slug: string) {
  return useQuery({
    queryKey: ["category", slug],
    queryFn: () => api.categories.get(slug),
    enabled: !!slug,
    placeholderData: (previousData) => previousData,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCategorySkills(slug: string, params?: Partial<SearchParams>) {
  return useQuery({
    queryKey: ["category", slug, "skills", params],
    queryFn: () => api.categories.getSkills(slug, params),
    enabled: !!slug,
    placeholderData: (previousData) => previousData,
  });
}

export function useCompositions(params?: Partial<SearchParams>) {
  return useQuery({
    queryKey: ["compositions", params],
    queryFn: () => api.compositions.list(params),
    placeholderData: (previousData) => previousData,
    staleTime: 2 * 60 * 1000,
  });
}

export function useComposition(slug: string) {
  return useQuery({
    queryKey: ["composition", slug],
    queryFn: () => api.compositions.get(slug),
    enabled: !!slug,
  });
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: () => api.dashboard.stats(),
    staleTime: 2 * 60 * 1000,
  });
}

export function useUsageTrends(days = 30) {
  return useQuery({
    queryKey: ["dashboard", "usage-trends", days],
    queryFn: () => api.dashboard.usageTrends(days),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCategoryDistribution() {
  return useQuery({
    queryKey: ["dashboard", "category-distribution"],
    queryFn: () => api.dashboard.categoryDistribution(),
    staleTime: 10 * 60 * 1000,
  });
}

export function usePopularSkills(limit = 10) {
  return useQuery({
    queryKey: ["dashboard", "popular-skills", limit],
    queryFn: () => api.dashboard.popularSkills(limit),
    staleTime: 3 * 60 * 1000,
  });
}