"use client";

import { createContext, useContext, useState, useCallback, useMemo, useEffect } from "react";
import { translations } from "./translations";
import type { Locale } from "./translations";

type TranslationValue = string | Record<string, string | number | Record<string, unknown>>;

interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
  isZh: boolean;
}

const I18nContext = createContext<I18nContextType | null>(null);

function getNestedValue(obj: Record<string, unknown>, path: string): string {
  const result = path.split(".").reduce<unknown>(
    (acc, key) =>
      acc && typeof acc === "object" && key in acc ? (acc as Record<string, unknown>)[key] : undefined,
    obj
  );
  return typeof result === "string" ? result : path;
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  useEffect(() => {
    try {
      const stored = localStorage.getItem("locale") as Locale | null;
      if (stored && (stored === "en" || stored === "zh")) {
        setLocaleState(stored);
      }
    } catch {}
  }, []);

  const setLocale = useCallback((newLocale: Locale) => {
    setLocaleState(newLocale);
    try {
      localStorage.setItem("locale", newLocale);
    } catch {}
  }, []);

  const t = useCallback(
    (key: string, params?: Record<string, string | number>): string => {
      const value = getNestedValue(translations[locale] as unknown as Record<string, unknown>, key);
      let text = typeof value === "string" ? value : key;

      if (params) {
        Object.entries(params).forEach(([paramKey, paramValue]) => {
          text = text.replace(new RegExp(`\\{${paramKey}\\}`, "g"), String(paramValue));
        });
      }

      return text;
    },
    [locale]
  );

  const value = useMemo(
    () => ({ locale, setLocale, t, isZh: locale === "zh" }),
    [locale, setLocale, t]
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used within an I18nProvider");
  }
  return context;
}
