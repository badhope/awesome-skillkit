import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Resolve a BCP-47 locale tag from our internal "en" | "zh" enum.
 */
export function resolveLocale(locale: "en" | "zh"): string {
  return locale === "zh" ? "zh-CN" : "en-US";
}

export function formatDate(
  date: string | Date,
  format: "short" | "long" | "relative" = "short",
  locale: "en" | "zh" = "en"
): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const intlLocale = resolveLocale(locale);
  if (format === "relative") {
    return formatRelative(d, locale);
  }
  if (format === "short") {
    return d.toLocaleDateString(intlLocale, { month: "short", day: "numeric", year: "numeric" });
  }
  return d.toLocaleDateString(intlLocale, {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

export function formatNumber(num: number, locale: "en" | "zh" = "en"): string {
  // Use full Intl formatting for accuracy; fall back to compact suffix
  // for the very large numbers where we want "1.2M" style abbreviations.
  if (Math.abs(num) >= 1000) {
    const intl = new Intl.NumberFormat(resolveLocale(locale), {
      notation: "compact",
      maximumFractionDigits: 1,
    });
    return intl.format(num);
  }
  return new Intl.NumberFormat(resolveLocale(locale)).format(num);
}

function formatRelative(d: Date, locale: "en" | "zh"): string {
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const months = Math.floor(days / 30);
  const years = Math.floor(days / 365);

  // Use Intl.RelativeTimeFormat for proper localization
  const rtf = new Intl.RelativeTimeFormat(resolveLocale(locale), { numeric: "auto" });

  if (seconds < 60) return rtf.format(-seconds, "second");
  if (minutes < 60) return rtf.format(-minutes, "minute");
  if (hours < 24) return rtf.format(-hours, "hour");
  if (days < 30) return rtf.format(-days, "day");
  if (months < 12) return rtf.format(-months, "month");
  return rtf.format(-years, "year");
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + "...";
}

export function slugify(str: string): string {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "published":
      return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
    case "draft":
      return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400";
    case "deprecated":
      return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400";
    case "archived":
      return "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400";
    default:
      return "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400";
  }
}

export function getRatingLabel(rating: number, locale: "en" | "zh" = "en"): string {
  if (locale === "zh") {
    if (rating >= 4.5) return "极好";
    if (rating >= 4.0) return "很好";
    if (rating >= 3.0) return "良好";
    if (rating >= 2.0) return "一般";
    return "较差";
  }
  if (rating >= 4.5) return "Excellent";
  if (rating >= 4.0) return "Very Good";
  if (rating >= 3.0) return "Good";
  if (rating >= 2.0) return "Fair";
  return "Poor";
}
