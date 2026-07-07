"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { api, User } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [erro, setErro] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErro("");
    const form = new FormData(event.currentTarget);

    try {
      await api<User>("/api/auth/login/", {
        method: "POST",
        body: JSON.stringify({
          username: form.get("username"),
          password: form.get("password"),
        }),
      });
      router.push("/home");
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Erro ao entrar.");
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <div>
          <p className="eyebrow">Think PS</p>
          <h1>Entrar</h1>
        </div>
        {erro && <p className="toast">{erro}</p>}
        <form className="form" onSubmit={submit}>
          <label>
            Usuario
            <input name="username" autoComplete="username" required />
          </label>
          <label>
            Senha
            <input name="password" type="password" autoComplete="current-password" required />
          </label>
          <button className="primary-button" type="submit">Entrar</button>
        </form>
        <p className="muted">
          Ainda nao tem conta? <Link href="/register">Criar conta</Link>
        </p>
      </section>
    </main>
  );
}
