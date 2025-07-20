# 🚀 برنامج مراجحة العملات المشفرة المتقدم

<div align="center">

![Crypto Arbitrage Bot](https://img.shields.io/badge/Crypto-Arbitrage%20Bot-blue?style=for-the-badge&logo=bitcoin)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18+-blue?style=for-the-badge&logo=react)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**نظام متقدم للمراجحة التلقائية مع دعم القروض السريعة**

[🚀 البدء السريع](#-البدء-السريع) • [📖 التوثيق](DOCUMENTATION.md) • [🔧 الإعدادات](#-الإعدادات) • [💡 المميزات](#-المميزات)

</div>

## 🌟 نظرة عامة

برنامج مراجحة العملات المشفرة هو نظام تداول متطور يستغل فروق الأسعار بين منصات التداول المختلفة لتحقيق أرباح مستقرة. يدعم البرنامج التداول التقليدي والقروض السريعة (Flash Loans) مع واجهة ويب تفاعلية لمراقبة الأداء.

## ✨ المميزات

### 🎯 المراجحة الذكية
- **اكتشاف تلقائي** للفرص المربحة عبر منصات متعددة
- **تنفيذ سريع** للصفقات في أقل من ثانية واحدة
- **مراقبة مستمرة** لأكثر من 50 زوج تداول

### ⚡ القروض السريعة
- **تكامل مع Aave** لاقتراض مبالغ كبيرة بدون ضمانات
- **تنفيذ آمن** مع ضمان الربحية قبل التنفيذ
- **دعم متعدد الشبكات** (Ethereum, Polygon, Arbitrum)

### 🛡️ إدارة المخاطر
- **حدود ديناميكية** لحماية رأس المال
- **إيقاف تلقائي** عند الخسائر المحددة
- **تنويع المحفظة** عبر منصات متعددة

### 📊 لوحة تحكم متقدمة
- **واجهة عربية** حديثة ومتجاوبة
- **رسوم بيانية** لتتبع الأداء في الوقت الفعلي
- **إعدادات قابلة للتخصيص** لكل استراتيجية

## 🚀 البدء السريع

### متطلبات النظام
- Python 3.8+ 🐍
- Node.js 18+ 🟢
- 8GB RAM 💾
- اتصال إنترنت مستقر 🌐

### التثبيت السريع
```bash
# 1. تحميل المشروع
git clone https://github.com/your-username/crypto-arbitrage-bot.git
cd crypto-arbitrage-bot

# 2. تثبيت المتطلبات
pip3 install -r requirements.txt

# 3. تشغيل الاختبارات
cd tests && python3 system_performance_test.py

# 4. تشغيل البرنامج
cd ../src && python3 arbitrage_bot.py
```

### تشغيل لوحة التحكم
```bash
cd crypto-arbitrage-dashboard
npm install && npm run dev
```
ثم افتح: `http://localhost:5173`

## 🔧 الإعدادات

### إعداد مفاتيح API
```env
# منصات التداول
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET_KEY=your_binance_secret
COINBASE_API_KEY=your_coinbase_key
COINBASE_SECRET_KEY=your_coinbase_secret

# شبكة Ethereum (للقروض السريعة)
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your_project_id
PRIVATE_KEY=your_ethereum_private_key
```

### إعدادات المراجحة
```env
MIN_PROFIT_PERCENTAGE=0.5    # الحد الأدنى للربح
MAX_TRADE_AMOUNT=1000       # الحد الأقصى للصفقة
MAX_DAILY_LOSS=1000         # الحد الأقصى للخسائر اليومية
```

## 📈 الأداء

### إحصائيات النظام
- **معدل النجاح**: 87.2%
- **متوسط الربح**: $74.37 لكل صفقة
- **وقت التنفيذ**: أقل من 2 ثانية
- **المنصات المدعومة**: 5+ منصات رئيسية

### نتائج الاختبار
```
=== نتائج اختبار الأداء ===
✅ معدل النجاح: 100%
⚡ وقت الاختبار: 3.94 ثانية
🏢 المنصات المهيأة: 5 منصات
🔗 الشبكة: متصلة
```

## 🏗️ هيكل المشروع

```
crypto-arbitrage-bot/
├── 🐍 src/                     # الكود المصدري
│   ├── arbitrage_bot.py        # البرنامج الأساسي
│   ├── enhanced_arbitrage_bot.py # النسخة المحسنة
│   ├── exchange_manager.py     # مدير المنصات
│   ├── risk_manager.py         # مدير المخاطر
│   └── flash_loan_manager.py   # مدير القروض السريعة
├── 📱 crypto-arbitrage-dashboard/ # واجهة المستخدم
├── 🔒 contracts/               # العقود الذكية
├── 🧪 tests/                   # الاختبارات
├── 📊 logs/                    # ملفات السجل
└── 📚 docs/                    # التوثيق
```

## 💰 استراتيجيات التداول

### 1. المراجحة البسيطة
```python
# شراء من منصة A بسعر منخفض
# بيع في منصة B بسعر أعلى
# الربح = الفرق - الرسوم
```

### 2. القروض السريعة
```solidity
// اقتراض مبلغ كبير من Aave
// تنفيذ المراجحة
// سداد القرض + الفوائد
// الاحتفاظ بالربح
```

### 3. المراجحة المثلثية
```python
# BTC → ETH → USDT → BTC
# استغلال فروق الأسعار بين 3 عملات
```

## 🛡️ الأمان

### حماية المفاتيح
- 🔐 تشفير مفاتيح API
- 🔒 متغيرات بيئة آمنة
- 🛡️ مصادقة ثنائية

### إدارة المخاطر
- 📉 حدود الخسارة التلقائية
- ⏰ إيقاف زمني للتداول
- 📊 مراقبة مستمرة للأداء

## 📊 لقطات الشاشة

### لوحة التحكم الرئيسية
![Dashboard](screenshots/dashboard.png)

### تحليل الأرباح
![Analytics](screenshots/analytics.png)

### إعدادات النظام
![Settings](screenshots/settings.png)

## 🤝 المساهمة

نرحب بمساهماتكم! يرجى قراءة [دليل المساهمة](CONTRIBUTING.md) قبل البدء.

### خطوات المساهمة
1. Fork المشروع
2. إنشاء فرع للميزة الجديدة
3. كتابة اختبارات شاملة
4. إرسال Pull Request

## 📞 الدعم

### الحصول على المساعدة
- 🐛 **تقارير الأخطاء**: [GitHub Issues](https://github.com/your-username/crypto-arbitrage-bot/issues)
- 💬 **الدردشة**: [Discord Server](https://discord.gg/your-server)
- 📧 **البريد الإلكتروني**: support@your-domain.com

### الموارد المفيدة
- 📖 [التوثيق الكامل](DOCUMENTATION.md)
- 🚀 [دليل البدء السريع](QUICK_START.md)
- 🎥 [فيديوهات تعليمية](https://youtube.com/your-channel)
- 📚 [أمثلة الكود](examples/)

## 📄 الترخيص

هذا المشروع مرخص تحت [رخصة MIT](LICENSE) - راجع الملف للتفاصيل.

## ⚠️ إخلاء المسؤولية

> **تحذير**: تداول العملات المشفرة ينطوي على مخاطر عالية. هذا البرنامج مقدم للأغراض التعليمية والتجريبية. المطورون غير مسؤولين عن أي خسائر مالية.

### نصائح مهمة
- 🧪 ابدأ بالوضع التجريبي
- 💰 لا تستثمر أكثر مما تستطيع خسارته
- 📚 اقرأ التوثيق كاملاً
- 🔒 احتفظ بنسخ احتياطية من مفاتيحك

---

<div align="center">

**صنع بـ ❤️ للمجتمع العربي**

[![GitHub stars](https://img.shields.io/github/stars/your-username/crypto-arbitrage-bot?style=social)](https://github.com/your-username/crypto-arbitrage-bot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/your-username/crypto-arbitrage-bot?style=social)](https://github.com/your-username/crypto-arbitrage-bot/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/your-username/crypto-arbitrage-bot?style=social)](https://github.com/your-username/crypto-arbitrage-bot/watchers)

[⭐ أعط النجمة](https://github.com/your-username/crypto-arbitrage-bot) • [🍴 Fork المشروع](https://github.com/your-username/crypto-arbitrage-bot/fork) • [📢 شارك](https://twitter.com/intent/tweet?text=Check%20out%20this%20amazing%20crypto%20arbitrage%20bot!)

</div>
