"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Home, LogOut, Package, ShoppingCart, UserRound, UserRoundPlus } from "lucide-react";
import { api, User } from "@/lib/api";

export type SidebarItem = "home" | "produtos" | "carrinho" | "usuario" | "novo-usuario";

type SidebarProps = {
  user: User;
  active: SidebarItem;
};

const iconLinkClasses =
  "flex min-h-12 w-full items-center justify-center rounded-lg text-slate-300 transition-colors hover:bg-slate-800 hover:text-white";

function linkClasses(isActive: boolean) {
  return `${iconLinkClasses} ${isActive ? "bg-slate-800 text-white" : ""}`;
}

export function Sidebar({ user, active }: SidebarProps) {
  const router = useRouter();
  const isManager = user.role === "manager";

  async function logout() {
    await api("/api/auth/logout/", {
      method: "POST",
      body: JSON.stringify({}),
    });
    router.push("/");
  }

  return (
    <aside className="grid min-h-screen grid-rows-[1fr_auto] gap-7 bg-slate-900 px-5 py-7 text-slate-50">
      <nav className="grid content-start gap-2" aria-label="Navegação principal">
        <Link className={linkClasses(active === "home")} href="/home" title="Home">
          <Home className="h-6 w-6" />
          <span className="sr-only">Home</span>
        </Link>
        <Link className={linkClasses(active === "produtos")} href="/products" title="Produtos">
          <Package className="h-6 w-6" />
          <span className="sr-only">Produtos</span>
        </Link>
        {!isManager && (
          <Link className={linkClasses(active === "carrinho")} href="/cart" title="Carrinho">
            <ShoppingCart className="h-6 w-6" />
            <span className="sr-only">Carrinho</span>
          </Link>
        )}
        <Link className={linkClasses(active === "usuario")} href="/profile" title="Perfil">
          <UserRound className="h-6 w-6" />
          <span className="sr-only">Perfil</span>
        </Link>
        {isManager && (
          <Link className={linkClasses(active === "novo-usuario")} href="/register" title="Usuários">
            <UserRoundPlus className="h-6 w-6" />
            <span className="sr-only">Usuários</span>
          </Link>
        )}
      </nav>

      <div>
        <button className={iconLinkClasses} type="button" onClick={logout} title="Sair">
          <LogOut className="h-6 w-6" />
          <span className="sr-only">Sair</span>
        </button>
      </div>
    </aside>
  );
}
