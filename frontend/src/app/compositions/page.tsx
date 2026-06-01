"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Search,
  GitBranch,
  ArrowUpDown,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
  X,
  Grid3X3,
  List,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import { useCompositions } from "@/hooks/useSkills";
import { useDebounce } from "@/hooks/useSearch";
import { formatDate, getInitials, cn } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";
import type { Composition } from "@/types";

const sortOptions = [
  { value: "newest", label: "" },
  { value: "updated", label: "" },
  { value: "downloads", label: "" },
  { value: "rating", label: "" },
];

export default function CompositionsPage() {
  const { t } = useI18n();
  const [searchQuery, setSearchQuery] = useState("");
  const [sort, setSort] = useState("newest");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"grid" | "list">("list");
  const debouncedSearch = useDebounce(searchQuery, 400);

  const sortOptionsLocalized = [
    { value: "newest", label: t("composition.sortOptions.newest") },
    { value: "updated", label: t("composition.sortOptions.updated") },
    { value: "downloads", label: t("composition.sortOptions.mostUsed") },
    { value: "rating", label: t("composition.sortOptions.highestRated") },
  ];

  const { data, isLoading } = useCompositions({
    q: debouncedSearch || undefined,
    sort: sort as "newest" | "updated" | "downloads" | "rating",
    page,
    page_size: 12,
  });

  return (
    <div className="container mx-auto px-4 py-6 sm:py-8">
      <div className="mb-6 sm:mb-8">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight mb-1 sm:mb-2">
              {t("composition.title")}
            </h1>
            <p className="text-sm sm:text-base text-muted-foreground">
              {t("composition.subtitle")}
              {data?.total !== undefined && (
                <span className="ml-1 text-xs sm:text-sm font-medium">
                  ({data.total.toLocaleString()} {t("composition.total")})
                </span>
              )}
            </p>
          </div>
          <div className="flex items-center gap-1 shrink-0">
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

      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder={t("composition.searchPlaceholder")}
            className="pl-10 pr-10 h-11 md:h-12"
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

        <div className="relative min-w-[130px] sm:min-w-[160px]">
          <select
            value={sort}
            onChange={(e) => {
              setSort(e.target.value);
              setPage(1);
            }}
            className="h-11 md:h-12 w-full rounded-lg border border-input bg-background px-3 py-2 text-xs sm:text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring appearance-none pr-8"
          >
            {sortOptionsLocalized.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <ArrowUpDown className="absolute right-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground pointer-events-none" />
        </div>
      </div>

      {isLoading ? (
        <div className={cn(
          "grid gap-3 sm:gap-4",
          viewMode === "list" ? "grid-cols-1" : "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
        )}>
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className={cn(viewMode === "list" ? "h-[180px]" : "h-[240px]", "rounded-xl")} />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className={cn(
            "grid gap-3 sm:gap-4",
            viewMode === "list" ? "grid-cols-1" : "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
          )}>
            {data.items.map((composition: Composition) => (
              <Link
                key={composition.id}
                href={`/compositions/${composition.slug}`}
                className="group"
              >
                <Card
                  className={cn(
                    "h-full transition-all duration-300 hover:border-primary/50 hover:shadow-lg hover:-translate-y-1 rounded-xl",
                    viewMode === "list" && "sm:flex-row sm:items-center"
                  )}
                >
                  <CardHeader className={cn(
                    "pb-3",
                    viewMode === "list" && "sm:p-4 sm:pb-0 sm:w-[200px] shrink-0"
                  )}>
                    <div className="flex items-start gap-2 sm:gap-3">
                      <div className="flex h-9 w-9 sm:h-10 sm:w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 group-hover:from-emerald-500/30 group-hover:to-teal-500/30 transition-colors">
                        <GitBranch className="h-4 w-4 sm:h-5 sm:w-5 text-emerald-500" />
                      </div>
                      <div className={cn(
                        "min-w-0",
                        viewMode === "list" && "sm:hidden"
                      )}>
                        <CardTitle className="text-sm truncate group-hover:text-primary transition-colors leading-snug">
                          {composition.name}
                        </CardTitle>
                        <CardDescription className="text-xs mt-0.5">
                          {composition.items.length} {t("composition.skills")}
                        </CardDescription>
                      </div>
                      {viewMode === "list" && (
                        <div className="hidden sm:block min-w-0">
                          <p className="font-medium text-sm truncate group-hover:text-primary transition-colors leading-snug">
                            {composition.name}
                          </p>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {composition.items.length} {t("composition.skills")}
                          </p>
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent
                    className={cn(
                      "space-y-3",
                      viewMode === "list" && "sm:p-4 sm:pt-0 sm:flex-1"
                    )}
                  >
                    <p
                      className={cn(
                        "text-xs sm:text-sm text-muted-foreground line-clamp-2 leading-relaxed",
                        viewMode === "list" && "sm:line-clamp-1 hidden xs:block"
                      )}
                    >
                      {composition.description}
                    </p>

                    <div className="flex flex-wrap items-center gap-1.5">
                      <Badge
                        variant={composition.is_public ? "success" : "secondary"}
                        className="text-xs"
                      >
                        {composition.is_public ? "Public" : "Private"}
                      </Badge>
                    </div>

                    <div className={cn(
                      "flex items-center justify-between pt-2 border-t text-xs text-muted-foreground",
                      viewMode === "list" && "sm:pt-0 sm:border-l sm:pl-4 sm:border-t-0"
                    )}>
                      <div className="flex items-center gap-2">
                        {composition.owner && (
                          <>
                            <Avatar className="h-5 w-5 sm:h-6 sm:w-6">
                              <AvatarImage src={composition.owner.avatar_url || undefined} />
                              <AvatarFallback className="text-[8px] xs:text-[10px]">
                                {getInitials(
                                  composition.owner.full_name || composition.owner.username
                                )}
                              </AvatarFallback>
                            </Avatar>
                            <span className="hidden xs:inline">@{composition.owner.username}</span>
                          </>
                        )}
                      </div>
                      <span>{formatDate(composition.updated_at, "relative")}</span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
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
                <ChevronLeft className="h-4 w-4 sm:hidden" />
              </Button>

              <div className="hidden sm:flex items-center gap-1">
                {Array.from({ length: data.total_pages }, (_, i) => i + 1)
                  .filter((p) => p === 1 || p === data.total_pages || Math.abs(p - page) <= 1)
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
                <ChevronRight className="h-4 w-4 ml-1 hidden sm:inline-block" />
                <ChevronRight className="h-4 w-4 sm:hidden" />
              </Button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-16 sm:py-20 px-4">
          <div className="flex h-14 w-14 sm:h-16 sm:w-16 items-center justify-center rounded-2xl bg-muted mx-auto mb-4">
            <GitBranch className="h-7 w-7 sm:h-8 sm:w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg sm:text-xl font-semibold mb-2">{t("composition.noResults")}</h3>
          <p className="text-sm sm:text-base text-muted-foreground mb-4 max-w-md mx-auto leading-relaxed">
            {debouncedSearch ? t("composition.noResultsSearch") : t("composition.noResultsEmpty")}
          </p>
          <Link href="/compositions/new">
            <Button variant="gradient" className="text-sm sm:text-base">
              <Sparkles className="mr-2 h-4 w-4" />
              {t("composition.createFirst")}
            </Button>
          </Link>
        </div>
      )}
    </div>
  );
}
