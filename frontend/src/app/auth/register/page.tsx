"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Mail, Lock, User, Eye, EyeOff, Library, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";

const registerSchema = z
  .object({
    full_name: z.string().min(2, "Name must be at least 2 characters"),
    username: z
      .string()
      .min(3, "Username must be at least 3 characters")
      .regex(/^[a-zA-Z0-9_]+$/, "Only letters, numbers, and underscores"),
    email: z.string().email("Please enter a valid email address"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Must contain at least one uppercase letter")
      .regex(/[a-z]/, "Must contain at least one lowercase letter")
      .regex(/[0-9]/, "Must contain at least one number"),
    password_confirm: z.string(),
  })
  .refine((data) => data.password === data.password_confirm, {
    message: "Passwords do not match",
    path: ["password_confirm"],
  });

type RegisterForm = z.infer<typeof registerSchema>;

function getPasswordStrength(password: string): { score: number; label: string; color: string } {
  if (!password) return { score: 0, label: "", color: "" };
  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;

  if (score <= 2) return { score, label: "Weak", color: "bg-destructive" };
  if (score <= 4) return { score, label: "Fair", color: "bg-yellow-500" };
  return { score, label: "Strong", color: "bg-green-500" };
}

export default function RegisterPage() {
  const { t } = useI18n();
  const { register: registerUser, loading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const passwordValue = watch("password", "");
  const strength = getPasswordStrength(passwordValue);

  const onSubmit = async (data: RegisterForm) => {
    setServerError(null);
    try {
      await registerUser(data);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : t("auth.registerFailed"));
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
          <h1 className="text-xl sm:text-2xl font-bold">{t("auth.createAccount")}</h1>
          <p className="text-muted-foreground text-xs sm:text-sm mt-1">
            {t("auth.createAccountDesc")}
          </p>
        </div>

        <Card>
          <CardHeader className="pb-3 sm:pb-6">
            <CardTitle className="text-base sm:text-lg">{t("auth.signUp")}</CardTitle>
            <CardDescription className="text-xs sm:text-sm">
              {t("auth.signUpDesc")}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 sm:space-y-5">
              {serverError && (
                <div className="p-3 rounded-lg bg-destructive/10 text-destructive text-xs sm:text-sm">
                  {serverError}
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div className="space-y-2">
                  <label htmlFor="full_name" className="text-sm font-medium block">
                    {t("auth.fullName")}
                  </label>
                  <Input
                    id="full_name"
                    placeholder={t("auth.fullNamePlaceholder")}
                    icon={<User className="h-4 w-4" />}
                    error={errors.full_name?.message}
                    {...register("full_name")}
                    className="h-11 md:h-12"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="username" className="text-sm font-medium block">
                    {t("auth.username")}
                  </label>
                  <Input
                    id="username"
                    placeholder={t("auth.usernamePlaceholder")}
                    icon={<User className="h-4 w-4" />}
                    error={errors.username?.message}
                    {...register("username")}
                    className="h-11 md:h-12"
                  />
                </div>
              </div>

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
                    placeholder={t("auth.createPassword")}
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
                {passwordValue && (
                  <div className="mt-2 space-y-1.5">
                    <div className="flex gap-1.5">
                      {[1, 2, 3, 4, 5].map((level) => (
                        <div
                          key={level}
                          className={cn(
                            "h-1 flex-1 rounded-full transition-colors",
                            level <= strength.score ? strength.color : "bg-muted"
                          )}
                        />
                      ))}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {strength.label} password
                    </p>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <label htmlFor="password_confirm" className="text-sm font-medium block">
                  {t("auth.confirmPassword")}
                </label>
                <Input
                  id="password_confirm"
                  type="password"
                  placeholder={t("auth.confirmPasswordPlaceholder")}
                  icon={<Lock className="h-4 w-4" />}
                  error={errors.password_confirm?.message}
                  {...register("password_confirm")}
                  className="h-11 md:h-12"
                />
              </div>

              <div className="text-xs sm:text-sm text-muted-foreground">
                <label className="flex items-start gap-2 cursor-pointer">
                  <input type="checkbox" className="rounded border-input h-4 w-4 mt-0.5 shrink-0" required />
                  <span>
                    {t("auth.agreeTerms")}{" "}
                    <Link href="/terms" className="text-primary hover:underline">
                      {t("auth.termsOfService")}
                    </Link>
                    {" "}
                    {t("common.and")}
                    {" "}
                    <Link href="/privacy" className="text-primary hover:underline">
                      {t("auth.privacyPolicy")}
                    </Link>
                  </span>
                </label>
              </div>

              <Button
                type="submit"
                className="w-full h-11 md:h-12 text-sm sm:text-base"
                size="lg"
                disabled={loading}
              >
                {loading ? t("common.loading") : t("auth.createAccountButton")}
                {!loading && <ArrowRight className="ml-2 h-4 w-4" />}
              </Button>
            </form>

            <div className="mt-5 sm:mt-6 text-center text-xs sm:text-sm">
              <span className="text-muted-foreground">{t("auth.hasAccount")} </span>
              <Link
                href="/auth/login"
                className="text-primary hover:text-primary/80 font-medium"
              >
                {t("auth.signInLink")}
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
