import type { User, LoginRequest, RegisterRequest, AuthResponse } from "@/types";
import { api } from "./api";

const USER_KEY = "user";

// Note: tokens are now stored in HttpOnly cookies by the backend; we
// no longer touch them from JS. We only cache the *user* in
// localStorage for fast initial render; the server is the source of
// truth and is re-queried on every page load.
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

export function setUser(user: User): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearUser(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(USER_KEY);
}

export function isAuthenticated(): boolean {
  // The browser owns the cookie. We use the cached user as a hint;
  // `useAuth` will verify with the server on first mount.
  return !!getStoredUser();
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await api.auth.login(data);
  if (response.user) {
    setUser(response.user);
  }
  return response;
}

export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await api.auth.register(data);
  if (response.user) {
    setUser(response.user);
  }
  return response;
}

export async function logout(): Promise<void> {
  try {
    await api.auth.logout();
  } catch {
    // Even if the server call fails (network, expired cookie), wipe
    // the local user so the UI doesn't show a stale session.
  } finally {
    clearUser();
  }
}

export async function fetchCurrentUser(): Promise<User | null> {
  try {
    const data = await api.auth.me();
    if (data?.user) {
      setUser(data.user);
      return data.user;
    }
    clearUser();
    return null;
  } catch {
    clearUser();
    return null;
  }
}
