"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Mail, Lock, Eye, EyeOff, Library, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/lib/i18n";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { t } = useI18n();
  const { login, loading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setServerError(null);
    try {
      await login(data);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : t("auth.loginFailed"));
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-8 sm:py-12 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-6 sm:mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-3 sm:mb-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 text-white">
              <Library className="h-5 w-5" />
            </div>
            <span className="font-bold text-lg bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
              SkillLib
            </span>
          </Link>
          <h1 className="text-xl sm:text-2xl font-bold">{t("auth.welcomeBack")}</h1>
          <p className="text-muted-foreground text-xs sm:text-sm mt-1">
            {t("auth.welcomeBackDesc")}
          </p>
        </div>

        <Card>
          <CardHeader className="pb-3 sm:pb-6">
            <CardTitle className="text-base sm:text-lg">{t("auth.signIn")}</CardTitle>
            <CardDescription className="text-xs sm:text-sm">
              {t("auth.signInDesc")}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 sm:space-y-5">
              {serverError && (
                <div className="p-3 rounded-lg bg-destructive/10 text-destructive text-xs sm:text-sm">
                  {serverError}
                </div>
              )}

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium block">
                  {t("auth.email")}
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder={t("auth.emailPlaceholder")}
                  icon={<Mail className="h-4 w-4" />}
                  error={errors.email?.message}
                  {...register("email")}
                  className="h-11 md:h-12"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium block">
                  {t("auth.password")}
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder={t("auth.passwordPlaceholder")}
                    icon={<Lock className="h-4 w-4" />}
                    rightIcon={
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="text-muted-foreground hover:text-foreground p-0.5"
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    }
                    error={errors.password?.message}
                    {...register("password")}
                    className="h-11 md:h-12"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-xs sm:text-sm">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="rounded border-input h-4 w-4" />
                  <span className="text-muted-foreground">{t("auth.rememberMe")}</span>
                </label>
                <Link
                  href="/auth/forgot-password"
                  className="text-primary hover:text-primary/80 whitespace-nowrap"
                >
                  {t("auth.forgotPassword")}
                </Link>
              </div>

              <Button
                type="submit"
                className="w-full h-11 md:h-12 text-sm sm:text-base"
                size="lg"
                disabled={loading}
              >
                {loading ? t("common.loading") : t("auth.signInButton")}
                {!loading && <ArrowRight className="ml-2 h-4 w-4" />}
              </Button>
            </form>

            <div className="mt-5 sm:mt-6 text-center text-xs sm:text-sm">
              <span className="text-muted-foreground">{t("auth.noAccount")} </span>
              <Link
                href="/auth/register"
                className="text-primary hover:text-primary/80 font-medium"
              >
                {t("auth.createOne")}
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
