"use client";

import * as React from "react";
import { usePathname, useRouter } from "next/navigation";
import { authService, UserSession } from "@/services/api";
import { Loader2 } from "lucide-react";

interface AuthContextType {
  user: UserSession | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string, remember: boolean) => Promise<void>;
  register: (email: string, name: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<UserSession | null>(null);
  const [token, setToken] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  
  const pathname = usePathname();
  const router = useRouter();

  // 1. Session Restoration on load
  React.useEffect(() => {
    async function restoreSession() {
      try {
        const storedToken = localStorage.getItem("filmaura_jwt");
        if (storedToken) {
          const fetchedUser = await authService.getCurrentUser(storedToken);
          setToken(storedToken);
          setUser(fetchedUser);
        }
      } catch (err) {
        console.warn("Session restoration failed:", err);
        localStorage.removeItem("filmaura_jwt");
        localStorage.removeItem("filmaura_session");
      } finally {
        setIsLoading(false);
      }
    }
    restoreSession();
  }, []);

  // 2. Client-side route protection redirects
  React.useEffect(() => {
    if (isLoading) return;

    const isPublicPath = pathname === "/login" || pathname === "/register";
    
    if (!user && !isPublicPath) {
      // Force redirect to login page for private views
      router.push("/login");
    } else if (user && isPublicPath) {
      // Redirect authenticated users away from login/register to dashboard home
      router.push("/");
    }
  }, [user, isLoading, pathname, router]);

  const login = async (email: string, password: string, remember: boolean) => {
    setIsLoading(true);
    try {
      const response = await authService.login(email, password);
      setUser(response.user);
      setToken(response.token);
      
      if (remember) {
        localStorage.setItem("filmaura_jwt", response.token);
        localStorage.setItem("filmaura_session", JSON.stringify(response.user));
      } else {
        sessionStorage.setItem("filmaura_jwt", response.token);
      }
      
      router.push("/");
    } catch (err) {
      setIsLoading(false);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, name: string, password: string) => {
    setIsLoading(true);
    try {
      await authService.register(email, name, password);
      router.push("/login");
    } catch (err) {
      setIsLoading(false);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
      setUser(null);
      setToken(null);
      localStorage.removeItem("filmaura_jwt");
      localStorage.removeItem("filmaura_session");
      sessionStorage.removeItem("filmaura_jwt");
      router.push("/login");
    } catch (err) {
      console.error("Logout failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const value = React.useMemo(
    () => ({
      user,
      token,
      isLoading,
      login,
      register,
      logout,
    }),
    [user, token, isLoading]
  );

  // Render a full-page loading spinner while recovering session credentials
  if (isLoading && pathname !== "/login" && pathname !== "/register") {
    return (
      <div className="flex h-screen w-screen flex-col items-center justify-center bg-[#06070a] text-foreground">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="mt-4 text-xs font-semibold text-muted-foreground animate-pulse">
          Restoring Cinematic Session...
        </p>
      </div>
    );
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be called within an AuthProvider");
  }
  return context;
}
