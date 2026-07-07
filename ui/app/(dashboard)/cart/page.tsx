"use client";

import { FormEvent, useEffect, useState } from "react";
import { useCurrentUser } from "@/components/AuthShell";
import { api, CartItem } from "@/lib/api";

type CartResponse = {
  itens: CartItem[];
  total: number;
};

export default function CartPage() {
  const { user } = useCurrentUser();
  const [items, setItems] = useState<CartItem[]>([]);
  const [total, setTotal] = useState(0);
  const [toast, setToast] = useState("");

  async function load() {
    const data = await api<CartResponse>("/api/compras/carrinho/");
    setItems(data.itens);
    setTotal(data.total);
  }

  useEffect(() => {
    load().catch(() => setToast("Nao foi possivel carregar o carrinho."));
  }, []);

  async function updateItem(event: FormEvent<HTMLFormElement>, item: CartItem) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api(`/api/compras/carrinho/${item.id}/`, {
      method: "PATCH",
      body: JSON.stringify({ quantidade: form.get("quantidade") }),
    });
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
      {toast && <p className="toast">{toast}</p>}
      <header className="page-header">
        <div>
          <p className="eyebrow">Carrinho</p>
          <h1>Minhas compras</h1>
          <small className="role-label">{user.role}</small>
        </div>
        <strong>R$ {total.toFixed(2)}</strong>
      </header>

      <section className="panel">
        <div className="data-table">
          <div className="row cart head"><span>Produto</span><span>Quantidade</span><span>Valor</span><span>Subtotal</span><span>Acao</span></div>
          {items.map((item) => (
            <div className="row cart" key={item.id}>
              <strong>{item.nome}</strong>
              <form className="inline-form" onSubmit={(event) => updateItem(event, item)}>
                <input className="quantity-input" name="quantidade" type="number" min="1" defaultValue={item.quantidade} />
                <button className="primary-button" type="submit">Salvar</button>
              </form>
              <span>R$ {item.valor.toFixed(2)}</span>
              <span>R$ {(item.subtotal ?? item.valor * item.quantidade).toFixed(2)}</span>
              <button className="danger-button" onClick={() => removeItem(item)}>Excluir</button>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
