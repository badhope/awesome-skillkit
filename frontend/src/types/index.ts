export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  avatar_url: string | null;
  bio: string | null;
  role: "user" | "moderator" | "admin";
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon: string | null;
  parent_id: string | null;
  children: Category[];
  skill_count: number;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  color: string | null;
  usage_count: number;
}

export interface SkillVersion {
  id: string;
  skill_id: string;
  version: string;
  changelog: string;
  metadata: Record<string, unknown>;
  is_latest: boolean;
  download_url: string | null;
  created_at: string;
  created_by: User | null;
}

export interface SkillDependency {
  id: string;
  skill_id: string;
  dependency_skill_id: string;
  dependency_skill?: Skill;
  version_constraint: string | null;
  is_optional: boolean;
  created_at: string;
}

export interface SkillMetric {
  id: string;
  skill_id: string;
  downloads_count: number;
  views_count: number;
  uses_count: number;
  likes_count: number;
  average_rating: number;
  ratings_count: number;
  updated_at: string;
}

export interface SkillReview {
  id: string;
  skill_id: string;
  user_id: string;
  user?: User;
  rating: number;
  title: string;
  content: string;
  pros: string | null;
  cons: string | null;
  created_at: string;
  updated_at: string;
}

export interface Skill {
  id: string;
  name: string;
  slug: string;
  description: string;
  long_description: string | null;
  category_id: string;
  category?: Category;
  author_id: string;
  author?: User;
  icon_url: string | null;
  banner_url: string | null;
  status: "draft" | "published" | "deprecated" | "archived";
  visibility: "public" | "private" | "unlisted";
  version: string;
  license: string | null;
  homepage_url: string | null;
  repository_url: string | null;
  documentation_url: string | null;
  tags: Tag[];
  versions: SkillVersion[];
  dependencies: SkillDependency[];
  metrics: SkillMetric | null;
  embedding: number[] | null;
  created_at: string;
  updated_at: string;
}

export interface CompositionNode {
  id: string;
  skill_id: string;
  skill?: Skill;
  position_x: number;
  position_y: number;
  config: Record<string, unknown>;
  input_mapping: Record<string, string>;
  output_mapping: Record<string, string>;
}

export interface CompositionEdge {
  id: string;
  source_node_id: string;
  target_node_id: string;
  source_output: string;
  target_input: string;
  condition: Record<string, unknown> | null;
  label: string | null;
}

export interface Composition {
  id: string;
  name: string;
  slug: string;
  description: string;
  author_id: string;
  author?: User;
  status: "draft" | "published" | "archived";
  visibility: "public" | "private" | "unlisted";
  nodes: CompositionNode[];
  edges: CompositionEdge[];
  input_schema: Record<string, unknown> | null;
  output_schema: Record<string, unknown> | null;
  tags: Tag[];
  metrics: SkillMetric | null;
  created_at: string;
  updated_at: string;
}

export interface UsageRecord {
  id: string;
  user_id: string;
  skill_id: string;
  skill?: Skill;
  input_params: Record<string, unknown> | null;
  output_result: Record<string, unknown> | null;
  duration_ms: number | null;
  status: "success" | "failed" | "running" | "pending";
  created_at: string;
}

export interface DashboardStats {
  total_skills: number;
  total_compositions: number;
  total_users: number;
  total_downloads: number;
  skills_published_today: number;
  active_users_today: number;
}

export interface UsageTrend {
  date: string;
  count: number;
  downloads: number;
  views: number;
}

export interface CategoryDistribution {
  category_name: string;
  skill_count: number;
  percentage: number;
}

export interface PopularSkill {
  skill: Skill;
  use_count: number;
  rating: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, string[]>;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  password_confirm: string;
  full_name: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

export interface SearchParams {
  q: string;
  category?: string;
  tags?: string[];
  status?: string;
  sort?: "relevance" | "rating" | "downloads" | "newest" | "updated";
  page?: number;
  page_size?: number;
}

export interface SkillCreateRequest {
  name: string;
  description: string;
  long_description?: string;
  category_id: string;
  tags?: string[];
  license?: string;
  homepage_url?: string;
  repository_url?: string;
  documentation_url?: string;
  visibility?: "public" | "private" | "unlisted";
}

export interface SkillUpdateRequest {
  name?: string;
  description?: string;
  long_description?: string;
  category_id?: string;
  tags?: string[];
  license?: string;
  homepage_url?: string;
  repository_url?: string;
  documentation_url?: string;
  visibility?: "public" | "private" | "unlisted";
  status?: "draft" | "published" | "deprecated" | "archived";
}

export interface ReviewCreateRequest {
  rating: number;
  title: string;
  content: string;
  pros?: string;
  cons?: string;
}

export interface CompositionCreateRequest {
  name: string;
  description: string;
  nodes: Omit<CompositionNode, "id">[];
  edges: Omit<CompositionEdge, "id">[];
  tags?: string[];
  visibility?: "public" | "private" | "unlisted";
}