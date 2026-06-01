"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface CarouselProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  autoPlay?: boolean;
  interval?: number;
  showArrows?: boolean;
  className?: string;
  itemClassName?: string;
}

function Carousel<T>({
  items,
  renderItem,
  autoPlay = false,
  interval = 5000,
  showArrows = true,
  className,
  itemClassName,
}: CarouselProps<T>) {
  const [currentIndex, setCurrentIndex] = React.useState(0);
  const [isPaused, setIsPaused] = React.useState(false);
  const scrollRef = React.useRef<HTMLDivElement>(null);
  const isMobileRef = React.useRef(false);

  React.useEffect(() => {
    isMobileRef.current = window.innerWidth < 768;
  }, []);

  const scrollToIndex = React.useCallback((index: number) => {
    const safeIndex = Math.max(0, Math.min(index, items.length - 1));
    setCurrentIndex(safeIndex);
    if (scrollRef.current) {
      const child = scrollRef.current.children[safeIndex] as HTMLElement | undefined;
      if (child) {
        scrollRef.current.scrollTo({
          left: child.offsetLeft - scrollRef.current.offsetLeft,
          behavior: "smooth",
        });
      }
    }
  }, [items.length]);

  const goNext = React.useCallback(() => {
    scrollToIndex(currentIndex + 1 >= items.length ? 0 : currentIndex + 1);
  }, [currentIndex, items.length, scrollToIndex]);

  const goPrev = React.useCallback(() => {
    scrollToIndex(currentIndex - 1 < 0 ? items.length - 1 : currentIndex - 1);
  }, [currentIndex, items.length, scrollToIndex]);

  const handleScroll = React.useCallback(() => {
    if (!scrollRef.current || isMobileRef.current) return;

    const container = scrollRef.current;
    const scrollLeft = container.scrollLeft;
    const children = Array.from(container.children) as HTMLElement[];

    let closestIndex = 0;
    let closestDistance = Infinity;

    children.forEach((child, index) => {
      const distance = Math.abs(child.offsetLeft - container.offsetLeft - scrollLeft);
      if (distance < closestDistance) {
        closestDistance = distance;
        closestIndex = index;
      }
    });

    setCurrentIndex(closestIndex);
  }, []);

  React.useEffect(() => {
    if (!autoPlay || isPaused) return;

    const timer = setInterval(goNext, interval);
    return () => clearInterval(timer);
  }, [autoPlay, interval, isPaused, goNext]);

  if (items.length === 0) return null;

  return (
    <div
      className={cn("relative group", className)}
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
      onFocus={() => setIsPaused(true)}
      onBlur={() => setIsPaused(false)}
    >
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className={cn(
          "flex overflow-x-auto snap-x snap-mandatory snap-center scrollbar-hide gap-4",
          "scroll-smooth [-ms-overflow-style:none] [scrollbar-width:none]",
          "[&::-webkit-scrollbar]:hidden [&::-webkit-scrollbar]:touch-pan-x",
          "overscroll-x-contain"
        )}
        role="region"
        aria-roledescription="carousel"
        aria-label="Featured content"
      >
        {items.map((item, index) => (
          <div
            key={index}
            className={cn(
              "snap-start shrink-0 first:ml-[calc(50vw-50%+0rem)] last:mr-[calc(50vw-50%+0rem)] sm:first:ml-0 sm:last:mr-0",
              itemClassName
            )}
            role="group"
            aria-roledescription="slide"
            aria-label={`Slide ${index + 1} of ${items.length}`}
          >
            {renderItem(item, index)}
          </div>
        ))}
      </div>

      {showArrows && (
        <>
          <button
            onClick={goPrev}
            className={cn(
              "absolute left-0 top-1/2 -translate-y-1/2 z-10",
              "rounded-full bg-background/80 backdrop-blur-sm shadow-md p-2",
              "opacity-0 group-hover:opacity-100 transition-opacity",
              "hover:bg-background focus:outline-none focus:ring-2 focus:ring-ring",
              "hidden sm:flex items-center justify-center",
              "min-h-[40px] min-w-[40px]"
            )}
            aria-label="Previous slide"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            onClick={goNext}
            className={cn(
              "absolute right-0 top-1/2 -translate-y-1/2 z-10",
              "rounded-full bg-background/80 backdrop-blur-sm shadow-md p-2",
              "opacity-0 group-hover:opacity-100 transition-opacity",
              "hover:bg-background focus:outline-none focus:ring-2 focus:ring-ring",
              "hidden sm:flex items-center justify-center",
              "min-h-[40px] min-w-[40px]"
            )}
            aria-label="Next slide"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </>
      )}

      <div className="flex justify-center gap-1.5 pt-4">
        {items.map((_, index) => (
          <button
            key={index}
            onClick={() => scrollToIndex(index)}
            className={cn(
              "rounded-full transition-all duration-300 min-h-[8px] min-w-[8px]",
              currentIndex === index
                ? "bg-primary w-6 h-2"
                : "bg-muted-foreground/30 w-2 h-2 hover:bg-muted-foreground/50"
            )}
            aria-label={`Go to slide ${index + 1}`}
            aria-current={currentIndex === index ? "true" : undefined}
          />
        ))}
      </div>
    </div>
  );
}

export { Carousel };
export type { CarouselProps };
