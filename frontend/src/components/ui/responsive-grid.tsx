"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface ResponsiveGridProps {
  children: React.ReactNode;
  minColumnWidth?: number;
  gap?: number;
  className?: string;
}

function ResponsiveGrid({
  children,
  minColumnWidth = 300,
  gap = 16,
  className,
}: ResponsiveGridProps) {
  return (
    <div
      className={cn("w-full", className)}
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(auto-fill, minmax(${minColumnWidth}px, 1fr))`,
        gap: `${gap}px`,
      }}
      role="list"
    >
      {React.Children.map(children, (child, index) =>
        child ? <div key={index} role="listitem">{child}</div> : null
      )}
    </div>
  );
}

export { ResponsiveGrid };
export type { ResponsiveGridProps };
