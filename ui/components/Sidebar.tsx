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
    <aside className="sidebar">
      <nav className="sidebar-main" aria-label="Navegacao principal">
        <Link className={active === "home" ? "active" : ""} href="/home" title="Home">
          <Home />
          <span>Home</span>
        </Link>
        <Link className={active === "produtos" ? "active" : ""} href="/products" title="Produtos">
          <Package />
          <span>Produtos</span>
        </Link>
        {!isManager && (
          <Link className={active === "carrinho" ? "active" : ""} href="/cart" title="Carrinho">
            <ShoppingCart />
            <span>Carrinho</span>
          </Link>
        )}
        <Link className={active === "usuario" ? "active" : ""} href="/profile" title="Usuario">
          <UserRound />
          <span>Usuario</span>
        </Link>
        {isManager && (
          <Link className={active === "novo-usuario" ? "active" : ""} href="/register" title="Novo usuario">
            <UserRoundPlus />
            <span>Novo usuario</span>
          </Link>
        )}
      </nav>

      <div className="sidebar-bottom">
        <span className="brand-mark" title={`${user.username} (${user.role})`}>
          {user.username[0]?.toUpperCase()}
        </span>
        <button className="logout-button" type="button" onClick={logout} title="Sair">
          <LogOut />
          <span>Sair</span>
        </button>
      </div>
    </aside>
  );
}
