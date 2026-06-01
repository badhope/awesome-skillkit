import { createContext, useContext, useState, useEffect, useCallback, useMemo } from "react";

export type Locale = "en" | "zh";

export interface TranslationKeys {
  common: {
    home: string;
    search: string;
    skills: string;
    categories: string;
    tags: string;
    login: string;
    register: string;
    logout: string;
    dashboard: string;
    settings: string;
    loading: string;
    error: string;
    retry: string;
    save: string;
    cancel: string;
    delete: string;
    edit: string;
    create: string;
    back: string;
    next: string;
    prev: string;
    more: string;
    less: string;
    showAll: string;
    filter: string;
    sort: string;
    results: string;
    noResults: string;
    popular: string;
    trending: string;
    featured: string;
    newest: string;
    rating: string;
    downloads: string;
    views: string;
    version: string;
    author: string;
    description: string;
    status: string;
    actions: string;
    copy: string;
    copied: string;
    share: string;
    download: string;
    use: string;
    install: string;
    all: string;
    none: string;
  };
  nav: {
    home: string;
    browse: string;
    search: string;
    categories: string;
    compositions: string;
    dashboard: string;
    signIn: string;
    signUp: string;
    profile: string;
    signOut: string;
    themeToggle: string;
    skills: string;
    more: string;
    toggleMenu: string;
    closeMenu: string;
    language: string;
    english: string;
    chinese: string;
    searchPlaceholder: string;
    searchPlaceholderMobile: string;
    allCategories: string;
    favorites: string;
  };
  hero: {
    title: string;
    subtitle: string;
    searchPlaceholder: string;
    popularSearches: string;
    ctaTitle: string;
    ctaDescription: string;
    ctaButton: string;
    categories: { title: string; subtitle: string };
  };
  skills: {
    title: string;
    subtitle: string;
    totalSkills: string;
    filterByCategory: string;
    filterByTag: string;
    sortBy: string;
    relevance: string;
    highestRated: string;
    mostDownloaded: string;
    newest: string;
    recentlyUpdated: string;
    clearFilters: string;
    noSkillsFound: string;
    tryAdjusting: string;
    noPublishedYet: string;
    pageOf: string;
    perPage: string;
    showing: string;
    viewAll: string;
  };
  skillDetail: {
    versions: string;
    dependencies: string;
    similarSkills: string;
    reviews: string;
    overview: string;
    usage: string;
    backToList: string;
    useSkill: string;
    downloadSkill: string;
    rateSkill: string;
    copyPrompt: string;
    promptCopied: string;
    lastUpdated: string;
    complexity: string;
    license: string;
    source: string;
    platform: string;
    tags: string;
    changelog: string;
    noReviews: string;
    writeReview: string;
    submitReview: string;
    avgRating: string;
    totalRatings: string;
    viewCount: string;
    downloadCount: string;
    details: string;
    published: string;
    draft: string;
    deprecated: string;
    archived: string;
    byAuthor: string;
    updated: string;
  };
  category: {
    title: string;
    subtitle: string;
    skillCount: string;
    subcategories: string;
    noCategories: string;
    browseByCategory: string;
    all: string;
    clear: string;
    selectCategory: string;
    skillsCount: string;
    showAll: string;
  };
  search: {
    title: string;
    subtitle: string;
    placeholder: string;
    placeholderHero: string;
    placeholderNav: string;
    semanticSearchHint: string;
    noResults: string;
    tryDifferent: string;
    foundResults: string;
    sorting: string;
    recentSearches: string;
    popularSuggestions: string;
    viewAllResults: string;
    clearRecent: string;
    clearSearch: string;
    loading: string;
  };
  auth: {
    loginTitle: string;
    loginSubtitle: string;
    registerTitle: string;
    registerSubtitle: string;
    email: string;
    password: string;
    confirmPassword: string;
    username: string;
    fullName: string;
    forgotPassword: string;
    rememberMe: string;
    orContinueWith: string;
    noAccount: string;
    hasAccount: string;
    createAccount: string;
    signInAccount: string;
    agreeTerms: string;
    termsLink: string;
    privacyLink: string;
    passwordStrength: string;
    weak: string;
    fair: string;
    good: string;
    strong: string;
    invalidEmail: string;
    requiredField: string;
    passwordMismatch: string;
    accountCreated: string;
    loginFailed: string;
  };
  dashboard: {
    title: string;
    overview: string;
    usageTrends: string;
    popularSkills: string;
    categoryDistribution: string;
    totalSkills: string;
    totalUsers: string;
    totalCategories: string;
    totalUsage: string;
    successRate: string;
    activeUsers7d: string;
    newSkills30d: string;
    platformOverview: string;
    topTags: string;
    dailyActivity: string;
  };
  composition: {
    title: string;
    subtitle: string;
    createComposition: string;
    editComposition: string;
    noCompositions: string;
    workflow: string;
    items: string;
    addItem: string;
    removeItem: string;
    reorder: string;
    config: string;
    runComposition: string;
    noItems: string;
  };
  footer: {
    description: string;
    quickLinks: string;
    resources: string;
    legal: string;
    about: string;
    docs: string;
    api: string;
    blog: string;
    github: string;
    terms: string;
    privacy: string;
    contact: string;
    madeWith: string;
    copyright: string;
    product: string;
    browseSkills: string;
    categoriesLink: string;
    compositionsLink: string;
    searchLink: string;
    dashboardLink: string;
    documentation: string;
    apiReference: string;
    tutorials: string;
    changelog: string;
    discord: string;
    twitter: string;
    forum: string;
    contributors: string;
    privacyPolicy: string;
    termsOfService: string;
    license: string;
    security: string;
  };
  meta: {
    siteName: string;
    siteDescription: string;
  };
}

const translations: Record<Locale, TranslationKeys> = {
  en: {
    common: {
      home: "Home",
      search: "Search",
      skills: "Skills",
      categories: "Categories",
      tags: "Tags",
      login: "Login",
      register: "Register",
      logout: "Logout",
      dashboard: "Dashboard",
      settings: "Settings",
      loading: "Loading...",
      error: "An error occurred",
      retry: "Retry",
      save: "Save",
      cancel: "Cancel",
      delete: "Delete",
      edit: "Edit",
      create: "Create",
      back: "Back",
      next: "Next",
      prev: "Previous",
      more: "More",
      less: "Less",
      showAll: "Show All",
      filter: "Filter",
      sort: "Sort",
      results: "Results",
      noResults: "No results found",
      popular: "Popular",
      trending: "Trending",
      featured: "Featured",
      newest: "Newest",
      rating: "Rating",
      downloads: "Downloads",
      views: "Views",
      version: "Version",
      author: "Author",
      description: "Description",
      status: "Status",
      actions: "Actions",
      copy: "Copy",
      copied: "Copied!",
      share: "Share",
      download: "Download",
      use: "Use",
      install: "Install",
      all: "All",
      none: "None",
    },
    nav: {
      home: "Home",
      browse: "Browse",
      search: "Search",
      categories: "Categories",
      compositions: "Compositions",
      dashboard: "Dashboard",
      signIn: "Sign In",
      signUp: "Get Started",
      profile: "Profile",
      signOut: "Sign Out",
      themeToggle: "Toggle theme",
      skills: "Skills",
      more: "More",
      toggleMenu: "Toggle menu",
      closeMenu: "Close menu",
      language: "Language",
      english: "English",
      chinese: "中文",
      searchPlaceholder: "Search skills, categories, tags...",
      searchPlaceholderMobile: "Search skills...",
      allCategories: "All Categories",
      favorites: "Favorites",
    },
    hero: {
      title: "Discover AI Skills for Every Task",
      subtitle:
        "Explore, compose, and share powerful AI skills. From NLP to computer vision, find the perfect skill for your project.",
      searchPlaceholder: "Search skills by name, tag, or description...",
      popularSearches: "Popular Searches",
      ctaTitle: "Ready to Get Started?",
      ctaDescription:
        "Join thousands of developers using AI skills to build smarter applications faster.",
      ctaButton: "Explore Skills",
      categories: { title: "Browse Categories", subtitle: "Find skills by domain" },
    },
    skills: {
      title: "AI Skills Library",
      subtitle: "Browse and discover AI-powered skills for your projects",
      totalSkills: "Total Skills",
      filterByCategory: "Filter by Category",
      filterByTag: "Filter by Tag",
      sortBy: "Sort By",
      relevance: "Relevance",
      highestRated: "Highest Rated",
      mostDownloaded: "Most Downloaded",
      newest: "Newest First",
      recentlyUpdated: "Recently Updated",
      clearFilters: "Clear Filters",
      noSkillsFound: "No skills found",
      tryAdjusting: "Try adjusting your filters or search terms",
      noPublishedYet: "No skills published yet",
      pageOf: "of",
      perPage: "per page",
      showing: "Showing",
      viewAll: "View All",
    },
    skillDetail: {
      versions: "Versions",
      dependencies: "Dependencies",
      similarSkills: "Similar Skills",
      reviews: "Reviews",
      overview: "Overview",
      usage: "Usage",
      backToList: "Back to List",
      useSkill: "Use Skill",
      downloadSkill: "Download Skill",
      rateSkill: "Rate Skill",
      copyPrompt: "Copy Prompt",
      promptCopied: "Prompt Copied!",
      lastUpdated: "Last Updated",
      complexity: "Complexity",
      license: "License",
      source: "Source",
      platform: "Platform",
      tags: "Tags",
      changelog: "Changelog",
      noReviews: "No reviews yet",
      writeReview: "Write a Review",
      submitReview: "Submit Review",
      avgRating: "Average Rating",
      totalRatings: "Total Ratings",
      viewCount: "View Count",
      downloadCount: "Download Count",
      details: "Details",
      published: "Published",
      draft: "Draft",
      deprecated: "Deprecated",
      archived: "Archived",
      byAuthor: "by @{author}",
      updated: "Updated {time}",
    },
    category: {
      title: "Categories",
      subtitle: "Browse skills by category",
      skillCount: "{count} skills",
      subcategories: "Subcategories",
      noCategories: "No categories available",
      browseByCategory: "Browse by Category",
      all: "All Categories",
      clear: "Clear",
      selectCategory: "Select Category",
      skillsCount: "{count} skills",
      showAll: "Show All Categories",
    },
    search: {
      title: "Search Skills",
      subtitle: "Find the perfect AI skill for your needs",
      placeholder: "Search skills by name, description, or tags...",
      placeholderHero: "Search the entire skill library...",
      placeholderNav: "Search...",
      semanticSearchHint: 'Try natural language queries like "summarize text" or "extract entities"',
      noResults: 'No results found for "{query}"',
      tryDifferent: "Try different keywords or browse categories",
      foundResults: "results found",
      sorting: "Sort Results",
      recentSearches: "Recent Searches",
      popularSuggestions: "Popular Suggestions",
      viewAllResults: 'View all results for "{query}"',
      clearRecent: "Clear recent searches",
      clearSearch: "Clear search",
      loading: "Searching...",
    },
    auth: {
      loginTitle: "Welcome Back",
      loginSubtitle: "Sign in to access your dashboard and saved skills",
      registerTitle: "Create Account",
      registerSubtitle: "Join the AI Skill community today",
      email: "Email Address",
      password: "Password",
      confirmPassword: "Confirm Password",
      username: "Username",
      fullName: "Full Name",
      forgotPassword: "Forgot Password?",
      rememberMe: "Remember me",
      orContinueWith: "Or continue with",
      noAccount: "Don't have an account?",
      hasAccount: "Already have an account?",
      createAccount: "Create Account",
      signInAccount: "Sign In",
      agreeTerms: "I agree to the {terms} and {privacy}",
      termsLink: "Terms of Service",
      privacyLink: "Privacy Policy",
      passwordStrength: "Password Strength",
      weak: "Weak",
      fair: "Fair",
      good: "Good",
      strong: "Strong",
      invalidEmail: "Please enter a valid email address",
      requiredField: "This field is required",
      passwordMismatch: "Passwords do not match",
      accountCreated: "Account created successfully!",
      loginFailed: "Invalid email or password",
    },
    dashboard: {
      title: "Dashboard",
      overview: "Overview",
      usageTrends: "Usage Trends",
      popularSkills: "Popular Skills",
      categoryDistribution: "Category Distribution",
      totalSkills: "Total Skills",
      totalUsers: "Total Users",
      totalCategories: "Total Categories",
      totalUsage: "Total Usage",
      successRate: "Success Rate",
      activeUsers7d: "Active Users (7d)",
      newSkills30d: "New Skills (30d)",
      platformOverview: "Platform Overview",
      topTags: "Top Tags",
      dailyActivity: "Daily Activity",
    },
    composition: {
      title: "Skill Compositions",
      subtitle: "Combine multiple skills into powerful workflows",
      createComposition: "Create Composition",
      editComposition: "Edit Composition",
      noCompositions: "No compositions yet",
      workflow: "Workflow",
      items: "Items",
      addItem: "Add Item",
      removeItem: "Remove Item",
      reorder: "Reorder",
      config: "Configuration",
      runComposition: "Run Composition",
      noItems: "No items in this composition",
    },
    footer: {
      description:
        "A comprehensive library of AI-powered skills. Discover, share, and compose intelligent capabilities for your applications.",
      quickLinks: "Quick Links",
      resources: "Resources",
      legal: "Legal",
      about: "About",
      docs: "Documentation",
      api: "API Reference",
      blog: "Blog",
      github: "GitHub",
      terms: "Terms of Service",
      privacy: "Privacy Policy",
      contact: "Contact",
      madeWith: "Made with love by the community",
      copyright: "© {year} AI Skill Library. All rights reserved.",
      product: "Product",
      browseSkills: "Browse Skills",
      categoriesLink: "Categories",
      compositionsLink: "Compositions",
      searchLink: "Search",
      dashboardLink: "Dashboard",
      documentation: "Documentation",
      apiReference: "API Reference",
      tutorials: "Tutorials",
      changelog: "Changelog",
      discord: "Discord",
      twitter: "Twitter",
      forum: "Forum",
      contributors: "Contributors",
      privacyPolicy: "Privacy Policy",
      termsOfService: "Terms of Service",
      license: "License",
      security: "Security",
    },
    meta: {
      siteName: "AI Skill Library",
      siteDescription:
        "Discover, share, and compose AI skills. A comprehensive library of intelligent capabilities for modern applications.",
    },
  },

  zh: {
    common: {
      home: "首页",
      search: "搜索",
      skills: "技能库",
      categories: "分类",
      tags: "标签",
      login: "登录",
      register: "注册",
      logout: "退出登录",
      dashboard: "控制台",
      settings: "设置",
      loading: "加载中...",
      error: "发生错误",
      retry: "重试",
      save: "保存",
      cancel: "取消",
      delete: "删除",
      edit: "编辑",
      create: "创建",
      back: "返回",
      next: "下一页",
      prev: "上一页",
      more: "更多",
      less: "收起",
      showAll: "显示全部",
      filter: "筛选",
      sort: "排序",
      results: "结果",
      noResults: "暂无结果",
      popular: "热门",
      trending: "趋势",
      featured: "推荐",
      newest: "最新",
      rating: "评分",
      downloads: "下载量",
      views: "浏览量",
      version: "版本",
      author: "作者",
      description: "描述",
      status: "状态",
      actions: "操作",
      copy: "复制",
      copied: "已复制！",
      share: "分享",
      download: "下载",
      use: "使用",
      install: "安装",
      all: "全部",
      none: "无",
    },
    nav: {
      home: "首页",
      browse: "浏览",
      search: "搜索",
      categories: "分类",
      compositions: "组合技能",
      dashboard: "控制台",
      signIn: "登录",
      signUp: "立即开始",
      profile: "个人中心",
      signOut: "退出登录",
      themeToggle: "切换主题",
      skills: "技能库",
      more: "更多",
      toggleMenu: "切换菜单",
      closeMenu: "关闭菜单",
      language: "语言",
      english: "English",
      chinese: "中文",
      searchPlaceholder: "搜索技能、分类、标签...",
      searchPlaceholderMobile: "搜索技能...",
      allCategories: "全部分类",
      favorites: "收藏夹",
    },
    hero: {
      title: "发现适用于各种任务的AI技能",
      subtitle:
        "探索、组合和分享强大的AI技能。从自然语言处理到计算机视觉，为您的项目找到完美的技能。",
      searchPlaceholder: "按名称、标签或描述搜索技能...",
      popularSearches: "热门搜索",
      ctaTitle: "准备好开始了吗？",
      ctaDescription:
        "加入数千名使用AI技能更快构建智能应用的开发者行列。",
      ctaButton: "探索技能",
      categories: { title: "浏览分类", subtitle: "按领域查找技能" },
    },
    skills: {
      title: "AI技能库",
      subtitle: "浏览和发现适用于您项目的AI驱动技能",
      totalSkills: "总技能数",
      filterByCategory: "按分类筛选",
      filterByTag: "按标签筛选",
      sortBy: "排序方式",
      relevance: "相关度",
      highestRated: "最高评分",
      mostDownloaded: "最多下载",
      newest: "最新发布",
      recentlyUpdated: "最近更新",
      clearFilters: "清除筛选",
      noSkillsFound: "未找到技能",
      tryAdjusting: "尝试调整筛选条件或搜索词",
      noPublishedYet: "尚无已发布的技能",
      pageOf: "/ 共",
      perPage: "条/页",
      showing: "显示",
      viewAll: "查看全部",
    },
    skillDetail: {
      versions: "版本历史",
      dependencies: "依赖项",
      similarSkills: "相似技能",
      reviews: "评价",
      overview: "概览",
      usage: "使用方法",
      backToList: "返回列表",
      useSkill: "使用技能",
      downloadSkill: "下载技能",
      rateSkill: "评价技能",
      copyPrompt: "复制提示词",
      promptCopied: "提示词已复制！",
      lastUpdated: "最后更新",
      complexity: "复杂度",
      license: "许可证",
      source: "来源",
      platform: "平台",
      tags: "标签",
      changelog: "更新日志",
      noReviews: "暂无评价",
      writeReview: "撰写评价",
      submitReview: "提交评价",
      avgRating: "平均评分",
      totalRatings: "总评分数",
      viewCount: "浏览次数",
      downloadCount: "下载次数",
      details: "详情",
      published: "已发布",
      draft: "草稿",
      deprecated: "已弃用",
      archived: "已归档",
      byAuthor: "作者 @{author}",
      updated: "更新于 {time}",
    },
    category: {
      title: "分类",
      subtitle: "按分类浏览技能",
      skillCount: "{count} 个技能",
      subcategories: "子分类",
      noCategories: "暂无可用分类",
      browseByCategory: "按分类浏览",
      all: "全部分类",
      clear: "清除",
      selectCategory: "选择分类",
      skillsCount: "{count} 个技能",
      showAll: "显示全部分类",
    },
    search: {
      title: "搜索技能",
      subtitle: "找到适合您需求的AI技能",
      placeholder: "按名称、描述或标签搜索技能...",
      placeholderHero: "搜索整个技能库...",
      placeholderNav: "搜索...",
      semanticSearchHint: "尝试自然语言查询，如「总结文本」或「提取实体」",
      noResults: '"{query}" 未找到结果',
      tryDifferent: "尝试不同的关键词或浏览分类",
      foundResults: "个结果",
      sorting: "排序方式",
      recentSearches: "最近搜索",
      popularSuggestions: "热门推荐",
      viewAllResults: '查看"{query}"的全部结果',
      clearRecent: "清除历史记录",
      clearSearch: "清除搜索",
      loading: "搜索中...",
    },
    auth: {
      loginTitle: "欢迎回来",
      loginSubtitle: "登录以访问控制台和保存的技能",
      registerTitle: "创建账户",
      registerSubtitle: "立即加入AI技能社区",
      email: "邮箱地址",
      password: "密码",
      confirmPassword: "确认密码",
      username: "用户名",
      fullName: "姓名",
      forgotPassword: "忘记密码？",
      rememberMe: "记住我",
      orContinueWith: "或通过以下方式继续",
      noAccount: "还没有账户？",
      hasAccount: "已有账户？",
      createAccount: "创建账户",
      signInAccount: "登录",
      agreeTerms: "我同意{terms}和{privacy}",
      termsLink: "服务条款",
      privacyLink: "隐私政策",
      passwordStrength: "密码强度",
      weak: "弱",
      fair: "一般",
      good: "良好",
      strong: "强",
      invalidEmail: "请输入有效的邮箱地址",
      requiredField: "此字段为必填项",
      passwordMismatch: "两次输入的密码不一致",
      accountCreated: "账户创建成功！",
      loginFailed: "邮箱或密码错误",
    },
    dashboard: {
      title: "控制台",
      overview: "数据概览",
      usageTrends: "使用趋势",
      popularSkills: "热门技能",
      categoryDistribution: "分类分布",
      totalSkills: "总技能数",
      totalUsers: "总用户数",
      totalCategories: "总分类数",
      totalUsage: "总使用量",
      successRate: "成功率",
      activeUsers7d: "近7日活跃用户",
      newSkills30d: "近30日新增技能",
      platformOverview: "平台概览",
      topTags: "热门标签",
      dailyActivity: "每日活跃度",
    },
    composition: {
      title: "技能组合",
      subtitle: "将多个技能组合为强大的工作流",
      createComposition: "创建组合",
      editComposition: "编辑组合",
      noCompositions: "暂无组合",
      workflow: "工作流",
      items: "项目",
      addItem: "添加项目",
      removeItem: "移除项目",
      reorder: "调整顺序",
      config: "配置",
      runComposition: "运行组合",
      noItems: "此组合中暂无项目",
    },
    footer: {
      description:
        "一个全面的AI技能库。发现、分享和组合智能能力，为您的应用赋能。",
      quickLinks: "快速链接",
      resources: "资源",
      legal: "法律信息",
      about: "关于我们",
      docs: "文档",
      api: "API参考",
      blog: "博客",
      github: "GitHub",
      terms: "服务条款",
      privacy: "隐私政策",
      contact: "联系我们",
      madeWith: "由社区用心打造",
      copyright: "© {year} AI 技能库。保留所有权利。",
      product: "产品",
      browseSkills: "浏览技能",
      categoriesLink: "分类",
      compositionsLink: "组合",
      searchLink: "搜索",
      dashboardLink: "控制台",
      documentation: "文档",
      apiReference: "API 参考",
      tutorials: "教程",
      changelog: "更新日志",
      discord: "Discord",
      twitter: "Twitter",
      forum: "论坛",
      contributors: "贡献者",
      privacyPolicy: "隐私政策",
      termsOfService: "服务条款",
      license: "许可协议",
      security: "安全",
    },
    meta: {
      siteName: "AI技能库",
      siteDescription: "发现、分享和组合AI技能。为现代应用提供全面的智能能力库。",
    },
  },
};

export function getTranslations(locale: Locale): TranslationKeys {
  return translations[locale];
}

function getDefaultLocale(): Locale {
  if (typeof window === "undefined") return "en";
  const stored = localStorage.getItem("skilllib-locale") as Locale | null;
  if (stored && (stored === "en" || stored === "zh")) return stored;
  const browserLang = navigator.language.toLowerCase();
  if (browserLang.startsWith("zh")) return "zh";
  return "en";
}

export function detectLocale(): Locale {
  return getDefaultLocale();
}

export { translations };

type NestedObject = Record<string, unknown>;

function getNestedValue(obj: NestedObject, path: string): string {
  const keys = path.split(".");
  let current: unknown = obj;
  for (const key of keys) {
    if (current && typeof current === "object" && key in (current as NestedObject)) {
      current = (current as NestedObject)[key];
    } else {
      return path;
    }
  }
  return typeof current === "string" ? current : path;
}

export interface I18nContextType {
  t: (key: string) => string;
  locale: Locale;
  isZh: boolean;
  setLocale: (locale: Locale) => void;
}

const I18nContext = createContext<I18nContextType | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const stored = localStorage.getItem("skilllib-locale") as Locale | null;
    if (stored && (stored === "en" || stored === "zh")) {
      setLocaleState(stored);
    } else {
      const browserLang = navigator.language.toLowerCase();
      setLocaleState(browserLang.startsWith("zh") ? "zh" : "en");
    }
    setMounted(true);
  }, []);

  const setLocale = useCallback((newLocale: Locale) => {
    setLocaleState(newLocale);
    if (typeof window !== "undefined") {
      localStorage.setItem("skilllib-locale", newLocale);
      document.documentElement.lang = newLocale === "zh" ? "zh-CN" : "en";
    }
  }, []);

  const t = useCallback(
    (key: string): string => {
      const dict = translations[locale];
      const value = getNestedValue(dict as unknown as NestedObject, key);
      return value;
    },
    [locale]
  );

  const value = useMemo<I18nContextType>(
    () => ({ t, locale, isZh: locale === "zh", setLocale }),
    [t, locale, setLocale]
  );

  if (!mounted) {
    return (
      <I18nContext.Provider
        value={{
          t: (k) => getNestedValue(translations.en as unknown as NestedObject, k),
          locale: "en",
          isZh: false,
          setLocale: () => {},
        }}
      >
        {children}
      </I18nContext.Provider>
    );
  }

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextType {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used within an I18nProvider");
  }
  return context;
}

export { I18nContext };
