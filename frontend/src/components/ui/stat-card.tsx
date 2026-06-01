"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

type TrendDirection = "up" | "down" | "neutral";

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  trend?: {
    direction: TrendDirection;
    value: string;
  };
  className?: string;
}

function StatCard({ icon: Icon, label, value, trend, className }: StatCardProps) {
  const trendConfig = {
    up: {
      icon: TrendingUp,
      colorClass: "text-emerald-600 dark:text-emerald-400",
      bgClass: "bg-emerald-50 dark:bg-emerald-900/20",
    },
    down: {
      icon: TrendingDown,
      colorClass: "text-red-600 dark:text-red-400",
      bgClass: "bg-red-50 dark:bg-red-900/20",
    },
    neutral: {
      icon: Minus,
      colorClass: "text-muted-foreground",
      bgClass: "bg-muted",
    },
  };

  return (
    <div
      className={cn(
        "rounded-xl border bg-card text-card-foreground shadow-sm transition-shadow hover:shadow-md",
        "p-4 sm:p-6",
        className
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1 flex-1 min-w-0">
          <p className="text-xs sm:text-sm font-medium text-muted-foreground uppercase tracking-wide">
            {label}
          </p>
          <p className={cn("font-bold tracking-tight", "text-2xl sm:text-3xl")}>
            {value}
          </p>
          {trend && (() => {
            const config = trendConfig[trend.direction];
            const TrendIcon = config.icon;
            return (
              <div
                className={cn(
                  "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium mt-1.5",
                  config.bgClass,
                  config.colorClass
                )}
              >
                <TrendIcon className="h-3 w-3" />
                <span>{trend.value}</span>
              </div>
            );
          })()}
        </div>
        <div
          className={cn(
            "rounded-lg flex items-center justify-center shrink-0",
            "w-10 h-10 sm:w-12 sm:h-12",
            "bg-primary/10 text-primary"
          )}
        >
          <Icon className="h-5 w-5 sm:h-6 sm:w-6" />
        </div>
      </div>
    </div>
  );
}

export { StatCard };
export type { StatCardProps, TrendDirection };
