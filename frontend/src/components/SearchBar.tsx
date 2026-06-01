"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  X,
  Loader2,
  Sparkles,
  Clock,
  TrendingUp,
  ArrowRight,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { useDebouncedSearch } from "@/hooks/useSearch";
import api from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { Skill } from "@/types";

export interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  className?: string;
  size?: "sm" | "md" | "lg" | "full";
}

const RECENT_SEARCHES_KEY = "skilllib-recent-searches";
const MAX_RECENT_SEARCHES = 5;

interface RecentSearch {
  query: string;
  timestamp: number;
}

function getRecentSearches(): RecentSearch[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(RECENT_SEARCHES_KEY);
    if (!raw) return [];
    const parsed: RecentSearch[] = JSON.parse(raw);
    return parsed.sort((a, b) => b.timestamp - a.timestamp).slice(0, MAX_RECENT_SEARCHES);
  } catch {
    return [];
  }
}

function saveRecentSearch(query: string): void {
  if (typeof window === "undefined" || !query.trim()) return;
  try {
    const existing = getRecentSearches();
    const filtered = existing.filter((s) => s.query !== query.trim());
    const updated = [{ query: query.trim(), timestamp: Date.now() }, ...filtered].slice(
      0,
      MAX_RECENT_SEARCHES
    );
    localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
  } catch {
    // ignore storage errors
  }
}

function clearRecentSearches(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(RECENT_SEARCHES_KEY);
  } catch {
    // ignore
  }
}

const POPULAR_SUGGESTIONS = [
  "AI Chat",
  "Image Generation",
  "Text Analysis",
  "Code Assistant",
  "Translation",
];

const sizeConfig = {
  sm: {
    container: "max-w-sm",
    input: "h-9 text-sm pl-9 pr-8 rounded-lg",
    icon: "h-4 w-4 left-3",
    itemMinH: "min-h-10",
  },
  md: {
    container: "max-w-xl",
    input: "h-10 text-sm pl-10 pr-10 rounded-xl",
    icon: "h-4 w-4 left-3",
    itemMinH: "min-h-11",
  },
  lg: {
    container: "max-w-2xl",
    input: "h-12 text-base pl-12 pr-12 rounded-xl",
    icon: "h-5 w-5 left-4",
    itemMinH: "min-h-12",
  },
  full: {
    container: "max-w-3xl",
    input: "h-14 md:h-16 text-base md:text-lg pl-12 md:pl-14 pr-14 md:pr-16 rounded-2xl",
    icon: "h-6 w-6 left-4 md:left-5",
    itemMinH: "min-h-14 md:min-h-16",
  },
};

function SearchSkeleton() {
  return (
    <div className="space-y-1 p-2">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex items-center gap-3 px-3 py-2.5">
          <Skeleton className="h-8 w-8 rounded-lg shrink-0" />
          <div className="flex-1 space-y-1.5">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function SearchBar({
  placeholder,
  onSearch,
  className,
  size = "md",
}: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Skill[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [isFocused, setIsFocused] = useState(false);
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const debouncedQuery = useDebouncedSearch(query, 300);
  const { t } = useI18n();
  const config = sizeConfig[size];

  useEffect(() => {
    setRecentSearches(getRecentSearches());
  }, []);

  useEffect(() => {
    if (!debouncedQuery || debouncedQuery.length < 2) {
      setResults([]);
      setIsLoading(false);
      return;
    }

    const fetchResults = async () => {
      setIsLoading(true);
      try {
        const data = await api.skills.search({
          q: debouncedQuery,
          page_size: size === "full" ? 8 : 5,
        });
        setResults(data.items);
        setIsOpen(true);
        setSelectedIndex(-1);
      } catch {
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [debouncedQuery, size]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setIsFocused(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("touchstart", handleClickOutside as EventListener);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside as EventListener);
    };
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const totalItems =
        results.length > 0
          ? results.length + 1
          : recentSearches.length > 0
            ? recentSearches.length + 1
            : 0;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < totalItems - 1 ? prev + 1 : totalItems > 0 ? 0 : -1
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : totalItems - 1));
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < results.length && results[selectedIndex]) {
          handleSelect(results[selectedIndex]!);
        } else if (results.length > 0) {
          handleSubmit();
        } else if (
          selectedIndex >= results.length &&
          selectedIndex < results.length + recentSearches.length
        ) {
          const idx = selectedIndex - results.length;
          const recent = recentSearches[idx];
          if (recent) {
            setQuery(recent.query);
            handleSubmitWith(recent.query);
          }
        } else {
          handleSubmit();
        }
      } else if (e.key === "Escape") {
        setIsOpen(false);
        setIsFocused(false);
        inputRef.current?.blur();
      }
    },
    [results, recentSearches, selectedIndex]
  );

  const handleSelect = useCallback(
    (skill: Skill) => {
      saveRecentSearch(skill.name);
      setIsOpen(false);
      setQuery("");
      setIsFocused(false);
      onSearch?.(skill.name);
      router.push(`/skills/${skill.slug}`);
    },
    [router, onSearch]
  );

  const handleSubmit = useCallback(() => {
    if (query.trim()) {
      saveRecentSearch(query);
      setIsOpen(false);
      setIsFocused(false);
      onSearch?.(query.trim());
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  }, [query, router, onSearch]);

  const handleSubmitWith = useCallback(
    (q: string) => {
      saveRecentSearch(q);
      setIsOpen(false);
      setIsFocused(false);
      onSearch?.(q);
      router.push(`/search?q=${encodeURIComponent(q)}`);
    },
    [router, onSearch]
  );

  const handleClear = () => {
    setQuery("");
    setResults([]);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const showDropdown =
    isOpen &&
    (isLoading ||
      results.length > 0 ||
      (query.length >= 2 && !isLoading) ||
      (!query && (recentSearches.length > 0 || true)));

  return (
    <div ref={containerRef} className={cn("relative w-full", config.container, className)}>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
      >
        <div className="relative group">
          <Search
            className={cn(
              "absolute top-1/2 -translate-y-1/2 text-muted-foreground transition-all duration-200",
              config.icon,
              isFocused && "scale-110 text-primary"
            )}
          />
          <Input
            ref={inputRef}
            type="search"
            placeholder={
              placeholder ||
              (size === "full"
                ? t("search.placeholder_hero")
                : size === "md"
                  ? t("search.placeholder_nav")
                  : t("search.placeholder"))
            }
            className={cn(
              config.input,
              "bg-muted/50 border-muted-foreground/20 focus-visible:bg-background focus-visible:border-primary/50 shadow-sm transition-all duration-200"
            )}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => {
              setIsFocused(true);
              if ((query && results.length > 0) || (!query && recentSearches.length > 0)) {
                setIsOpen(true);
              } else if (!query) {
                setIsOpen(true);
              }
            }}
          />

          {/* Right side controls */}
          <div className={cn("absolute top-1/2 -translate-y-1/2 flex items-center gap-1", size === "sm" ? "right-2.5" : "right-3")}>
            {isLoading && <Loader2 className={cn("animate-spin text-muted-foreground", size === "sm" ? "h-3.5 w-3.5" : "h-5 w-5")} />}
            {query && !isLoading && (
              <button
                type="button"
                onClick={handleClear}
                className={cn(
                  "rounded-full hover:bg-muted transition-colors",
                  size === "sm" ? "p-0.5" : "p-1"
                )}
                aria-label={t("search.clear_search")}
              >
                <X className={cn("text-muted-foreground", size === "sm" ? "h-3 w-3" : "h-4 w-4")} />
              </button>
            )}
          </div>
        </div>
      </form>

      {/* Dropdown */}
      {showDropdown && (
        <div
          className={cn(
            "absolute top-full mt-2 w-full rounded-xl border bg-popover shadow-2xl overflow-hidden z-50 animate-in fade-in-0 zoom-in-95 duration-200 max-h-[60vh] md:max-h-[70vh] overflow-y-auto"
          )}
          role="listbox"
        >
          {isLoading ? (
            <SearchSkeleton />
          ) : results.length > 0 ? (
            <>
              <div className="p-1.5">
                {results.map((skill, index) => (
                  <button
                    key={skill.id}
                    role="option"
                    aria-selected={index === selectedIndex}
                    onClick={() => handleSelect(skill)}
                    onMouseEnter={() => setSelectedIndex(index)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 rounded-lg text-left transition-colors",
                      config.itemMinH,
                      index === selectedIndex
                        ? "bg-accent"
                        : "hover:bg-accent/50 active:bg-accent"
                    )}
                  >
                    <div className="flex h-9 w-9 md:h-10 md:w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500/20 to-indigo-500/20">
                      {skill.icon_url ? (
                        <img
                          src={skill.icon_url}
                          alt={skill.name}
                          className="h-5 w-5 md:h-6 md:w-6 rounded object-cover"
                        />
                      ) : (
                        <Sparkles className="h-4 w-4 md:h-5 md:w-5 text-violet-500" />
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate">{skill.name}</p>
                      <p className="text-xs text-muted-foreground truncate line-clamp-1">
                        {skill.description}
                      </p>
                    </div>
                    {skill.category && (
                      <span className="text-[11px] text-muted-foreground shrink-0 hidden sm:inline-block">
                        {skill.category.name}
                      </span>
                    )}
                  </button>
                ))}
              </div>

              {/* View All Results */}
              <div className="border-t px-3 py-2">
                <button
                  onClick={handleSubmit}
                  className="w-full flex items-center justify-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors font-medium min-h-[36px] rounded-lg hover:bg-accent/50"
                >
                  {t("search.view_all_results").replace("{query}", `"${query}"`)}
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </>
          ) : query.length >= 2 && !isLoading ? (
            /* No Results */
            <div className="p-8 text-center">
              <Search className="h-8 w-8 text-muted-foreground mx-auto mb-3 opacity-50" />
              <p className="text-sm text-muted-foreground">
                {t("search.no_results").replace("{query}", `"${query}"`)}
              </p>
              <button
                onClick={handleSubmit}
                className="mt-3 text-xs text-primary hover:text-primary/80 underline"
              >
                {t("search.view_all_results").replace("{query}", `"${query}"`)}
              </button>
            </div>
          ) : (
            /* Empty State: Recent Searches + Popular Suggestions */
            <div className="py-2">
              {/* Recent Searches */}
              {recentSearches.length > 0 && (
                <div className="mb-2">
                  <div className="flex items-center justify-between px-4 py-2">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                      <Clock className="h-3.5 w-3.5" />
                      {t("search.recent_searches")}
                    </span>
                    <button
                      onClick={() => {
                        clearRecentSearches();
                        setRecentSearches([]);
                      }}
                      className="text-xs text-muted-foreground hover:text-foreground transition-colors min-h-[28px] px-1.5"
                    >
                      {t("search.clear_recent")}
                    </button>
                  </div>
                  <div className="px-2 pb-1">
                    {recentSearches.map((item, index) => (
                      <button
                        key={`${item.query}-${item.timestamp}`}
                        role="option"
                        aria-selected={index === selectedIndex}
                        onClick={() => {
                          setQuery(item.query);
                          handleSubmitWith(item.query);
                        }}
                        onMouseEnter={() => setSelectedIndex(results.length + index)}
                        className={cn(
                          "w-full flex items-center gap-3 px-3 rounded-lg text-left transition-colors",
                          config.itemMinH,
                          results.length + index === selectedIndex
                            ? "bg-accent"
                            : "hover:bg-accent/50 active:bg-accent"
                        )}
                      >
                        <Clock className="h-4 w-4 shrink-0 text-muted-foreground" />
                        <span className="text-sm truncate">{item.query}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Popular Suggestions */}
              <div className="border-t pt-2">
                <div className="px-4 py-2">
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                    <TrendingUp className="h-3.5 w-3.5" />
                    {t("search.popular_suggestions")}
                  </span>
                </div>
                <div className="px-2 pb-2 flex flex-wrap gap-1.5">
                  {POPULAR_SUGGESTIONS.map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => {
                        setQuery(suggestion);
                        handleSubmitWith(suggestion);
                      }}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border bg-background text-xs text-muted-foreground hover:text-foreground hover:bg-accent hover:border-primary/30 transition-all duration-200 min-h-[32px]"
                    >
                      <Search className="h-3 w-3" />
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
