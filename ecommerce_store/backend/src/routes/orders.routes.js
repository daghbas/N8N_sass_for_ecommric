import { Router } from 'express';
import { requireAuth } from '../middleware/auth.js';

export const orderRoutes = (db) => {
  const router = Router();

  router.get('/my', requireAuth, async (req, res) => {
    const orders = await db.all('SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC', req.user.id);
    return res.json(orders);
  });

  router.post('/', requireAuth, async (req, res) => {
    const { items, shipping_address, payment_method } = req.body;
    if (!Array.isArray(items) || items.length === 0) return res.status(400).json({ error: 'No items' });

    let total = 0;
    const resolvedItems = [];

    for (const i of items) {
      const product = await db.get('SELECT id,price,stock,title FROM products WHERE id = ?', Number(i.product_id));
      if (!product) return res.status(404).json({ error: `Product ${i.product_id} not found` });
      const qty = Number(i.quantity);
      if (qty < 1 || qty > product.stock) return res.status(400).json({ error: `Invalid qty for ${product.title}` });
      total += qty * product.price;
      resolvedItems.push({ product_id: product.id, quantity: qty, price: product.price });
    }

    const order = await db.run(
      'INSERT INTO orders(user_id,total_amount,status,shipping_address,payment_method) VALUES (?,?,?,?,?)',
      req.user.id,
      total,
      'paid',
      shipping_address,
      payment_method
    );

    for (const item of resolvedItems) {
      await db.run(
        'INSERT INTO order_items(order_id,product_id,quantity,price) VALUES (?,?,?,?)',
        order.lastID,
        item.product_id,
        item.quantity,
        item.price
      );
      await db.run('UPDATE products SET stock = stock - ? WHERE id = ?', item.quantity, item.product_id);
    }

    const created = await db.get('SELECT * FROM orders WHERE id = ?', order.lastID);
    return res.status(201).json(created);
  });

  return router;
};
