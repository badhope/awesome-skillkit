"use client";

import { useState } from "react";
import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

interface SkillRatingProps {
  value: number;
  onChange?: (value: number) => void;
  readonly?: boolean;
  size?: "sm" | "md" | "lg";
  count?: number;
  showLabel?: boolean;
}

const sizeClasses = {
  sm: "h-3.5 w-3.5",
  md: "h-5 w-5",
  lg: "h-7 w-7",
};

const labelSizes = {
  sm: "text-xs",
  md: "text-sm",
  lg: "text-base",
};

export function SkillRating({
  value,
  onChange,
  readonly = false,
  size = "md",
  count,
  showLabel = false,
}: SkillRatingProps) {
  const [hoverValue, setHoverValue] = useState<number | null>(null);
  const [isHovering, setIsHovering] = useState(false);

  const displayValue = hoverValue ?? value;

  const ratingLabels = ["Poor", "Fair", "Good", "Very Good", "Excellent"];

  return (
    <div className="flex items-center gap-1.5">
      <div
        className="flex items-center"
        onMouseEnter={() => !readonly && setIsHovering(true)}
        onMouseLeave={() => {
          if (!readonly) {
            setIsHovering(false);
            setHoverValue(null);
          }
        }}
      >
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            disabled={readonly}
            onClick={() => onChange?.(star)}
            onMouseEnter={() => !readonly && setHoverValue(star)}
            className={cn(
              "transition-all duration-150",
              !readonly && "cursor-pointer hover:scale-110",
              readonly && "cursor-default"
            )}
            aria-label={`Rate ${star} stars`}
          >
            <Star
              className={cn(
                sizeClasses[size],
                "transition-colors",
                star <= displayValue
                  ? "text-amber-400 fill-amber-400"
                  : "text-muted-foreground/30 fill-muted-foreground/10"
              )}
            />
          </button>
        ))}
      </div>

      {showLabel && isHovering && hoverValue && (
        <span className={cn("font-medium text-amber-500", labelSizes[size])}>
          {ratingLabels[hoverValue - 1]}
        </span>
      )}

      {count !== undefined && (
        <span className={cn("text-muted-foreground", labelSizes[size])}>
          ({count})
        </span>
      )}
    </div>
  );
}