# Knesset & Nest Recruitment Platform — Production-Ready Foundation

This version keeps the working staff login, candidate registration, resume handling, live job publishing, candidate workflow and staff dashboard, while adding production-oriented infrastructure.

## What was upgraded
- PostgreSQL support with connection reuse and health checks.
- Redis-backed cache/session/throttling when `REDIS_URL` is configured.
- DRF anonymous/user API throttling.
- Cache-backed staff login rate limiting.
- Database indexes for high-volume candidate/job queries.
- Production static files via WhiteNoise.
- Optional S3-compatible object storage for resumes.
- Gunicorn production server.
- Docker Compose with PostgreSQL + Redis + Django.
- Configurable frontend API origin with `VITE_API_BASE_URL`.
- Secure cookie/HTTPS settings controlled by environment variables.
- Database health endpoint at `/api/health/`.

## Local development
### Backend
```powershell
cd backend
python manage.py migrate
python manage.py runserver 5000
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

## Production-like local stack
Requires Docker Desktop:
```powershell
cd backend
docker compose up --build
```
The Django API will be available at `http://localhost:5000`.

## PostgreSQL + Redis production checklist
Set these environment variables on the server:
- `DJANGO_SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `REDIS_URL`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`
- `SECURE_COOKIES=True` when serving through HTTPS

For resumes at scale, configure the optional S3-compatible variables in `backend/.env.example` rather than keeping user files on the application container.

## Staff login
Create or keep a staff user with:
```powershell
python manage.py createsuperuser
```
The existing staff login uses Django sessions and CSRF protection.

## Job opportunities
Staff can create jobs, save drafts, publish/unpublish, edit, and delete. Publishing changes the stored record's `is_published` flag; it does not erase the job.

## Important scaling note
This project is production-oriented, but no software stack can promise a specific number of simultaneous users without load testing against the actual server/database/storage sizes. Before a high-traffic launch, run load tests and monitor PostgreSQL, Redis, API latency, errors and storage.
