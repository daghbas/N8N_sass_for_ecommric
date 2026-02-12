import express from 'express';
import cors from 'cors';

import { connectDb } from './db.js';
import { authRoutes } from './routes/auth.routes.js';
import { productRoutes } from './routes/products.routes.js';
import { orderRoutes } from './routes/orders.routes.js';
import { adminRoutes } from './routes/admin.routes.js';
import { integrationRoutes } from './routes/integration.routes.js';

const port = process.env.PORT || 4100;

const start = async () => {
  const db = await connectDb();
  const app = express();

  app.use(cors());
  app.use(express.json());

  app.get('/health', (_req, res) => res.json({ status: 'ok' }));
  app.use('/api/auth', authRoutes(db));
  app.use('/api/products', productRoutes(db));
  app.use('/api/orders', orderRoutes(db));
  app.use('/api/admin', adminRoutes(db));
  app.use('/api/integration', integrationRoutes(db));

  app.listen(port, () => console.log(`Backend running on :${port}`));
};

start();
