"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Search,
  SlidersHorizontal,
  ArrowUpDown,
  X,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Grid3X3,
  List,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { SkillCard } from "@/components/SkillCard";
import { CategoryFilter } from "@/components/CategoryFilter";
import { Skeleton } from "@/components/ui/skeleton";
import { useSkills, useCategoryTree } from "@/hooks/useSkills";
import { useDebounce } from "@/hooks/useSearch";
import { cn } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";
import type { SearchParams as SearchParamsType } from "@/types";

const popularTags = [
  "NLP", "Computer Vision", "LLM", "Embeddings", "Classification",
  "Translation", "Summarization", "OCR", "Speech", "Generation",
];

function SkillsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { t } = useI18n();

  const [searchQuery, setSearchQuery] = useState(searchParams.get("q") || "");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(
    searchParams.get("category") || null
  );
  const [selectedTags, setSelectedTags] = useState<string[]>(
    searchParams.get("tags")?.split(",").filter(Boolean) || []
  );
  const [sort, setSort] = useState<string>(searchParams.get("sort") || "relevance");
  const [page, setPage] = useState(Number(searchParams.get("page")) || 1);
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  const debouncedSearch = useDebounce(searchQuery, 400);

  const queryParams: Partial<SearchParamsType> = {
    q: debouncedSearch || undefined,
    category: selectedCategory || undefined,
    tags: selectedTags.length > 0 ? selectedTags : undefined,
    sort: sort as SearchParamsType["sort"],
    page,
    page_size: 12,
  };

  const { data, isLoading } = useSkills(queryParams);
  const { data: categoryTree } = useCategoryTree();

  const updateURL = () => {
    const params = new URLSearchParams();
    if (debouncedSearch) params.set("q", debouncedSearch);
    if (selectedCategory) params.set("category", selectedCategory);
    if (selectedTags.length > 0) params.set("tags", selectedTags.join(","));
    if (sort !== "relevance") params.set("sort", sort);
    if (page > 1) params.set("page", page.toString());
    const query = params.toString();
    router.push(`/skills${query ? `?${query}` : ""}`, { scroll: false });
  };

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
    setPage(1);
  };

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedCategory(null);
    setSelectedTags([]);
    setSort("relevance");
    setPage(1);
  };

  const hasFilters =
    debouncedSearch || selectedCategory || selectedTags.length > 0 || sort !== "relevance";

  const sortOptions = [
    { value: "relevance", label: t("skills.sortOptions.relevance") },
    { value: "rating", label: t("skills.sortOptions.rating") },
    { value: "downloads", label: t("skills.sortOptions.downloads") },
    { value: "newest", label: t("skills.sortOptions.newest") },
    { value: "updated", label: t("skills.sortOptions.updated") },
  ];

  return (
    <div className="container mx-auto px-4 py-6 sm:py-8">
      <div className="mb-6 sm:mb-8">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight mb-1 sm:mb-2">
              {t("skills.title")}
            </h1>
            <p className="text-sm sm:text-base text-muted-foreground">
              {t("skills.subtitle")}
              {data?.total !== undefined && (
                <span className="ml-1 text-xs sm:text-sm font-medium">
                  ({data.total.toLocaleString()} {t("skills.total")})
                </span>
              )}
            </p>
          </div>
          <div className="hidden lg:flex items-center gap-1 shrink-0">
            <Button
              variant={viewMode === "grid" ? "secondary" : "ghost"}
              size="icon-sm"
              onClick={() => setViewMode("grid")}
            >
              <Grid3X3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === "list" ? "secondary" : "ghost"}
              size="icon-sm"
              onClick={() => setViewMode("list")}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6 lg:gap-8">
        <aside className="hidden lg:block w-64 shrink-0">
          <div className="sticky top-20 space-y-6">
            {categoryTree && (
              <CategoryFilter
                categories={categoryTree}
                selectedCategory={selectedCategory}
                onSelect={setSelectedCategory}
              />
            )}

            <div>
              <h3 className="font-semibold text-sm mb-3">{t("skills.popularTags")}</h3>
              <div className="flex flex-wrap gap-2">
                {popularTags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => toggleTag(tag)}
                    className={cn(
                      "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors border",
                      selectedTags.includes(tag)
                        ? "bg-primary text-primary-foreground border-primary"
                        : "text-muted-foreground border-muted-foreground/20 hover:bg-accent hover:text-foreground"
                    )}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>

            {hasFilters && (
              <Button variant="outline" size="sm" className="w-full" onClick={clearFilters}>
                {t("skills.clearFilters")}
              </Button>
            )}
          </div>
        </aside>

        <div className="flex-1 min-w-0 space-y-4">
          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder={t("skills.searchPlaceholder")}
                  className="pl-10 h-11 md:h-12"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setPage(1);
                  }}
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery("")}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground p-1"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                  className="lg:hidden h-11 md:h-12"
                >
                  <SlidersHorizontal className="h-4 w-4 mr-2" />
                  {t("skills.filters")}
                </Button>

                <div className="relative min-w-[120px] sm:min-w-[140px]">
                  <select
                    value={sort}
                    onChange={(e) => {
                      setSort(e.target.value);
                      setPage(1);
                    }}
                    className="h-11 md:h-12 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring appearance-none pr-8"
                  >
                    {sortOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  <ArrowUpDown className="absolute right-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground pointer-events-none" />
                </div>
              </div>
            </div>

            {selectedTags.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
                <span className="text-xs sm:text-sm text-muted-foreground shrink-0">{t("skills.tags")}:</span>
                {selectedTags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="gap-1 shrink-0">
                    {tag}
                    <button onClick={() => toggleTag(tag)}>
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
                <button
                  onClick={() => setSelectedTags([])}
                  className="text-xs text-primary hover:text-primary/80 shrink-0 whitespace-nowrap"
                >
                  {t("common.clearAll")}
                </button>
              </div>
            )}

            {showFilters && (
              <div className="lg:hidden p-4 border rounded-xl bg-card space-y-4 animate-in slide-in-from-top-2 duration-200">
                {categoryTree && (
                  <CategoryFilter
                    categories={categoryTree}
                    selectedCategory={selectedCategory}
                    onSelect={setSelectedCategory}
                  />
                )}
                <div>
                  <h3 className="font-semibold text-sm mb-3">{t("skills.popularTags")}</h3>
                  <div className="flex flex-wrap gap-2">
                    {popularTags.map((tag) => (
                      <button
                        key={tag}
                        onClick={() => toggleTag(tag)}
                        className={cn(
                          "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors border",
                          selectedTags.includes(tag)
                            ? "bg-primary text-primary-foreground border-primary"
                            : "text-muted-foreground border-muted-foreground/20 hover:bg-accent hover:text-foreground"
                        )}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>
                {hasFilters && (
                  <Button variant="outline" size="sm" className="w-full" onClick={clearFilters}>
                    {t("skills.clearFilters")}
                  </Button>
                )}
              </div>
            )}
          </div>

          {isLoading ? (
            <div className={cn(
              "grid gap-3 sm:gap-4",
              viewMode === "list" ? "grid-cols-1" : "grid-cols-1 md:grid-cols-2 xl:grid-cols-3"
            )}>
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className={cn(viewMode === "list" ? "h-[180px]" : "h-[240px]", "rounded-xl")} />
              ))}
            </div>
          ) : data && data.items.length > 0 ? (
            <>
              <div className={cn(
                "grid gap-3 sm:gap-4",
                viewMode === "list" ? "grid-cols-1" : "grid-cols-1 md:grid-cols-2 xl:grid-cols-3"
              )}>
                {data.items.map((skill) => (
                  <SkillCard key={skill.id} skill={skill} />
                ))}
              </div>

              {data.total_pages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-6 sm:mt-8">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    className="h-9 px-3"
                  >
                    <ChevronLeft className="h-4 w-4 mr-1 hidden xs:inline-block" />
                    <span className="hidden sm:inline">{t("common.previous")}</span>
                    <ChevronLeft className="h-4 w-4 sm:hidden" />
                  </Button>

                  <div className="hidden sm:flex items-center gap-1">
                    {Array.from({ length: data.total_pages }, (_, i) => i + 1)
                      .filter(
                        (p) =>
                          p === 1 ||
                          p === data.total_pages ||
                          Math.abs(p - page) <= 1
                      )
                      .map((p, index, arr) => (
                        <div key={p} className="flex items-center">
                          {index > 0 && arr[index - 1] !== p - 1 && (
                            <span className="px-1 text-muted-foreground">...</span>
                          )}
                          <Button
                            variant={p === page ? "default" : "ghost"}
                            size="sm"
                            onClick={() => setPage(p)}
                            className="w-9 h-9"
                          >
                            {p}
                          </Button>
                        </div>
                      ))}
                  </div>

                  <div className="sm:hidden text-xs text-muted-foreground">
                    {page} / {data.total_pages}
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= data.total_pages}
                    onClick={() => setPage((p) => p + 1)}
                    className="h-9 px-3"
                  >
                    <span className="hidden sm:inline">{t("common.next")}</span>
                    <ChevronRight className="h-4 w-4 ml-1 hidden sm:inline-block" />
                    <ChevronRight className="h-4 w-4 sm:hidden" />
                  </Button>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-16 sm:py-20 px-4">
              <div className="flex h-14 w-14 sm:h-16 sm:w-16 items-center justify-center rounded-2xl bg-muted mx-auto mb-4">
                <Sparkles className="h-7 w-7 sm:h-8 sm:w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg sm:text-xl font-semibold mb-2">{t("skills.noResults")}</h3>
              <p className="text-sm sm:text-base text-muted-foreground mb-4 max-w-md mx-auto">
                {hasFilters ? t("skills.noResultsHint") : t("skills.noResultsEmpty")}
              </p>
              {hasFilters && (
                <Button variant="outline" onClick={clearFilters}>
                  {t("skills.clearFilters")}
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function SkillsPage() {
  const { t } = useI18n();

  return (
    <Suspense
      fallback={
        <div className="container mx-auto px-4 py-6 sm:py-8">
          <div className="mb-6 sm:mb-8">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight mb-1 sm:mb-2">
              {t("skills.title")}
            </h1>
            <p className="text-sm sm:text-base text-muted-foreground">{t("common.loading")}</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-[240px] rounded-xl" />
            ))}
          </div>
        </div>
      }
    >
      <SkillsContent />
    </Suspense>
  );
}
