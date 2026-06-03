"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import {
  login as authLogin,
  register as authRegister,
  logout as authLogout,
  getStoredUser,
  fetchCurrentUser,
} from "@/lib/auth";
import type { User, LoginRequest, RegisterRequest } from "@/types";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const loadUser = useCallback(async () => {
    // Render the cached user first (no flicker), then let the server
    // re-validate via the HttpOnly cookie. If the cookie is gone,
    // fetchCurrentUser clears the cache and returns null.
    const storedUser = getStoredUser();
    if (storedUser) {
      setUser(storedUser);
    }
    try {
      const freshUser = await fetchCurrentUser();
      if (freshUser) {
        setUser(freshUser);
      } else {
        setUser(null);
      }
    } catch {
      // Network blip — keep showing the cached user rather than
      // logging them out for an unrelated reason.
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = useCallback(
    async (data: LoginRequest) => {
      setError(null);
      setLoading(true);
      try {
        const response = await authLogin(data);
        setUser(response.user);
        toast.success(`Welcome back, ${response.user.full_name || response.user.username}!`);
        router.push("/dashboard");
        router.refresh();
        return response;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Login failed";
        setError(message);
        toast.error(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [router]
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      setError(null);
      setLoading(true);
      try {
        const response = await authRegister(data);
        setUser(response.user);
        toast.success("Account created successfully! Welcome aboard!");
        router.push("/dashboard");
        router.refresh();
        return response;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Registration failed";
        setError(message);
        toast.error(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [router]
  );

  const logout = useCallback(async () => {
    try {
      await authLogout();
      setUser(null);
      toast.success("Logged out successfully");
      router.push("/");
      router.refresh();
    } catch {
      setUser(null);
      router.push("/");
      router.refresh();
    }
  }, [router]);

  return {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refresh: loadUser,
  };
}