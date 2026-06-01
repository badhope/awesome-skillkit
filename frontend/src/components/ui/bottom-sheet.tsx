"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";
import { useBodyLock } from "@/hooks/useBodyLock";

type SnapPoint = "peek" | "half" | "full";

interface BottomSheetProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  snap?: SnapPoint[];
}

const SNAP_HEIGHTS: Record<SnapPoint, string> = {
  peek: "25%",
  half: "50%",
  full: "90%",
};

function BottomSheet({
  open,
  onClose,
  children,
  title,
  snap = ["half"],
}: BottomSheetProps) {
  const [isMobile, setIsMobile] = React.useState(false);
  const [currentSnap, setCurrentSnap] = React.useState<SnapPoint>("half");
  const sheetRef = React.useRef<HTMLDivElement>(null);
  const dragStartY = React.useRef<number | null>(null);
  const dragStartTop = React.useRef<number | null>(null);

  useBodyLock(open);

  React.useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);

  React.useEffect(() => {
    if (open) {
      setCurrentSnap(snap[snap.length - 1] ?? "half");
    }
  }, [open, snap]);

  const getSnapHeight = (s: SnapPoint) => SNAP_HEIGHTS[s];

  const handleDragStart = React.useCallback(
    (e: React.TouchEvent | React.MouseEvent) => {
      if (!sheetRef.current) return;
      dragStartY.current = "touches" in e ? (e.touches[0]?.clientY ?? 0) : e.clientY;
      dragStartTop.current = sheetRef.current.getBoundingClientRect().top;
      sheetRef.current.style.transition = "none";
    },
    []
  );

  const handleDragMove = React.useCallback(
    (e: React.TouchEvent | React.MouseEvent) => {
      if (
        !sheetRef.current ||
        dragStartY.current === null ||
        dragStartTop.current === null
      )
        return;

      const clientY = "touches" in e ? (e.touches[0]?.clientY ?? 0) : e.clientY;
      const delta = clientY - dragStartY.current;
      if (delta > 0) {
        sheetRef.current.style.transform = `translateY(${delta}px)`;
      }
    },
    []
  );

  const handleDragEnd = React.useCallback(() => {
    if (!sheetRef.current || dragStartY.current === null || dragStartTop.current === null)
      return;

    const currentTop = sheetRef.current.getBoundingClientRect().top;
    const delta = currentTop - dragStartTop.current;

    sheetRef.current.style.transition = "";

    if (delta > 100) {
      onClose();
    } else {
      sheetRef.current.style.transform = "";
    }

    dragStartY.current = null;
    dragStartTop.current = null;
  }, [onClose]);

  const snapTo = React.useCallback(
    (targetSnap: SnapPoint) => {
      setCurrentSnap(targetSnap);
    },
    []
  );

  if (!open) return null;

  if (!isMobile) {
    return (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center"
        role="dialog"
        aria-modal="true"
        aria-label={title ?? "Dialog"}
      >
        <div
          className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-in fade-in-0"
          onClick={onClose}
        />
        <div
          ref={sheetRef as React.RefObject<HTMLDivElement>}
          className={cn(
            "relative z-50 w-full max-w-lg max-h-[85vh] overflow-y-auto rounded-xl border bg-background p-6 shadow-xl",
            "animate-in zoom-in-95 fade-in-0 slide-in-from-bottom-2"
          )}
        >
          {title && (
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">{title}</h2>
              <button
                onClick={onClose}
                className="rounded-md p-1.5 hover:bg-accent transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center"
                aria-label="Close"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          )}
          {children}
        </div>
      </div>
    );
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end"
      role="dialog"
      aria-modal="true"
      aria-label={title ?? "Bottom Sheet"}
    >
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-in fade-in-0"
        onClick={onClose}
      />

      <div
        ref={sheetRef as React.RefObject<HTMLDivElement>}
        className={cn(
          "relative z-50 w-full rounded-t-xl border-t bg-background shadow-2xl",
          "animate-in slide-in-from-bottom"
        )}
        style={{ height: getSnapHeight(currentSnap), transition: "height 300ms ease-out" }}
        onTouchStart={handleDragStart}
        onTouchMove={handleDragMove}
        onTouchEnd={handleDragEnd}
      >
        <div className="flex flex-col h-full">
          <div
            className="flex justify-center pt-3 pb-2 cursor-grab active:cursor-grabbing touch-none select-none shrink-0"
            onTouchStart={handleDragStart}
            onTouchMove={handleDragMove}
            onTouchEnd={handleDragEnd}
          >
            <div className="w-10 h-1 rounded-full bg-muted-foreground/30" />
          </div>

          {snap.length > 1 && (
            <div className="flex justify-center gap-1.5 pb-2 shrink-0">
              {snap.map((s) => (
                <button
                  key={s}
                  onClick={() => snapTo(s)}
                  className={cn(
                    "w-6 h-1.5 rounded-full transition-all",
                    currentSnap === s ? "bg-primary w-8" : "bg-muted-foreground/30"
                  )}
                  aria-label={`Snap to ${s}`}
                />
              ))}
            </div>
          )}

          {title && (
            <div className="px-4 pb-3 shrink-0">
              <h2 className="text-base font-semibold text-center">{title}</h2>
            </div>
          )}

          <div className="flex-1 overflow-y-auto overscroll-contain px-4 pb-6">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

export { BottomSheet };
export type { BottomSheetProps, SnapPoint };
