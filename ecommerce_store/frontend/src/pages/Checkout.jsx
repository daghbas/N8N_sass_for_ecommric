import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';

export const Checkout = () => {
  const { cart, setCart, user } = useApp();
  const [address, setAddress] = useState('Riyadh, King Fahad Rd');
  const navigate = useNavigate();

  const submit = async () => {
    if (!user) return alert('Please login first');
    try {
      await api('/api/orders', {
        method: 'POST',
        body: JSON.stringify({
          items: cart.map((c) => ({ product_id: c.id, quantity: c.quantity })),
          shipping_address: address,
          payment_method: 'card'
        })
      });
      setCart([]);
      navigate('/account');
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <div className="max-w-xl">
      <h2 className="text-2xl font-bold mb-4">Checkout</h2>
      <textarea value={address} onChange={(e) => setAddress(e.target.value)} className="w-full border rounded p-2 mb-3" rows={3} />
      <button onClick={submit} className="px-4 py-2 bg-indigo-600 text-white rounded">Place order</button>
    </div>
  );
};
