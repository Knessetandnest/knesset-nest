from django.urls import path
from .views import register, registration_status, CandidateList, CandidateDetail, CandidateNotes, InterviewListCreate, ReferralListCreate, PlacementCreate, staff_dashboard, resume_download, audit_activity
urlpatterns=[
 path('registrations/',register), path('registrations/<str:registration_id>/',registration_status),
 path('staff/dashboard/',staff_dashboard), path('staff/activity/',audit_activity),
 path('candidates/',CandidateList.as_view()), path('candidates/<int:pk>/',CandidateDetail.as_view()),
 path('candidates/<int:candidate_id>/resume/',resume_download), path('candidates/<int:candidate_id>/notes/',CandidateNotes.as_view()),
 path('candidates/<int:candidate_id>/interviews/',InterviewListCreate.as_view()), path('candidates/<int:candidate_id>/referrals/',ReferralListCreate.as_view()), path('candidates/<int:candidate_id>/placements/',PlacementCreate.as_view()),
]
