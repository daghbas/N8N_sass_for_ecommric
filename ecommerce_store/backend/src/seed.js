import bcrypt from 'bcryptjs';
import { connectDb } from './db.js';

const products = [
  { title: 'Premium Hoodie', slug: 'premium-hoodie', description: 'Comfort fit hoodie for daily wear.', price: 59.99, stock: 80, category: 'Fashion', image_url: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab' },
  { title: 'Wireless Headphones', slug: 'wireless-headphones', description: 'Noise cancelling over-ear headphones.', price: 129.0, stock: 45, category: 'Electronics', image_url: 'https://images.unsplash.com/photo-1518444065439-e933c06ce9cd' },
  { title: 'Desk Lamp', slug: 'desk-lamp', description: 'Minimal LED lamp with touch control.', price: 39.5, stock: 120, category: 'Home', image_url: 'https://images.unsplash.com/photo-1519710164239-da123dc03ef4' },
  { title: 'Running Shoes', slug: 'running-shoes', description: 'Lightweight shoes for training.', price: 89.9, stock: 65, category: 'Sports', image_url: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff' },
  { title: 'Smart Watch', slug: 'smart-watch', description: 'Track health and activity with premium sensors.', price: 149.0, stock: 40, category: 'Electronics', image_url: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30' },
  { title: 'Leather Backpack', slug: 'leather-backpack', description: 'Durable premium backpack for daily use.', price: 109.5, stock: 33, category: 'Fashion', image_url: 'https://images.unsplash.com/photo-1491637639811-60e2756cc1c7' }
];

const customers = [
  ['Sara Ahmad', 'sara@shopmail.com', 'Customer@123'],
  ['Omar Khaled', 'omar@shopmail.com', 'Customer@123'],
  ['Lina Yusuf', 'lina@shopmail.com', 'Customer@123'],
  ['Mazen Ali', 'mazen@shopmail.com', 'Customer@123'],
  ['Noor Hassan', 'noor@shopmail.com', 'Customer@123']
];

const supportEvents = [
  ['Sara Ahmad', 'sara@shopmail.com', 'My order has not arrived for 5 days, please check.', 'Order Issue'],
  ['Omar Khaled', 'omar@shopmail.com', 'I want a refund for a damaged product.', 'Refund Request'],
  ['Lina Yusuf', 'lina@shopmail.com', 'The app checkout page crashes on payment.', 'Technical Support'],
  ['Mazen Ali', 'mazen@shopmail.com', 'Your shipping service is very slow and disappointing.', 'Complaint'],
  ['Noor Hassan', 'noor@shopmail.com', 'Do you ship internationally to UAE?', 'General Inquiry']
];

const seed = async () => {
  const db = await connectDb();
  await db.exec(`
    DELETE FROM order_items;
    DELETE FROM orders;
    DELETE FROM products;
    DELETE FROM users;
    DELETE FROM integration_config;
    DELETE FROM support_events;
  `);

  const adminHash = await bcrypt.hash('Admin@123', 10);
  const admin = await db.run('INSERT INTO users(name,email,password_hash,role) VALUES (?,?,?,?)', 'Store Admin', 'admin@store.com', adminHash, 'admin');

  const customerIds = [];
  for (const [name, email, pass] of customers) {
    const hash = await bcrypt.hash(pass, 10);
    const created = await db.run('INSERT INTO users(name,email,password_hash,role) VALUES (?,?,?,?)', name, email, hash, 'customer');
    customerIds.push(created.lastID);
  }

  const productIds = [];
  for (const p of products) {
    const created = await db.run(
      'INSERT INTO products(title,slug,description,price,stock,category,image_url) VALUES (?,?,?,?,?,?,?)',
      p.title, p.slug, p.description, p.price, p.stock, p.category, p.image_url
    );
    productIds.push({ id: created.lastID, price: p.price });
  }

  // Seed realistic paid orders
  for (let i = 0; i < 5; i++) {
    const userId = customerIds[i % customerIds.length];
    const p1 = productIds[i % productIds.length];
    const p2 = productIds[(i + 1) % productIds.length];
    const qty1 = (i % 2) + 1;
    const qty2 = 1;
    const total = qty1 * p1.price + qty2 * p2.price;

    const order = await db.run(
      'INSERT INTO orders(user_id,total_amount,status,shipping_address,payment_method) VALUES (?,?,?,?,?)',
      userId,
      total,
      'paid',
      `Riyadh District ${i + 1}`,
      'card'
    );

    await db.run('INSERT INTO order_items(order_id,product_id,quantity,price) VALUES (?,?,?,?)', order.lastID, p1.id, qty1, p1.price);
    await db.run('INSERT INTO order_items(order_id,product_id,quantity,price) VALUES (?,?,?,?)', order.lastID, p2.id, qty2, p2.price);
    await db.run('UPDATE products SET stock = stock - ? WHERE id = ?', qty1, p1.id);
    await db.run('UPDATE products SET stock = stock - ? WHERE id = ?', qty2, p2.id);
  }

  await db.run(
    'INSERT INTO integration_config(store_name,store_url,platform,outbound_api_key,outbound_api_secret,webhook_token,saas_support_endpoint) VALUES (?,?,?,?,?,?,?)',
    'ProStore Demo',
    'http://localhost:5173',
    'Custom API',
    'store_out_api_key_demo_123',
    'store_out_api_secret_demo_123',
    'store_webhook_token_demo_123',
    'http://localhost:8000/api/v1/support'
  );

  for (const [name, email, msg, hint] of supportEvents) {
    await db.run(
      'INSERT INTO support_events(customer_name,customer_email,message,category_hint) VALUES (?,?,?,?)',
      name, email, msg, hint
    );
  }

  console.log('✅ Seed complete with products, customers, orders, and integration test data');
  console.log('Admin: admin@store.com / Admin@123');
  console.log(`Admin user id: ${admin.lastID}`);
};

seed();
