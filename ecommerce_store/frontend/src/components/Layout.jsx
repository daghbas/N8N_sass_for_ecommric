import { Link } from 'react-router-dom';
import { useApp } from '../context/AppContext';

export const Layout = ({ children }) => {
  const { user, cart, logout } = useApp();

  return (
    <div>
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
          <Link to="/" className="font-bold text-xl text-indigo-600">ProStore</Link>
          <nav className="flex gap-4 items-center text-sm">
            <Link to="/products">Products</Link>
            <Link to="/cart">Cart ({cart.reduce((a, c) => a + c.quantity, 0)})</Link>
            {user?.role === 'admin' && <Link to="/admin">Admin</Link>}
            {user ? (
              <button onClick={logout} className="px-3 py-1 bg-slate-900 text-white rounded">Logout</button>
            ) : (
              <Link to="/login" className="px-3 py-1 bg-slate-900 text-white rounded">Login</Link>
            )}
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
    </div>
  );
};
