"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/Button";
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
    <main className="grid min-h-screen place-items-center bg-slate-100 p-6">
      <section className="grid w-[min(100%,420px)] gap-5 rounded-lg border border-slate-200 bg-white p-7 shadow-[0_18px_45px_rgba(31,41,55,0.08)]">
        <div>
          <p className="mb-2 text-xs font-bold uppercase text-slate-500">Think PS</p>
          <h1 className="text-2xl font-bold">Entrar</h1>
        </div>
        {erro && (
          <p className="fixed right-5 top-5 z-20 w-[min(360px,calc(100vw-36px))] rounded-md bg-slate-900 px-4 py-3 text-white shadow-xl">
            {erro}
          </p>
        )}
        <form className="grid gap-3" onSubmit={submit}>
          <label className="grid gap-2 text-sm font-bold">
            Usuário
            <input className="min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2" name="username" autoComplete="username" required />
          </label>
          <label className="grid gap-2 text-sm font-bold">
            Senha
            <input className="min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2" name="password" type="password" autoComplete="current-password" required />
          </label>
          <Button type="submit">Entrar</Button>
        </form>
      </section>
    </main>
  );
}
