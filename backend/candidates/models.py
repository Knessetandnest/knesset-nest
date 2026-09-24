from django.db import models

class Candidate(models.Model):
    STATUS_CHOICES=[('NEW','NEW'),('RESUME_REVIEWED','RESUME REVIEWED'),('CONTACTED','CONTACTED'),('INTERVIEW','INTERVIEW'),('REFERRED','REFERRED'),('SELECTED','SELECTED'),('JOINED','JOINED')]
    registration_id=models.CharField(max_length=30,unique=True,editable=False)
    full_name=models.CharField(max_length=150)
    phone=models.CharField(max_length=30)
    email=models.EmailField(blank=True)
    current_location=models.CharField(max_length=150)
    highest_qualification=models.CharField(max_length=150)
    experience=models.CharField(max_length=100)
    key_skills=models.TextField()
    preferred_role=models.CharField(max_length=150)
    preferred_work_location=models.CharField(max_length=150,blank=True)
    expected_salary=models.CharField(max_length=100,blank=True)
    status=models.CharField(max_length=30,choices=STATUS_CHOICES,default='NEW')
    consent=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-created_at']
        indexes=[
            models.Index(fields=['status','created_at'], name='cand_status_created_idx'),
            models.Index(fields=['phone'], name='cand_phone_idx'),
            models.Index(fields=['current_location'], name='cand_location_idx'),
        ]

class Resume(models.Model):
    candidate=models.OneToOneField(Candidate,on_delete=models.CASCADE,related_name='resume')
    file=models.FileField(upload_to='resumes/%Y/%m/')
    original_name=models.CharField(max_length=255)
    uploaded_at=models.DateTimeField(auto_now_add=True)

class CandidateNote(models.Model):
    candidate=models.ForeignKey(Candidate,on_delete=models.CASCADE,related_name='notes')
    note=models.TextField()
    created_by=models.CharField(max_length=150,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']

class Interview(models.Model):
    candidate=models.ForeignKey(Candidate,on_delete=models.CASCADE,related_name='interviews')
    scheduled_at=models.DateTimeField(null=True,blank=True)
    employer=models.CharField(max_length=200,blank=True)
    notes=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

class Referral(models.Model):
    candidate=models.ForeignKey(Candidate,on_delete=models.CASCADE,related_name='referrals')
    employer=models.CharField(max_length=200)
    role=models.CharField(max_length=200,blank=True)
    notes=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

class Placement(models.Model):
    candidate=models.OneToOneField(Candidate,on_delete=models.CASCADE,related_name='placement')
    employer=models.CharField(max_length=200)
    role=models.CharField(max_length=200,blank=True)
    joined_on=models.DateField(null=True,blank=True)
    notes=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
