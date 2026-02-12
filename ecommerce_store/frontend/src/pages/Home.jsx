import { Link } from 'react-router-dom';

export const Home = () => (
  <section className="grid md:grid-cols-2 gap-8 items-center">
    <div>
      <h1 className="text-4xl font-extrabold mb-4">Modern E-commerce Store Demo</h1>
      <p className="text-slate-600 mb-6">Full store project with React + Node.js + SQLite, including admin dashboard, product management, customers, orders and checkout.</p>
      <div className="flex gap-3">
        <Link to="/products" className="px-5 py-3 rounded bg-indigo-600 text-white">Shop now</Link>
        <Link to="/admin" className="px-5 py-3 rounded border">Admin dashboard</Link>
      </div>
    </div>
    <div className="bg-white border rounded-xl p-6">
      <ul className="space-y-2 text-slate-700">
        <li>✅ Product catalog + details</li>
        <li>✅ Cart + checkout flow</li>
        <li>✅ Auth for customers/admin</li>
        <li>✅ Admin analytics and orders</li>
      </ul>
    </div>
  </section>
);
