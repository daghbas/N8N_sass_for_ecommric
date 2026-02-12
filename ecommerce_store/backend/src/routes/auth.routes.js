import { Router } from 'express';
import bcrypt from 'bcryptjs';
import { signToken } from '../utils/auth.js';

export const authRoutes = (db) => {
  const router = Router();

  router.post('/register', async (req, res) => {
    const { name, email, password } = req.body;
    if (!name || !email || !password) return res.status(400).json({ error: 'Missing fields' });

    const exists = await db.get('SELECT id FROM users WHERE email = ?', email.toLowerCase());
    if (exists) return res.status(409).json({ error: 'Email already exists' });

    const hash = await bcrypt.hash(password, 10);
    const result = await db.run(
      'INSERT INTO users(name,email,password_hash,role) VALUES (?,?,?,?)',
      name,
      email.toLowerCase(),
      hash,
      'customer'
    );

    const user = { id: result.lastID, name, email: email.toLowerCase(), role: 'customer' };
    return res.status(201).json({ user, token: signToken(user) });
  });

  router.post('/login', async (req, res) => {
    const { email, password } = req.body;
    const user = await db.get('SELECT * FROM users WHERE email = ?', (email || '').toLowerCase());
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });

    const ok = await bcrypt.compare(password || '', user.password_hash);
    if (!ok) return res.status(401).json({ error: 'Invalid credentials' });

    const payload = { id: user.id, name: user.name, email: user.email, role: user.role };
    return res.json({ user: payload, token: signToken(payload) });
  });

  return router;
};
