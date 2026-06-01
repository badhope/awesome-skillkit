"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  illustration?: React.ReactNode;
  className?: string;
}

function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  illustration,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center text-center py-12 px-4 sm:py-20 sm:px-6",
        className
      )}
    >
      {illustration && (
        <div className="mb-6 max-w-[200px] sm:max-w-[280px]">{illustration}</div>
      )}

      <div
        className={cn(
          "rounded-full bg-muted flex items-center justify-center mb-4 sm:mb-6",
          "w-16 h-16 sm:w-20 sm:h-20"
        )}
      >
        <Icon className={cn("text-muted-foreground", "h-7 w-7 sm:h-8 sm:w-8")} />
      </div>

      <h3 className={cn("font-semibold text-muted-foreground mb-2", "text-lg sm:text-xl")}>
        {title}
      </h3>

      <p className="text-muted-foreground text-sm sm:text-base max-w-md mb-6">
        {description}
      </p>

      {action && (
        <button
          onClick={action.onClick}
          className={cn(
            "inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200",
            "min-h-[44px] px-5 py-2.5 text-sm",
            "bg-primary text-primary-foreground shadow hover:bg-primary/90 hover:shadow-md",
            "active:scale-[0.98] touch-manipulation select-none"
          )}
        >
          {action.label}
        </button>
      )}
    </div>
  );
}

export { EmptyState };
export type { EmptyStateProps };
