"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import {
  Search,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Download,
  Users,
  GitBranch,
  Star,
  Zap,
  Shield,
  Cpu,
  BookOpen,
  ChevronRight,
  Flame,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { SearchBar } from "@/components/SearchBar";
import { SkillCard } from "@/components/SkillCard";
import { useFeaturedSkills, useTrendingSkills, useCategories } from "@/hooks/useSkills";
import { useI18n } from "@/lib/i18n";

const quickActions = [
  { key: "popular", icon: Star },
  { key: "newest", icon: Sparkles },
  { key: "trending", icon: TrendingUp },
  { key: "ai", icon: Cpu },
  { key: "webDev", icon: Zap },
  { key: "dataScience", icon: BookOpen },
] as const;

const featureItems = [
  { iconKey: "lightningFast", icon: Zap },
  { iconKey: "verifiedSecure", icon: Shield },
  { iconKey: "composable", icon: Cpu },
  { iconKey: "wellDocumented", icon: BookOpen },
] as const;

export default function HomePage() {
  const { t } = useI18n();
  const { data: featuredSkills, isLoading: featuredLoading } = useFeaturedSkills();
  const { data: trendingSkills, isLoading: trendingLoading } = useTrendingSkills(8);
  const { data: categories } = useCategories();
  const [counted, setCounted] = useState(false);
  const carouselRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setCounted(true);
  }, []);

  const stats = [
    {
      icon: Sparkles,
      value: t("hero.stats.skills.value"),
      label: t("hero.stats.skills.label"),
    },
    {
      icon: GitBranch,
      value: t("hero.stats.categories.value"),
      label: t("hero.stats.categories.label"),
    },
    {
      icon: Star,
      value: t("hero.stats.tests.value"),
      label: t("hero.stats.tests.label"),
    },
    {
      icon: Download,
      value: t("hero.stats.downloads.value"),
      label: t("hero.stats.downloads.label"),
    },
    {
      icon: Users,
      value: t("hero.stats.developers.value"),
      label: t("hero.stats.developers.label"),
    },
    {
      icon: Cpu,
      value: t("hero.stats.compositions.value"),
      label: t("hero.stats.compositions.label"),
    },
  ];

  return (
    <div className="flex flex-col">
      <section className="relative overflow-hidden min-h-[500px] sm:min-h-[600px] md:h-[75vh] lg:h-[80vh]">
        <div
          className="absolute inset-0 -z-10"
          style={{
            background:
              "radial-gradient(ellipse at 20% 50%, hsl(var(--primary) / 0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, hsl(var(--chart-2) / 0.06) 0%, transparent 50%), radial-gradient(ellipse at 50% 80%, hsl(var(--chart-5) / 0.05) 0%, transparent 50%)",
          }}
        />
        <div className="absolute inset-0 -z-10 opacity-30"
          style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, hsl(var(--border)) 1px, transparent 0)`,
            backgroundSize: "24px 24px",
          }}
        />

        <div className="container mx-auto px-4 h-full flex items-center justify-center py-12 sm:py-16 md:py-20 lg:py-0">
          <div className="w-full max-w-4xl mx-auto space-y-6 sm:space-y-8 text-center">
            <div className="inline-flex items-center gap-2 rounded-full border bg-muted/50 px-3 sm:px-4 py-1.5 text-xs sm:text-sm animate-fade-in">
              <Sparkles className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-primary" />
              <span className="text-muted-foreground">{t("hero.badge")}</span>
              <Badge variant="purple" className="ml-1 text-xs">{t("hero.badgeLabel")}</Badge>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight animate-slide-up leading-tight">
              {t("hero.title1")}
              <br />
              <span className="bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent animate-gradient">
                {t("hero.title2")}
              </span>
            </h1>

            <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto animate-fade-in leading-relaxed">
              {t("hero.subtitle")}
            </p>

            <div className="flex justify-center pt-2 animate-slide-up">
              <SearchBar size="full" />
            </div>

            <div className="flex items-center justify-start sm:justify-center gap-2 sm:gap-3 overflow-x-auto pb-2 scrollbar-none animate-fade-in px-4 sm:px-0">
              {quickActions.map(({ key, icon: Icon }) => (
                <button
                  key={key}
                  className="shrink-0 inline-flex items-center gap-1.5 rounded-full border bg-background/80 backdrop-blur-sm px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm font-medium text-muted-foreground hover:text-foreground hover:border-primary/30 transition-all duration-200 hover:shadow-sm"
                  onClick={() => {}}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{t(`hero.quickActions.${key}`)}</span>
                </button>
              ))}
            </div>

            <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 sm:gap-4 pt-4 sm:pt-6 animate-fade-in">
              {stats.map((stat, index) => (
                <div
                  key={stat.label}
                  className="text-center animate-fade-in"
                  style={{ animationDelay: `${index * 80}ms` }}
                >
                  <stat.icon className="h-5 w-5 sm:h-6 sm:w-6 mx-auto mb-1 sm:mb-2 text-primary" />
                  <div className="text-sm sm:text-xl font-bold">{stat.value}</div>
                  <div className="text-[10px] sm:text-sm text-muted-foreground hidden xs:inline-block sm:inline">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="py-12 sm:py-16 md:py-20">
        <div className="container mx-auto px-4">
          <div className="flex items-end justify-between mb-6 sm:mb-8">
            <div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
                {t("hero.featured.title")}
              </h2>
              <p className="text-sm sm:text-base text-muted-foreground mt-1">
                {t("hero.featured.subtitle")}
              </p>
            </div>
            <Link
              href="/skills"
              className="shrink-0 hidden sm:flex items-center gap-1 text-sm text-primary hover:text-primary/80 transition-colors ml-4"
            >
              {t("common.viewAll")} <ChevronRight className="h-4 w-4" />
            </Link>
          </div>

          <div
            ref={carouselRef}
            className="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-4 scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0 sm:grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 sm:overflow-visible"
          >
            {featuredLoading
              ? Array.from({ length: 6 }).map((_, i) => (
                  <Card
                    key={i}
                    className="shrink-0 w-[85vw] sm:w-full h-[220px] sm:h-[200px] animate-pulse bg-muted snap-center rounded-xl"
                  />
                ))
              : featuredSkills?.slice(0, 8).map((skill) => (
                  <div key={skill.id} className="shrink-0 w-[85vw] sm:w-full snap-center">
                    <SkillCard skill={skill} featured />
                  </div>
                ))}
          </div>

          <div className="sm:hidden mt-2 text-center">
            <Link
              href="/skills"
              className="inline-flex items-center gap-1 text-sm text-primary hover:text-primary/80 transition-colors"
            >
              {t("common.viewAll")} <ChevronRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      <section className="py-12 sm:py-16 md:py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
              {t("hero.categories.title")}
            </h2>
            <p className="text-sm sm:text-base text-muted-foreground mt-2">
              {t("hero.categories.subtitle")}
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4">
            {categories?.slice(0, 10).map((category) => (
              <Link
                key={category.id}
                href={`/categories/${category.slug}`}
                className="group"
              >
                <Card className="h-full transition-all duration-300 hover:border-primary/50 hover:shadow-lg hover:-translate-y-1 rounded-xl sm:rounded-xl">
                  <CardContent className="p-3 sm:p-4 md:p-6 text-center">
                    <div className="flex h-10 w-10 sm:h-12 sm:w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-indigo-500/20 mx-auto mb-2 sm:mb-3 group-hover:from-violet-500/30 group-hover:to-indigo-500/30 transition-colors">
                      <Sparkles className="h-5 w-5 sm:h-6 sm:w-6 text-violet-500" />
                    </div>
                    <h3 className="font-semibold text-sm sm:text-base mb-1 group-hover:text-primary transition-colors line-clamp-1">
                      {category.name}
                    </h3>
                    <p className="text-xs sm:text-sm text-muted-foreground line-clamp-1 sm:line-clamp-2 mb-2 hidden sm:block">
                      {category.description}
                    </p>
                    <Badge variant="secondary" className="text-xs">
                      {category.skill_count} {t("category.skills")}
                    </Badge>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>

          <div className="text-center mt-6 sm:mt-8">
            <Link href="/categories">
              <Button variant="outline" size="lg" className="text-sm sm:text-base">
                {t("hero.categories.viewAll")}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <section className="py-12 sm:py-16 md:py-20">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between mb-6 sm:mb-8">
            <div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight flex items-center gap-2">
                <TrendingUp className="h-6 w-6 sm:h-7 sm:w-7 text-primary shrink-0" />
                <span className="truncate">{t("hero.trending.title")}</span>
              </h2>
              <p className="text-sm sm:text-base text-muted-foreground mt-1">
                {t("hero.trending.subtitle")}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
            {trendingLoading
              ? Array.from({ length: 8 }).map((_, i) => (
                  <Card key={i} className="h-[200px] sm:h-[220px] animate-pulse bg-muted rounded-xl" />
                ))
              : trendingSkills?.map((skill) => (
                  <div key={skill.id} className="relative">
                    <SkillCard skill={skill} />
                    <div className="absolute top-2 right-2 z-10">
                      <Flame className="h-4 w-4 text-orange-500 fill-orange-500" />
                    </div>
                  </div>
                ))}
          </div>
        </div>
      </section>

      <section className="py-12 sm:py-16 md:py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
              {t("hero.features.title")}
            </h2>
            <p className="text-sm sm:text-base text-muted-foreground mt-2">
              {t("hero.features.subtitle")}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            {featureItems.map(({ iconKey, icon: Icon }, index) => (
              <Card
                key={iconKey}
                className="border-none bg-background/50 backdrop-blur hover:shadow-lg transition-all duration-300 animate-fade-in rounded-xl"
                style={{ animationDelay: `${index * 120}ms` }}
              >
                <CardContent className="p-4 sm:p-6">
                  <div className="flex h-10 w-10 sm:h-12 sm:w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-indigo-500/20 mb-3 sm:mb-4">
                    <Icon className="h-5 w-5 sm:h-6 sm:w-6 text-violet-500" />
                  </div>
                  <h3 className="font-semibold text-sm sm:text-base mb-1 sm:mb-2">
                    {t(`hero.features.${iconKey}.title`)}
                  </h3>
                  <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                    {t(`hero.features.${iconKey}.description`)}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="py-12 sm:py-16 md:py-20">
        <div className="container mx-auto px-4">
          <div className="relative overflow-hidden rounded-2xl sm:rounded-3xl bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 p-8 sm:p-12 md:p-16 text-white text-center">
            <div
              className="absolute inset-0 opacity-40"
              style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              }}
            />
            <div className="relative z-10 max-w-2xl mx-auto space-y-4 sm:space-y-6">
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold leading-tight">
                {t("hero.cta.title")}
              </h2>
              <p className="text-white/80 text-sm sm:text-lg leading-relaxed">
                {t("hero.cta.description")}
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 pt-2">
                <Link href="/auth/register">
                  <Button size="lg" variant="secondary" className="w-full sm:w-auto text-sm sm:text-base">
                    {t("hero.cta.getStarted")}
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/docs">
                  <Button
                    size="lg"
                    variant="outline"
                    className="w-full sm:w-auto border-white/30 text-white hover:bg-white/10 hover:text-white text-sm sm:text-base"
                  >
                    {t("hero.cta.readDocs")}
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
