from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "registration_id", "created_at")
    search_fields = ("action", "registration_id")
    list_filter = ("action", "created_at")
    readonly_fields = ("action", "registration_id", "details", "created_at")


from .models import JobOpportunity

@admin.register(JobOpportunity)
class JobOpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "is_published", "closing_date", "updated_at")
    list_filter = ("is_published", "employment_type", "location")
    search_fields = ("title", "company", "location", "description")
    list_editable = ("is_published",)
