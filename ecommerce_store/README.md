# Ecommerce Store Project (React + Node.js + SQLite)

هذا مشروع متجر إلكتروني متكامل يمكن اعتباره متجرًا حقيقيًا للتجارب الأكاديمية، ثم يتم ربطه مع منصة الـ SaaS الأساسية.

## ماذا يحتوي؟

- **Backend**: Node.js + Express + SQLite
- **Frontend**: React + Vite + Tailwind (CDN)
- **واجهات كاملة**:
  - الصفحة الرئيسية
  - المنتجات
  - تفاصيل المنتج
  - السلة
  - الدفع
  - تسجيل/دخول
  - حساب العميل
  - Dashboard صاحب المتجر (Admin)
- **إدارة المتجر**:
  - إحصائيات
  - إدارة المنتجات
  - إدارة الطلبات
- **Seed Data مكتمل**:
  - Admin
  - 5 عملاء
  - 6 منتجات
  - 5 طلبات مدفوعة
  - بيانات تكامل جاهزة للربط مع SaaS
  - رسائل دعم seeded للاختبار

## التشغيل

### Backend
```bash
cd backend
npm install
npm run seed
npm run dev
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

- Backend: `http://localhost:4100`
- Frontend: `http://localhost:5173`

## بيانات دخول تجريبية

- Admin: `admin@store.com` / `Admin@123`
- Customers (from seed):
  - `sara@shopmail.com` / `Customer@123`
  - `omar@shopmail.com` / `Customer@123`
  - `lina@shopmail.com` / `Customer@123`
  - `mazen@shopmail.com` / `Customer@123`
  - `noor@shopmail.com` / `Customer@123`

## Endpoints مفيدة لاختبار الربط مع SaaS

- `GET /api/integration/status`
  - يرجّع بيانات المتجر + credentials + target endpoint لـ SaaS.
- `GET /api/integration/support-events`
  - رسائل العملاء seeded للاختبار.
- `GET /api/integration/sample-support-payload`
  - payload جاهز + curl command لإرساله إلى `/api/v1/support` في منصة SaaS.

## خطوات التحقق الكاملة (Checklist)

1. شغّل seed ثم backend/frontend.
2. افتح `http://localhost:5173` وتأكد أن المنتجات تظهر.
3. ادخل كـ Admin وافتح `/admin` وتأكد من ظهور:
   - المنتجات
   - العملاء
   - الطلبات
   - الإيرادات
4. ادخل كـ Customer وجرب إضافة منتج للسلة ثم Checkout.
5. نفذ:
   - `GET http://localhost:4100/api/integration/status`
   - `GET http://localhost:4100/api/integration/sample-support-payload`
6. استخدم `curl_example` المولد لإرسال رسالة دعم إلى منصة SaaS وشاهد التصنيف والرد.

## كيف نربطه مع منصة SaaS الأساسية؟

- هذا المشروع يمثل **متجر خارجي فعلي**.
- من منصة SaaS الأساسية، يتم إدخال:
  - Store URL = عنوان backend أو storefront
  - API Token / Secret = credentials (أو API keys مخصصة)
- ثم يتم إرسال أحداث الطلبات/الدعم من هذا المتجر إلى SaaS عبر webhook + API.
