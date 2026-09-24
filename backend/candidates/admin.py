from django.contrib import admin
from .models import Candidate, Resume, Interview, Referral, Placement
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display=('registration_id','full_name','phone','preferred_role','status','created_at')
    search_fields=('registration_id','full_name','phone','email')
    list_filter=('status','created_at')
admin.site.register(Resume); admin.site.register(Interview); admin.site.register(Referral); admin.site.register(Placement)
