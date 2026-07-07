"use client";

import { FormEvent, useEffect, useState } from "react";
import { Pencil, Plus, X } from "lucide-react";
import { Button } from "@/components/Button";
import { useCurrentUser } from "@/components/AuthShell";
import { api, Product } from "@/lib/api";

type ProductsResponse = {
  role: "manager" | "user";
  produtos: Product[];
  usando_mock: boolean;
};

const inputClasses = "min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2";

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
    load().catch(() => setToast("Não foi possível carregar os produtos."));
  }, []);

  function openCreateModal() {
    setEditing({ id: "", nome: "", quantidade: 0, valor: 0 });
  }

  function closeModal() {
    setEditing(null);
  }

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
    closeModal();
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
      {toast && (
        <p className="fixed right-5 top-5 z-20 w-[min(360px,calc(100vw-36px))] rounded-md bg-slate-900 px-4 py-3 text-white shadow-xl">
          {toast}
        </p>
      )}

      <header className="flex items-center justify-between gap-5">
        <div>
          <p className="mb-2 text-xs font-bold uppercase text-slate-500">Produtos</p>
          <h1 className="text-xl font-bold">Itens disponíveis</h1>
        </div>
        {isManager && (
          <Button type="button" onClick={openCreateModal}>
            <Plus />
            Cadastrar produto
          </Button>
        )}
      </header>

      <section className="grid gap-6 rounded-lg border border-slate-200 bg-white p-6 shadow-[0_14px_32px_rgba(15,23,42,0.06)]">
        <form className="grid grid-cols-[1fr_auto] gap-3 max-[860px]:grid-cols-1" onSubmit={search}>
          <input className={inputClasses} value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Pesquisar produto" />
          <Button type="submit">Pesquisar</Button>
        </form>

        <div className="overflow-hidden rounded-lg border border-slate-200">
          <table className="w-full table-fixed border-collapse text-left">
            <colgroup>
              <col className="w-[20%]" />
              <col className="w-[14%]" />
              <col className="w-[16%]" />
              <col className="w-[12%]" />
            </colgroup>
            <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500 max-[860px]:hidden">
              <tr className="border-b border-slate-200">
                <th className="px-4 py-4">Produto</th>
                <th className="px-4 py-4">Estoque</th>
                <th className="px-4 py-4">Valor</th>
                <th className="px-4 py-4">
                  <span className="sr-only">Ação</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {produtos.map((produto) => (
                <ProductRow key={produto.id} product={produto} isManager={isManager} onEdit={setEditing} onBuy={buy} />
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {editing && (
        <div className="fixed inset-0 z-30 grid place-items-center bg-slate-900/50 p-6">
          <section
            className="grid w-[min(100%,520px)] gap-5 rounded-lg border border-slate-200 bg-white p-6 shadow-2xl"
            aria-modal="true"
            role="dialog"
          >
            <div className="flex items-center justify-between gap-5">
              <div>
                <p className="mb-2 text-xs font-bold uppercase text-slate-500">
                  {editing.id ? "Editar produto" : "Novo produto"}
                </p>
                <h2 className="text-xl font-bold">
                  {editing.id ? editing.nome : "Cadastrar produto"}
                </h2>
              </div>
              <Button variant="icon" type="button" onClick={closeModal} aria-label="Fechar">
                <X />
              </Button>
            </div>

            <form className="grid gap-3" onSubmit={saveProduct}>
              <label className="grid gap-2 text-sm font-bold">
                Nome
                <input className={inputClasses} name="nome" defaultValue={editing.nome} required />
              </label>
              <label className="grid gap-2 text-sm font-bold">
                Estoque
                <input className={inputClasses} name="quantidade" type="number" min="0" defaultValue={editing.quantidade} required />
              </label>
              <label className="grid gap-2 text-sm font-bold">
                Valor
                <input className={inputClasses} name="valor" type="number" min="0" step="0.01" defaultValue={editing.valor} required />
              </label>
              <Button type="submit">
                {editing.id ? "Salvar alterações" : "Cadastrar produto"}
              </Button>
            </form>
          </section>
        </div>
      )}
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
    <tr className="border-b border-slate-200 last:border-b-0 max-[860px]:grid max-[860px]:grid-cols-1 max-[860px]:gap-3 max-[860px]:border max-[860px]:p-4">
      <td className="px-4 py-4 font-bold max-[860px]:p-0">{product.nome}</td>
      <td className="px-4 py-4 max-[860px]:p-0">{product.quantidade}</td>
      <td className="px-4 py-4 max-[860px]:p-0">R$ {product.valor.toFixed(2)}</td>
      <td className="px-4 py-4 max-[860px]:p-0">
        {isManager ? (
          <Button variant="ghost" type="button" onClick={() => onEdit(product)}>
            <Pencil />
            Editar
          </Button>
        ) : (
          <span className="flex items-center gap-2">
            <input className="min-h-10 w-20 rounded-md border border-slate-300 bg-white px-3 py-2" type="number" min="1" max={product.quantidade} value={quantity} onChange={(event) => setQuantity(Number(event.target.value))} />
            <Button type="button" onClick={() => onBuy(product, quantity)}>
              Comprar
            </Button>
          </span>
        )}
      </td>
    </tr>
  );
}
