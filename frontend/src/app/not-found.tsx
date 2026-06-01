"use client";

import { FileQuestion, Home, Search, Sparkles } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";

export default function NotFound() {
  const { t, isZh } = useI18n();

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12 bg-gradient-to-b from-background to-muted/30">
      <div className="w-full max-w-lg text-center space-y-8">
        <div className="relative inline-flex">
          <div className="absolute inset-0 rounded-full bg-primary/10 blur-2xl" />
          <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-primary/5 border border-primary/10">
            <FileQuestion className="h-12 w-12 text-primary" />
          </div>
        </div>

        <div className="space-y-3">
          <p className="text-7xl sm:text-8xl font-extrabold tracking-tight bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent select-none">
            404
          </p>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
            {t("errors.notFoundTitle")}
          </h1>
          <p className="text-muted-foreground text-sm sm:text-base max-w-md mx-auto">
            {t("errors.notFoundDescription")}
          </p>
          <p className="text-xs text-muted-foreground/80 sm:hidden">
            {isZh
              ? "请检查链接是否正确,或返回首页继续浏览。"
              : "Check the URL or return home to keep exploring."}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link href="/" className="w-full sm:w-auto min-w-[150px]">
            <Button variant="default" size="lg" className="w-full">
              <Home className="mr-2 h-4 w-4" />
              {t("errors.goHome")}
            </Button>
          </Link>
          <Link href="/skills" className="w-full sm:w-auto min-w-[150px]">
            <Button variant="outline" size="lg" className="w-full">
              <Sparkles className="mr-2 h-4 w-4" />
              {t("errors.browseSkills")}
            </Button>
          </Link>
        </div>

        <div className="pt-2 text-xs text-muted-foreground/70">
          <Link
            href="/search"
            className="inline-flex items-center gap-1 hover:text-foreground transition-colors"
          >
            <Search className="h-3 w-3" />
            {isZh ? "或者尝试搜索" : "Or try searching"}
          </Link>
        </div>
      </div>
    </div>
  );
}
