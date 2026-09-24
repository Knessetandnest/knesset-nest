from django.urls import path
from .views import health, info, csrf_token, staff_login, staff_logout, staff_me, public_jobs, staff_jobs, staff_job_detail

urlpatterns = [
    path("jobs/", public_jobs, name="public-jobs"),
    path("health/", health, name="health"),
    path("info/", info, name="info"),
    path("staff/csrf/", csrf_token, name="staff-csrf"),
    path("staff/login/", staff_login, name="staff-login"),
    path("staff/logout/", staff_logout, name="staff-logout"),
    path("staff/me/", staff_me, name="staff-me"),
    path("staff/jobs/", staff_jobs, name="staff-jobs"),
    path("staff/jobs/<int:job_id>/", staff_job_detail, name="staff-job-detail"),
]
