"use client";

import { Loader2 } from "lucide-react";
import { Skeleton, SkeletonCard } from "@/components/ui/skeleton";
import { useI18n } from "@/lib/i18n";

export default function GlobalLoading() {
  const { t, isZh } = useI18n();

  return (
    <div
      className="min-h-[calc(100vh-4rem)] w-full"
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <div className="container mx-auto px-4 lg:px-6 py-10 space-y-8">
        <div className="flex flex-col items-center justify-center text-center space-y-3 pt-6">
          <div className="relative inline-flex">
            <div className="absolute inset-0 rounded-full bg-primary/20 blur-xl animate-pulse" />
            <Loader2 className="relative h-10 w-10 text-primary animate-spin" />
          </div>
          <h1 className="text-lg sm:text-xl font-semibold tracking-tight">
            {t("errors.loadingTitle")}
          </h1>
          <p className="text-sm text-muted-foreground">
            {isZh
              ? "正在为您准备最佳体验…"
              : t("errors.loadingDescription")}
          </p>
        </div>

        <div className="space-y-6">
          <div className="space-y-2">
            <Skeleton className="h-8 w-1/3" />
            <Skeleton className="h-4 w-1/2" />
          </div>

          <div className="flex items-center gap-2 overflow-hidden">
            <Skeleton className="h-10 flex-1 rounded-lg" />
            <Skeleton className="h-10 w-24 rounded-lg" />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
        </div>

        <span className="sr-only">{t("errors.loadingTitle")}</span>
      </div>
    </div>
  );
}
