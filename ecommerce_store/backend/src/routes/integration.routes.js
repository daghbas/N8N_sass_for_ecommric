import { Router } from 'express';

export const integrationRoutes = (db) => {
  const router = Router();

  router.get('/status', async (_req, res) => {
    const cfg = await db.get('SELECT * FROM integration_config ORDER BY id DESC LIMIT 1');
    const [{ c: events }] = await db.all('SELECT COUNT(*) as c FROM support_events');
    if (!cfg) return res.status(404).json({ error: 'No integration config found. Run seed first.' });

    return res.json({
      store: {
        name: cfg.store_name,
        url: cfg.store_url,
        platform: cfg.platform,
      },
      credentials: {
        outbound_api_key: cfg.outbound_api_key,
        outbound_api_secret: cfg.outbound_api_secret,
        webhook_token: cfg.webhook_token,
      },
      saas_support_endpoint: cfg.saas_support_endpoint,
      seeded_support_events: events,
    });
  });

  router.get('/support-events', async (_req, res) => {
    const rows = await db.all('SELECT * FROM support_events ORDER BY id DESC LIMIT 50');
    return res.json(rows);
  });

  router.get('/sample-support-payload', async (_req, res) => {
    const cfg = await db.get('SELECT * FROM integration_config ORDER BY id DESC LIMIT 1');
    const event = await db.get('SELECT * FROM support_events ORDER BY id DESC LIMIT 1');
    if (!cfg || !event) return res.status(404).json({ error: 'Seed data missing. Run seed first.' });

    const payload = {
      source: 'external_ecommerce_store',
      api_key: cfg.outbound_api_key,
      webhook_token: cfg.webhook_token,
      customer_id: `cust_${event.id}`,
      customer_email: event.customer_email,
      message: event.message,
      metadata: {
        platform: cfg.platform,
        store_name: cfg.store_name,
        category_hint: event.category_hint,
        store_url: cfg.store_url,
      },
    };

    return res.json({
      target: cfg.saas_support_endpoint,
      payload,
      curl_example: `curl -X POST ${cfg.saas_support_endpoint} -H \"Content-Type: application/json\" -d '${JSON.stringify({ customer_id: payload.customer_id, message: payload.message })}'`,
    });
  });

  return router;
};
