"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Library,
  Github,
  Twitter,
  Mail,
  Heart,
  ChevronDown,
  Globe,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";

interface FooterLink {
  href: string;
  labelKey: string;
}

interface FooterSection {
  titleKey: string;
  links: FooterLink[];
}

const footerSections: FooterSection[] = [
  {
    titleKey: "footer.product",
    links: [
      { href: "/skills", labelKey: "footer.browse_skills" },
      { href: "/categories", labelKey: "footer.categories_link" },
      { href: "/compositions", labelKey: "footer.compositions_link" },
      { href: "/search", labelKey: "footer.search_link" },
      { href: "/dashboard", labelKey: "footer.dashboard_link" },
    ],
  },
  {
    titleKey: "footer.resources",
    links: [
      { href: "/docs", labelKey: "footer.documentation" },
      { href: "/api", labelKey: "footer.api_reference" },
      { href: "/tutorials", labelKey: "footer.tutorials" },
      { href: "/blog", labelKey: "footer.blog" },
      { href: "/changelog", labelKey: "footer.changelog" },
    ],
  },
  {
    titleKey: "footer.community",
    links: [
      { href: "/discord", labelKey: "footer.discord" },
      { href: "/github", labelKey: "footer.github" },
      { href: "/twitter", labelKey: "footer.twitter" },
      { href: "/forum", labelKey: "footer.forum" },
      { href: "/contributors", labelKey: "footer.contributors" },
    ],
  },
  {
    titleKey: "footer.legal",
    links: [
      { href: "/privacy", labelKey: "footer.privacy_policy" },
      { href: "/terms", labelKey: "footer.terms_of_service" },
      { href: "/license", labelKey: "footer.license" },
      { href: "/security", labelKey: "footer.security" },
    ],
  },
];

const socialLinks = [
  { href: "https://github.com", icon: Github, label: "GitHub" },
  { href: "https://twitter.com", icon: Twitter, label: "Twitter" },
  { href: "mailto:hello@skilllib.dev", icon: Mail, label: "Email" },
];

function CollapsibleSection({
  titleKey,
  links,
  defaultOpen = false,
}: {
  titleKey: string;
  links: FooterLink[];
  defaultOpen?: boolean;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const { t } = useI18n();

  return (
    <div className="border-b md:border-b-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full py-4 md:py-0 md:mb-4 text-left group"
        aria-expanded={isOpen}
      >
        <h3 className="font-semibold text-sm md:text-base">{t(titleKey)}</h3>
        <ChevronDown
          className={cn(
            "h-5 w-5 shrink-0 text-muted-foreground transition-transform duration-200 md:hidden",
            isOpen && "rotate-180"
          )}
        />
      </button>
      <ul
        className={cn(
          "space-y-2.5 md:space-y-2 overflow-hidden transition-all duration-300 md:transition-none",
          isOpen ? "max-h-[500px] opacity-100 pb-4 md:max-h-none md:opacity-100 md:pb-0" : "max-h-0 opacity-0 md:max-h-none md:opacity-100"
        )}
      >
        {links.map((link) => (
          <li key={link.href}>
            <Link
              href={link.href}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-block min-h-[44px] -ml-1 px-1 py-1 rounded-md hover:bg-accent/50 md:min-h-0 md:p-0"
            >
              {t(link.labelKey)}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function Footer() {
  const [currentYear] = useState(() => new Date().getFullYear());
  const { t, isZh, setLocale } = useI18n();

  return (
    <footer className="border-t bg-card/50 mt-auto">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12 lg:py-16">
        {/* Brand & Social Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-12 mb-10 md:mb-12">
          {/* Brand Column */}
          <div className="lg:col-span-1">
            <Link href="/" className="flex items-center gap-2.5 mb-4 group inline-block">
              <div className="flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-500/20 group-hover:shadow-violet-500/40 transition-shadow duration-300">
                <Library className="h-5 w-5" />
              </div>
              <span className="font-bold text-lg bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
                SkillLib
              </span>
            </Link>
            <p className="text-sm text-muted-foreground leading-relaxed mb-5 max-w-xs">
              {t("footer.description")}
            </p>

            {/* Social Icons */}
            <div className="flex items-center gap-3 mb-6">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-xl text-muted-foreground hover:text-foreground hover:bg-accent border border-transparent hover:border-border transition-all duration-200"
                  aria-label={social.label}
                >
                  <social.icon className="h-5 w-5" />
                </a>
              ))}
            </div>

            {/* Language Switcher */}
            <button
              onClick={() => setLocale(isZh ? "en" : "zh")}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-accent border border-transparent hover:border-border transition-all duration-200 min-h-[44px]"
            >
              <Globe className="h-4 w-4" />
              <span>{isZh ? "English" : "中文"}</span>
            </button>
          </div>

          {/* Link Columns - Collapsible on Mobile */}
          <div className="lg:col-span-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-8 gap-y-2">
              {footerSections.map((section) => (
                <CollapsibleSection
                  key={section.titleKey}
                  titleKey={section.titleKey}
                  links={section.links}
                  defaultOpen={false}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t pt-6 md:pt-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-xs sm:text-sm text-muted-foreground text-center sm:text-left">
              {t("footer.copyright").replace("{year}", String(currentYear))}
            </p>
            <p className="text-xs sm:text-sm text-muted-foreground flex items-center gap-1.5">
              {t("footer.made_with").replace(
                "love",
                ""
              )}
              <Heart className="h-3.5 w-3.5 text-red-500 fill-red-500 animate-pulse" />
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
