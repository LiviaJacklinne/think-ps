"use client";

import Link from "next/link";
import { Package, ShoppingCart, UserRound, Users } from "lucide-react";
import { useCurrentUser } from "@/components/AuthShell";

const cardClasses =
  "grid min-h-56 content-between gap-5 rounded-lg border border-slate-200 bg-white p-6 hover:border-teal-700";

const iconClasses = "grid h-14 w-14 place-items-center rounded-lg bg-teal-100 text-teal-700";

export default function HomePage() {
  const { user } = useCurrentUser();

  return (
    <>
      <header className="flex items-center justify-between gap-5">
        <div>
          <p className="mb-2 text-xs font-bold uppercase text-slate-500">Home</p>
          <h1 className="text-xl font-bold">Olá, {user.username}</h1>
        </div>
      </header>

      <nav className="grid grid-cols-3 gap-5 max-[860px]:grid-cols-1">
        <Link href="/products" className={cardClasses}>
          <span className={iconClasses}><Package /></span>
          <strong>Produtos</strong>
          <small>Coisas a serem compradas</small>
        </Link>

        {user.role !== "manager" && (
          <Link href="/cart" className={cardClasses}>
            <span className={iconClasses}><ShoppingCart /></span>
            <strong>Carrinho</strong>
            <small>Listar o que foi comprado</small>
          </Link>
        )}

        <Link href="/profile" className={cardClasses}>
          <span className={iconClasses}><UserRound /></span>
          <strong>Perfil</strong>
          <small>Dados do perfil</small>
        </Link>

        {user.role === "manager" && (
          <Link href="/register" className={cardClasses}>
            <span className={iconClasses}><Users /></span>
            <strong>Usuários</strong>
            <small>Cadastrar usuários</small>
          </Link>
        )}
      </nav>
    </>
  );
}
