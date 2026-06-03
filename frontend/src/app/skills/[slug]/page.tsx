"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Download,
  Star,
  Eye,
  Clock,
  GitBranch,
  ExternalLink,
  BookOpen,
  Github,
  ChevronRight,
  Home,
  Copy,
  Check,
  Heart,
  Share2,
  AlertTriangle,
  Box,
  Users,
  Calendar,
  Tag,
  ArrowUpRight,
  ArrowLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { SkillRating } from "@/components/SkillRating";
import { SkillCard } from "@/components/SkillCard";
import {
  useSkill,
  useSkillVersions,
  useSkillDependencies,
  useSkillReviews,
  useSimilarSkills,
  useDownloadSkill,
} from "@/hooks/useSkills";
import { formatDate, formatNumber, getInitials, getStatusColor, cn } from "@/lib/utils";
import { isAuthenticated } from "@/lib/auth";
import { useI18n } from "@/lib/i18n";
import type { SkillReview } from "@/types";

export default function SkillDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { t, locale } = useI18n();
  const { data: skill, isLoading } = useSkill(slug);
  const { data: versions } = useSkillVersions(slug);
  const { data: dependencies } = useSkillDependencies(slug);
  const { data: reviewsData } = useSkillReviews(slug);
  const { data: similarSkills } = useSimilarSkills(slug);
  const downloadMutation = useDownloadSkill();
  const [copied, setCopied] = useState(false);

  const handleCopyInstall = () => {
    if (skill) {
      navigator.clipboard.writeText(`skill install ${skill.slug}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-6 sm:py-8 space-y-6">
        <Skeleton className="h-5 w-40 sm:w-48" />
        <div className="flex gap-4 sm:gap-6">
          <Skeleton className="h-24 w-24 sm:h-32 sm:w-32 rounded-xl shrink-0" />
          <div className="space-y-3 flex-1 min-w-0">
            <Skeleton className="h-7 w-56 sm:h-8 sm:w-72" />
            <Skeleton className="h-4 w-full max-w-[400px]" />
            <Skeleton className="h-4 w-3/4" />
            <div className="flex gap-2 pt-2">
              <Skeleton className="h-10 w-28 rounded-lg" />
              <Skeleton className="h-10 w-10 rounded-lg" />
              <Skeleton className="h-10 w-10 rounded-lg" />
            </div>
          </div>
        </div>
        <Skeleton className="h-[300px] sm:h-[400px] w-full rounded-xl" />
      </div>
    );
  }

  if (!skill) {
    return (
      <div className="container mx-auto px-4 py-16 sm:py-20 text-center">
        <AlertTriangle className="h-12 w-12 sm:h-16 sm:w-16 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl sm:text-2xl font-bold mb-2">{t("skillDetail.notFound")}</h2>
        <p className="text-sm sm:text-base text-muted-foreground mb-4 max-w-md mx-auto">
          {t("skillDetail.notFoundDesc")}
        </p>
        <Link href="/skills">
          <Button>{t("skillDetail.browseSkills")}</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 sm:py-8">
      <nav className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-muted-foreground mb-4 sm:mb-6 overflow-x-auto pb-2 scrollbar-none -mx-4 px-4 sm:mx-0 sm:px-0">
        <Link href="/" className="hover:text-foreground transition-colors shrink-0 flex items-center">
          <Home className="h-3.5 w-3.5" />
        </Link>
        <ChevronRight className="h-3 w-3 sm:h-3.5 sm:w-3.5 shrink-0" />
        <Link href="/skills" className="hover:text-foreground transition-colors shrink-0 truncate">
          {t("common.skills")}
        </Link>
        <ChevronRight className="h-3 w-3 sm:h-3.5 sm:w-3.5 shrink-0" />
        {skill.category && (
          <>
            <Link
              href={`/categories/${skill.category.slug}`}
              className="hover:text-foreground transition-colors shrink-0 truncate"
            >
              {skill.category.name}
            </Link>
            <ChevronRight className="h-3 w-3 sm:h-3.5 sm:w-3.5 shrink-0" />
          </>
        )}
        <span className="text-foreground font-medium truncate">{skill.name}</span>
      </nav>

      <div className="flex flex-col lg:flex-row gap-6 lg:gap-8">
        <div className="flex-1 min-w-0 space-y-5 sm:space-y-6">
          <div className="space-y-4">
            <div className="flex items-start gap-3 sm:gap-4">
              <div className="flex h-14 w-14 sm:h-20 sm:w-20 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-indigo-500/20">
                {skill.icon_url ? (
                  <img
                    src={skill.icon_url}
                    alt={skill.name}
                    className="h-9 w-9 sm:h-12 sm:w-12 rounded-lg object-cover"
                  />
                ) : (
                  <Box className="h-7 w-7 sm:h-10 sm:w-10 text-violet-500" />
                )}
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2 mb-1.5 sm:mb-2">
                  <h1 className="text-xl sm:text-2xl md:text-3xl font-bold leading-tight">{skill.name}</h1>
                  <Badge className={cn(getStatusColor(skill.status), "text-xs")}>{skill.status}</Badge>
                  <Badge variant="outline" className="text-xs">v{skill.version}</Badge>
                </div>

                <p className="text-xs sm:text-sm text-muted-foreground mb-2 sm:mb-3 line-clamp-2">
                  {skill.description}
                </p>

                <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs sm:text-sm text-muted-foreground">
                  {skill.metrics && (
                    <>
                      <span className="flex items-center gap-1">
                        <Star className="h-3.5 w-3.5 text-amber-500 fill-amber-500" />
                        {skill.metrics.average_rating.toFixed(1)}
                        <span className="text-muted-foreground/70">
                          ({skill.metrics.ratings_count})
                        </span>
                      </span>
                      <span className="flex items-center gap-1">
                        <Download className="h-3.5 w-3.5" />
                        {formatNumber(skill.metrics.downloads_count, locale)}
                      </span>
                      <span className="flex items-center gap-1 hidden sm:inline-flex">
                        <Eye className="h-3.5 w-3.5" />
                        {formatNumber(skill.metrics.views_count, locale)}
                      </span>
                    </>
                  )}
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" />
                    {formatDate(skill.updated_at, "relative", locale)}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
              <Button
                variant="gradient"
                onClick={() => downloadMutation.mutate({ slug: skill.slug })}
                disabled={downloadMutation.isPending}
                className="w-full sm:w-auto h-11 md:h-12"
              >
                <Download className="mr-2 h-4 w-4" />
                {t("skillDetail.download")}
              </Button>
              <Button variant="outline" onClick={handleCopyInstall} className="w-full sm:w-auto h-11 md:h-12">
                {copied ? (
                  <Check className="mr-2 h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="mr-2 h-4 w-4" />
                )}
                {copied ? t("skillDetail.copied") : t("skillDetail.copyInstall")}
              </Button>
              <div className="flex gap-2">
                <Button variant="ghost" size="icon" className="h-11 w-11 md:h-12 md:w-12">
                  <Heart className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-11 w-11 md:h-12 md:w-12">
                  <Share2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          <Tabs defaultValue="overview" className="mt-4 sm:mt-6">
            <TabsList className="w-full justify-start overflow-x-auto scrollbar-hide h-auto p-0.5 bg-muted/50 rounded-lg">
              <TabsTrigger value="overview" className="text-xs sm:text-sm px-2 sm:px-3 py-2 whitespace-nowrap data-[state=active]:bg-background shadow-sm rounded-md">
                {t("skillDetail.overview")}
              </TabsTrigger>
              <TabsTrigger value="usage" className="text-xs sm:text-sm px-2 sm:px-3 py-2 whitespace-nowrap data-[state=active]:bg-background shadow-sm rounded-md">
                {t("skillDetail.usage")}
              </TabsTrigger>
              <TabsTrigger value="dependencies" className="text-xs sm:text-sm px-2 sm:px-3 py-2 whitespace-nowrap data-[state=active]:bg-background shadow-sm rounded-md">
                {t("skillDetail.dependencies")}
              </TabsTrigger>
              <TabsTrigger value="versions" className="text-xs sm:text-sm px-2 sm:px-3 py-2 whitespace-nowrap data-[state=active]:bg-background shadow-sm rounded-md">
                {t("skillDetail.versions")}
              </TabsTrigger>
              <TabsTrigger value="reviews" className="text-xs sm:text-sm px-2 sm:px-3 py-2 whitespace-nowrap data-[state=active]:bg-background shadow-sm rounded-md">
                {t("skillDetail.reviews")}
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-4 sm:mt-6">
              <Card>
                <CardContent className="p-4 sm:p-6">
                  {skill.long_description ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <p className="whitespace-pre-wrap text-sm sm:text-base leading-relaxed">{skill.long_description}</p>
                    </div>
                  ) : (
                    <p className="text-sm sm:text-base text-muted-foreground">
                      {t("skillDetail.noDescription")}
                    </p>
                  )}

                  {skill.tags && skill.tags.length > 0 && (
                    <div className="mt-6 pt-6 border-t">
                      <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                        <Tag className="h-4 w-4" />
                        {t("skillDetail.tags")}
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {skill.tags.map((tag) => (
                          <Badge key={tag.id} variant="secondary" className="text-xs">
                            {tag.name}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {(skill.homepage_url || skill.repository_url || skill.documentation_url) && (
                    <div className="mt-6 pt-6 border-t">
                      <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                        <ExternalLink className="h-4 w-4" />
                        {t("skillDetail.links")}
                      </h4>
                      <div className="space-y-2">
                        {skill.homepage_url && (
                          <a
                            href={skill.homepage_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-sm text-primary hover:underline"
                          >
                            <ExternalLink className="h-3.5 w-3.5" />
                            {t("skillDetail.homepage")}
                          </a>
                        )}
                        {skill.repository_url && (
                          <a
                            href={skill.repository_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-sm text-primary hover:underline"
                          >
                            <Github className="h-3.5 w-3.5" />
                            {t("skillDetail.repository")}
                          </a>
                        )}
                        {skill.documentation_url && (
                          <a
                            href={skill.documentation_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-sm text-primary hover:underline"
                          >
                            <BookOpen className="h-3.5 w-3.5" />
                            {t("skillDetail.documentation")}
                          </a>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="usage" className="mt-4 sm:mt-6">
              <Card>
                <CardContent className="p-4 sm:p-6">
                  <h3 className="font-semibold text-base sm:text-lg mb-4">{t("skillDetail.howToUse")}</h3>
                  <div className="bg-muted rounded-lg p-3 sm:p-4 overflow-x-auto">
                    <pre className="text-xs sm:text-sm overflow-x-auto">
                      <code>{`# Install the skill\nskill install ${skill.slug}\n\n# Import in your project\nimport { ${skill.slug.replace(/-/g, "_")} } from "@skills/${skill.slug}";\n\n# Basic usage\nconst result = await ${skill.slug.replace(/-/g, "_")}({\n  input: "your input here",\n  // ... other parameters\n});`}</code>
                    </pre>
                  </div>

                  <div className="mt-6">
                    <h4 className="font-semibold text-sm sm:text-base mb-2">{t("skillDetail.apiReference")}</h4>
                    <p className="text-xs sm:text-sm text-muted-foreground">
                      {t("skillDetail.apiReferenceDesc")}{" "}
                      <Link
                        href={skill.documentation_url || "/docs"}
                        className="text-primary hover:underline"
                      >
                        {t("skillDetail.documentationPage")}
                      </Link>
                      .
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="dependencies" className="mt-4 sm:mt-6">
              <Card>
                <CardContent className="p-4 sm:p-6">
                  <h3 className="font-semibold text-base sm:text-lg mb-4 flex items-center gap-2">
                    <GitBranch className="h-4 w-4" />
                    {t("skillDetail.dependencies")}
                  </h3>
                  {dependencies && dependencies.length > 0 ? (
                    <div className="space-y-3">
                      {dependencies.map((dep) => (
                        <Link
                          key={dep.id}
                          href={`/skills/${dep.slug}`}
                          className="flex items-center gap-3 p-3 rounded-lg border hover:border-primary/50 transition-colors"
                        >
                          <div className="flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500/20 to-indigo-500/20 shrink-0">
                            <Box className="h-4 w-4 sm:h-5 sm:w-5 text-violet-500" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm">{dep.name}</p>
                            <p className="text-xs text-muted-foreground truncate">
                              {dep.description}
                            </p>
                          </div>
                          <ArrowUpRight className="h-4 w-4 text-muted-foreground shrink-0" />
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      {t("skillDetail.noDependencies")}
                    </p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="versions" className="mt-4 sm:mt-6">
              <Card>
                <CardContent className="p-4 sm:p-6">
                  <h3 className="font-semibold text-base sm:text-lg mb-4 flex items-center gap-2">
                    <GitBranch className="h-4 w-4" />
                    {t("skillDetail.versionHistory")}
                  </h3>
                  {versions && versions.length > 0 ? (
                    <div className="space-y-4">
                      {versions.map((version) => (
                        <div
                          key={version.id}
                          className="flex items-start gap-3 sm:gap-4 p-3 rounded-lg border"
                        >
                          <div className="flex flex-col items-center">
                            <div
                              className={cn(
                                "h-2.5 w-2.5 sm:h-3 sm:w-3 rounded-full",
                                version.is_latest
                                  ? "bg-primary ring-2 ring-primary/30"
                                  : "bg-muted-foreground/30"
                              )}
                            />
                            <div className="w-px h-full bg-border mt-1" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-sm">{version.version}</span>
                              {version.is_latest && (
                                <Badge variant="purple" className="text-xs">
                                  {t("skillDetail.latest")}
                                </Badge>
                              )}
                            </div>
                            <p className="text-xs sm:text-sm text-muted-foreground mb-1">
                              {version.changelog}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {formatDate(version.created_at, "short", locale)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      {t("skillDetail.noVersions")}
                    </p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="reviews" className="mt-4 sm:mt-6">
              <Card>
                <CardContent className="p-4 sm:p-6">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-3">
                    <h3 className="font-semibold text-base sm:text-lg flex items-center gap-2">
                      <Star className="h-4 w-4" />
                      {t("skillDetail.reviews")}
                      {skill.metrics && (
                        <span className="text-muted-foreground font-normal text-sm">
                          ({skill.metrics.ratings_count})
                        </span>
                      )}
                    </h3>
                    {isAuthenticated() && (
                      <Button variant="outline" size="sm" className="shrink-0">
                        {t("skillDetail.writeReview")}
                      </Button>
                    )}
                  </div>

                  {reviewsData && reviewsData.items.length > 0 ? (
                    <div className="space-y-4">
                      {reviewsData.items.map((review: SkillReview) => (
                        <div key={review.id} className="p-3 sm:p-4 rounded-lg border">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2 sm:gap-3">
                              <Avatar className="h-7 w-7 sm:h-8 sm:w-8">
                                <AvatarImage
                                  src={review.user?.avatar_url || undefined}
                                />
                                <AvatarFallback className="text-[10px] sm:text-xs">
                                  {review.user
                                    ? getInitials(review.user.full_name || review.user.username)
                                    : "U"}
                                </AvatarFallback>
                              </Avatar>
                              <div>
                                <p className="text-xs sm:text-sm font-medium">
                                  {review.user?.full_name || review.user?.username || "Anonymous"}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  {formatDate(review.created_at, "relative", locale)}
                                </p>
                              </div>
                            </div>
                            <SkillRating value={review.rating} readonly size="sm" />
                          </div>
                          <h4 className="font-medium text-sm mb-1">{review.title}</h4>
                          <p className="text-xs sm:text-sm text-muted-foreground">{review.content}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 sm:py-12">
                      <Star className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                      <p className="text-sm text-muted-foreground">
                        {t("skillDetail.noReviews")}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <aside className="lg:w-80 shrink-0 space-y-4 sm:space-y-6 order-first lg:order-last">
          {skill.author && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-xs sm:text-sm flex items-center gap-2">
                  <Users className="h-3.5 w-3.5" />
                  {t("skillDetail.author")}
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex items-center gap-3">
                  <Avatar className="h-9 w-9 sm:h-10 sm:w-10">
                    <AvatarImage src={skill.author.avatar_url || undefined} />
                    <AvatarFallback className="text-xs">
                      {getInitials(skill.author.full_name || skill.author.username)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="min-w-0">
                    <p className="font-medium text-sm truncate">{skill.author.full_name}</p>
                    <p className="text-xs text-muted-foreground">@{skill.author.username}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-xs sm:text-sm">{t("skillDetail.stats")}</CardTitle>
            </CardHeader>
            <CardContent className="pt-0 space-y-2.5 sm:space-y-3">
              {skill.metrics && (
                <>
                  <div className="flex items-center justify-between text-xs sm:text-sm">
                    <span className="text-muted-foreground flex items-center gap-1.5 sm:gap-2">
                      <Download className="h-3.5 w-3.5" />
                      {t("skillDetail.downloads")}
                    </span>
                    <span className="font-medium">{formatNumber(skill.metrics.downloads_count, locale)}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs sm:text-sm">
                    <span className="text-muted-foreground flex items-center gap-1.5 sm:gap-2">
                      <Eye className="h-3.5 w-3.5" />
                      {t("skillDetail.views")}
                    </span>
                    <span className="font-medium">{formatNumber(skill.metrics.views_count, locale)}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs sm:text-sm">
                    <span className="text-muted-foreground flex items-center gap-1.5 sm:gap-2">
                      <Heart className="h-3.5 w-3.5 fill-none" />
                      {t("skillDetail.likes")}
                    </span>
                    <span className="font-medium">{formatNumber(skill.metrics.likes_count, locale)}</span>
                  </div>
                </>
              )}
              <div className="flex items-center justify-between text-xs sm:text-sm">
                <span className="text-muted-foreground flex items-center gap-1.5 sm:gap-2">
                  <Calendar className="h-3.5 w-3.5" />
                  {t("skillDetail.created")}
                </span>
                <span className="font-medium">{formatDate(skill.created_at, "short", locale)}</span>
              </div>
              {skill.license && (
                <div className="flex items-center justify-between text-xs sm:text-sm">
                  <span className="text-muted-foreground">{t("skillDetail.license")}</span>
                  <span className="font-medium">{skill.license}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {similarSkills && similarSkills.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-xs sm:text-sm">{t("skillDetail.similarSkills")}</CardTitle>
              </CardHeader>
              <CardContent className="pt-0 space-y-2 sm:space-y-3">
                <div className="flex lg:flex-col gap-2 sm:gap-3 overflow-x-auto pb-1 lg:overflow-visible scrollbar-hide">
                  {similarSkills.slice(0, 5).map((similar) => (
                    <Link
                      key={similar.id}
                      href={`/skills/${similar.slug}`}
                      className="flex items-center gap-2 sm:gap-3 p-2 sm:p-2.5 rounded-lg hover:bg-accent transition-colors shrink-0 lg:shrink"
                    >
                      <div className="flex h-8 w-8 sm:h-8 sm:w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500/20 to-indigo-500/20 shrink-0">
                        <Box className="h-4 w-4 text-violet-500" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-xs sm:text-sm font-medium truncate">{similar.name}</p>
                        <p className="text-[10px] xs:text-xs text-muted-foreground truncate hidden xs:block">
                          {similar.description}
                        </p>
                      </div>
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {skill.tags && skill.tags.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-xs sm:text-sm">{t("skillDetail.tags")}</CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex flex-wrap gap-1.5">
                  {skill.tags.map((tag) => (
                    <Badge key={tag.id} variant="secondary" className="text-xs">
                      {tag.name}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </aside>
      </div>
    </div>
  );
}
