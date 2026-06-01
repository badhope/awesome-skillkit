"use client";

import { useState, useMemo } from "react";
import {
  ChevronRight,
  ChevronDown,
  ChevronLeft,
  Folder,
  FolderOpen,
  Grid3X3,
  X,
  SlidersHorizontal,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";
import type { Category } from "@/types";

export interface CategoryFilterProps {
  categories: Category[];
  selectedCategory: string | null;
  onSelect: (slug: string | null) => void;
  className?: string;
}

function getCategoryIcon(name: string): string {
  const iconMap: Record<string, string> = {
    "nlp": "💬",
    "computer vision": "👁️",
    "audio": "🎵",
    "generation": "✨",
    "analysis": "📊",
    "classification": "🏷️",
    "translation": "🌐",
    "code": "💻",
    "data": "📁",
    "embedding": "🧠",
    "agent": "🤖",
    "multimodal": "🎨",
    "reasoning": "🧮",
    "search": "🔍",
    "recommendation": "⭐",
    "automation": "⚡",
  };
  const lower = name.toLowerCase();
  return (
    iconMap[lower] ||
    Object.entries(iconMap).find(([key]) => lower.includes(key))?.[1] ||
    "📂"
  );
}

function CategoryItem({
  category,
  selectedCategory,
  onSelect,
  depth = 0,
}: {
  category: Category;
  selectedCategory: string | null;
  onSelect: (slug: string | null) => void;
  depth?: number;
}) {
  const [expanded, setExpanded] = useState(depth < 1);
  const hasChildren = category.children && category.children.length > 0;
  const isSelected = selectedCategory === category.slug;
  const isParentSelected =
    selectedCategory &&
    category.children &&
    (category.children.some((c) => c.slug === selectedCategory) ||
      category.children.some(
        (c) => c.children && c.children.some((cc) => cc.slug === selectedCategory)
      ));

  const handleClick = () => {
    if (isSelected) {
      onSelect(null);
    } else {
      onSelect(category.slug);
    }
    if (hasChildren) {
      setExpanded(!expanded);
    }
  };

  return (
    <div>
      <button
        onClick={handleClick}
        className={cn(
          "w-full flex items-center gap-2 rounded-lg text-sm transition-all duration-200 group min-h-[36px] md:min-h-[40px]",
          depth > 0 && "ml-4 md:ml-6",
          isSelected
            ? "bg-primary/10 text-primary font-semibold border border-primary/20"
            : isParentSelected
              ? "text-foreground bg-accent/50 font-medium"
              : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
        )}
        style={{ paddingLeft: `${depth * 16 + 12}px` }}
      >
        {/* Expand/Collapse Toggle */}
        <span
          className={cn(
            "flex items-center justify-center shrink-0 w-5 h-5 rounded hover:bg-background transition-colors",
            !hasChildren && "invisible"
          )}
        >
          {hasChildren && (
            <>
              <ChevronDown
                className={cn(
                  "h-3.5 w-3.5 transition-transform duration-200",
                  expanded ? "rotate-0" : "-rotate-90"
                )}
              />
            </>
          )}
        </span>

        {/* Icon */}
        <span className="shrink-0 text-sm md:text-base">
          {category.icon || getCategoryIcon(category.name)}
        </span>

        {/* Name */}
        <span className="flex-1 truncate text-left">{category.name}</span>

        {/* Count Badge */}
        <Badge
          variant="secondary"
          className={cn(
            "text-[10px] px-1.5 py-0 h-5 tabular-nums font-mono shrink-0",
            isSelected
              ? "bg-primary/20 text-primary"
              : "bg-muted text-muted-foreground"
          )}
        >
          {category.skill_count}
        </Badge>
      </button>

      {/* Children */}
      {hasChildren && expanded && (
        <div
          className={cn(
            "overflow-hidden transition-all duration-300 ease-out",
            expanded ? "max-h-[1000px] opacity-100" : "max-h-0 opacity-0"
          )}
        >
          {category.children!.map((child) => (
            <CategoryItem
              key={child.id}
              category={child}
              selectedCategory={selectedCategory}
              onSelect={onSelect}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function CategoryFilter({
  categories,
  selectedCategory,
  onSelect,
  className,
}: CategoryFilterProps) {
  const [mobileSheetOpen, setMobileSheetOpen] = useState(false);
  const { t } = useI18n();

  const allCategoriesFlat = useMemo(() => {
    const flat: Category[] = [];
    for (const cat of categories) {
      flat.push(cat);
      if (cat.children) {
        flat.push(...cat.children);
        cat.children.forEach((child) => {
          if (child.children) {
            flat.push(...child.children);
          }
        });
      }
    }
    return flat;
  }, [categories]);

  return (
    <div className={cn("space-y-4", className)}>
      {/* Desktop & Tablet: Full Tree View */}
      <div className="hidden md:block">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-sm flex items-center gap-2">
            <Grid3X3 className="h-4 w-4" />
            {t("category.title")}
          </h3>
          {selectedCategory && (
            <button
              onClick={() => onSelect(null)}
              className="text-xs text-primary hover:text-primary/80 transition-colors font-medium min-h-[28px] px-2 rounded-md hover:bg-primary/10"
            >
              {t("category.clear")}
            </button>
          )}
        </div>

        <div className="space-y-0.5">
          {/* All Categories Option */}
          <button
            onClick={() => onSelect(null)}
            className={cn(
              "w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 min-h-[40px]",
              !selectedCategory
                ? "bg-primary/10 text-primary font-semibold border border-primary/20"
                : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
            )}
          >
            <Grid3X3 className="h-4 w-4 shrink-0" />
            <span>{t("category.all")}</span>
          </button>

          {/* Category Tree */}
          {categories.map((category) => (
            <CategoryItem
              key={category.id}
              category={category}
              selectedCategory={selectedCategory}
              onSelect={onSelect}
              depth={0}
            />
          ))}
        </div>
      </div>

      {/* Mobile: Chip Row + Sheet */}
      <div className="md:hidden">
        {/* Horizontal Scrollable Chips */}
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-none pb-2 -mx-1 px-1">
          {/* All Categories Chip */}
          <button
            onClick={() => onSelect(null)}
            className={cn(
              "shrink-0 inline-flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium border transition-all duration-200 min-h-[36px]",
              !selectedCategory
                ? "bg-primary text-primary-foreground border-primary shadow-sm"
                : "bg-background text-muted-foreground border-border hover:border-primary/30 hover:text-foreground"
            )}
          >
            <Grid3X3 className="h-3.5 w-3.5" />
            {t("category.all")}
          </button>

          {/* Top-level Category Chips */}
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => onSelect(cat.slug === selectedCategory ? null : cat.slug)}
              className={cn(
                "shrink-0 inline-flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium border transition-all duration-200 min-h-[36px]",
                cat.slug === selectedCategory
                  ? "bg-primary text-primary-foreground border-primary shadow-sm"
                  : "bg-background text-muted-foreground border-border hover:border-primary/30 hover:text-foreground"
              )}
            >
              <span className="text-sm">{cat.icon || getCategoryIcon(cat.name)}</span>
              <span className="truncate max-w-[120px]">{cat.name}</span>
              <span
                className={cn(
                  "tabular-nums text-[10px] px-1 rounded-full",
                  cat.slug === selectedCategory
                    ? "bg-white/20"
                    : "bg-muted"
                )}
              >
                {cat.skill_count}
              </span>
            </button>
          ))}

          {/* Show All Button - Opens Bottom Sheet */}
          <button
            onClick={() => setMobileSheetOpen(true)}
            className="shrink-0 inline-flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium border border-dashed border-muted-foreground/30 text-muted-foreground hover:border-primary/30 hover:text-primary transition-all duration-200 min-h-[36px]"
          >
            <SlidersHorizontal className="h-3.5 w-3.5" />
            {t("category.show_all")}
          </button>
        </div>
      </div>

      {/* Mobile Bottom Sheet / Modal */}
      {mobileSheetOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm md:hidden"
            onClick={() => setMobileSheetOpen(false)}
            aria-hidden="true"
          />

          {/* Sheet Panel */}
          <div
            className={cn(
              "fixed bottom-0 left-0 right-0 z-[60] bg-background rounded-t-2xl shadow-2xl md:hidden",
              "transform transition-transform duration-300 ease-out max-h-[80vh]"
            )}
          >
            {/* Handle Bar */}
            <div className="sticky top-0 bg-background rounded-t-2xl z-10">
              <div className="flex items-center justify-center pt-3 pb-2">
                <div className="w-10 h-1 rounded-full bg-muted-foreground/30" />
              </div>

              {/* Header */}
              <div className="flex items-center justify-between px-4 pb-3 border-b">
                <h3 className="font-semibold text-base flex items-center gap-2">
                  <Grid3X3 className="h-5 w-5" />
                  {t("category.title")}
                </h3>
                <button
                  onClick={() => setMobileSheetOpen(false)}
                  className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-xl hover:bg-accent transition-colors"
                  aria-label="Close"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Scrollable Content */}
            <div className="overflow-y-auto overscroll-contain pb-6 max-h-[calc(80vh-60px)]">
              <div className="p-3 space-y-0.5">
                {/* All Categories */}
                <button
                  onClick={() => {
                    onSelect(null);
                    setMobileSheetOpen(false);
                  }}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 min-h-12 rounded-xl text-base font-medium transition-all duration-200",
                    !selectedCategory
                      ? "bg-primary/10 text-primary font-semibold border border-primary/20"
                      : "text-foreground hover:bg-accent"
                  )}
                >
                  <Grid3X3 className="h-5 w-5 shrink-0" />
                  <span>{t("category.all")}</span>
                  {!selectedCategory && (
                    <ChevronRight className="h-4 w-4 ml-auto text-primary" />
                  )}
                </button>

                {/* Full Tree in Sheet */}
                {categories.map((category) => (
                  <div key={category.id}>
                    <CategoryItem
                      category={category}
                      selectedCategory={selectedCategory}
                      onSelect={(slug) => {
                        onSelect(slug);
                        setMobileSheetOpen(false);
                      }}
                      depth={0}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
