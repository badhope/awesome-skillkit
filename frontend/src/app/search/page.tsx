"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Search, Sparkles, X, ArrowUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SkillCard } from "@/components/SkillCard";
import { Skeleton } from "@/components/ui/skeleton";
import { useSearchSkills } from "@/hooks/useSkills";
import { useDebounce } from "@/hooks/useSearch";
import { useI18n } from "@/lib/i18n";

function SearchContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { t } = useI18n();
  const initialQuery = searchParams.get("q") || "";

  const [query, setQuery] = useState(initialQuery);
  const [sort, setSort] = useState<string>("relevance");
  const debouncedQuery = useDebounce(query, 400);

  const { data, isLoading } = useSearchSkills({
    q: debouncedQuery,
    sort: sort as "relevance" | "rating" | "downloads" | "newest" | "updated",
    page_size: 24,
  });

  useEffect(() => {
    if (debouncedQuery) {
      const params = new URLSearchParams();
      params.set("q", debouncedQuery);
      if (sort !== "relevance") params.set("sort", sort);
      router.push(`/search?${params.toString()}`, { scroll: false });
    }
  }, [debouncedQuery, sort, router]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const sortOptions = [
    { value: "relevance", label: t("search.sortOptions.relevance") },
    { value: "rating", label: t("search.sortOptions.rating") },
    { value: "downloads", label: t("search.sortOptions.downloads") },
    { value: "newest", label: t("search.sortOptions.newest") },
  ];

  return (
    <div className="container mx-auto px-4 py-6 sm:py-8">
      <div className="max-w-2xl mx-auto mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-center mb-2">
          {t("search.title")}
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground text-center mb-5 sm:mb-6">
          {t("search.subtitle")}
        </p>

        <form onSubmit={handleSubmit} className="relative mb-4">
          <Search className="absolute left-3.5 sm:left-4 top-1/2 -translate-y-1/2 h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground" />
          <Input
            type="search"
            placeholder={t("search.placeholder")}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-10 sm:pl-12 pr-11 sm:pr-12 h-12 sm:h-14 text-sm sm:text-lg rounded-xl border-2 border-muted-foreground/20 focus-visible:border-primary/50 shadow-sm"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery("")}
              className="absolute right-3.5 sm:right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground p-1"
            >
              <X className="h-4 w-4 sm:h-5 sm:w-5" />
            </button>
          )}
        </form>

        <div className="flex items-center justify-center gap-2">
          <div className="relative min-w-[130px] sm:min-w-[160px]">
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              className="h-9 sm:h-10 w-full rounded-lg border border-input bg-background px-3 py-1.5 sm:py-2 text-xs sm:text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring appearance-none pr-8"
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

      {!debouncedQuery ? (
        <div className="text-center py-16 sm:py-20 px-4">
          <div className="flex h-16 w-16 sm:h-20 sm:w-20 items-center justify-center rounded-2xl bg-muted mx-auto mb-4">
            <Search className="h-8 w-8 sm:h-10 sm:w-10 text-muted-foreground" />
          </div>
          <h2 className="text-lg sm:text-xl font-semibold mb-2">{t("search.searchForSkills")}</h2>
          <p className="text-sm sm:text-base text-muted-foreground max-w-md mx-auto leading-relaxed">
            {t("search.emptyDesc")}
          </p>
        </div>
      ) : isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {Array.from({ length: 9 }).map((_, i) => (
            <Skeleton key={i} className="h-[220px] sm:h-[240px] rounded-xl" />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <div>
          <p className="text-sm sm:text-base text-muted-foreground mb-4 sm:mb-6 px-1">
            {`${t("search.found")} ${data.total} "${debouncedQuery}"`}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
            {data.items.map((skill) => (
              <SkillCard key={skill.id} skill={skill} />
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-16 sm:py-20 px-4">
          <Sparkles className="h-10 w-10 sm:h-12 sm:w-12 text-muted-foreground mx-auto mb-3 sm:mb-4" />
          <h2 className="text-lg sm:text-xl font-semibold mb-2">{t("search.noResults")}</h2>
          <p className="text-sm sm:text-base text-muted-foreground mb-4 max-w-lg mx-auto leading-relaxed">
            {`${t("search.noResultsDesc")} "${debouncedQuery}"`}
          </p>
          <Button variant="outline" onClick={() => setQuery("")}>
            {t("search.clearSearch")}
          </Button>
        </div>
      )}
    </div>
  );
}

export default function SearchPage() {
  const { t } = useI18n();

  return (
    <Suspense
      fallback={
        <div className="container mx-auto px-4 py-6 sm:py-8">
          <div className="max-w-2xl mx-auto mb-8">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-center mb-2">
              {t("search.title")}
            </h1>
            <p className="text-sm sm:text-base text-muted-foreground text-center mb-6">
              {t("search.loading")}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-[240px] rounded-xl" />
            ))}
          </div>
        </div>
      }
    >
      <SearchContent />
    </Suspense>
  );
}
