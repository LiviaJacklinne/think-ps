"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { useCurrentUser } from "@/components/AuthShell";
import { api, User } from "@/lib/api";

export default function NewUserPage() {
  const router = useRouter();
  const { user } = useCurrentUser();
  const [erro, setErro] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErro("");
    const form = new FormData(event.currentTarget);

    try {
      await api<User>("/api/auth/cadastro/", {
        method: "POST",
        body: JSON.stringify({
          username: form.get("username"),
          email: form.get("email"),
          password: form.get("password"),
          role: form.get("role"),
        }),
      });
      router.push("/home");
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Erro ao cadastrar.");
    }
  }

  return (
    <>
      <header className="page-header">
        <div>
          <p className="eyebrow">Novo usuario</p>
          <p className="text-xs">Cadastrar usuario</p>
        </div>
      </header>

      <section className="panel">
        {erro && <p className="toast">{erro}</p>}
        <form className="form" onSubmit={submit}>
          <label>
            Usuario
            <input name="username" autoComplete="username" required />
          </label>
          <label>
            E-mail
            <input name="email" type="email" autoComplete="email" />
          </label>
          <label>
            Senha
            <input name="password" type="password" autoComplete="new-password" required />
          </label>
          <label>
            Role
            <select name="role" defaultValue="user">
              <option value="user">user</option>
              <option value="manager">manager</option>
            </select>
          </label>
          <button className="primary-button" type="submit">Cadastrar</button>
        </form>
      </section>
    </>
  );
}
