import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from django.core.checks import run_checks
errors=run_checks()
for e in errors:
    print(f'{e.id}: {e.msg}')
raise SystemExit(1 if errors else 0)
