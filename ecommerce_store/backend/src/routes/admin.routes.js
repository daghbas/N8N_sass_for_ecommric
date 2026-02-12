import { Router } from 'express';
import { requireAuth, requireAdmin } from '../middleware/auth.js';

export const adminRoutes = (db) => {
  const router = Router();

  router.get('/stats', requireAuth, requireAdmin, async (_req, res) => {
    const [{ c: products }] = await db.all('SELECT COUNT(*) as c FROM products');
    const [{ c: customers }] = await db.all("SELECT COUNT(*) as c FROM users WHERE role='customer'");
    const [{ c: orders }] = await db.all('SELECT COUNT(*) as c FROM orders');
    const [{ total }] = await db.all('SELECT COALESCE(SUM(total_amount),0) as total FROM orders');

    return res.json({ products, customers, orders, revenue: total });
  });

  router.get('/orders', requireAuth, requireAdmin, async (_req, res) => {
    const list = await db.all(
      `SELECT o.*, u.name as customer_name, u.email as customer_email
       FROM orders o JOIN users u ON o.user_id=u.id ORDER BY o.id DESC`
    );
    return res.json(list);
  });

  return router;
};
