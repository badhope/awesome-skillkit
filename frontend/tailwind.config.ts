import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    screens: {
      sm: "640px",
      md: "768px",
      lg: "1024px",
      xl: "1280px",
      "2xl": "1400px",
    },
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        chart: {
          1: "hsl(var(--chart-1))",
          2: "hsl(var(--chart-2))",
          3: "hsl(var(--chart-3))",
          4: "hsl(var(--chart-4))",
          5: "hsl(var(--chart-5))",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "Inter", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "Fira Code", "Consolas", "monospace"],
        display: ["var(--font-inter)", "Inter", "system-ui", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
      },
      fontSize: {
        xs: ["var(--font-size-xs)", { lineHeight: "1rem", letterSpacing: "0.025em" }],
        sm: ["var(--font-size-sm)", { lineHeight: "1.25rem", letterSpacing: "0.015em" }],
        base: ["var(--font-size-base)", { lineHeight: "1.5rem", letterSpacing: "0" }],
        lg: ["var(--font-size-lg)", { lineHeight: "1.75rem", letterSpacing: "-0.01em" }],
        xl: ["var(--font-size-xl)", { lineHeight: "1.75rem", letterSpacing: "-0.02em" }],
        "2xl": ["var(--font-size-2xl)", { lineHeight: "2rem", letterSpacing: "-0.02em" }],
        "3xl": ["var(--font-size-3xl)", { lineHeight: "2.25rem", letterSpacing: "-0.02em" }],
        "4xl": ["var(--font-size-4xl)", { lineHeight: "2.75rem", letterSpacing: "-0.03em" }],
        "5xl": ["var(--font-size-5xl)", { lineHeight: "3.5rem", letterSpacing: "-0.03em" }],
      },
      spacing: {
        "responsive-xs": "var(--spacing-xs)",
        "responsive-sm": "var(--spacing-sm)",
        "responsive-md": "var(--spacing-md)",
        "responsive-lg": "var(--spacing-lg)",
        "responsive-xl": "var(--spacing-xl)",
        "responsive-2xl": "var(--spacing-2xl)",
        "responsive-3xl": "var(--spacing-3xl)",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        xl: "var(--radius-xl)",
        "2xl": "var(--radius-2xl)",
        "3xl": "var(--radius-3xl)",
      },
      boxShadow: {
        responsive: "var(--shadow-sm)",
        "responsive-md": "var(--shadow-md)",
        "responsive-lg": "var(--shadow-lg)",
        "responsive-xl": "var(--shadow-xl)",
      },
      transitionDuration: {
        fast: "150ms",
        base: "200ms",
        slow: "300ms",
        slower: "500ms",
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
      zIndex: {
        dropdown: "100",
        sticky: "200",
        overlay: "300",
        modal: "400",
        popover: "500",
        tooltip: "600",
        toast: "700",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "fade-in-left": {
          from: { opacity: "0", transform: "translateX(-10px)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
        "slide-up": {
          from: { opacity: "0", transform: "translateY(16px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "slide-down": {
          from: { opacity: "0", transform: "translateY(-16px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in": {
          from: { opacity: "0", transform: "scale(0.95)" },
          to: { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "pulse-subtle": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "fade-in": "fade-in 0.3s ease-out forwards",
        "fade-in-left": "fade-in-left 0.3s ease-out forwards",
        "slide-up": "slide-up 0.3s ease-out forwards",
        "slide-down": "slide-down 0.3s ease-out forwards",
        "scale-in": "scale-in 0.2s ease-out forwards",
        shimmer: "shimmer 2s infinite linear",
        "pulse-subtle": "pulse-subtle 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
