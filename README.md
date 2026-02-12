# EcommAI SaaS - Multi Store Academic Edition

هذا الإصدار يحقق طلبك الأكاديمي:

- شركة واحدة يمكنها ربط **متجرين أو أكثر**.
- لكل متجر **Dashboard خاص**.
- لكل متجر يتم توليد:
  - `internal_api_key`
  - `internal_webhook_token`
- مع حفظ بيانات الربط الخارجية للمتجر:
  - `external_api_token`
  - `external_api_secret`

كما يوجد دعم AI عبر n8n + Gemini، وجدولة ونشر X تلقائيًا عبر n8n.

---

## دمج Workflow في n8n (مهم)

نعم، تم تنفيذ نسخة **Workflow موحدة** تعمل بنفس السلوك الحالي لمسارين:

1. مسار دعم العملاء (Gemini Classification + Reply)
2. مسار نشر X (جدولة/نشر)

الملف الجديد:

- `n8n/unified_support_and_x_workflow.json`

هذا الملف يحتوي Webhookين داخل نفس Workflow:

- `POST /webhook/customer-support`
- `POST /webhook/x-publish`

وكل مسار ما زال يحتفظ بنفس منطقه الحالي بدون تغيير في واجهات Flask.

> يمكنك الاستمرار باستخدام الملفين المنفصلين أو استخدام الملف الموحد. الأفضل للمشروع الآن: الملف الموحد.

---

## إجابة سؤالك مباشرة

النظام **لا يبني متجر e-commerce جديد بدل متجرك الحالي**.

النظام مصمم لكي تقوم الشركة بـ **ربط متجرها الخارجي الحالي** (مثل Shopify / WooCommerce / أو أي منصة فيها API وWebhooks).

يعني أي متجر خارجي يمكن ربطه بشرط توفر:

1. `Store URL`
2. `API Token`
3. `API Secret`
4. Webhook أو إمكانية إرسال requests إلى النظام

بعد الربط، التطبيق يولد مفاتيح داخلية (API Key + Webhook Token) لاستخدامها في التكامل بين المتجر وFlask/n8n بشكل منظم.

---

## قاعدة البيانات (النمذجة)

### Company
يمثل الشركة المالكة.

### User
حسابات الدخول الخاصة بالشركة.

### Store
يمثل كل متجر فعلي (Store 1 / Store 2 ...):
- اسم المتجر
- المنصة
- رابط المتجر
- توكن/سيكرت API الخارجي
- API Key داخلي + Webhook Token داخلي (يتم توليدهما تلقائيًا)
- ربط X لكل متجر

### ScheduledPost
منشورات X المجدولة لكل متجر.

---

## كيف نطبق سيناريو متجرين فعليًا؟

1. سجل حساب شركة من `/register` مع بيانات **المتجر الأول**.
2. ادخل `/dashboard`.
3. استخدم نموذج "ربط متجر جديد" لإضافة **المتجر الثاني**.
4. ستجد قائمة المتاجر، وكل متجر له زر:
   - `Open Store Dashboard`
5. افتح كل متجر على حدة وسترى:
   - بيانات API الخاصة به
   - تكامل X خاص به
   - جدولة ونشر محتوى خاص به
   - سجل المنشورات الخاص به فقط

بهذا تصبح عندك عزل واضح لكل متجر داخل نفس حساب الشركة.

---

## كيف يتم الربط الصحيح مع المتجر؟

الطريقة المقترحة (الأكاديمية الصحيحة):

- على منصة المتجر (Shopify/WooCommerce/Custom):
  - تنشئ App / API Access
  - تحصل على `external_api_token` و `external_api_secret`
  - تضيف Webhook من المتجر إلى endpoint داخل نظامك
- داخل تطبيقنا:
  - نحفظ بيانات الربط في جدول `stores`
  - نولد `internal_api_key` و `internal_webhook_token`
  - هذه القيم تستخدم للتحقق من أي طلب قادم من المتجر أو n8n

> في الإنتاج: يفضّل تشفير التوكنز، واستخدام HMAC verification للويبهوك.

---

## المسارات المهمة

- Company Dashboard: `GET /dashboard`
- Store Dashboard: `GET /dashboard/store/<store_id>`
- Add Store: `POST /stores/add`
- Connect X per store: `POST /stores/<store_id>/connect-x`
- Schedule post per store: `POST /stores/<store_id>/publishing/schedule`
- Run pending per store: `POST /stores/<store_id>/publishing/run-pending`
- AI support API: `POST /api/v1/support`

---

## التشغيل المحلي

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

ثم:
- افتح `http://localhost:8000`
- أنشئ شركة + متجر أول
- أضف متجر ثاني من لوحة الشركة

---

## n8n Workflows

- دعم العملاء (منفصل): `n8n/customer_support_gemini_workflow.json`
- نشر X (منفصل): `n8n/x_publishing_workflow.json`
- **موحد (مفضل):** `n8n/unified_support_and_x_workflow.json`


---

## مشروع متجر خارجي متكامل (جديد)

تم إنشاء مشروع متجر خارجي كامل داخل:

- `ecommerce_store/backend` (Node.js + Express + SQLite)
- `ecommerce_store/frontend` (React + Vite + Tailwind)

هذا المتجر يستخدم كمتجر فعلي للتجربة، ثم يتم ربطه بمنصة الـ SaaS الأساسية كـ External Store.

يمكنك الآن اختبار الربط الحقيقي عبر مشروع `ecommerce_store` باستخدام endpoint:

- `GET /api/integration/sample-support-payload`

ثم إرسال الـ payload الناتج إلى:

- `http://localhost:8000/api/v1/support`

لمشاهدة التصنيف والرد الذكي عمليًا.
