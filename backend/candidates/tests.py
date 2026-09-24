from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Candidate

class RecruitmentTests(TestCase):
    def setUp(self):
        self.client=APIClient()
        self.staff=get_user_model().objects.create_user(username='staff',password='StrongPassword123!',is_staff=True)
        self.candidate=Candidate.objects.create(registration_id='KN-2026-00001',full_name='Test Candidate',phone='9999999999',email='candidate@example.com',current_location='Hosur',highest_qualification='Degree',experience='Fresher',key_skills='Python',preferred_role='Developer',consent=True)
    def staff_login(self):
        self.client.force_authenticate(user=self.staff)
    def test_public_status_is_private(self):
        r=self.client.get('/api/registrations/KN-2026-00001/'); self.assertEqual(r.status_code,200); self.assertNotIn('full_name',r.json())
    def test_candidate_list_requires_staff(self): self.assertEqual(self.client.get('/api/candidates/').status_code,401)
    def test_registration_accepts_valid_resume(self):
        f=SimpleUploadedFile('resume.pdf',b'%PDF-1.4 test',content_type='application/pdf')
        r=self.client.post('/api/registrations/',{'full_name':'New Candidate','phone':'8888888888','current_location':'Bengaluru','highest_qualification':'Degree','experience':'1 year','key_skills':'Django','preferred_role':'Backend Developer','consent':'true','resume':f},format='multipart')
        self.assertEqual(r.status_code,201)
    def test_staff_can_filter_and_update_candidate(self):
        self.staff_login(); r=self.client.get('/api/candidates/?q=Test'); self.assertEqual(r.status_code,200); self.assertEqual(len(r.json()),1)
        r=self.client.patch(f'/api/candidates/{self.candidate.id}/',{'status':'INTERVIEW'},format='json'); self.assertEqual(r.status_code,200); self.assertEqual(r.json()['status'],'INTERVIEW')
    def test_resume_download_requires_staff(self):
        self.assertEqual(self.client.get(f'/api/candidates/{self.candidate.id}/resume/').status_code,404)
