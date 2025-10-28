import { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [buyer, setBuyer] = useState("");
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState("");
  const [purchases, setPurchases] = useState([]);
  const [totals, setTotals] = useState({ by_buyer: {}, total: 0 });

  async function fetchData() {
    const res = await axios.get(`${API_BASE}/purchases`);
    setPurchases(res.data);
    const tot = await axios.get(`${API_BASE}/totals`);
    setTotals(tot.data);
  }

  useEffect(() => { fetchData(); }, []);

  async function handleAdd() {
    await axios.post(`${API_BASE}/purchases`, { buyer, amount: parseFloat(amount), date });
    setBuyer(""); setAmount(""); setDate("");
    fetchData();
  }

  async function handleDelete(id) {
    await axios.delete(`${API_BASE}/purchases/${id}`);
    fetchData();
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4 text-center">Controle de Compras</h1>

      <div className="flex gap-2 mb-4 justify-center">
        <input className="border p-2 rounded" placeholder="Comprador" value={buyer} onChange={e => setBuyer(e.target.value)} />
        <input className="border p-2 rounded" placeholder="Valor" type="number" value={amount} onChange={e => setAmount(e.target.value)} />
        <input className="border p-2 rounded" type="date" value={date} onChange={e => setDate(e.target.value)} />
        <button className="bg-blue-500 text-white px-4 py-2 rounded" onClick={handleAdd}>Adicionar</button>
      </div>

      <table className="w-full border text-center">
        <thead>
          <tr className="bg-gray-200">
            <th>Comprador</th><th>Valor</th><th>Data</th><th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {purchases.map(p => (
            <tr key={p.id} className="border-t">
              <td>{p.buyer}</td>
              <td>R$ {p.amount.toFixed(2)}</td>
              <td>{p.date}</td>
              <td>
                <button onClick={() => handleDelete(p.id)} className="text-red-500 hover:underline">
                  Excluir
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="mt-6 text-center">
        <h2 className="font-bold text-lg mb-2">Totais</h2>
        {Object.entries(totals.by_buyer).map(([buyer, total]) => (
          <p key={buyer}>{buyer}: R$ {total.toFixed(2)}</p>
        ))}
        <p className="font-semibold mt-2">Total geral: R$ {totals.total.toFixed(2)}</p>
      </div>

      <div className="mt-4 flex justify-center gap-2">
        <a href={`${API_BASE}/export/pdf`} className="bg-gray-700 text-white px-4 py-2 rounded">Exportar PDF</a>
        <a href={`${API_BASE}/export/excel`} className="bg-green-600 text-white px-4 py-2 rounded">Exportar Excel</a>
      </div>
    </div>
  );
}