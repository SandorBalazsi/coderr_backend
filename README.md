# Coderr Backend (Django + DRF)
Minimal Django REST backend scaffold wiring basic auth, offers, orders, and reviews.

Quick start

1. Create and activate a Python virtual environment, then install requirements:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

2. Run migrations and (optionally) create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

3. Run the development server:

```bash
python manage.py runserver
```

Run tests:

```bash
python manage.py test
```

API (high level)

- `POST /api/auth/register/` — register a new user (returns token)
- `POST /api/auth/login/` — obtain auth token
- `GET /api/offers/` — list offers (supports search, ordering and filters)
- `POST /api/offers/` — create an offer (authenticated)
- `GET /api/offers/{id}/` — retrieve offer detail
- `PUT/PATCH /api/offers/{id}/` — update offer (authenticated)
- `DELETE /api/offers/{id}/` — delete offer (authenticated)
- `GET /api/offerdetails/` — list offer detail tiers
- `POST /api/orders/` — create an order (authenticated)
- `GET/PUT/PATCH/DELETE /api/orders/{id}/` — order CRUD (permissions apply)
- `POST /api/reviews/` — create a review (authenticated, customer users)

Notes

- Token authentication is used for the auth endpoints; created tokens are returned
	on register/login.
- Some endpoints enforce custom permissions (e.g. business vs customer users).
- See the `auth_app` and `marketplace_app` modules for models, serializers,
	views and permission behavior.

If you'd like, I can also add example curl requests for the auth flow or commit
these README changes.  
