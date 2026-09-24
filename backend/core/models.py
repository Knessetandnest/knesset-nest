from django.db import models

class AuditLog(models.Model):
    action=models.CharField(max_length=120)
    registration_id=models.CharField(max_length=40,blank=True)
    details=models.JSONField(default=dict,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']


class JobOpportunity(models.Model):
    title = models.CharField(max_length=180)
    company = models.CharField(max_length=180)
    location = models.CharField(max_length=180)
    employment_type = models.CharField(max_length=60, default="Full-time")
    salary = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    apply_url = models.URLField(blank=True, help_text="Optional external application link")
    contact_email = models.EmailField(blank=True, help_text="Optional email for applications")
    is_published = models.BooleanField(default=False)
    closing_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_published", "closing_date"], name="core_job_pub_close_idx"),
            models.Index(fields=["company"], name="core_job_company_idx"),
        ]

    def __str__(self):
        return f"{self.title} — {self.company}"
