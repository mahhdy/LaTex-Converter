# Technical Architecture & Future Development

این سند راهنمای فنی برای توسعه‌دهندگانی است که قصد دارند قابلیت‌های جدیدی به LaTeX2Astro اضافه کنند.

## 🏗 ساختار مدل‌ها

پروژه از مدل‌های داده‌ای صریح در `src/models/` استفاده می‌کند:
- `Book`: حاوی تمام اطلاعات کتاب، فصل‌ها و رجیستری لیبل‌ها. (تغییر در این مدل نیازمند بروزرسانی در `LatexParser` و `MarkdownConverter` است).
- `Chapter`: محتوای لاتک و مارک‌داون را به صورت جداگانه نگه می‌دارد.

## Asset & Visual Quality Handling

To ensure the best visual quality on the website:

1.  **Images**:
    - Place all images in the same folder as your `.tex` file or a subfolder.
    - Supported formats: `.jpg`, `.png`, `.pdf` (will be converted if necessary).
    - Use `\includegraphics` for consistent scaling.

2.  **Tables**:
    - The converter uses **Pandoc** to transform LaTeX `tabular` environments into standard Markdown tables.
    - For complex tables with merged cells, manual adjustment in the Markdown review step might be needed.

### Persian Table & Chart Reliability

To achieve consistent results for Persian documents:

1.  **Tables**:
    - Use the `tabularray` package for complex layouts; it produces more structured LaTeX that Pandoc converts more reliably.
    - Avoid nested tables if possible.
    - Test the Output in the "Review" step before finalization.

2.  **Charts & Diagrams (TikZ)**:
    - Standard Markdown ignores TikZ commands.
    - **Recommended**: Convert TikZ diagrams to standalone `.png` or `.pdf` files.
    - Use `\includegraphics` to reference them. This ensures the Persian typography in the diagram is preserved perfectly as an image on the web.

3.  **Articles & MD Input**: 
    - The tool now supports `Article` and `Markdown` types. 
    - Articles are saved as single files in `src/content/articles/fa/`.

4.  **PDF Publishing**:
    - The system automatically detects the generated `.pdf` from your LaTeX source and publishes it to the book's folder in Astro.
    - A direct download link is added to the book's overview page.

## Appendix & Folder Structure
- Books are now organized in a dedicated folder: `src/content/books/[lang]/[english-slug]/`.
- `index.md`: Title, description, and metadata.
- `ch01-name.md`, `app01-name.md`: Chapters and Appendices.
- Filenames and folders use the user-provided **English Slug** for better URL compatibility.

## 🔄 جریان داده (Data Flow)

1. `LatexParser` متن را به صورت بازگشتی می‌خواند و یک شیء `Book` خام تولید می‌کند.
2. `MarkdownConverter` محتوای لاتک هر فصل را به مارک‌داون تبدیل کرده و در همان شیء `Book` ذخیره می‌کند.
3. `ImageProcessor` تصاویر را پیدا کرده و آدرس‌های جدید را در مارک‌داون اصلاح می‌کند.
4. `ConversionOrchestrator` شیء نهایی را به فایل‌های فیزیکی تبدیل می‌کند.

## 🛠 زمینه‌های توسعه در آینده (بروزرسانی شده بر اساس بازخورد)

- **پشتیبانی از راست‌به‌چپ (RTL)**: رابط کاربری فعلی برای متون فارسی بهینه‌سازی نشده است. لازم است محیط نمایش بر اساس زبان انتخابی (یا به صورت خودکار) به حالت RTL تغییر کند.
- **استخراج هوشمند متادیتا (AI)**: بهبود فرآیند استخراج عنوان، موضوع و توضیحات با تحلیل متن مقدمه یا استفاده از مدل‌های زبانی (AI) برای پر کردن خودکار فیلدها.
- **بهبود تجربه کاربری (UX) پس از تبدیل**: 
    - افزودن یک صفحه گزارش نهایی (Success/Report Page) که جزئیات عملیات (فایل‌های ایجاد شده، وضعیت Push به گیت و مسیر محلی) را نمایش دهد.
    - جلوگیری از کلیک مجدد بر روی دکمه Finish با غیرفعال کردن آن یا انتقال به صفحه جدید.
- **گزارش تغییرات**: نمایش دقیق فایل‌هایی که در سایت اصلی تغییر کرده‌اند در انتهای فرآیند.
- **پشتیبانی از کتابشناسی (BibTeX)**: در حال حاضر رفرنس‌های کتابشناسی به صورت متن ساده تبدیل می‌شوند.

## 🧪 تست و عیب‌یابی

تست‌های پروژه در پوشه `tests/` قرار دارند. برای اطمینان از صحت تغییرات، همیشه تست `test_conversion_full.py` را اجرا کنید که کل خط لوله را با یک کتاب نمونه بررسی می‌کند.
