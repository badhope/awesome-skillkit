"use client";

import Link from "next/link";
import {
  Sparkles,
  Download,
  Eye,
  Star,
  Clock,
  ArrowUpRight,
  ArrowRight,
  Zap,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn, formatDate, formatNumber, getInitials, getStatusColor } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";
import type { Skill } from "@/types";

interface SkillCardProps {
  skill: Skill;
  variant?: "default" | "compact" | "featured";
  featured?: boolean;
  className?: string;
}

const MAX_TAGS_MOBILE = 3;

function StarRating({
  rating,
  size = "sm",
}: {
  rating: number;
  size?: "xs" | "sm" | "md";
}) {
  const starSize = {
    xs: "h-3 w-3",
    sm: "h-3.5 w-3.5",
    md: "h-4 w-4",
  };

  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          className={cn(
            starSize[size],
            i <= Math.round(rating)
              ? "text-amber-500 fill-amber-500"
              : "text-muted-foreground/30"
          )}
        />
      ))}
    </div>
  );
}

function ComplexityIndicator({ complexity }: { complexity: string }) {
  const config: Record<string, { color: string; label: string }> = {
    beginner: {
      color: "bg-emerald-500",
      label: "Beginner",
    },
    intermediate: {
      color: "bg-amber-500",
      label: "Intermediate",
    },
    advanced: {
      color: "bg-orange-500",
      label: "Advanced",
    },
    expert: {
      color: "bg-red-500",
      label: "Expert",
    },
  };

  const entry = config[complexity?.toLowerCase() ?? ""] ?? config.intermediate;

  if (!entry) return null;

  return (
    <div className="flex items-center gap-1.5">
      <span className={cn("h-2 w-2 rounded-full", entry.color)} />
      <span className="text-xs text-muted-foreground">{entry.label}</span>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const { t, locale } = useI18n();

  const statusConfig: Record<
    string,
    { variant: "success" | "warning" | "destructive" | "secondary"; labelKey: string }
  > = {
    published: { variant: "success", labelKey: "skill.published" },
    draft: { variant: "warning", labelKey: "skill.draft" },
    deprecated: { variant: "destructive", labelKey: "skill.deprecated" },
    archived: { variant: "secondary", labelKey: "skill.archived" },
  };

  const config = statusConfig[status] ?? statusConfig.draft!;

  return (
    <Badge variant={config!.variant} className="text-[10px] sm:text-xs font-medium">
      {t(config!.labelKey)}
    </Badge>
  );
}

export function SkillCard({ skill, variant = "default", featured, className }: SkillCardProps) {
  const { t, locale } = useI18n();
  const resolvedVariant = featured ? "featured" : variant;
  const isCompact = resolvedVariant === "compact";
  const isFeatured = resolvedVariant === "featured";

  const complexity =
    ((skill as unknown as Record<string, unknown>).metadata as
      | Record<string, unknown>
      | undefined)?.complexity as string | undefined ?? "intermediate";

  const tagsToShow = skill.tags || [];
  const hiddenCount = Math.max(0, tagsToShow.length - MAX_TAGS_MOBILE);

  if (isCompact) {
    return (
      <Link href={`/skills/${skill.slug}`} className="block group">
        <Card
          className={cn(
            "p-3 sm:p-4 transition-all duration-200 hover:border-primary/40 hover:shadow-md active:scale-[0.98]",
            isFeatured && "ring-1 ring-primary/20 border-primary/30 bg-gradient-to-br from-primary/[0.03] to-transparent",
            className
          )}
        >
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500/20 to-indigo-500/20 group-hover:from-violet-500/30 group-hover:to-indigo-500/30 transition-colors">
              {skill.icon_url ? (
                <img src={skill.icon_url} alt={skill.name} className="h-5 w-5 rounded object-cover" />
              ) : (
                <Sparkles className="h-5 w-5 text-violet-500" />
              )}
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-semibold text-sm truncate group-hover:text-primary transition-colors">
                {skill.name}
              </p>
              <div className="flex items-center gap-2 mt-0.5">
                {skill.category && (
                  <Badge variant="secondary" className="text-[9px] px-1.5 py-0 h-4">
                    {skill.category.name}
                  </Badge>
                )}
                {skill.metrics && (
                  <span className="text-[10px] text-muted-foreground flex items-center gap-0.5">
                    <Star className="h-2.5 w-2.5 text-amber-500 fill-amber-500" />
                    {skill.metrics.average_rating.toFixed(1)}
                  </span>
                )}
              </div>
            </div>
            <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground group-hover:text-primary group-hover:translate-x-0.5 transition-all opacity-0 group-hover:opacity-100" />
          </div>
        </Card>
      </Link>
    );
  }

  return (
    <Card
      className={cn(
        "group flex flex-col h-full transition-all duration-300 hover:border-primary/50 hover:shadow-lg hover:-translate-y-0.5 active:scale-[0.98] active:shadow-sm overflow-hidden",
        isFeatured &&
          "ring-2 ring-primary/20 border-primary/30 bg-gradient-to-br from-primary/[0.05] via-transparent to-violet-500/[0.03]",
        className
      )}
    >
      {/* Card Header */}
      <div className={cn("p-4 md:p-5", !isCompact && "pb-2")}>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 min-w-0 flex-1">
            <div
              className={cn(
                "shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-indigo-500/20 group-hover:from-violet-500/30 group-hover:to-indigo-500/30 transition-colors",
                isCompact ? "hidden" : "flex",
                isFeatured ? "h-12 w-12 sm:h-14 sm:w-14" : "h-11 w-11 sm:h-12 sm:w-12"
              )}
            >
              {skill.icon_url ? (
                <img
                  src={skill.icon_url}
                  alt={skill.name}
                  className={cn(
                    "rounded-lg object-cover",
                    isFeatured ? "h-7 w-7 sm:h-8 sm:w-8" : "h-6 w-6 sm:h-7 sm:w-7"
                  )}
                />
              ) : (
                <Sparkles
                  className={cn(
                    "text-violet-500",
                    isFeatured ? "h-6 w-6 sm:h-7 sm:w-7" : "h-5 w-5 sm:h-6 sm:w-6"
                  )}
                />
              )}
            </div>

            <div className="min-w-0 flex-1 pt-0.5">
              {/* Status & Featured Badge Row */}
              <div className="flex items-center gap-1.5 mb-1 flex-wrap">
                {isFeatured && (
                  <Badge variant="purple" className="text-[10px] px-1.5 py-0 h-5">
                    <Zap className="h-2.5 w-2.5 mr-1" />
                    {t("skill.featured")}
                  </Badge>
                )}
                <StatusBadge status={skill.status} />
              </div>

              {/* Title */}
              <h3
                className={cn(
                  "font-bold truncate group-hover:text-primary transition-colors leading-tight",
                  isFeatured ? "text-lg sm:text-xl" : "text-base sm:text-lg md:text-xl"
                )}
              >
                {skill.name}
              </h3>

              {/* Author */}
              {skill.author && (
                <div className="flex items-center gap-1.5 mt-1">
                  <Avatar className="h-4 w-4 sm:h-5 sm:w-5">
                    <AvatarImage src={skill.author.avatar_url || undefined} />
                    <AvatarFallback className="text-[7px] sm:text-[9px]">
                      {getInitials(skill.author.full_name || skill.author.username)}
                    </AvatarFallback>
                  </Avatar>
                  <span className="text-[11px] sm:text-xs text-muted-foreground truncate">
                    @{skill.author.username}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Body Content */}
      <div className={cn("px-4 md:px-5 flex-1 flex flex-col", isCompact ? "" : "pt-0")}>
        {/* Description */}
        <p
          className={cn(
            "text-muted-foreground leading-relaxed",
            "line-clamp-2 md:line-clamp-3",
            isCompact ? "text-xs" : "text-sm"
          )}
        >
          {skill.description}
        </p>

        {/* Category Badge & Complexity */}
        <div className="flex items-center gap-2 mt-3 flex-wrap">
          {skill.category && (
            <Badge
              variant="secondary"
              className={cn("font-medium shrink-0", isCompact ? "text-[10px]" : "text-xs")}
            >
              {skill.category.name}
            </Badge>
          )}
          {!isCompact && <ComplexityIndicator complexity={complexity} />}
        </div>

        {/* Tags */}
        {(tagsToShow.length > 0) && (
          <div className="flex flex-wrap items-center gap-1.5 mt-3">
            <span className="hidden md:inline-flex flex-wrap gap-1.5">
              {tagsToShow.map((tag) => (
                <Badge key={tag.id} variant="outline" className="text-xs">
                  {tag.name}
                </Badge>
              ))}
            </span>
            <span className="md:hidden inline-flex flex-wrap items-center gap-1.5">
              {tagsToShow.slice(0, MAX_TAGS_MOBILE).map((tag) => (
                <Badge key={tag.id} variant="outline" className="text-xs">
                  {tag.name}
                </Badge>
              ))}
              {hiddenCount > 0 && (
                <Badge variant="outline" className="text-xs text-muted-foreground">
                  +{hiddenCount}
                </Badge>
              )}
            </span>
          </div>
        )}

        {/* Stats Row */}
        {skill.metrics && (
          <div className="mt-3 pt-3 border-t">
            <div className="flex items-center gap-3 sm:gap-4 overflow-x-auto scrollbar-none pb-0.5">
              <div className="flex items-center gap-1 shrink-0">
                <StarRating rating={skill.metrics.average_rating} size="xs" />
                <span className="text-xs text-muted-foreground font-medium tabular-nums">
                  {skill.metrics.average_rating.toFixed(1)}
                </span>
              </div>
              <div className="flex items-center gap-1 shrink-0 text-xs text-muted-foreground">
                <Download className="h-3.5 w-3.5" />
                <span className="tabular-nums">{formatNumber(skill.metrics.downloads_count, locale)}</span>
              </div>
              <div className="flex items-center gap-1 shrink-0 text-xs text-muted-foreground">
                <Eye className="h-3.5 w-3.5" />
                <span className="tabular-nums">{formatNumber(skill.metrics.views_count, locale)}</span>
              </div>
              <div className="flex items-center gap-1 shrink-0 text-xs text-muted-foreground ml-auto">
                <Clock className="h-3 w-3" />
                <time dateTime={skill.updated_at}>
                  {formatDate(skill.updated_at, "relative")}
                </time>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-4 pt-3 border-t flex items-center gap-2 sm:gap-3">
          <Link
            href={`/skills/${skill.slug}`}
            className="flex-1 min-w-0"
          >
            <Button
              size="sm"
              className={cn(
                "w-full rounded-lg text-xs sm:text-sm font-medium min-h-[36px] sm:min-h-[40px]",
                isFeatured && "bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500"
              )}
            >
              <Zap className="h-3.5 w-3.5 mr-1.5 shrink-0" />
              <span className="truncate">{t("skill.use_skill")}</span>
            </Button>
          </Link>
          <Link href={`/skills/${skill.slug}`} className="shrink-0">
            <Button
              variant="outline"
              size="sm"
              className="rounded-lg text-xs sm:text-sm font-medium min-h-[36px] sm:min-h-[40px] px-3 sm:px-4"
            >
              <span className="hidden sm:inline">{t("skill.details")}</span>
              <ArrowUpRight className="h-3.5 w-3.5 sm:hidden" />
            </Button>
          </Link>
        </div>
      </div>
    </Card>
  );
}
