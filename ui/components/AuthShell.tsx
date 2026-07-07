"use client";

import type { ReactNode } from "react";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { api, User } from "@/lib/api";
import { Sidebar, SidebarItem } from "@/components/Sidebar";

type AuthContextValue = {
  user: User;
  setUser: (user: User) => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function activeFromPath(pathname: string): SidebarItem {
  if (pathname.startsWith("/products")) return "produtos";
  if (pathname.startsWith("/cart")) return "carrinho";
  if (pathname.startsWith("/profile")) return "usuario";
  if (pathname.startsWith("/register")) return "novo-usuario";
  return "home";
}

export function AuthShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    api<User>("/api/auth/me/")
      .then((currentUser) => {
        setUser(currentUser);

        if (currentUser.role === "manager" && pathname.startsWith("/cart")) {
          router.replace("/home");
        }

        if (currentUser.role !== "manager" && pathname.startsWith("/register")) {
          router.replace("/home");
        }
      })
      .catch(() => router.replace("/"));
  }, [pathname, router]);

  const value = useMemo(() => (user ? { user, setUser } : null), [user]);

  if (!user || !value) {
    return <main className="main-loading" />;
  }

  return (
    <AuthContext.Provider value={value}>
      <section className="dashboard">
        <Sidebar user={user} active={activeFromPath(pathname)} />
        <main className="main page-transition" key={pathname}>{children}</main>
      </section>
    </AuthContext.Provider>
  );
}

export function useCurrentUser() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useCurrentUser must be used inside AuthShell.");
  }

  return context;
}
