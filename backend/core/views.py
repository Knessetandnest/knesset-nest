import json
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods
from django.db import connection
from .throttling import staff_login_rate_limit
from .models import AuditLog

@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        database = "ok"
        status = "ok"
    except Exception:
        database = "error"
        status = "degraded"
    return JsonResponse({"service":"knesset-nest-recruitment-api","status":status,"backend":"django","database":database})

@require_GET
def info(request):
    return JsonResponse({"organization":"Knesset & Nest Foundation","website":"https://knessetandnest-web.web.app","phone":"9943471900","email":"knessetandnestfoundation@gmail.com","mode":"offline-recruitment"})

@ensure_csrf_cookie
@require_GET
def csrf_token(request):
    return JsonResponse({"csrfReady": True})

def _staff_role(user):
    if user.is_superuser: return "Admin"
    names=list(user.groups.values_list("name", flat=True))
    return names[0] if names else "Staff"

def _staff_payload(user):
    return {"authenticated": True, "username": user.username, "name": user.get_full_name() or user.username, "role": _staff_role(user)}

@require_GET
def staff_me(request):
    if request.user.is_authenticated and request.user.is_staff:
        return JsonResponse(_staff_payload(request.user))
    return JsonResponse({"authenticated": False}, status=401)

@csrf_protect
@staff_login_rate_limit()
@require_http_methods(["POST"])
def staff_login(request):
    try:
        data=json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail":"Invalid JSON."}, status=400)
    user=authenticate(request, username=str(data.get("username", "")).strip(), password=data.get("password", ""))
    if not user or not user.is_staff or not user.is_active:
        return JsonResponse({"detail":"Invalid staff username or password."}, status=401)
    login(request,user)
    return JsonResponse(_staff_payload(user))

@csrf_protect
@require_http_methods(["POST"])
def staff_logout(request):
    logout(request)
    return JsonResponse({"authenticated":False})



def _staff_only(request):
    return request.user.is_authenticated and request.user.is_staff and request.user.is_active

def _job_manager_only(request):
    user = request.user
    if not (user.is_authenticated and user.is_staff and user.is_active):
        return False
    return user.is_superuser or not user.groups.filter(name="Recruitment Viewer").exists()

def _job_payload(job):
    return {
        "id": job.id, "title": job.title, "company": job.company, "location": job.location,
        "employment_type": job.employment_type, "salary": job.salary, "description": job.description,
        "requirements": job.requirements, "apply_url": job.apply_url, "contact_email": job.contact_email,
        "is_published": job.is_published,
        "closing_date": job.closing_date.isoformat() if job.closing_date else None,
        "created_at": job.created_at.isoformat(), "updated_at": job.updated_at.isoformat(),
    }


@csrf_protect
@require_http_methods(["GET", "POST"])
def staff_jobs(request):
    from .models import JobOpportunity
    if not _staff_only(request):
        return JsonResponse({"detail": "Staff authentication required."}, status=403)
    if request.method == "GET":
        jobs = JobOpportunity.objects.all()
        return JsonResponse({"jobs": [_job_payload(j) for j in jobs]})
    if not _job_manager_only(request):
        return JsonResponse({"detail": "Job management permission required."}, status=403)
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON."}, status=400)
    required = ["title", "company", "location", "description"]
    if any(not str(data.get(k, "")).strip() for k in required):
        return JsonResponse({"detail": "Title, company, location and description are required."}, status=400)
    closing_date = None
    if data.get("closing_date"):
        try:
            closing_date = date.fromisoformat(str(data["closing_date"]))
        except ValueError:
            return JsonResponse({"detail": "Closing date must be YYYY-MM-DD."}, status=400)
    job = JobOpportunity.objects.create(
        title=str(data["title"]).strip()[:180], company=str(data["company"]).strip()[:180],
        location=str(data["location"]).strip()[:180], employment_type=str(data.get("employment_type") or "Full-time").strip()[:60],
        salary=str(data.get("salary") or "").strip()[:100], description=str(data["description"]).strip(),
        requirements=str(data.get("requirements") or "").strip(), apply_url=str(data.get("apply_url") or "").strip(),
        contact_email=str(data.get("contact_email") or "").strip(), is_published=bool(data.get("is_published", False)),
        closing_date=closing_date,
    )
    AuditLog.objects.create(action="JOB_CREATED", details={"job_id": job.id, "title": job.title, "staff": request.user.username})
    return JsonResponse({"job": _job_payload(job)}, status=201)


@csrf_protect
@require_http_methods(["PATCH", "DELETE"])
def staff_job_detail(request, job_id):
    from .models import JobOpportunity
    if not _staff_only(request):
        return JsonResponse({"detail": "Staff authentication required."}, status=403)
    if not _job_manager_only(request):
        return JsonResponse({"detail": "Job management permission required."}, status=403)
    try:
        job = JobOpportunity.objects.get(pk=job_id)
    except JobOpportunity.DoesNotExist:
        return JsonResponse({"detail": "Job opportunity not found."}, status=404)
    if request.method == "DELETE":
        title = job.title
        job.delete()
        AuditLog.objects.create(action="JOB_DELETED", details={"job_id": job_id, "title": title, "staff": request.user.username})
        return JsonResponse({"deleted": True})
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON."}, status=400)
    required = ["title", "company", "location", "description"]
    for field in required:
        if field in data and not str(data[field] or "").strip():
            return JsonResponse({"detail": f"{field.replace("_", " ").title()} cannot be empty."}, status=400)
    fields = ["title", "company", "location", "employment_type", "salary", "description", "requirements", "apply_url", "contact_email", "closing_date"]
    for field in fields:
        if field in data:
            if field == "closing_date":
                try:
                    value = date.fromisoformat(str(data[field])) if data[field] else None
                except ValueError:
                    return JsonResponse({"detail": "Closing date must be YYYY-MM-DD."}, status=400)
                setattr(job, field, value)
            else:
                setattr(job, field, str(data[field] or "").strip())
    if "is_published" in data:
        job.is_published = bool(data["is_published"])
    job.save()
    AuditLog.objects.create(action="JOB_UPDATED", details={"job_id": job.id, "title": job.title, "staff": request.user.username})
    return JsonResponse({"job": _job_payload(job)})


@require_GET
def public_jobs(request):
    from django.db.models import Q
    from django.utils import timezone
    from .models import JobOpportunity
    jobs = JobOpportunity.objects.filter(is_published=True).filter(
        Q(closing_date__isnull=True) | Q(closing_date__gte=timezone.localdate())
    )
    query = request.GET.get("q", "").strip()[:120]
    location = request.GET.get("location", "").strip()[:120]
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(company__icontains=query) | Q(description__icontains=query))
    if location:
        jobs = jobs.filter(location__icontains=location)
    return JsonResponse({"jobs": [{
        "id": j.id, "title": j.title, "company": j.company, "location": j.location,
        "employment_type": j.employment_type, "salary": j.salary, "description": j.description,
        "requirements": j.requirements, "apply_url": j.apply_url, "contact_email": j.contact_email,
        "closing_date": j.closing_date.isoformat() if j.closing_date else None,
        "updated_at": j.updated_at.isoformat()
    } for j in jobs[:100]]})
