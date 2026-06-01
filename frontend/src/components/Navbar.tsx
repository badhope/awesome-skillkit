"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import {
  Search,
  Menu,
  X,
  Sun,
  Moon,
  Library,
  ChevronDown,
  ChevronRight,
  User as UserIcon,
  LogOut,
  LayoutDashboard,
  Settings,
  Heart,
  GitBranch,
  Grid3X3,
  Sparkles,
  Globe,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn, getInitials } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";
import { isAuthenticated, getStoredUser, logout } from "@/lib/auth";
import { OfflineBanner } from "@/components/OfflineBanner";
import type { User } from "@/types";

interface NavLink {
  href: string;
  labelKey: string;
  icon: React.ComponentType<{ className?: string }>;
  children?: { href: string; labelKey: string }[];
}

const navLinks: NavLink[] = [
  { href: "/skills", labelKey: "nav.skills", icon: Sparkles },
  { href: "/categories", labelKey: "nav.categories", icon: Grid3X3 },
  { href: "/compositions", labelKey: "nav.compositions", icon: GitBranch },
];

const VISIBLE_LINKS_DESKTOP = 2;

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [mobileSearchQuery, setMobileSearchQuery] = useState("");
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const mobileDrawerRef = useRef<HTMLDivElement>(null);
  const { t, locale, isZh, setLocale } = useI18n();

  useEffect(() => {
    setMounted(true);
    setUser(getStoredUser());
    setAuthChecked(true);
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && mobileOpen) {
        setMobileOpen(false);
      }
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [mobileOpen]);

  useEffect(() => {
    if (pathname) {
      setMobileOpen(false);
    }
  }, [pathname]);

  const isActive = useCallback(
    (href: string) => {
      if (href === "/") return pathname === "/";
      return pathname?.startsWith(href);
    },
    [pathname]
  );

  const handleSearch = useCallback(
    (e: React.FormEvent, query: string) => {
      e.preventDefault();
      const trimmed = query.trim();
      if (trimmed) {
        router.push(`/search?q=${encodeURIComponent(trimmed)}`);
        setSearchQuery("");
        setMobileSearchQuery("");
        setMobileOpen(false);
      }
    },
    [router]
  );

  const handleLogout = async () => {
    await logout();
    setUser(null);
    setMobileOpen(false);
    router.push("/");
    router.refresh();
  };

  const toggleLanguage = () => {
    setLocale(isZh ? "en" : "zh");
  };

  const visibleLinks = navLinks.slice(0, VISIBLE_LINKS_DESKTOP);
  const moreLinks = navLinks.slice(VISIBLE_LINKS_DESKTOP);

  return (
    <>
      <OfflineBanner />
      <header
        className={cn(
          "sticky top-0 z-50 w-full transition-all duration-300",
          scrolled
            ? "bg-background/95 backdrop-blur-md supports-[backdrop-filter]:bg-background/80 border-b shadow-sm"
            : "bg-background/80 backdrop-blur-sm"
        )}
      >
      <div className="container mx-auto flex h-16 items-center justify-between px-4 lg:px-6">
        <div className="flex items-center gap-2 sm:gap-6">
          <Link href="/" className="flex items-center gap-2 group shrink-0">
            <div className="relative">
              <div className="absolute -inset-1 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 opacity-70 blur group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative flex h-8 w-8 sm:h-9 sm:w-9 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 text-white">
                <Library className="h-4 w-4 sm:h-5 sm:w-5" />
              </div>
            </div>
            <span
              className={cn(
                "font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent hidden sm:inline-block",
                scrolled ? "text-base lg:text-lg" : "text-sm lg:text-lg"
              )}
            >
              SkillLib
            </span>
          </Link>

          <nav className="hidden lg:flex items-center gap-1" role="navigation" aria-label="Main navigation">
            {visibleLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                  isActive(link.href)
                    ? "text-primary bg-primary/10"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                )}
              >
                <link.icon className="h-4 w-4" />
                {t(link.labelKey)}
              </Link>
            ))}

            {moreLinks.length > 0 && (
              <DropdownMenu open={moreOpen} onOpenChange={setMoreOpen}>
                <DropdownMenuTrigger asChild>
                  <button
                    className={cn(
                      "flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                      moreLinks.some((l) => isActive(l.href))
                        ? "text-primary bg-primary/10"
                        : "text-muted-foreground hover:text-foreground hover:bg-accent"
                    )}
                  >
                    {t("nav.more")}
                    <ChevronDown className="h-3.5 w-3.5" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48">
                  {moreLinks.map((link) => (
                    <DropdownMenuItem key={link.href} asChild>
                      <Link
                        href={link.href}
                        className={cn(
                          "flex items-center gap-2 cursor-pointer",
                          isActive(link.href) && "text-primary"
                        )}
                      >
                        <link.icon className="h-4 w-4" />
                        {t(link.labelKey)}
                      </Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </nav>

          <nav className="hidden md:flex lg:hidden items-center gap-1" role="navigation" aria-label="Tablet navigation">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "flex items-center gap-1.5 px-2.5 py-2 text-sm font-medium rounded-lg transition-colors",
                  isActive(link.href)
                    ? "text-primary bg-primary/10"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                )}
              >
                <link.icon className="h-4 w-4" />
                <span className="hidden xl:inline">{t(link.labelKey)}</span>
              </Link>
            ))}
          </nav>
        </div>

        <div className="hidden md:flex items-center gap-3 flex-1 max-w-md mx-4 lg:mx-8">
          <form onSubmit={(e) => handleSearch(e, searchQuery)} className="w-full">
            <div className="relative group">
              <Search
                className={cn(
                  "absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground transition-transform duration-200",
                  "group-focus-within:scale-110 group-focus-within:text-primary"
                )}
              />
              <Input
                type="search"
                placeholder={t("nav.search_placeholder")}
                className="pl-10 h-9 bg-muted/50 border-muted-foreground/20 focus-visible:bg-background focus-visible:border-primary/30 transition-all duration-200"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </form>
        </div>

        <div className="flex items-center gap-1.5 sm:gap-2">
          {mounted && (
            <>
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="rounded-lg hidden sm:inline-flex"
                aria-label={t("nav.toggle_theme")}
              >
                {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </Button>

              <Button
                variant="ghost"
                size="icon-sm"
                onClick={toggleLanguage}
                className="rounded-lg hidden sm:inline-flex"
                aria-label={t("nav.language")}
              >
                <Globe className="h-4 w-4" />
              </Button>
            </>
          )}

          {authChecked && isAuthenticated() && user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 sm:h-9 sm:w-9 rounded-full p-0" size="icon-sm">
                  <Avatar className="h-7 w-7 sm:h-8 sm:w-8">
                    <AvatarImage src={user.avatar_url || undefined} alt={user.username} />
                    <AvatarFallback className="text-[10px] sm:text-xs">
                      {getInitials(user.full_name || user.username)}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" sideOffset={8}>
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium">{user.full_name}</p>
                    <p className="text-xs text-muted-foreground">@{user.username}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/dashboard" className="cursor-pointer">
                    <LayoutDashboard className="mr-2 h-4 w-4" />
                    {t("nav.dashboard")}
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href={`/profile/${user.username}`} className="cursor-pointer">
                    <UserIcon className="mr-2 h-4 w-4" />
                    {t("nav.profile")}
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/favorites" className="cursor-pointer">
                    <Heart className="mr-2 h-4 w-4" />
                    {t("nav.favorites")}
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings" className="cursor-pointer">
                    <Settings className="mr-2 h-4 w-4" />
                    {t("nav.settings")}
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-destructive focus:text-destructive cursor-pointer">
                  <LogOut className="mr-2 h-4 w-4" />
                  {t("nav.sign_out")}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className="hidden md:flex items-center gap-1.5 sm:gap-2">
              <Link href="/auth/login">
                <Button variant="ghost" size="sm">
                  {t("nav.sign_in")}
                </Button>
              </Link>
              <Link href="/auth/register">
                <Button variant="gradient" size="sm">
                  {t("nav.get_started")}
                </Button>
              </Link>
            </div>
          )}

          <Button
            variant="ghost"
            size="icon-sm"
            className="md:hidden rounded-lg min-h-[44px] min-w-[44px]"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label={mobileOpen ? t("nav.close_menu") : t("nav.toggle_menu")}
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile Overlay Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm md:hidden"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Mobile Drawer */}
      <div
        ref={mobileDrawerRef}
        className={cn(
          "fixed top-0 right-0 z-[60] h-full w-[85%] max-w-sm bg-background shadow-2xl md:hidden",
          "transform transition-transform duration-300 ease-out",
          mobileOpen ? "translate-x-0" : "translate-x-full"
        )}
        aria-label={t("nav.toggle_menu")}
        role="dialog"
        aria-modal="true"
      >
        <div className="flex h-full flex-col">
          {/* Drawer Header */}
          <div className="flex items-center justify-between px-4 py-4 border-b shrink-0">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 text-white">
                <Library className="h-4 w-4" />
              </div>
              <span className="font-bold text-base bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
                SkillLib
              </span>
            </div>
            <button
              onClick={() => setMobileOpen(false)}
              className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-accent transition-colors"
              aria-label={t("nav.close_menu")}
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Search Bar */}
          <div className="px-4 py-3 border-b shrink-0">
            <form onSubmit={(e) => handleSearch(e, mobileSearchQuery)}>
              <div className="relative group">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <Input
                  type="search"
                  placeholder={t("nav.search_placeholder_mobile")}
                  className="pl-11 h-12 text-base rounded-xl bg-muted/50 focus-visible:bg-background"
                  value={mobileSearchQuery}
                  onChange={(e) => setMobileSearchQuery(e.target.value)}
                  autoFocus={false}
                />
              </div>
            </form>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto overscroll-contain">
            <nav className="px-3 py-2 space-y-1" role="navigation" aria-label="Mobile navigation">
              {navLinks.map((link) => (
                <div key={link.href}>
                  <Link
                    href={link.href}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      "flex items-center gap-3 px-3 min-h-12 rounded-lg text-base font-medium transition-colors",
                      isActive(link.href)
                        ? "text-primary bg-primary/10"
                        : "text-foreground hover:bg-accent"
                    )}
                  >
                    <link.icon className="h-5 w-5 shrink-0" />
                    <span>{t(link.labelKey)}</span>
                    <ChevronRight className="h-4 w-4 ml-auto shrink-0 text-muted-foreground" />
                  </Link>
                </div>
              ))}

              {/* Category Accordion Section */}
              <div className="pt-2 pb-1">
                <button
                  onClick={() =>
                    setExpandedCategory(expandedCategory === "cats" ? null : "cats")
                  }
                  className="flex items-center gap-3 px-3 min-h-12 w-full rounded-lg text-base font-medium text-foreground hover:bg-accent transition-colors"
                >
                  <Grid3X3 className="h-5 w-5 shrink-0" />
                  <span>{t("nav.categories")}</span>
                  <ChevronDown
                    className={cn(
                      "h-4 w-4 ml-auto shrink-0 text-muted-foreground transition-transform duration-200",
                      expandedCategory === "cats" && "rotate-180"
                    )}
                  />
                </button>
                {expandedCategory === "cats" && (
                  <div className="ml-4 mt-1 space-y-0.5 animate-in slide-in-from-top-2 duration-200">
                    <Link
                      href="/categories"
                      onClick={() => setMobileOpen(false)}
                      className="flex items-center gap-2 px-3 min-h-11 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                    >
                      {t("nav.all_categories")}
                    </Link>
                    <Link
                      href="/categories?filter=popular"
                      onClick={() => setMobileOpen(false)}
                      className="flex items-center gap-2 px-3 min-h-11 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                    >
                      ⭐ Popular
                    </Link>
                    <Link
                      href="/categories?filter=recent"
                      onClick={() => setMobileOpen(false)}
                      className="flex items-center gap-2 px-3 min-h-11 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                    >
                      🕐 Recent
                    </Link>
                  </div>
                )}
              </div>
            </nav>

            {/* Theme & Language */}
            <div className="px-3 py-3 border-t mt-2 space-y-1">
              {mounted && (
                <>
                  <button
                    onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                    className="flex items-center gap-3 px-3 min-h-12 w-full rounded-lg text-base font-medium text-foreground hover:bg-accent transition-colors"
                  >
                    {theme === "dark" ? (
                      <Sun className="h-5 w-5 shrink-0" />
                    ) : (
                      <Moon className="h-5 w-5 shrink-0" />
                    )}
                    <span>{t("nav.toggle_theme")}</span>
                  </button>

                  <button
                    onClick={toggleLanguage}
                    className="flex items-center gap-3 px-3 min-h-12 w-full rounded-lg text-base font-medium text-foreground hover:bg-accent transition-colors"
                  >
                    <Globe className="h-5 w-5 shrink-0" />
                    <span>{t("nav.language")}</span>
                    <span className="ml-auto text-sm text-muted-foreground uppercase font-mono">
                      {isZh ? "中" : "En"}
                    </span>
                  </button>
                </>
              )}
            </div>

            {/* Auth Section */}
            {authChecked && !isAuthenticated() && (
              <div className="px-4 py-4 border-t space-y-3">
                <Link href="/auth/login" onClick={() => setMobileOpen(false)}>
                  <Button variant="outline" className="w-full h-12 text-base font-medium rounded-xl">
                    {t("nav.sign_in")}
                  </Button>
                </Link>
                <Link href="/auth/register" onClick={() => setMobileOpen(false)}>
                  <Button variant="gradient" className="w-full h-12 text-base font-medium rounded-xl">
                    {t("nav.get_started")}
                  </Button>
                </Link>
              </div>
            )}

            {authChecked && isAuthenticated() && user && (
              <div className="px-4 py-4 border-t space-y-1">
                <div className="flex items-center gap-3 px-2 py-2">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={user.avatar_url || undefined} alt={user.username} />
                    <AvatarFallback>{getInitials(user.full_name || user.username)}</AvatarFallback>
                  </Avatar>
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{user.full_name}</p>
                    <p className="text-xs text-muted-foreground truncate">@{user.username}</p>
                  </div>
                </div>
                <Link
                  href="/dashboard"
                  onClick={() => setMobileOpen(false)}
                  className="flex items-center gap-3 px-3 min-h-11 rounded-lg text-sm text-foreground hover:bg-accent transition-colors"
                >
                  <LayoutDashboard className="h-4 w-4" />
                  {t("nav.dashboard")}
                </Link>
                <Link
                  href={`/profile/${user.username}`}
                  onClick={() => setMobileOpen(false)}
                  className="flex items-center gap-3 px-3 min-h-11 rounded-lg text-sm text-foreground hover:bg-accent transition-colors"
                >
                  <UserIcon className="h-4 w-4" />
                  {t("nav.profile")}
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-3 px-3 min-h-11 w-full rounded-lg text-sm text-destructive hover:bg-destructive/10 transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                  {t("nav.sign_out")}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      </header>
    </>
  );
}
