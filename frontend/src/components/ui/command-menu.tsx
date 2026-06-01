"use client";

import * as React from "react";
import { Command, CommandInput, CommandList, CommandEmpty, CommandGroup, CommandItem } from "cmdk";
import { Search, BookOpen, FolderOpen, Navigation, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useBodyLock } from "@/hooks/useBodyLock";

interface CommandItemData {
  id: string;
  label: string;
  icon?: React.ReactNode;
  section: "skills" | "categories" | "navigation";
  action?: () => void;
  href?: string;
}

interface CommandMenuProps {
  open: boolean;
  onClose: () => void;
  skills?: Omit<CommandItemData, "section">[];
  categories?: Omit<CommandItemData, "section">[];
  navigation?: Omit<CommandItemData, "section">[];
  isLoading?: boolean;
}

const SECTION_ICONS: Record<string, React.ReactNode> = {
  skills: <BookOpen className="h-4 w-4" />,
  categories: <FolderOpen className="h-4 w-4" />,
  navigation: <Navigation className="h-4 w-4" />,
};

function CommandMenu({
  open,
  onClose,
  skills = [],
  categories = [],
  navigation = [],
  isLoading = false,
}: CommandMenuProps) {
  const [search, setSearch] = React.useState("");
  const [isMobile, setIsMobile] = React.useState(false);

  useBodyLock(open);

  React.useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);

  React.useEffect(() => {
    if (open) setSearch("");
  }, [open]);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (open) onClose();
      }
      if (e.key === "Escape" && open) {
        e.preventDefault();
        onClose();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  const allItems: CommandItemData[] = [
    ...skills.map((s) => ({ ...s, section: "skills" as const })),
    ...categories.map((c) => ({ ...c, section: "categories" as const })),
    ...navigation.map((n) => ({ ...n, section: "navigation" as const })),
  ];

  const handleSelect = (id: string) => {
    const item = allItems.find((i) => i.id === id);
    if (item?.action) item.action();
    onClose();
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100]"
      role="dialog"
      aria-modal="true"
      aria-label="Command menu"
    >
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-in fade-in-0"
        onClick={onClose}
      />
      <div
        className={cn(
          "fixed z-[101] bg-background border shadow-2xl overflow-hidden animate-in zoom-in-95 fade-in-0",
          isMobile
            ? "inset-x-0 bottom-0 top-[10%] rounded-t-xl"
            : "left-1/2 top-[20%] w-full max-w-xl -translate-x-1/2 rounded-xl"
        )}
      >
        <Command className="flex flex-col h-full" loop>
          <div className="flex items-center border-b px-4">
            <Search className="h-4 w-4 shrink-0 text-muted-foreground mr-3" />
            <CommandInput
              value={search}
              onValueChange={setSearch}
              placeholder="Type a command or search..."
              className={cn(
                "flex h-12 w-full rounded-md bg-transparent py-3 text-base outline-none",
                "placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50",
                "sm:text-sm"
              )}
            />
            <kbd
              className={cn(
                "pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground",
                "hidden sm:inline-flex"
              )}
            >
              ESC
            </kbd>
          </div>

          <CommandList className="overflow-y-auto overscroll-contain p-2 max-h-[60vh] sm:max-h-[400px]">
            {isLoading && (
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                <Loader2 className="h-5 w-5 animate-spin mr-2" />
                Loading...
              </div>
            )}

            {!isLoading && search && (() => {
              const filtered = allItems.filter((item) =>
                item.label.toLowerCase().includes(search.toLowerCase())
              );
              if (filtered.length === 0) {
                return (
                  <CommandEmpty className="py-8 text-center text-sm text-muted-foreground">
                    No results found for &quot;{search}&quot;
                  </CommandEmpty>
                );
              }
              return null;
            })()}

            {!isLoading && skills.length > 0 && (
              <CommandGroup heading="Skills">
                {skills.map((skill) => (
                  <CommandItem
                    key={skill.id}
                    value={skill.id}
                    onSelect={() => handleSelect(skill.id)}
                    className={cn(
                      "flex cursor-pointer select-none items-center rounded-md px-2 py-2.5 text-sm outline-none min-h-[44px]",
                      "aria-selected:bg-accent aria-selected:text-accent-foreground",
                      "data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
                      "touch-manipulation"
                    )}
                  >
                    {skill.icon ?? SECTION_ICONS.skills}
                    <span className="ml-2 truncate">{skill.label}</span>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}

            {!isLoading && categories.length > 0 && (
              <CommandGroup heading="Categories">
                {categories.map((category) => (
                  <CommandItem
                    key={category.id}
                    value={category.id}
                    onSelect={() => handleSelect(category.id)}
                    className={cn(
                      "flex cursor-pointer select-none items-center rounded-md px-2 py-2.5 text-sm outline-none min-h-[44px]",
                      "aria-selected:bg-accent aria-selected:text-accent-foreground",
                      "data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
                      "touch-manipulation"
                    )}
                  >
                    {category.icon ?? SECTION_ICONS.categories}
                    <span className="ml-2 truncate">{category.label}</span>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}

            {!isLoading && navigation.length > 0 && (
              <CommandGroup heading="Navigation">
                {navigation.map((nav) => (
                  <CommandItem
                    key={nav.id}
                    value={nav.id}
                    onSelect={() => handleSelect(nav.id)}
                    className={cn(
                      "flex cursor-pointer select-none items-center rounded-md px-2 py-2.5 text-sm outline-none min-h-[44px]",
                      "aria-selected:bg-accent aria-selected:text-accent-foreground",
                      "data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
                      "touch-manipulation"
                    )}
                  >
                    {nav.icon ?? SECTION_ICONS.navigation}
                    <span className="ml-2 truncate">{nav.label}</span>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>

          <div className="border-t px-4 py-2.5 text-xs text-muted-foreground flex items-center gap-4">
            <div className="flex items-center gap-1 hidden sm:flex">
              <kbd className="inline-flex h-5 items-center rounded border bg-muted px-1.5 font-mono text-[10px]">
                ↑↓
              </kbd>
              <span>Navigate</span>
            </div>
            <div className="flex items-center gap-1 hidden sm:flex">
              <kbd className="inline-flex h-5 items-center rounded border bg-muted px-1.5 font-mono text-[10px]">
                ↵
              </kbd>
              <span>Select</span>
            </div>
            <div className="flex items-center gap-1">
              <kbd className="inline-flex h-5 items-center rounded border bg-muted px-1.5 font-mono text-[10px]">
                ⌘K
              </kbd>
              <span>Open</span>
            </div>
          </div>
        </Command>
      </div>
    </div>
  );
}

export { CommandMenu };
export type { CommandMenuProps, CommandItemData };