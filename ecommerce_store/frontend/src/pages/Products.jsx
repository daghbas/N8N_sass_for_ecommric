import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';

export const Products = () => {
  const [items, setItems] = useState([]);
  const { addToCart } = useApp();

  useEffect(() => {
    api('/api/products').then(setItems).catch(console.error);
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Products</h2>
      <div className="grid md:grid-cols-3 gap-4">
        {items.map((p) => (
          <article key={p.id} className="bg-white border rounded-xl overflow-hidden">
            <img src={p.image_url} alt={p.title} className="h-44 w-full object-cover" />
            <div className="p-4">
              <h3 className="font-semibold">{p.title}</h3>
              <p className="text-sm text-slate-600 mb-2">{p.category}</p>
              <p className="font-bold mb-3">${p.price}</p>
              <div className="flex gap-2">
                <button onClick={() => addToCart(p)} className="px-3 py-2 rounded bg-indigo-600 text-white text-sm">Add to cart</button>
                <Link to={`/products/${p.slug}`} className="px-3 py-2 rounded border text-sm">Details</Link>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
};
