import type { User, AuthTokens, LoginRequest, RegisterRequest, AuthResponse } from "@/types";
import { api } from "./api";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const USER_KEY = "user";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr) as User;
  } catch {
    return null;
  }
}

export function setTokens(tokens: AuthTokens): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export function setUser(user: User): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuth(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await api.auth.login(data);
  setTokens(response.tokens);
  setUser(response.user);
  return response;
}

export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await api.auth.register(data);
  setTokens(response.tokens);
  setUser(response.user);
  return response;
}

export async function logout(): Promise<void> {
  try {
    await api.auth.logout();
  } catch {
    // Silently catch logout errors
  } finally {
    clearAuth();
  }
}

export async function refreshAuth(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;
  try {
    const tokens = await api.auth.refreshToken(refreshToken);
    setTokens(tokens);
    return true;
  } catch {
    clearAuth();
    return false;
  }
}

export async function fetchCurrentUser(): Promise<User | null> {
  try {
    const data = await api.auth.me();
    setUser(data.user);
    return data.user;
  } catch {
    return null;
  }
}