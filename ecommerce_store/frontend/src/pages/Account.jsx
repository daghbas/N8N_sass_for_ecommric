import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';

export const Account = () => {
  const { user } = useApp();
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    if (user) api('/api/orders/my').then(setOrders).catch(console.error);
  }, [user]);

  if (!user) return <p>Please login first.</p>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">My account</h2>
      <div className="bg-white border rounded p-4 mb-4">{user.name} - {user.email}</div>
      <h3 className="font-semibold mb-2">My orders</h3>
      <div className="space-y-2">
        {orders.map((o) => (
          <div key={o.id} className="bg-white border rounded p-3 flex justify-between">
            <span>Order #{o.id} - {o.status}</span><strong>${o.total_amount}</strong>
          </div>
        ))}
      </div>
    </div>
  );
};
