# Coderr Backend (Django + DRF)

Minimal Django REST backend scaffold wiring basic auth, offers, orders, and reviews.

Quick start

1. Create a Python virtualenv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run migrations and create superuser:

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

3. Run server:

```bash
python manage.py runserver
```

API endpoints
- `POST /api/auth/register/` — user registration (returns token)
- `POST /api/auth/login/` — obtain auth token
- `GET/POST /api/offers/` — list / create offers
- `GET/PUT/DELETE /api/offers/{id}/` — offer CRUD
- `POST /api/orders/` — create order
- `POST /api/reviews/` — create review

Extend per the provided checklist and endpoint docs.
# coderr_backend
