"use client";

import { FormEvent, useEffect, useState } from "react";
import { useCurrentUser } from "@/components/AuthShell";
import { api, Product } from "@/lib/api";

type ProductsResponse = {
  role: "manager" | "user";
  produtos: Product[];
  usando_mock: boolean;
};

export default function ProductPage() {
  const { user } = useCurrentUser();
  const [produtos, setProdutos] = useState<Product[]>([]);
  const [busca, setBusca] = useState("");
  const [toast, setToast] = useState("");
  const [editing, setEditing] = useState<Product | null>(null);

  async function load(q = "") {
    const data = await api<ProductsResponse>(`/api/compras/produtos/${q ? `?q=${encodeURIComponent(q)}` : ""}`);
    setProdutos(data.produtos);
  }

  useEffect(() => {
    load().catch(() => setToast("Nao foi possivel carregar produtos."));
  }, []);

  async function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await load(busca);
  }

  async function saveProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload = {
      nome: form.get("nome"),
      quantidade: form.get("quantidade"),
      valor: form.get("valor"),
    };

    await api(editing?.id ? `/api/compras/produtos/${editing.id}/` : "/api/compras/produtos/", {
      method: editing?.id ? "PATCH" : "POST",
      body: JSON.stringify(payload),
    });
    setEditing(null);
    setToast("Produto salvo.");
    await load(busca);
  }

  async function buy(product: Product, quantidade: number) {
    await api(`/api/compras/produtos/${product.id}/comprar/`, {
      method: "POST",
      body: JSON.stringify({ quantidade }),
    });
    setToast("Produto adicionado ao carrinho.");
    await load(busca);
  }

  const isManager = user.role === "manager";

  return (
    <>
      {toast && <p className="toast">{toast}</p>}
      <header className="page-header">
        <div>
          <p className="eyebrow">Produtos</p>
         <p className="text-lg text-red-500 font-bold">
  Itens disponiveis
</p>
        </div>
        {isManager && <button className="primary-button" onClick={() => setEditing({ id: "", nome: "", quantidade: 0, valor: 0 })}>Cadastrar produto</button>}
      </header>

      <section className="panel">
        <form className="toolbar" onSubmit={search}>
          <input value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Pesquisar produto" />
          <button className="primary-button" type="submit">Pesquisar</button>
        </form>

        {editing && (
          <form className="form" onSubmit={saveProduct}>
            <label>Nome<input name="nome" defaultValue={editing.nome} required /></label>
            <label>Quantidade<input name="quantidade" type="number" min="0" defaultValue={editing.quantidade} required /></label>
            <label>Valor<input name="valor" type="number" min="0" step="0.01" defaultValue={editing.valor} required /></label>
            <button className="primary-button" type="submit">Salvar</button>
          </form>
        )}

        <div className="data-table">
          <div className="row head"><span>Produto</span><span>Quantidade</span><span>Valor</span><span>Acao</span></div>
          {produtos.map((produto) => (
            <ProductRow key={produto.id} product={produto} isManager={isManager} onEdit={setEditing} onBuy={buy} />
          ))}
        </div>
      </section>
    </>
  );
}

function ProductRow({
  product,
  isManager,
  onEdit,
  onBuy,
}: {
  product: Product;
  isManager: boolean;
  onEdit: (product: Product) => void;
  onBuy: (product: Product, quantity: number) => void;
}) {
  const [quantity, setQuantity] = useState(1);

  return (
    <div className="row">
      <strong>{product.nome}</strong>
      <span>{product.quantidade}</span>
      <span>R$ {product.valor.toFixed(2)}</span>
      {isManager ? (
        <button className="secondary-button" onClick={() => onEdit(product)}>Editar</button>
      ) : (
        <span className="inline-form">
          <input className="quantity-input" type="number" min="1" max={product.quantidade} value={quantity} onChange={(event) => setQuantity(Number(event.target.value))} />
          <button className="primary-button" onClick={() => onBuy(product, quantity)}>Comprar</button>
        </span>
      )}
    </div>
  );
}
