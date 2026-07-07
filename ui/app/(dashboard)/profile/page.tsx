"use client";

import { FormEvent, useState } from "react";
import { Pencil } from "lucide-react";
import { useCurrentUser } from "@/components/AuthShell";
import { api, User } from "@/lib/api";

export default function UserPage() {
  const { user, setUser } = useCurrentUser();
  const [editing, setEditing] = useState(false);
  const [toast, setToast] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
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
  }

  return (
    <>
      {toast && <p className="toast">{toast}</p>}
      <header className="page-header">
        <div>
          <p className="eyebrow">Usuario</p>
          <h1>Minha conta</h1>
          <small className="role-label">{user.role}</small>
        </div>
      </header>

      <section className="panel">
        <div className="page-header">
          <div className="inline-form">
            <span className="brand-mark">{user.username[0]?.toUpperCase()}</span>
            <strong>{user.username}</strong>
          </div>
          <button className="secondary-button" onClick={() => setEditing(true)}><Pencil size={18} /> Editar</button>
        </div>

        <form className="form" onSubmit={submit}>
          <label>Usuario<input name="username" defaultValue={user.username} readOnly={!editing} required /></label>
          <label>E-mail<input name="email" type="email" defaultValue={user.email} readOnly={!editing} /></label>
          <label>Nova senha<input name="password" type="password" readOnly={!editing} placeholder="Preencha apenas se quiser alterar" /></label>
          {editing && <button className="primary-button" type="submit">Salvar alteracoes</button>}
        </form>
      </section>
    </>
  );
}
