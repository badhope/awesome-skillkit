"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";
import { Loader2 } from "lucide-react";

interface LoadMoreProps {
  onLoadMore: () => void;
  hasMore: boolean;
  isLoading: boolean;
  totalCount?: number;
  loadedCount?: number;
  className?: string;
}

function LoadMore({
  onLoadMore,
  hasMore,
  isLoading,
  totalCount,
  loadedCount,
  className,
}: LoadMoreProps) {
  const { t } = useI18n();
  if (!hasMore && loadedCount !== undefined && loadedCount > 0) {
    return (
      <div
        className={cn(
          "flex items-center justify-center py-8 text-sm text-muted-foreground",
          className
        )}
      >
        {totalCount !== undefined ? (
          <span>
            {t("loadMore.showingAll", { loaded: loadedCount, total: totalCount })}
          </span>
        ) : (
          <span>{t("loadMore.noMoreItems")}</span>
        )}
      </div>
    );
  }

  if (!hasMore) {
    return null;
  }

  return (
    <div className={cn("flex justify-center py-6", className)}>
      <button
        onClick={onLoadMore}
        disabled={isLoading}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-200",
          "min-h-[44px] px-6 py-2.5 text-sm border bg-background",
          "hover:bg-accent hover:text-accent-foreground",
          "disabled:pointer-events-none disabled:opacity-50",
          "active:scale-[0.98] touch-manipulation select-none"
        )}
      >
        {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
        {isLoading ? t("loadMore.loading") : t("loadMore.loadMore")}
      </button>
    </div>
  );
}

export { LoadMore };
export type { LoadMoreProps };
