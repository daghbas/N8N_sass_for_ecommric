import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';

export const Register = () => {
  const [name, setName] = useState('New Customer');
  const [email, setEmail] = useState('new@shopmail.com');
  const [password, setPassword] = useState('Customer@123');
  const { login } = useApp();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    try {
      const data = await api('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({ name, email, password })
      });
      login(data);
      navigate('/');
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <form onSubmit={submit} className="max-w-md bg-white border rounded-xl p-6 space-y-3">
      <h2 className="text-xl font-bold">Create account</h2>
      <input value={name} onChange={(e) => setName(e.target.value)} className="w-full border rounded p-2" />
      <input value={email} onChange={(e) => setEmail(e.target.value)} className="w-full border rounded p-2" />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full border rounded p-2" />
      <button className="w-full bg-indigo-600 text-white py-2 rounded">Register</button>
    </form>
  );
};
