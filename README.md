# CLASSIO — Luxury Fragrance Store (Django)

A full source-code starter for a luxury perfume storefront and staff management dashboard.

## Included pages
- Homepage with featured and latest products
- Catalogue with search, brand/category filters and sorting
- Product details with main image, gallery thumbnails, zoom lightbox, notes, stock and product enquiries
- Our Story and Contact pages
- Session shopping bag, checkout request and private confirmation page
- Staff sign-in, dashboard metrics, product listing, add/edit/delete with multi-image uploader
- Order list/details/status management, enquiries and resolution controls
- Django admin for brands, categories, products, orders and users

## Local setup (Python 3.11+)

```powershell
cd classio_project
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

For macOS/Linux replace activation with `source .venv/bin/activate` and `copy` with `cp`.

Then open `http://127.0.0.1:8000/`. Log in at `/accounts/login/`; staff see `/dashboard/`. Use `/django-admin/` to manage brands, categories and users. **Create at least one Brand and Category before creating products.** Initial categories can be added via `seed_demo`. Upload your own real product images; no fake product images are preloaded.

## Product images
- Main image required at product creation; optional when editing, so existing image is preserved.
- Each additional image is stored in its own `ProductImage` row; up to 12 gallery images per product.
- Drag/drop or file picker, instant previews, replacement and removal (gallery removal only executes on Save).
- Main images cannot be removed without providing a replacement. Legacy records without images show a branded SVG fallback.
- Pillow validates real image content, extension, format and per-file size server-side (default 5 MB). JS validation is only a convenience.
- Files use UUID filenames under `media/products/` and `media/products/gallery/`.
- The original uploaded file is kept unchanged. Use image CDN or derivatives in a high-traffic deployment.
- Each product has editable main image alternative text. Gallery images receive auto-generated descriptive alternative text, editable in Django admin.

## Data and payments
The checkout creates an **order request** stored in the database; it does not charge cards, calculate tax/shipping, send notifications, or integrate payment gateways. Add a verified payment provider before accepting online payments. Inventory is decreased when an order request is placed. The status is changed manually by staff.

## Production
- Set `DJANGO_DEBUG=False`, a strong `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS` in `.env`.
- Run `python manage.py collectstatic --noinput` and host with Gunicorn/ASGI behind HTTPS.
- **Static assets:** WhiteNoise serves collected static files. **Media:** Django's debug media route works only during development. In production configure your reverse proxy to serve `MEDIA_ROOT` at `MEDIA_URL` or use S3-compatible storage. Example Nginx:

```nginx
location /media/ {
    alias /srv/classio/media/;
    autoindex off;
}
client_max_body_size 70M;
```

- Use persistent volume for `media/`; secure backups. The built-in SQLite database suits local demos; consider PostgreSQL and transactional storage at scale.
- Change demo copy, company details, shipping terms and policies before launch.
- Add rate limiting/CAPTCHA, email order confirmations, GDPR/privacy documentation, audit logs, and operational monitoring before public launch.

## Tests
```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test shop
```

## Notes
Images are deleted from local media storage when gallery/product records are deleted or the main image is replaced. Image cleanup is for filesystem storage; adapt the file lifecycle for an external storage backend if needed.
