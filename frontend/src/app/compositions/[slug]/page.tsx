"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Home,
  ChevronRight,
  GitBranch,
  Box,
  ArrowRight,
  ArrowUpRight,
  AlertTriangle,
  Download,
  Star,
  Eye,
  Clock,
  Share2,
  Heart,
  Play,
  Settings,
  Layers,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { useComposition } from "@/hooks/useSkills";
import { useI18n } from "@/lib/i18n";
import { formatDate, formatNumber, getInitials, cn } from "@/lib/utils";
import type { CompositionNode } from "@/types";

export default function CompositionDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: composition, isLoading } = useComposition(slug);
  const { t } = useI18n();

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 space-y-6">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-12 w-96" />
        <Skeleton className="h-[500px] w-full rounded-xl" />
      </div>
    );
  }

  if (!composition) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <AlertTriangle className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-2xl font-bold mb-2">{t("compositionDetail.notFoundTitle")}</h2>
        <p className="text-muted-foreground mb-4">
          {t("compositionDetail.notFoundDescription")}
        </p>
        <Link href="/compositions">
          <Button>{t("compositionDetail.browseCompositions")}</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <nav className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
        <Link href="/" className="hover:text-foreground transition-colors">
          <Home className="h-3.5 w-3.5" />
        </Link>
        <ChevronRight className="h-3.5 w-3.5" />
        <Link href="/compositions" className="hover:text-foreground transition-colors">
          {t("compositionDetail.breadcrumb")}
        </Link>
        <ChevronRight className="h-3.5 w-3.5" />
        <span className="text-foreground font-medium truncate">{composition.name}</span>
      </nav>

      <div className="flex flex-col lg:flex-row gap-8">
        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-4 mb-6">
            <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20">
              <GitBranch className="h-8 w-8 text-emerald-500" />
            </div>

            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-3 mb-2">
                <h1 className="text-2xl sm:text-3xl font-bold">{composition.name}</h1>
                <Badge className={composition.is_public ? "bg-emerald-500/10 text-emerald-500" : "bg-muted text-muted-foreground"}>
                  {composition.is_public ? t("compositionDetail.public") : t("compositionDetail.private")}
                </Badge>
              </div>
              <p className="text-muted-foreground mb-3">{composition.description}</p>
              <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                {composition.owner && (
                  <span className="flex items-center gap-1.5">
                    <Avatar className="h-5 w-5">
                      <AvatarImage src={composition.owner.avatar_url || undefined} />
                      <AvatarFallback className="text-[8px]">
                        {getInitials(
                          composition.owner.full_name || composition.owner.username
                        )}
                      </AvatarFallback>
                    </Avatar>
                    @{composition.owner.username}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {t("compositionDetail.updatedRelative", { time: formatDate(composition.updated_at, "relative") })}
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 mb-6">
            <Button variant="gradient">
              <Play className="mr-2 h-4 w-4" />
              {t("compositionDetail.runComposition")}
            </Button>
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              {t("compositionDetail.export")}
            </Button>
            <Button variant="ghost" size="icon">
              <Heart className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon">
              <Share2 className="h-4 w-4" />
            </Button>
          </div>

          <Tabs defaultValue="workflow" className="mt-6">
            <TabsList>
              <TabsTrigger value="workflow">{t("compositionDetail.workflowTab")}</TabsTrigger>
              <TabsTrigger value="schema">{t("compositionDetail.schemaTab")}</TabsTrigger>
              <TabsTrigger value="details">{t("compositionDetail.detailsTab")}</TabsTrigger>
            </TabsList>

            <TabsContent value="workflow" className="mt-4">
              <Card>
                <CardContent className="p-6">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <GitBranch className="h-4 w-4" />
                    {t("compositionDetail.workflowVisualization")}
                  </h3>

                  <div className="relative bg-muted/50 rounded-xl p-8 min-h-[400px] overflow-auto">
                    <div className="flex flex-col items-center gap-4">
                      {composition.items.map((node: CompositionNode, index: number) => (
                        <div key={node.id} className="flex flex-col items-center">
                          <Link
                            href={node.skill ? `/skills/${node.skill.slug}` : "#"}
                            className="flex items-center gap-3 p-4 rounded-xl border bg-card hover:border-primary/50 hover:shadow-md transition-all w-72"
                          >
                            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500/20 to-indigo-500/20">
                              <Box className="h-5 w-5 text-violet-500" />
                            </div>
                            <div className="min-w-0 flex-1">
                              <p className="font-medium text-sm truncate">
                                {node.skill?.name || t("compositionDetail.unknownSkill")}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {t("compositionDetail.step", { n: node.sort_order + 1 })}
                              </p>
                            </div>
                            <ArrowUpRight className="h-4 w-4 text-muted-foreground shrink-0" />
                          </Link>

                          {index < composition.items.length - 1 && (
                            <div className="flex flex-col items-center py-2">
                              <div className="w-0.5 h-8 bg-gradient-to-b from-primary/50 to-primary/20" />
                              <ArrowRight className="h-4 w-4 text-primary" />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {composition.items.map((node: CompositionNode) => (
                      <div key={node.id} className="hidden">
                        {node.notes}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="schema" className="mt-4">
              <Card>
                <CardContent className="p-6">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Settings className="h-4 w-4" />
                    {t("compositionDetail.inputOutputSchema")}
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                    <h4 className="text-sm font-semibold mb-3">{t("compositionDetail.metadata")}</h4>
                    <div className="bg-muted rounded-lg p-4">
                      {composition.metadata && Object.keys(composition.metadata).length > 0 ? (
                        <pre className="text-xs overflow-x-auto">
                          <code>{JSON.stringify(composition.metadata, null, 2)}</code>
                        </pre>
                      ) : (
                        <p className="text-sm text-muted-foreground">
                          {t("compositionDetail.noMetadata")}
                        </p>
                      )}
                    </div>
                  </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="details" className="mt-4">
              <Card>
                <CardContent className="p-6">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Layers className="h-4 w-4" />
                    {t("compositionDetail.nodeDetails")}
                  </h3>
                  <div className="space-y-4">
                    {composition.items.map((node: CompositionNode) => (
                      <div key={node.id} className="p-4 rounded-lg border">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant="purple" className="text-xs">
                            {t("compositionDetail.step", { n: node.sort_order + 1 })}
                          </Badge>
                          <span className="font-medium text-sm">
                            {node.skill?.name || t("compositionDetail.unknownSkill")}
                          </span>
                        </div>
                        {node.notes && (
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">{t("compositionDetail.notes")}</p>
                            <p className="text-sm">{node.notes}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <aside className="lg:w-72 shrink-0 space-y-6">
          {composition.owner && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">{t("common.author")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={composition.owner.avatar_url || undefined} />
                    <AvatarFallback>
                      {getInitials(
                        composition.owner.full_name || composition.owner.username
                      )}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium text-sm">{composition.owner.full_name}</p>
                    <p className="text-xs text-muted-foreground">
                      @{composition.owner.username}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">{t("compositionDetail.stats")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">{t("compositionDetail.items")}</span>
                <span className="font-medium">{composition.items.length}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">{t("compositionDetail.created")}</span>
                <span className="font-medium">{formatDate(composition.created_at, "short")}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">{t("compositionDetail.updated")}</span>
                <span className="font-medium">{formatDate(composition.updated_at, "short")}</span>
              </div>
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  );
}