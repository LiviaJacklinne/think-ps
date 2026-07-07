"use client";

import { FormEvent, useEffect, useState } from "react";
import { Pencil, Plus, X } from "lucide-react";
import { Button } from "@/components/Button";
import { api, User } from "@/lib/api";

type UsersResponse = {
  usuarios: User[];
};

type ModalMode = "create" | "edit";

export default function NewUserPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [modalMode, setModalMode] = useState<ModalMode | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [erro, setErro] = useState("");
  const [toast, setToast] = useState("");

  async function loadUsers() {
    const data = await api<UsersResponse>("/api/auth/usuarios/");
    setUsers(data.usuarios);
  }

  useEffect(() => {
    loadUsers().catch((error) => {
      setErro(error instanceof Error ? error.message : "Erro ao carregar usuários.");
    });
  }, []);

  function openCreateModal() {
    setErro("");
    setSelectedUser(null);
    setModalMode("create");
  }

  function openEditModal(user: User) {
    setErro("");
    setSelectedUser(user);
    setModalMode("edit");
  }

  function closeModal() {
    setModalMode(null);
    setSelectedUser(null);
    setErro("");
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErro("");

    const form = new FormData(event.currentTarget);
    const payload = {
      username: form.get("username"),
      email: form.get("email"),
      password: form.get("password"),
      role: form.get("role"),
    };

    try {
      if (modalMode === "edit" && selectedUser) {
        await api<User>(`/api/auth/usuarios/${selectedUser.id}/`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
        setToast("Usuário atualizado.");
      } else {
        await api<User>("/api/auth/cadastro/", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        setToast("Usuário criado.");
      }

      await loadUsers();
      closeModal();
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Erro ao salvar usuário.");
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
          <p className="mb-2 text-xs font-bold uppercase text-slate-500">Usuários</p>
          <h1 className="text-xl font-bold">Usuários cadastrados</h1>
        </div>
        <Button type="button" iconSize={18} onClick={openCreateModal}>
          <Plus/>
          Criar usuário
        </Button>
      </header>

      <section className="grid gap-6 rounded-lg border border-slate-200 bg-white p-6 shadow-[0_14px_32px_rgba(15,23,42,0.06)]">
        {erro && !modalMode && <p className="text-slate-500">{erro}</p>}

        <div className="grid overflow-hidden rounded-lg border border-slate-200">
          <div className="grid min-h-12 grid-cols-[1.1fr_1.4fr_0.65fr_auto] items-center gap-4 border-b border-slate-200 bg-slate-50 px-4 py-3 text-xs font-bold uppercase text-slate-500 max-[860px]:hidden">
            <span>Usuário</span>
            <span>E-mail</span>
            <span>Role</span>
            <span>Ações</span>
          </div>

          {users.map((user) => (
            <div
              className="grid min-h-16 grid-cols-[1.1fr_1.4fr_0.65fr_auto] items-center gap-4 border-b border-slate-200 px-4 py-3 last:border-b-0 max-[860px]:grid-cols-1 max-[860px]:rounded-lg max-[860px]:border"
              key={user.id}
            >
              <div className="flex items-center gap-3">
                <span className="grid h-9 w-9 flex-none place-items-center rounded-full bg-teal-700 text-sm font-bold text-white">
                  {user.username[0]?.toUpperCase()}
                </span>
                <strong>{user.username}</strong>
              </div>
              <span>{user.email || "Sem e-mail"}</span>
              <span className="w-fit rounded-full bg-teal-100 px-3 py-1 text-sm font-bold text-teal-700">
                {user.role}
              </span>
              <Button variant="ghost" type="button" onClick={() => openEditModal(user)}>
                <Pencil size={4} />
                Editar
              </Button>
            </div>
          ))}

          {!users.length && !erro && (
            <div className="px-4 py-7 text-center text-slate-500">
              Nenhum usuário cadastrado.
            </div>
          )}
        </div>
      </section>

      {modalMode && (
        <div className="fixed inset-0 z-30 grid place-items-center bg-slate-900/50 p-6">
          <section
            className="grid w-[min(100%,520px)] gap-5 rounded-lg border border-slate-200 bg-white p-6 shadow-2xl"
            aria-modal="true"
            role="dialog"
          >
            <div className="flex items-center justify-between gap-5">
              <div>
                <p className="mb-2 text-xs font-bold uppercase text-slate-500">
                  {modalMode === "edit" ? "Editar" : "Novo usuário"}
                </p>
                <h2 className="text-xl font-bold">
                  {modalMode === "edit" ? selectedUser?.username : "Criar usuário"}
                </h2>
              </div>
              <Button variant="icon" type="button" onClick={closeModal} aria-label="Fechar">
                <X/>
              </Button>
            </div>

            {erro && <p className="rounded-md bg-red-100 px-3 py-2 font-bold text-red-800">{erro}</p>}

            <form className="grid gap-3" onSubmit={submit}>
              <label className="grid gap-2 text-sm font-bold">
                Usuário
                <input
                  className="min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2"
                  name="username"
                  autoComplete="username"
                  defaultValue={selectedUser?.username ?? ""}
                  required
                />
              </label>
              <label className="grid gap-2 text-sm font-bold">
                E-mail
                <input
                  className="min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2"
                  name="email"
                  type="email"
                  autoComplete="email"
                  defaultValue={selectedUser?.email ?? ""}
                />
              </label>
              <label className="grid gap-2 text-sm font-bold">
                Senha
                <input
                  className="min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required={modalMode === "create"}
                  placeholder={modalMode === "edit" ? "Preencha apenas se quiser alterar" : ""}
                />
              </label>
              <label className="grid gap-2 text-sm font-bold">
                Role
                <select
                  className="min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2"
                  name="role"
                  defaultValue={selectedUser?.role ?? "user"}
                >
                  <option value="user">User</option>
                  <option value="manager">Manager</option>
                </select>
              </label>
              <Button type="submit">
                Salvar
              </Button>
            </form>
          </section>
        </div>
      )}
    </>
  );
}
