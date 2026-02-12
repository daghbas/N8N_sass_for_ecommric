import { Router } from 'express';
import { requireAuth, requireAdmin } from '../middleware/auth.js';

export const productRoutes = (db) => {
  const router = Router();

  router.get('/', async (req, res) => {
    const items = await db.all('SELECT * FROM products ORDER BY id DESC');
    res.json(items);
  });

  router.get('/:slug', async (req, res) => {
    const item = await db.get('SELECT * FROM products WHERE slug = ?', req.params.slug);
    if (!item) return res.status(404).json({ error: 'Not found' });
    return res.json(item);
  });

  router.post('/', requireAuth, requireAdmin, async (req, res) => {
    const { title, slug, description, price, stock, category, image_url } = req.body;
    if (!title || !slug || !description || !price || stock == null || !category || !image_url) {
      return res.status(400).json({ error: 'Missing fields' });
    }
    const result = await db.run(
      'INSERT INTO products(title,slug,description,price,stock,category,image_url) VALUES (?,?,?,?,?,?,?)',
      title, slug, description, Number(price), Number(stock), category, image_url
    );
    const created = await db.get('SELECT * FROM products WHERE id = ?', result.lastID);
    return res.status(201).json(created);
  });

  router.put('/:id', requireAuth, requireAdmin, async (req, res) => {
    const { title, description, price, stock, category, image_url } = req.body;
    await db.run(
      `UPDATE products SET title=?,description=?,price=?,stock=?,category=?,image_url=? WHERE id=?`,
      title, description, Number(price), Number(stock), category, image_url, Number(req.params.id)
    );
    const updated = await db.get('SELECT * FROM products WHERE id = ?', Number(req.params.id));
    return res.json(updated);
  });

  router.delete('/:id', requireAuth, requireAdmin, async (req, res) => {
    await db.run('DELETE FROM products WHERE id = ?', Number(req.params.id));
    return res.json({ success: true });
  });

  return router;
};
