# Production deployment checklist

## 1. PostgreSQL
Use a managed PostgreSQL service. Create a database and keep its connection string in `DATABASE_URL`.

## 2. Redis
Use a managed Redis service. Put its connection URL in `REDIS_URL`. Redis is used for caching, throttling and session acceleration.

## 3. Django API
Set:
- `DEBUG=False`
- a strong `DJANGO_SECRET_KEY`
- production `ALLOWED_HOSTS`
- production `CORS_ALLOWED_ORIGINS`
- production `CSRF_TRUSTED_ORIGINS`
- `SECURE_COOKIES=True` behind HTTPS
- `COOKIE_SAMESITE=None` when the frontend and API are on different sites/origins; keep HTTPS enabled in that configuration.
- `DATABASE_URL`
- `REDIS_URL`

Run:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:5000 --workers 3 --threads 2 --timeout 60
```
Adjust worker count after load testing based on CPU/RAM.

## 4. Resume storage
For multiple API instances, configure the optional S3-compatible variables. Do not rely on local container disk for production resumes.

## 5. Frontend
Build the React app and deploy its `dist` directory to a CDN/static host. If the API is on another origin, set `VITE_API_BASE_URL` before building.

## 6. HTTPS
Terminate TLS at your platform/load balancer and keep secure cookies enabled.

## 7. Backups and monitoring
Enable automated PostgreSQL backups, Redis monitoring, application logs, uptime checks and error tracking.

## 8. Capacity testing
Before a high-traffic launch, load-test login, public jobs, registration and staff dashboard separately. Scale the API horizontally only after verifying database connection limits and query latency.
