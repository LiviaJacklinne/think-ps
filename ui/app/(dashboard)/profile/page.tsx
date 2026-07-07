"use client";

import { FormEvent, useState } from "react";
import { Pencil } from "lucide-react";
import { Button } from "@/components/Button";
import { useCurrentUser } from "@/components/AuthShell";
import { api, User } from "@/lib/api";

const inputClasses = "min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2 disabled:bg-slate-100";

function friendlyProfileError(error: unknown) {
  const message = error instanceof Error ? error.message : "";

  if (message.toLowerCase().includes("e-mail ja cadastrado")) {
    return "Este e-mail já está sendo usado por outro usuário. Escolha outro e tente novamente.";
  }

  if (message.toLowerCase().includes("usuario ja cadastrado")) {
    return "Este nome de usuário já está em uso. Escolha outro e tente novamente.";
  }

  return message || "Não foi possível atualizar o perfil. Revise os dados e tente novamente.";
}

export default function UserPage() {
  const { user, setUser } = useCurrentUser();
  const [editing, setEditing] = useState(false);
  const [toast, setToast] = useState("");
  const [erro, setErro] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErro("");
    const form = new FormData(event.currentTarget);

    try {
      const updated = await api<User>("/api/auth/me/", {
        method: "POST",
        body: JSON.stringify({
          username: form.get("username"),
          email: form.get("email"),
          password: form.get("password"),
        }),
      });
      setUser(updated);
      setEditing(false);
      setToast("Perfil atualizado.");
    } catch (error) {
      setErro(friendlyProfileError(error));
    }
  }

  return (
    <>
      {toast && (
        <p className="fixed right-5 top-5 z-20 w-[min(360px,calc(100vw-36px))] rounded-md bg-slate-900 px-4 py-3 text-white shadow-xl">
          {toast}
        </p>
      )}

      <header className="flex items-center justify-between gap-5">
        <div>
          <p className="mb-2 text-xs font-bold uppercase text-slate-500">Perfil</p>
          <h1 className="text-xl font-bold">Minha conta</h1>
        </div>
      </header>

      <section className="grid gap-6 rounded-lg border border-slate-200 bg-white p-6 shadow-[0_14px_32px_rgba(15,23,42,0.06)]">
        <div className="flex items-center justify-between gap-5">
          <div className="flex items-center gap-3">
            <span className="grid h-11 w-11 place-items-center rounded-full bg-teal-700 text-xl font-bold text-white">
              {user.username[0]?.toUpperCase()}
            </span>
            <strong>{user.username}</strong>
          </div>
          <Button
            variant="ghost"
            iconSize={16}
            type="button"
            onClick={() => {
              setErro("");
              setEditing(true);
            }}
          >
            <Pencil />
            Editar
          </Button>
        </div>

        {erro && (
          <p className="rounded-md bg-red-50 px-4 py-3 text-sm font-bold text-red-800">
            {erro}
          </p>
        )}

        <form className="grid gap-3" onSubmit={submit}>
          <label className="grid gap-2 text-sm font-bold">
            Usuário
            <input className={inputClasses} name="username" defaultValue={user.username} readOnly={!editing} required />
          </label>
          <label className="grid gap-2 text-sm font-bold">
            E-mail
            <input className={inputClasses} name="email" type="email" defaultValue={user.email} readOnly={!editing} />
          </label>
          <label className="grid gap-2 text-sm font-bold">
            Nova senha
            <input className={inputClasses} name="password" type="password" readOnly={!editing} placeholder="Preencha apenas se quiser alterar" />
          </label>
          {editing && (
            <div className="flex flex-wrap items-center gap-3">
              <Button type="submit">Salvar</Button>
              <Button
                variant="ghost"
                type="button"
                onClick={() => {
                  setErro("");
                  setEditing(false);
                }}
              >
                Cancelar
              </Button>
            </div>
          )}
        </form>
      </section>
    </>
  );
}
