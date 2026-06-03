"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Sparkles,
  Download,
  Users,
  GitBranch,
  TrendingUp,
  Activity,
  Star,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  UsageTrendChart,
  PopularSkillsChart,
  CategoryDistributionChart,
  StatsOverviewChart,
} from "@/components/Charts";
import {
  useDashboardStats,
  useUsageTrends,
  useCategoryDistribution,
  usePopularSkills,
} from "@/hooks/useSkills";
import { isAuthenticated } from "@/lib/auth";
import { formatNumber, cn } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";

export default function DashboardPage() {
  const router = useRouter();
  const { t, locale } = useI18n();
  // Render only after we've checked auth on the client. The first paint
  // happens during hydration with whatever localStorage says; without
  // this guard the dashboard would briefly mount and immediately
  // redirect to /auth/login on every reload of an authenticated user.
  const [authReady, setAuthReady] = useState(false);
  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/auth/login");
      return;
    }
    setAuthReady(true);
  }, [router]);

  const statsQuery = useDashboardStats();
  const trendsQuery = useUsageTrends(30);
  const distributionQuery = useCategoryDistribution();
  const popularSkillsQuery = usePopularSkills(10);

  if (!authReady) {
    return (
      <div className="container mx-auto px-4 py-6 sm:py-8">
        <div className="mb-6 sm:mb-8">
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-72" />
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 sm:h-28 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  const stats = statsQuery.data;
  const trends = trendsQuery.data;
  const distribution = distributionQuery.data;
  const popularSkills = popularSkillsQuery.data;

  const statCards = [
    {
      label: t("dashboard.totalSkills"),
      value: stats?.total_skills ?? 0,
      icon: Sparkles,
      color: "text-violet-500",
      bg: "bg-violet-500/10",
    },
    {
      label: t("dashboard.totalCompositions"),
      value: stats?.total_compositions ?? 0,
      icon: GitBranch,
      color: "text-emerald-500",
      bg: "bg-emerald-500/10",
    },
    {
      label: t("dashboard.totalUsers"),
      value: stats?.total_users ?? 0,
      icon: Users,
      color: "text-sky-500",
      bg: "bg-sky-500/10",
    },
    {
      label: t("dashboard.totalDownloads"),
      value: stats?.total_downloads ?? 0,
      icon: Download,
      color: "text-amber-500",
      bg: "bg-amber-500/10",
    },
  ];

  return (
    <div className="container mx-auto px-4 py-6 sm:py-8">
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight mb-1 sm:mb-2">
          {t("dashboard.title")}
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground">
          {t("dashboard.subtitle")}
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
        {statCards.map((stat) => (
          <Card key={stat.label} className="hover:shadow-lg transition-shadow rounded-xl">
            <CardContent className="p-3 sm:p-4 md:p-6">
              <div className="flex items-center justify-between mb-2 sm:mb-3">
                <div className={cn("flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-xl", stat.bg)}>
                  <stat.icon className={cn("h-4 w-4 sm:h-5 sm:w-5", stat.color)} />
                </div>
              </div>
              <div className="text-lg sm:text-2xl font-bold">
                {statsQuery.isLoading ? (
                  <Skeleton className="h-7 w-16 sm:h-8 sm:w-20" />
                ) : (
                  formatNumber(stat.value, locale)
                )}
              </div>
              <p className="text-xs sm:text-sm text-muted-foreground leading-tight mt-0.5">
                {stat.label}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
        <div>
          {trendsQuery.isLoading ? (
            <Skeleton className="h-[280px] sm:h-[320px] md:h-[380px] rounded-xl" />
          ) : trends ? (
            <UsageTrendChart data={trends} />
          ) : null}
        </div>
        <div>
          {popularSkillsQuery.isLoading ? (
            <Skeleton className="h-[280px] sm:h-[320px] md:h-[380px] rounded-xl" />
          ) : popularSkills ? (
            <PopularSkillsChart data={popularSkills} />
          ) : null}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
        <div>
          {distributionQuery.isLoading ? (
            <Skeleton className="h-[280px] sm:h-[320px] md:h-[380px] rounded-xl" />
          ) : distribution ? (
            <CategoryDistributionChart data={distribution} />
          ) : null}
        </div>
        <div>
          {stats ? (
            <StatsOverviewChart
              totalSkills={stats.total_skills}
              totalCompositions={stats.total_compositions}
              totalUsers={stats.total_users}
              totalDownloads={stats.total_downloads}
            />
          ) : (
            <Skeleton className="h-[280px] sm:h-[320px] md:h-[380px] rounded-xl" />
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        <Card className="rounded-xl">
          <CardHeader className="pb-3">
            <CardTitle className="text-xs sm:text-sm flex items-center gap-2">
              <Activity className="h-3.5 w-3.5 text-primary" />
              {t("dashboard.recentActivity")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {stats ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs sm:text-sm">
                  <span className="text-muted-foreground truncate pr-2">
                    {t("dashboard.skillsToday")}
                  </span>
                  <span className="font-medium shrink-0">{stats.skills_published_today}</span>
                </div>
                <div className="flex items-center justify-between text-xs sm:text-sm">
                  <span className="text-muted-foreground truncate pr-2">
                    {t("dashboard.activeUsersToday")}
                  </span>
                  <span className="font-medium shrink-0">{stats.active_users_today}</span>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="rounded-xl">
          <CardHeader className="pb-3">
            <CardTitle className="text-xs sm:text-sm flex items-center gap-2">
              <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />
              {t("dashboard.quickActions")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-xs sm:text-sm">
              <a href="/skills/new" className="block text-primary hover:underline py-0.5">
                + {t("dashboard.createSkill")}
              </a>
              <a href="/compositions/new" className="block text-primary hover:underline py-0.5">
                + {t("dashboard.createComposition")}
              </a>
              <a href="/docs" className="block text-primary hover:underline py-0.5">
                {t("dashboard.viewDocs")}
              </a>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-xl sm:col-span-2 lg:col-span-1">
          <CardHeader className="pb-3">
            <CardTitle className="text-xs sm:text-sm flex items-center gap-2">
              <Star className="h-3.5 w-3.5 text-amber-500" />
              {t("dashboard.topRated")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {popularSkills ? (
              <div className="space-y-2">
                {popularSkills.slice(0, 5).map((item) => (
                  <div key={item.skill.id} className="flex items-center justify-between text-xs sm:text-sm">
                    <span className="truncate text-muted-foreground pr-2">
                      {item.skill.name}
                    </span>
                    <span className="font-medium flex items-center gap-1 shrink-0">
                      <Star className="h-3 w-3 text-amber-500 fill-amber-500" />
                      {item.rating.toFixed(1)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-4 w-full" />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
