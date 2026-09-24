from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parent
required = [
    "manage.py", "requirements.txt", "config/settings.py", "config/urls.py",
    "core/views.py", "core/models.py", "candidates/views.py", "candidates/models.py",
    "candidates/migrations/0001_initial.py", "candidates/migrations/0002_candidate_note.py",
    "candidates/migrations/0003_production_indexes.py", "core/migrations/0001_initial.py",
    "core/migrations/0002_jobopportunity.py", "core/migrations/0003_production_indexes.py",
]
missing = [p for p in required if not (ROOT / p).exists()]
if missing:
    raise SystemExit(f"Missing required files: {missing}")

for path in ROOT.rglob("*.py"):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

settings = (ROOT / "config/settings.py").read_text(encoding="utf-8")
for token in ["whitenoise.middleware.WhiteNoiseMiddleware", "CSRF_COOKIE_SAMESITE", "SESSION_COOKIE_SAMESITE", "CORS_ALLOW_CREDENTIALS=True"]:
    if token not in settings:
        raise SystemExit(f"Expected production setting missing: {token}")

frontend = ROOT.parent / "frontend/src/App.tsx"
source = frontend.read_text(encoding="utf-8")
for token in ["credentials:'include'", "X-CSRFToken", "/api/staff/csrf/", "/api/registrations/"]:
    if token not in source:
        raise SystemExit(f"Expected frontend integration missing: {token}")

print("Bundle source checks passed.")
