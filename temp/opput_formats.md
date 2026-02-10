
#### مرحله ۳: به‌روزرسانی خودکار ratings.json / Step 3: Auto-Update ratings.json

یک کران‌جاب (CRON job) برای به‌روزرسانی روزانه بسازید:

Create a CRON job for daily updates:

```bash
# اسکریپت Node.js / Node.js Script
node scripts/update-ratings.js
```

```javascript
// scripts/update-ratings.js
const db = /* اتصال به دیتابیس / connect to database */;
const ratings = await db.getAllRatings();
fs.writeFileSync('src/data/ratings.json', JSON.stringify(ratings, null, 2));
```

---

## 🔍 پیش‌نویس‌ها (Drafts)

### تغییرات انجام شده / Changes Made

**قبلاً / Before:**

- پیش‌نویس‌ها فقط در صفحه `/drafts` نمایش داده می‌شدند
- Drafts only shown on `/drafts` page

**اکنون / Now:**

- پیش‌نویس‌ها در لیست‌های اصلی (مقالات، کتاب‌ها) نمایش داده می‌شوند
- کاربران می‌توانند پیش‌نویس‌ها را امتیازدهی کنند
- Drafts shown in main lists (articles, books)
- Users can rate drafts

### چگونه پیش‌نویس بسازم؟ / How to Create a Draft?

در frontmatter فایل Markdown:

```markdown
---
title: "عنوان مقاله"
draft: true
lang: fa
publishDate: 2026-02-10
categories:
  - فلسفه
tags:
  - اخلاق
---

محتوای پیش‌نویس...
```

### کجا نمایش داده می‌شود؟ / Where Are Drafts Shown?

✅ **نمایش داده می‌شود / Shown:**

- صفحات لیست مقالات و کتاب‌ها / Articles and books index pages
- نتایج جستجو / Search results
- سیستم امتیازدهی / Rating system
- داشبورد آنالیتیکس / Analytics dashboard

❌ **نمایش داده نمی‌شود / Not Shown:**

- فیدهای RSS
- برخی بخش‌های صفحه اصلی / Some homepage sections

---

## 🎨 داشبورد آنالیتیکس / Analytics Dashboard

### محل / Location

- فارسی: `/analytics`
- انگلیسی: `/en/analytics`

### ویژگی‌ها / Features

1. **TreeMap چند ردیفی** - الگوریتم squarified برای استفاده بهینه از فضا
2. **تب‌های تعاملی** - جابجایی بین برچسب‌ها و دسته‌بندی‌ها
3. **Tooltip هوشمند** - نمایش ۳ محتوای محبوب در هر برچسب/دسته

   Multi-row TreeMap with squarified algorithm
   Interactive tabs for tags/categories
   Smart tooltips showing top 3 popular items

### چگونه آنالیتیکس را سفارشی کنم؟ / How to Customize Analytics?

فایل: `src/pages/analytics.astro`

**تغییر رنگ‌های TreeMap / Change TreeMap Colors:**

```javascript
// خط ~80 / Line ~80
const hue = (index * 137.5) % 360; // تغییر دهید / modify this

// یا از رنگ‌های ثابت استفاده کنید / or use fixed colors
const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'];
fill: colors[index % colors.length]
```

**تغییر اندازه TreeMap / Change TreeMap Size:**

```javascript
const width = 800;  // پیش‌فرض / default
const height = 400;
```

---

## 🔧 تنظیمات اضافی / Additional Configuration

### 1. سئو (SEO)

فایل: `astro.config.mjs`

```javascript
export default defineConfig({
  site: 'https://yoursite.com', // دامنه واقعی خود را وارد کنید
});
```

### 2. نظرات Giscus

فایل: `src/components/Giscus.astro`

```astro
<script
  data-repo="username/repo"           ← تغییر دهید
  data-repo-id="your-repo-id"         ← تغییر دهید
  data-category="Announcements"
  data-category-id="your-category-id" ← تغییر دهید
>
```

### 3. خبرنامه Buttondown

فایل: `src/components/Newsletter.astro`

```html
<form action="https://buttondown.email/api/emails/embed-subscribe/YOUR_USERNAME" ← تغییر دهید
```

### 4. فرم تماس

فایل: `src/pages/contact.astro` یا `src/pages/en/contact.astro`

```html
<form action="https://formspree.io/f/YOUR_FORM_ID"> ← کد Formspree خود را وارد کنید
```

---

## 📝 چک‌لیست نهایی / Final Checklist

قبل از استقرار سایت (Before deployment):

- [ ] `stats.json` را با آمار واقعی پر کنید
- [ ] `ratings.json` را خالی بگذارید یا با داده‌های اولیه پر کنید
- [ ] دامنه سایت را در `astro.config.mjs` تنظیم کنید
- [ ] مشخصات Giscus را در `Giscus.astro` وارد کنید
- [ ] نام کاربری Buttondown را در `Newsletter.astro` تنظیم کنید
- [ ] کد Formspree را در صفحات تماس وارد کنید
- [ ] (اختیاری) API برای ذخیره امتیازات راه‌اندازی کنید

---

## ❓ سوالات متداول / FAQ

**پرسش:** آیا باید API برای امتیازدهی راه‌اندازی کنم؟
**پاسخ:** خیر، اختیاری است. می‌توانید فعلاً به صورت دستی `ratings.json` را به‌روز کنید.

**Q:** Do I need to set up an API for ratings?
**A:** No, it's optional. You can manually update `ratings.json` for now.

---

**پرسش:** چگونه آمار بازدید واقعی را ردیابی کنم؟
**پاسخ:** از Cloudflare Analytics یا Google Analytics استفاده کنید و داده‌ها را دستی به `stats.json` منتقل کنید.

**Q:** How do I track real visit statistics?
**A:** Use Cloudflare Analytics or Google Analytics and manually transfer data to `stats.json`.

---

**پرسش:** آیا می‌توانم پیش‌نویس‌ها را مخفی کنم؟
**پاسخ:** بله، فیلتر `&& !data.draft` را به فایل‌های index.astro اضافه کنید.

**Q:** Can I hide drafts?
**A:** Yes, add the `&& !data.draft` filter back to index.astro files.

---

## 🆘 پشتیبانی / Support

در صورت بروز مشکل:

1. فایل‌های لاگ را بررسی کنید: `npm run dev`
2. خطاهای مرورگر را در Console بررسی کنید
3. از اینجا آموزش ببینید: [walkthrough.md](file:///C:/Users/mahhd/.gemini/antigravity/brain/f9749375-8ff3-4b34-a4da-16410bd7dbda/walkthrough.md)

If you encounter issues:

1. Check log files: `npm run dev`
2. Check browser Console for errors
3. Review the walkthrough: [walkthrough.md](file:///C:/Users/mahhd/.gemini/antigravity/brain/f9749375-8ff3-4b34-a4da-16410bd7dbda/walkthrough.md)
