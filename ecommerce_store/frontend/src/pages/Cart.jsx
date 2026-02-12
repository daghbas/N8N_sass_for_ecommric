import { Link } from 'react-router-dom';
import { useApp } from '../context/AppContext';

export const Cart = () => {
  const { cart } = useApp();
  const total = cart.reduce((sum, i) => sum + i.price * i.quantity, 0);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Cart</h2>
      {cart.length === 0 ? <p>Cart is empty.</p> : (
        <div className="space-y-3">
          {cart.map((i) => (
            <div key={i.id} className="bg-white border rounded p-3 flex justify-between">
              <span>{i.title} x{i.quantity}</span>
              <strong>${(i.price * i.quantity).toFixed(2)}</strong>
            </div>
          ))}
          <div className="font-bold text-lg">Total: ${total.toFixed(2)}</div>
          <Link to="/checkout" className="inline-block px-4 py-2 bg-indigo-600 text-white rounded">Checkout</Link>
        </div>
      )}
    </div>
  );
};
