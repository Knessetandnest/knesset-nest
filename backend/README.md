# Knesset & Nest Foundation - Django Backend

Django REST Framework backend replacing the original Express backend.

## Run locally

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:5000
```

The API is available at `http://localhost:5000/api/` and Django admin at `/admin/`.

## PostgreSQL

Set `DATABASE_URL`, for example:

`postgresql://postgres:postgres@localhost:5432/knesset_nest`

## API

- `GET /api/health/`
- `GET /api/info/`
- `POST /api/registrations/` multipart form with candidate fields and `resume`
- `GET /api/registrations/<registration_id>/`
- `GET /api/candidates/`
- `GET/PATCH /api/candidates/<id>/`
- `GET/POST /api/candidates/<id>/interviews/`
- `GET/POST /api/candidates/<id>/referrals/`
- `POST /api/candidates/<id>/placements/`

Resume files are stored under Django `MEDIA_ROOT`. In production, use private object storage and protected download endpoints rather than exposing media files publicly.


## Security checklist

For production set a strong `DJANGO_SECRET_KEY`, `DEBUG=False`, explicit `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and HTTPS with `SECURE_COOKIES=True`. Use private object storage or protected download endpoints for resumes. Staff endpoints require Django staff authentication and CSRF protection. Public registration-status lookup returns only registration ID and status.

## Tests

Run `python manage.py test`.
