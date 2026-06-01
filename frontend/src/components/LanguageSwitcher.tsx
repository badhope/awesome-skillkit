"use client";

import { Globe } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import type { Locale } from "@/lib/i18n";

export function LanguageSwitcher() {
  const { locale, setLocale, isZh } = useI18n();

  const toggleLocale = () => {
    const next: Locale = isZh ? "en" : "zh";
    setLocale(next);
  };

  return (
    <button
      onClick={toggleLocale}
      className="relative inline-flex items-center gap-1.5 rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs font-medium text-foreground transition-all duration-200 hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 active:scale-95"
      aria-label={isZh ? "Switch to English" : "切换到中文"}
      title={isZh ? "Switch to English" : "切换到中文"}
    >
      <Globe className="h-3.5 w-3.5 shrink-0" />
      <span
        key={locale}
        className="inline-block transition-all duration-200 ease-out animate-fade-in"
      >
        {isZh ? "EN" : "中"}
      </span>
    </button>
  );
}
