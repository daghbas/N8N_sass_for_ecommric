import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';

const initialForm = {
  title: 'New Product',
  slug: 'new-product',
  description: 'Product description',
  price: 49,
  stock: 50,
  category: 'General',
  image_url: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30'
};

export const AdminDashboard = () => {
  const { user } = useApp();
  const [stats, setStats] = useState(null);
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState(initialForm);

  const load = async () => {
    const [st, or, pr] = await Promise.all([
      api('/api/admin/stats'),
      api('/api/admin/orders'),
      api('/api/products')
    ]);
    setStats(st); setOrders(or); setProducts(pr);
  };

  useEffect(() => {
    if (user?.role === 'admin') load().catch(console.error);
  }, [user]);

  if (!user) return <p>Please login first.</p>;
  if (user.role !== 'admin') return <p>Admin only.</p>;

  const createProduct = async (e) => {
    e.preventDefault();
    await api('/api/products', { method: 'POST', body: JSON.stringify(form) });
    setForm(initialForm);
    await load();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Store Owner Dashboard</h2>
      {stats && (
        <div className="grid md:grid-cols-4 gap-3">
          <div className="bg-white border rounded p-3">Products: {stats.products}</div>
          <div className="bg-white border rounded p-3">Customers: {stats.customers}</div>
          <div className="bg-white border rounded p-3">Orders: {stats.orders}</div>
          <div className="bg-white border rounded p-3">Revenue: ${stats.revenue}</div>
        </div>
      )}

      <form onSubmit={createProduct} className="bg-white border rounded-xl p-4 grid md:grid-cols-2 gap-3">
        <h3 className="md:col-span-2 font-semibold">Add Product</h3>
        {Object.keys(form).map((k) => (
          <input key={k} value={form[k]} onChange={(e) => setForm((p) => ({ ...p, [k]: e.target.value }))} className="border rounded p-2" placeholder={k} />
        ))}
        <button className="md:col-span-2 py-2 bg-indigo-600 text-white rounded">Save Product</button>
      </form>

      <div className="bg-white border rounded-xl p-4">
        <h3 className="font-semibold mb-2">Recent Orders</h3>
        <div className="space-y-2">
          {orders.map((o) => <div key={o.id} className="border rounded p-2 text-sm">#{o.id} {o.customer_name} - ${o.total_amount} - {o.status}</div>)}
        </div>
      </div>

      <div className="bg-white border rounded-xl p-4">
        <h3 className="font-semibold mb-2">Products List</h3>
        <div className="grid md:grid-cols-2 gap-2">
          {products.map((p) => <div key={p.id} className="border rounded p-2 text-sm">{p.title} (${p.price}) stock:{p.stock}</div>)}
        </div>
      </div>
    </div>
  );
};
