"use client";

import { FormEvent, useEffect, useState } from "react";
import { Pencil, Trash2, X } from "lucide-react";
import { Button } from "@/components/Button";
import { api, CartItem } from "@/lib/api";

type CartResponse = {
  itens: CartItem[];
  total: number;
};

export default function CartPage() {
  const [items, setItems] = useState<CartItem[]>([]);
  const [total, setTotal] = useState(0);
  const [toast, setToast] = useState("");
  const [erro, setErro] = useState("");
  const [editingItem, setEditingItem] = useState<CartItem | null>(null);

  async function load() {
    setErro("");
    const data = await api<CartResponse>("/api/compras/carrinho/");
    setItems(data.itens);
    setTotal(data.total);
  }

  useEffect(() => {
    load().catch((error) => {
      setErro(error instanceof Error ? error.message : "Não foi possível carregar o carrinho.");
    });
  }, []);

  async function updateItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!editingItem) {
      return;
    }

    const form = new FormData(event.currentTarget);
    await api(`/api/compras/carrinho/${editingItem.id}/`, {
      method: "PATCH",
      body: JSON.stringify({ quantidade: form.get("quantidade") }),
    });
    setEditingItem(null);
    setToast("Quantidade atualizada.");
    await load();
  }

  async function removeItem(item: CartItem) {
    await api(`/api/compras/carrinho/${item.id}/`, { method: "DELETE" });
    setToast("Item removido.");
    await load();
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
          <p className="mb-2 text-xs font-bold uppercase text-slate-500">Carrinho</p>
          <h1 className="text-xl font-bold">Minhas compras</h1>
        </div>
        <strong>R$ {total.toFixed(2)}</strong>
      </header>

      <section className="grid gap-6 rounded-lg border border-slate-200 bg-white p-6 shadow-[0_14px_32px_rgba(15,23,42,0.06)]">
        <div className="overflow-hidden rounded-lg border border-slate-200">
          <table className="w-full table-fixed border-collapse text-left">
            <colgroup>
              <col className="w-[25%]" />
              <col className="w-[16%]" />
              <col className="w-[16%]" />
              <col className="w-[16%]" />
              <col className="w-[10%]" />
            </colgroup>
            <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500 max-[860px]:hidden">
              <tr className="border-b border-slate-200">
                <th className="px-4 py-4">Produto</th>
                <th className="px-4 py-4">Quantidade</th>
                <th className="px-4 py-4">Valor</th>
                <th className="px-4 py-4">Subtotal</th>
                <th className="px-4 py-4">
                  <span className="sr-only">Ação</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {erro && (
                <tr>
                  <td className="px-4 py-7 text-center text-slate-500" colSpan={5}>
                    {erro}
                  </td>
                </tr>
              )}

              {!erro && items.length === 0 && (
                <tr>
                  <td className="px-4 py-7 text-center text-slate-500" colSpan={5}>
                    Nenhum item no carrinho.
                  </td>
                </tr>
              )}

              {!erro && items.map((item) => (
                <CartRow key={item.id} item={item} onEdit={setEditingItem} onRemove={removeItem} />
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {editingItem && (
        <div className="fixed inset-0 z-30 grid place-items-center bg-slate-900/50 p-6">
          <section
            className="grid w-[min(100%,520px)] gap-5 rounded-lg border border-slate-200 bg-white p-6 shadow-2xl"
            aria-modal="true"
            role="dialog"
          >
            <div className="flex items-center justify-between gap-5">
              <div>
                <p className="mb-2 text-xs font-bold uppercase text-slate-500">Editar carrinho</p>
                <h2 className="text-xl font-bold">{editingItem.nome}</h2>
              </div>
              <Button variant="icon" type="button" onClick={() => setEditingItem(null)} aria-label="Fechar">
                <X />
              </Button>
            </div>

            <div className="grid gap-2 rounded-lg bg-slate-50 p-4 text-sm text-slate-600">
              <p>
                <strong className="text-slate-900">Valor unitário:</strong> R$ {editingItem.valor.toFixed(2)}
              </p>
              <p>
                <strong className="text-slate-900">Quantidade atual:</strong> {editingItem.quantidade}
              </p>
              <p>
                <strong className="text-slate-900">Subtotal atual:</strong>{" "}
                R$ {(editingItem.subtotal ?? editingItem.valor * editingItem.quantidade).toFixed(2)}
              </p>
            </div>

            <form className="grid gap-3" onSubmit={updateItem}>
              <label className="grid gap-2 text-sm font-bold">
                Quantidade
                <input
                  className="min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2"
                  name="quantidade"
                  type="number"
                  min="1"
                  defaultValue={editingItem.quantidade}
                  required
                />
              </label>
              <div className="flex flex-wrap items-center gap-3">
                <Button type="submit">Salvar</Button>
                <Button variant="ghost" type="button" onClick={() => setEditingItem(null)}>
                  Cancelar
                </Button>
              </div>
            </form>
          </section>
        </div>
      )}
    </>
  );
}

function CartRow({
  item,
  onEdit,
  onRemove,
}: {
  item: CartItem;
  onEdit: (item: CartItem) => void;
  onRemove: (item: CartItem) => void;
}) {
  return (
    <tr className="border-b border-slate-200 last:border-b-0 max-[860px]:grid max-[860px]:grid-cols-1 max-[860px]:gap-3 max-[860px]:border max-[860px]:p-4">
      <td className="px-4 py-4 font-bold max-[860px]:p-0">{item.nome}</td>
      <td className="px-4 py-4 max-[860px]:p-0">{item.quantidade}</td>
      <td className="px-4 py-4 max-[860px]:p-0">R$ {item.valor.toFixed(2)}</td>
      <td className="px-4 py-4 max-[860px]:p-0">R$ {(item.subtotal ?? item.valor * item.quantidade).toFixed(2)}</td>
      <td className="px-4 py-4 max-[860px]:p-0">
        <div className="flex items-center gap-2">
          <Button
            variant="icon"
            iconSize={17}
            type="button"
            onClick={() => onEdit(item)}
            aria-label={`Editar ${item.nome}`}
            className="text-teal-700 hover:bg-teal-50 hover:text-teal-800"
          >
            <Pencil />
          </Button>
          <Button
            variant="icon"
            iconSize={17}
            type="button"
            onClick={() => onRemove(item)}
            aria-label={`Excluir ${item.nome}`}
            className="text-red-700 hover:bg-red-50 hover:text-red-800"
          >
            <Trash2 />
          </Button>
        </div>
      </td>
    </tr>
  );
}
