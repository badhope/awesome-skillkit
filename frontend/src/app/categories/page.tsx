"use client";

import Link from "next/link";
import { useState } from "react";
import { Sparkles, Folder, ArrowRight, Search, X } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useCategories } from "@/hooks/useSkills";
import { useDebounce } from "@/hooks/useSearch";
import { useI18n } from "@/lib/i18n";

export default function CategoriesPage() {
  const { t } = useI18n();
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearch = useDebounce(searchQuery, 300);
  const { data: categories, isLoading } = useCategories();

  const filteredCategories = categories?.filter(
    (cat) =>
      cat.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
      cat.description.toLowerCase().includes(debouncedSearch.toLowerCase())
  );

  return (
    <div className="container mx-auto px-4 py-6 sm:py-8">
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight mb-1 sm:mb-2">
          {t("category.title")}
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground">
          {t("category.subtitle")}
        </p>
      </div>

      <div className="mb-6 relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="search"
          placeholder={t("common.search")}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 pr-10 h-11 md:h-12"
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

      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4">
          {Array.from({ length: 10 }).map((_, i) => (
            <Skeleton key={i} className="h-[160px] sm:h-[180px] rounded-xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4">
          {filteredCategories?.map((category) => (
            <Link key={category.id} href={`/categories/${category.slug}`} className="group">
              <Card className="h-full transition-all duration-300 hover:border-primary/50 hover:shadow-lg hover:-translate-y-1 rounded-xl">
                <CardContent className="p-3 sm:p-4 md:p-6">
                  <div className="flex items-start justify-between mb-3 sm:mb-4">
                    <div className="flex h-10 w-10 sm:h-12 sm:w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-indigo-500/20 group-hover:from-violet-500/30 group-hover:to-indigo-500/30 transition-colors shrink-0">
                      <Folder className="h-5 w-5 sm:h-6 sm:w-6 text-violet-500" />
                    </div>
                    <Badge variant="secondary" className="text-xs shrink-0">
                      {category.skill_count} {t("category.skills")}
                    </Badge>
                  </div>

                  <h3 className="font-semibold text-sm sm:text-base mb-1 group-hover:text-primary transition-colors line-clamp-1 leading-snug">
                    {category.name}
                  </h3>
                  <p className="text-xs sm:text-sm text-muted-foreground line-clamp-2 mb-3 hidden xs:block leading-relaxed">
                    {category.description}
                  </p>

                  {category.children && category.children.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3 hidden sm:flex">
                      {category.children.slice(0, 3).map((child) => (
                        <Badge key={child.id} variant="outline" className="text-[10px] xs:text-xs">
                          {child.name}
                        </Badge>
                      ))}
                      {category.children.length > 3 && (
                        <Badge variant="outline" className="text-[10px] xs:text-xs">
                          +{category.children.length - 3}
                        </Badge>
                      )}
                    </div>
                  )}

                  <div className="flex items-center gap-1 text-xs sm:text-sm text-primary opacity-0 group-hover:opacity-100 transition-opacity font-medium">
                    {t("hero.categories.browse")} <ArrowRight className="h-3 w-3" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {!isLoading && (!filteredCategories || filteredCategories.length === 0) && (
        <div className="text-center py-16 sm:py-20">
          <Folder className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
          <h3 className="text-lg sm:text-xl font-semibold mb-2">{t("common.noResults")}</h3>
          <p className="text-sm sm:text-base text-muted-foreground">
            {searchQuery ? t("common.noResults") : ""}
          </p>
        </div>
      )}
    </div>
  );
}
