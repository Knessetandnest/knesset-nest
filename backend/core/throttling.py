from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.crypto import salted_hmac


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "unknown")


def staff_login_rate_limit(max_attempts=8, window_seconds=300):
    """Small cache-backed guard for the staff login endpoint.

    Redis is recommended in production; Django's configured cache backend is used.
    """
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.method == "POST":
                username = ""
                try:
                    import json
                    username = str(json.loads(request.body or "{}").get("username", "")).strip().lower()
                except Exception:
                    pass
                raw = f"{_client_ip(request)}:{username}"
                key = "staff-login:" + salted_hmac("staff-login", raw).hexdigest()
                count = cache.get(key, 0)
                if count >= max_attempts:
                    return JsonResponse({"detail": "Too many login attempts. Please try again in a few minutes."}, status=429)
                cache.set(key, count + 1, window_seconds)
            response = view(request, *args, **kwargs)
            if response.status_code in (200, 201):
                cache.delete(key)
            return response
        return wrapped
    return decorator
