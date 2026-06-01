"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Home, ChevronRight, Folder, AlertTriangle, Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { SkillCard } from "@/components/SkillCard";
import { useCategory, useCategorySkills } from "@/hooks/useSkills";
import { useDebounce } from "@/hooks/useSearch";
import { useI18n } from "@/lib/i18n";

export default function CategoryDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { t } = useI18n();
  const { data: category, isLoading: categoryLoading } = useCategory(slug);
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearch = useDebounce(searchQuery, 400);

  const { data: skillsData, isLoading: skillsLoading } = useCategorySkills(slug, {
    q: debouncedSearch || undefined,
    page_size: 24,
  });

  if (categoryLoading) {
    return (
      <div className="container mx-auto px-4 py-6 sm:py-8">
        <Skeleton className="h-5 w-40 mb-4" />
        <div className="flex items-center gap-3 mb-6">
          <Skeleton className="h-12 w-12 rounded-xl shrink-0" />
          <div className="space-y-2">
            <Skeleton className="h-7 w-56 sm:w-72" />
            <Skeleton className="h-4 w-full max-w-[300px]" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-[200px] rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (!category) {
    return (
      <div className="container mx-auto px-4 py-16 sm:py-20 text-center">
        <AlertTriangle className="h-12 w-12 sm:h-16 sm:w-16 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl sm:text-2xl font-bold mb-2">{t("category.notFound")}</h2>
        <p className="text-sm sm:text-base text-muted-foreground mb-4 max-w-md mx-auto">
          {t("category.notFoundDesc")}
        </p>
        <Link href="/categories">
          <Button>{t("category.browseCategories")}</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 sm:py-8">
      <nav className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-muted-foreground mb-4 sm:mb-6 overflow-x-auto pb-2 scrollbar-none -mx-4 px-4 sm:mx-0 sm:px-0">
        <Link href="/" className="hover:text-foreground transition-colors shrink-0 flex items-center">
          <Home className="h-3.5 w-3.5" />
        </Link>
        <ChevronRight className="h-3 w-3 sm:h-3.5 sm:w-3.5 shrink-0" />
        <Link href="/categories" className="hover:text-foreground transition-colors shrink-0 truncate">
          {t("common.categories")}
        </Link>
        <ChevronRight className="h-3 w-3 sm:h-3.5 sm:w-3.5 shrink-0" />
        <span className="text-foreground font-medium truncate">{category.name}</span>
      </nav>

      <div className="mb-6 sm:mb-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 mb-4">
          <div className="flex h-12 w-12 sm:h-14 sm:w-14 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-indigo-500/20 shrink-0">
            <Folder className="h-6 w-6 sm:h-7 sm:w-7 text-violet-500" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl md:text-3xl font-bold leading-tight">{category.name}</h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-0.5 sm:mt-1 line-clamp-2">
              {category.description}
            </p>
          </div>
        </div>

        {category.children && category.children.length > 0 && (
          <div className="mt-4">
            <h3 className="text-xs sm:text-sm font-semibold mb-2 sm:mb-3">{t("category.subcategories")}</h3>
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0 sm:flex-wrap">
              {category.children.map((child) => (
                <Link key={child.id} href={`/categories/${child.slug}`}>
                  <Badge
                    variant="outline"
                    className="hover:bg-accent cursor-pointer whitespace-nowrap text-xs"
                  >
                    {child.name} ({child.skill_count})
                  </Badge>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="mb-6 relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="search"
          placeholder={`${t("category.searchPlaceholder")} ${category.name}`}
          className="pl-10 pr-10 h-11 md:h-12"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
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

      {skillsLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-[220px] rounded-xl" />
          ))}
        </div>
      ) : skillsData && skillsData.items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {skillsData.items.map((skill) => (
            <SkillCard key={skill.id} skill={skill} />
          ))}
        </div>
      ) : (
        <div className="text-center py-14 sm:py-20 px-4">
          <Folder className="h-10 w-10 sm:h-12 sm:w-12 text-muted-foreground mx-auto mb-3 sm:mb-4" />
          <h3 className="text-base sm:text-lg font-semibold mb-2">{t("category.noSkills")}</h3>
          <p className="text-xs sm:text-sm text-muted-foreground max-w-md mx-auto">
            {debouncedSearch
              ? t("category.noSkillsSearch")
              : t("category.noSkillsEmpty")}
          </p>
        </div>
      )}
    </div>
  );
}
