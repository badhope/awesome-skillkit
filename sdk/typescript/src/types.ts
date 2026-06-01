export interface SkillDict {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  version: string;
  complexity: string | null;
  status: string | null;
  license: string | null;
  source_url: string | null;
  is_public: boolean;
  is_featured: boolean;
  download_count: number;
  view_count: number;
  usage_count: number;
  rating_avg: number;
  rating_count: number;
  content: Record<string, unknown>;
  metadata: Record<string, unknown>;
  category: CategoryDict | null;
  tags: TagDict[];
  author: UserBriefDict | null;
  created_at: string;
  updated_at: string;
  versions?: SkillVersionDict[];
  dependencies?: SkillDependencyDict[];
}

export interface SkillBriefDict {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  version: string;
  complexity: string | null;
  rating_avg: number;
  rating_count: number;
  download_count: number;
  created_at: string;
}

export interface CategoryDict {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  sort_order: number;
  parent_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  skill_count?: number;
  children?: CategoryDict[];
}

export interface TagDict {
  id: string;
  name: string;
  color: string | null;
  description: string | null;
  usage_count: number;
  created_at: string;
}

export interface SkillVersionDict {
  id: string;
  version: string;
  changelog: string | null;
  created_at: string;
  created_by: UserBriefDict | null;
}

export interface SkillDependencyDict {
  id: string;
  depends_on_skill_id: string;
  version_constraint: string | null;
  depends_on_skill: SkillBriefDict;
  created_at: string;
}

export interface UserBriefDict {
  id: string;
  username: string;
  full_name: string | null;
  avatar_url: string | null;
}

export interface UserDict {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenDict {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface SkillSearchResultDict {
  skill_id: string;
  name: string;
  description: string | null;
  score: number;
  category_id: string | null;
  tags: string[];
  version: string;
  author: string | null;
  usage_count: number;
  rating: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface AnalyticsDashboardDict {
  stats: DashboardStatsDict;
  popular_skills: PopularSkillDict[];
  trending_tags: TrendingTagDict[];
}

export interface DashboardStatsDict {
  total_skills: number;
  total_users: number;
  total_categories: number;
  total_usage: number;
  total_downloads: number;
  total_ratings: number;
  avg_rating: number;
}

export interface PopularSkillDict {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  download_count: number;
  usage_count: number;
  rating_avg: number;
  rating_count: number;
  category_name: string | null;
}

export interface TrendingTagDict {
  name: string;
  usage_count: number;
  recent_usage: number;
}

export interface SkillUsageTrendDict {
  date: string;
  count: number;
}

export interface SkillUsageTrendResponse {
  trend: SkillUsageTrendDict[];
  period: string;
}

export interface CompositionDict {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  is_public: boolean;
  metadata: Record<string, unknown>;
  owner: UserBriefDict | null;
  created_at: string;
  updated_at: string;
  items?: CompositionItemDict[];
}

export interface CompositionItemDict {
  id: string;
  sort_order: number;
  notes: string | null;
  skill: SkillBriefDict | null;
  created_at: string;
}

export interface SkillRatingResponse {
  id: string;
  rating: number;
  comment: string | null;
  user: UserBriefDict;
  created_at: string;
  updated_at: string;
}

export interface SkillSimilarDict {
  skill_id: string;
  name: string;
  description: string | null;
  score: number;
  tags: string[];
  version: string;
  author: string | null;
  rating: number;
}

export interface SkillUsageResponse {
  id: string;
  skill_id: string;
  user_id: string | null;
  action: string;
  created_at: string;
}

export interface ClientConfig {
  baseUrl: string;
  apiKey?: string;
  timeout?: number;
  maxRetries?: number;
  retryDelay?: number;
}