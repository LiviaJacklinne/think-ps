"use client";

import Link from "next/link";
import { Package, ShoppingCart, UserRound, Users } from "lucide-react";
import { useCurrentUser } from "@/components/AuthShell";

export default function HomePage() {
  const { user } = useCurrentUser();

  return (
    <>
      <header className="page-header">
        <div>
          <p className="eyebrow">Home</p>
          <h1>Ola, {user.username}</h1>
        </div>
      </header>

      <nav className="feature-grid">
        <Link href="/products" className="card">
          <span className="card-icon"><Package /></span>
          <strong>Produtos</strong>
          <small>Coisas a serem compradas</small>
        </Link>
        {user.role !== "manager" && (
          <Link href="/cart" className="card">
            <span className="card-icon"><ShoppingCart /></span>
            <strong>Carrinho</strong>
            <small>Listar o que foi comprado</small>
          </Link>
        )}
        <Link href="/profile" className="card">
          <span className="card-icon"><UserRound /></span>
          <strong>Usuario</strong>
          <small>Dados do usuario</small>
        </Link>
        {user.role === "manager" && (
          <Link href="/register" className="card">
            <span className="card-icon"><Users /></span>
            <strong>Novo usuario</strong>
            <small>Cadastrar usuarios</small>
          </Link>
        )}
      </nav>
    </>
  );
}
