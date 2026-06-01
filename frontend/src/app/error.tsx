"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCw, Home, Bug } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: ErrorPageProps) {
  const { t } = useI18n();

  useEffect(() => {
    if (typeof console !== "undefined") {
      console.error("Application error boundary caught:", error);
    }
  }, [error]);

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12 bg-gradient-to-b from-background to-muted/30">
      <div className="w-full max-w-lg text-center space-y-6">
        <div className="relative inline-flex">
          <div className="absolute inset-0 rounded-full bg-destructive/20 blur-2xl animate-pulse" />
          <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-destructive/10 border border-destructive/20">
            <AlertTriangle className="h-10 w-10 text-destructive" />
          </div>
        </div>

        <div className="space-y-2">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
            {t("errors.boundaryTitle")}
          </h1>
          <p className="text-muted-foreground text-sm sm:text-base">
            {t("errors.boundaryDescription")}
          </p>
          <p className="text-xs text-muted-foreground/80 sm:hidden">
            出现了一些问题，请重试或返回首页。
          </p>
        </div>

        {error?.message && (
          <div className="mx-auto max-w-md rounded-lg border bg-muted/50 p-3 text-left">
            <div className="flex items-start gap-2">
              <Bug className="h-4 w-4 mt-0.5 text-muted-foreground shrink-0" />
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-muted-foreground mb-1">
                  {t("errors.errorDetails")}
                </p>
                <p className="text-xs font-mono break-words text-foreground/80">
                  {error.message}
                </p>
                {error.digest && (
                  <p className="mt-1 text-[10px] font-mono text-muted-foreground">
                    ID: {error.digest}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Button
            onClick={reset}
            variant="default"
            size="lg"
            className="w-full sm:w-auto min-w-[140px]"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            {t("errors.tryAgain")}
          </Button>
          <Link href="/" className="w-full sm:w-auto min-w-[140px]">
            <Button variant="outline" size="lg" className="w-full">
              <Home className="mr-2 h-4 w-4" />
              {t("errors.backToHome")}
            </Button>
          </Link>
        </div>

        <p className="text-xs text-muted-foreground/70">
          {t("errors.supportHint")}
        </p>
      </div>
    </div>
  );
}
