# Online Store Kian

Online Store Kian is a full-stack online shop built with Django REST Framework, PostgreSQL, Redis, Celery, React, Vite, and Nginx. The project includes a polished bakery-style storefront, authenticated carts, checkout with address validation, discount codes, admin-managed product availability, and a complete Docker deployment setup.

## Project Preview

![Home hero](<picture from the project/Screenshot from 2026-05-24 02-39-00.png>)

![Product listing](<picture from the project/Screenshot from 2026-05-24 02-39-32.png>)

![Cart and checkout](<picture from the project/Screenshot from 2026-05-24 02-39-50.png>)

![Profile and addresses](<picture from the project/Screenshot from 2026-05-24 02-40-29.png>)

![Django admin / management](<picture from the project/Screenshot from 2026-05-24 02-40-38.png>)

## Features

### Storefront
- React + Vite frontend with a visual bakery-inspired design.
- Large black hero section with a croissant image animation and the `Online Store Kian` title animation.
- Category navigation for product groups such as croissants, coffee, gift boxes, and pastry.
- Product cards with images, price, category, description, and add-to-cart actions.
- Category-specific product pages where customers only select products from the chosen category.
- Cart sidebar with add, remove, increase, and decrease quantity controls.
- Footer with shop navigation and customer actions.

### Authentication and Customer Area
- Custom Django user model with email-based authentication.
- JWT login with access and refresh tokens.
- Customer profile editing for first name, last name, email, and phone.
- Customer address book with up to five saved addresses.
- Order history and current unpaid cart view inside the profile panel.

### Cart and Checkout
- Each authenticated user has a private cart.
- Users cannot access or modify another user’s cart.
- Checkout requires a complete profile and a manually selected complete address.
- Empty, missing, null, or invalid `address_id` values are rejected by the backend.
- Customers can still increase or decrease item quantities on the checkout page.
- Checkout supports admin-created discount codes.
- Successful payment creates an order, snapshots customer/address data, stores item prices, and decrements product inventory.

### Admin Management
- Django Admin supports product, category, cart, order, order item, address, and discount code management.
- Products include an `is_available` field for admin-controlled availability.
- Products with `is_available=False` or zero inventory are hidden from the storefront.
- Product price uses `DecimalField` for safer money handling.

### Backend/API
- Django 4.2 and Django REST Framework.
- PostgreSQL support for Docker/production-like deployment.
- SQLite support for local lightweight development.
- Redis cache/session support in Docker.
- Celery worker service included for asynchronous tasks.
- Nginx serves the built frontend, static files, media files, and proxies API requests to Django.

## Tech Stack

- Backend: Django, Django REST Framework, Simple JWT
- Database: PostgreSQL in Docker, SQLite for local development
- Cache/Broker: Redis
- Worker: Celery
- Frontend: React, Vite, Tailwind CSS, Lucide React
- Web server: Nginx
- Containerization: Docker and Docker Compose

## Docker Services

The Docker setup includes:

| Service | Purpose | Default Port |
| --- | --- | --- |
| `nginx` | Serves React build and proxies API/static/media | `8080` |
| `web` | Django + Gunicorn API server | `8001 -> 8000` |
| `db` | PostgreSQL 14 database | `15433 -> 5432` |
| `redis` | Redis cache and Celery broker | `6380 -> 6379` |
| `celery` | Celery worker | internal |

## Environment Files

The project includes:

- `.env.example`: template for local or production-like variables.
- `.env.docker`: ready-to-run Docker development variables.

Before using this in production, change these values:

- `SECRET_KEY`
- `DB_PASSWORD`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `ALLOWED_HOSTS`
- `DEBUG=False` should remain false in production.

## Run With Docker

Build all images:

```bash
docker compose build
```

Start the full stack:

```bash
docker compose up -d
```

Open the application:

```text
Frontend: http://127.0.0.1:8080/
Django API: http://127.0.0.1:8001/
Django Admin: http://127.0.0.1:8080/admin/
```

View running services:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f web
```

Stop services without deleting data volumes:

```bash
docker compose down
```

Stop services and remove database/static/media volumes:

```bash
docker compose down -v
```

## Create a Django Superuser in Docker

After the stack is running:

```bash
docker compose exec web python manage.py createsuperuser
```

Because the project uses a custom email-based user model, the admin login uses email rather than username.

## Useful Docker Commands

Run migrations manually:

```bash
docker compose exec web python manage.py migrate
```

Collect static files manually:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

Open Django shell:

```bash
docker compose exec web python manage.py shell
```

Restart only the web service:

```bash
docker compose restart web
```

## Local Development Without Docker

The project can still run locally with SQLite using `.env` settings:

```bash
.venv1/bin/python manage.py migrate
.venv1/bin/python manage.py runserver 127.0.0.1:8000
```

Frontend local development:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Local URLs:

```text
Frontend: http://127.0.0.1:5173/
Backend: http://127.0.0.1:8000/
Admin: http://127.0.0.1:8000/admin/
```

## Important Implementation Details

### User-specific carts

Carts are linked to authenticated users. The frontend no longer stores a shared `cart_id` in `localStorage`; instead it fetches the current user’s cart from:

```text
GET /carts/current/
```

Cart item operations are scoped to the authenticated owner, so users cannot read or modify another user’s cart.

### Checkout validation

Checkout requires:

- Authenticated user
- Non-empty cart
- Complete profile: first name, last name, email, phone
- Manually selected complete address
- Valid inventory for every cart item

The backend rejects missing, null, zero, incomplete, or foreign addresses.

### Product availability

Product visibility is controlled by:

- `Product.is_available`
- `Product.inventory`

The storefront API only returns products with:

```python
is_available=True
inventory__gt=0
```

### Discount codes

Discount codes are created and managed by admins in Django Admin. A valid active code applies the configured percentage discount during checkout and is marked as used after successful payment.

## Main API Routes

| Route | Description |
| --- | --- |
| `/products/` | Product list and filters |
| `/categories/` | Product categories |
| `/carts/current/` | Current authenticated user cart |
| `/carts/<cart_id>/items/` | Add/update/delete cart items |
| `/orders/` | Checkout and order history |
| `/addresses/` | Customer address book |
| `/discounts/validate/` | Validate discount code |
| `/register/` | Register user |
| `/login/` | JWT login |
| `/profile/` | Current profile |
| `/profile/update/` | Update profile |

## Verification Performed

The Docker and application setup was checked with:

```bash
docker compose config
npm run build
.venv1/bin/python manage.py check
docker compose build
```

The following flows were also tested during development:

- Login with JWT
- User-specific cart access
- Blocking cross-user cart access
- Blocking checkout with missing/null/invalid address
- Successful checkout with complete profile, selected address, and discount code
- Frontend production build

## Notes

- Docker stores PostgreSQL data in the `postgres_data` volume.
- Uploaded media is stored in the `media_volume` volume.
- Collected Django static files are stored in the `static_volume` volume.
- Nginx serves React from `/` and proxies API/admin routes to Django.
- Do not commit production secrets. Use `.env.example` as a template and keep real secrets outside version control.
