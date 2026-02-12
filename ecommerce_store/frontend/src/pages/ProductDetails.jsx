import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';

export const ProductDetails = () => {
  const { slug } = useParams();
  const [product, setProduct] = useState(null);
  const { addToCart } = useApp();

  useEffect(() => {
    api(`/api/products/${slug}`).then(setProduct).catch(console.error);
  }, [slug]);

  if (!product) return <p>Loading...</p>;

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <img src={product.image_url} alt={product.title} className="rounded-xl border w-full h-96 object-cover" />
      <div>
        <h1 className="text-3xl font-bold mb-2">{product.title}</h1>
        <p className="text-slate-600 mb-3">{product.description}</p>
        <p className="text-lg font-bold mb-4">${product.price}</p>
        <button onClick={() => addToCart(product)} className="px-4 py-2 bg-indigo-600 text-white rounded">Add to cart</button>
      </div>
    </div>
  );
};
