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
import { formatDate, formatNumber, getInitials, getStatusColor, cn } from "@/lib/utils";
import type { CompositionNode, CompositionEdge } from "@/types";

export default function CompositionDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: composition, isLoading } = useComposition(slug);

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
        <h2 className="text-2xl font-bold mb-2">Composition Not Found</h2>
        <p className="text-muted-foreground mb-4">
          The composition you are looking for does not exist or has been removed.
        </p>
        <Link href="/compositions">
          <Button>Browse Compositions</Button>
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
          Compositions
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
                <Badge className={cn(getStatusColor(composition.status))}>
                  {composition.status}
                </Badge>
              </div>
              <p className="text-muted-foreground mb-3">{composition.description}</p>
              <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                {composition.author && (
                  <span className="flex items-center gap-1.5">
                    <Avatar className="h-5 w-5">
                      <AvatarImage src={composition.author.avatar_url || undefined} />
                      <AvatarFallback className="text-[8px]">
                        {getInitials(
                          composition.author.full_name || composition.author.username
                        )}
                      </AvatarFallback>
                    </Avatar>
                    @{composition.author.username}
                  </span>
                )}
                {composition.metrics && (
                  <span className="flex items-center gap-1">
                    <Star className="h-4 w-4 text-amber-500 fill-amber-500" />
                    {composition.metrics.average_rating.toFixed(1)}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  Updated {formatDate(composition.updated_at, "relative")}
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 mb-6">
            <Button variant="gradient">
              <Play className="mr-2 h-4 w-4" />
              Run Composition
            </Button>
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Export
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
              <TabsTrigger value="workflow">Workflow</TabsTrigger>
              <TabsTrigger value="schema">Schema</TabsTrigger>
              <TabsTrigger value="details">Details</TabsTrigger>
            </TabsList>

            <TabsContent value="workflow" className="mt-4">
              <Card>
                <CardContent className="p-6">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <GitBranch className="h-4 w-4" />
                    Workflow Visualization
                  </h3>

                  <div className="relative bg-muted/50 rounded-xl p-8 min-h-[400px] overflow-auto">
                    <div className="flex flex-col items-center gap-4">
                      {composition.nodes.map((node: CompositionNode, index: number) => (
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
                                {node.skill?.name || `Node ${node.id}`}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                Step {index + 1}
                              </p>
                            </div>
                            <ArrowUpRight className="h-4 w-4 text-muted-foreground shrink-0" />
                          </Link>

                          {index < composition.nodes.length - 1 && (
                            <div className="flex flex-col items-center py-2">
                              <div className="w-0.5 h-8 bg-gradient-to-b from-primary/50 to-primary/20" />
                              <ArrowRight className="h-4 w-4 text-primary" />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {composition.edges.map((edge: CompositionEdge) => (
                      <div key={edge.id} className="hidden">
                        {edge.label}
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
                    Input/Output Schema
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-sm font-semibold mb-3">Input Schema</h4>
                      <div className="bg-muted rounded-lg p-4">
                        {composition.input_schema ? (
                          <pre className="text-xs overflow-x-auto">
                            <code>{JSON.stringify(composition.input_schema, null, 2)}</code>
                          </pre>
                        ) : (
                          <p className="text-sm text-muted-foreground">
                            No input schema defined
                          </p>
                        )}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-semibold mb-3">Output Schema</h4>
                      <div className="bg-muted rounded-lg p-4">
                        {composition.output_schema ? (
                          <pre className="text-xs overflow-x-auto">
                            <code>{JSON.stringify(composition.output_schema, null, 2)}</code>
                          </pre>
                        ) : (
                          <p className="text-sm text-muted-foreground">
                            No output schema defined
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
                    Node Details
                  </h3>
                  <div className="space-y-4">
                    {composition.nodes.map((node: CompositionNode, index: number) => (
                      <div key={node.id} className="p-4 rounded-lg border">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant="purple" className="text-xs">
                            Step {index + 1}
                          </Badge>
                          <span className="font-medium text-sm">
                            {node.skill?.name || "Unknown Skill"}
                          </span>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Input Mapping</p>
                            <pre className="text-xs bg-muted rounded p-2 overflow-x-auto">
                              <code>{JSON.stringify(node.input_mapping, null, 2)}</code>
                            </pre>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Output Mapping</p>
                            <pre className="text-xs bg-muted rounded p-2 overflow-x-auto">
                              <code>{JSON.stringify(node.output_mapping, null, 2)}</code>
                            </pre>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <aside className="lg:w-72 shrink-0 space-y-6">
          {composition.author && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Author</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={composition.author.avatar_url || undefined} />
                    <AvatarFallback>
                      {getInitials(
                        composition.author.full_name || composition.author.username
                      )}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium text-sm">{composition.author.full_name}</p>
                    <p className="text-xs text-muted-foreground">
                      @{composition.author.username}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Nodes</span>
                <span className="font-medium">{composition.nodes.length}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Edges</span>
                <span className="font-medium">{composition.edges.length}</span>
              </div>
              {composition.metrics && (
                <>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Downloads</span>
                    <span className="font-medium">
                      {formatNumber(composition.metrics.downloads_count)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Rating</span>
                    <span className="font-medium flex items-center gap-1">
                      <Star className="h-3.5 w-3.5 text-amber-500 fill-amber-500" />
                      {composition.metrics.average_rating.toFixed(1)}
                    </span>
                  </div>
                </>
              )}
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Created</span>
                <span className="font-medium">{formatDate(composition.created_at, "short")}</span>
              </div>
            </CardContent>
          </Card>

          {composition.tags && composition.tags.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Tags</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {composition.tags.map((tag) => (
                    <Badge key={tag.id} variant="secondary">
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