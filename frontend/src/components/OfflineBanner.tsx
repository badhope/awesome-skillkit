"use client";

import { WifiOff } from "lucide-react";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { useI18n } from "@/lib/i18n";

export function OfflineBanner() {
  const isOnline = useOnlineStatus();
  const { t, isZh } = useI18n();

  if (isOnline) return null;

  const title = t("errors.offlineTitle");
  const description = t("errors.offlineDescription");

  return (
    <div
      role="status"
      aria-live="assertive"
      aria-atomic="true"
      className="fixed top-0 left-0 right-0 z-[100] pointer-events-none"
    >
      <div className="pointer-events-auto w-full bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 text-white shadow-md">
        <div className="container mx-auto px-4 lg:px-6">
          <div className="flex items-center justify-center gap-2 sm:gap-3 py-2 sm:py-2.5 text-center">
            <span className="relative inline-flex shrink-0">
              <span className="absolute inline-flex h-full w-full rounded-full bg-white/30 opacity-75 animate-ping" />
              <WifiOff className="relative h-4 w-4 sm:h-5 sm:w-5" aria-hidden="true" />
            </span>
            <p className="text-xs sm:text-sm font-medium">
              <span className="font-semibold">{title}</span>
              <span className="mx-1.5 hidden sm:inline opacity-80">·</span>
              <span className="hidden sm:inline opacity-95">{description}</span>
              <span className="block sm:hidden text-[11px] opacity-90 mt-0.5">
                {isZh
                  ? "请检查网络连接"
                  : "Please check your connection"}
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default OfflineBanner;
