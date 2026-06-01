"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

interface ChipInputProps {
  chips: string[];
  onAdd: (chip: string) => void;
  onRemove: (index: number) => void;
  placeholder?: string;
  maxChips?: number;
  className?: string;
}

function ChipInput({
  chips,
  onAdd,
  onRemove,
  placeholder = "Type and press Enter...",
  maxChips = 10,
  className,
}: ChipInputProps) {
  const [inputValue, setInputValue] = React.useState("");
  const inputRef = React.useRef<HTMLInputElement>(null);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      const value = inputValue.trim().replace(/,$/, "");
      if (value && !chips.includes(value) && chips.length < maxChips) {
        onAdd(value);
        setInputValue("");
      }
    }
    if (e.key === "Backspace" && !inputValue && chips.length > 0) {
      onRemove(chips.length - 1);
    }
  };

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollLeft = scrollRef.current.scrollWidth;
    }
  }, [chips]);

  return (
    <div
      className={cn(
        "flex min-h-[44px] w-full flex-wrap items-center gap-1.5 rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 transition-colors duration-200",
        className
      )}
      onClick={() => inputRef.current?.focus()}
    >
      <div
        ref={scrollRef}
        className={cn(
          "flex flex-1 items-center gap-1.5 overflow-x-auto scrollbar-hide flex-wrap min-w-0",
          "[&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
        )}
      >
        {chips.map((chip, index) => (
          <span
            key={`${chip}-${index}`}
            className={cn(
              "inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary shrink-0",
              "animate-fade-in"
            )}
          >
            <span className="max-w-[120px] truncate">{chip}</span>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onRemove(index);
              }}
              className={cn(
                "rounded-full p-0.5 hover:bg-primary/20 transition-colors",
                "min-h-[24px] min-w-[24px] flex items-center justify-center touch-manipulation"
              )}
              aria-label={`Remove ${chip}`}
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={chips.length >= maxChips ? `Max ${maxChips} tags` : placeholder}
          disabled={chips.length >= maxChips}
          className={cn(
            "min-w-[100px] flex-1 bg-transparent outline-none placeholder:text-muted-foreground",
            "text-base sm:text-sm"
          )}
        />
      </div>
    </div>
  );
}

export { ChipInput };
export type { ChipInputProps };
