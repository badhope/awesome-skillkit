import { createContext, useContext, useState, useEffect, useCallback, useMemo } from "react";
import { translations, getTranslations } from "./translations";
import type { Locale, TranslationKeys } from "./types";

// Re-export so `import { Locale } from "@/lib/i18n"` and similar keep working.
export type { Locale, TranslationKeys } from "./types";
export { getTranslations } from "./translations";


export function getTranslations(locale: Locale): TranslationKeys {
  return translations[locale];
}

function getDefaultLocale(): Locale {
  if (typeof window === "undefined") return "en";
  const stored = localStorage.getItem("skilllib-locale") as Locale | null;
  if (stored && (stored === "en" || stored === "zh")) return stored;
  const browserLang = navigator.language.toLowerCase();
  if (browserLang.startsWith("zh")) return "zh";
  return "en";
}

export { translations };

type NestedObject = Record<string, unknown>;

function getNestedValue(obj: NestedObject, path: string): string {
  const keys = path.split(".");
  let current: unknown = obj;
  for (const key of keys) {
    if (current && typeof current === "object" && key in (current as NestedObject)) {
      current = (current as NestedObject)[key];
    } else {
      return path;
    }
  }
  return typeof current === "string" ? current : path;
}

// Quick {placeholder} replacement. Not as robust as a real i18n library —
// if a value happens to contain `{` it'll be replaced too. We accept that
// for now; if it bites, switch to intl-messageformat.
function interpolate(value: string, params?: Record<string, string | number>): string {
  if (!params) return value;
  let out = value;
  for (const [k, v] of Object.entries(params)) {
    out = out.replace(new RegExp(`\\{${k}\\}`, "g"), String(v));
  }
  return out;
}

export interface I18nContextType {
  t: (key: string, params?: Record<string, string | number>) => string;
  locale: Locale;
  isZh: boolean;
  setLocale: (locale: Locale) => void;
}

const I18nContext = createContext<I18nContextType | null>(null);

const LOCALE_STORAGE_KEY = "skilllib-locale";

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    // TODO: also accept a locale from a cookie so the server can pick it
    // before hydration. Right now the first paint is always English, which
    // flashes for non-en visitors.
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY) as Locale | null;
    if (stored === "en" || stored === "zh") {
      setLocaleState(stored);
    } else {
      // First visit: pick from the browser's preferred language.
      setLocaleState(navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en");
    }
    setMounted(true);
  }, []);

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next);
    if (typeof window !== "undefined") {
      localStorage.setItem(LOCALE_STORAGE_KEY, next);
      document.documentElement.lang = next === "zh" ? "zh-CN" : "en";
    }
  }, []);

  const t = useCallback(
    (key: string, params?: Record<string, string | number>): string => {
      let value = getNestedValue(translations[locale] as unknown as NestedObject, key);
      // Missing key in the active locale → fall back to English, then to
      // the key itself (which is a fine debugging signal in dev).
      if (value === key && locale !== "en") {
        value = getNestedValue(translations.en as unknown as NestedObject, key);
      }
      return interpolate(value, params);
    },
    [locale]
  );

  const value = useMemo<I18nContextType>(
    () => ({ t, locale, isZh: locale === "zh", setLocale }),
    [t, locale, setLocale]
  );

  // Before mount, render with the English dict so SSR/SSG output doesn't
  // briefly show "missing key" placeholders. The real locale lands in
  // the useEffect above.
  if (!mounted) {
    return (
      <I18nContext.Provider
        value={{
          t: (k, p) => interpolate(getNestedValue(translations.en as unknown as NestedObject, k), p),
          locale: "en",
          isZh: false,
          setLocale: () => {},
        }}
      >
        {children}
      </I18nContext.Provider>
    );
  }

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextType {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used within an I18nProvider");
  }
  return context;
}

export { I18nContext };

