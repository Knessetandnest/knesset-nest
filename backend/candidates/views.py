from django.http import FileResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_protect
from core.models import AuditLog
from .models import Candidate, Interview, Referral, Placement, CandidateNote
from .serializers import CandidateSerializer, RegistrationSerializer, InterviewSerializer, ReferralSerializer, PlacementSerializer, NoteSerializer

class StaffOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if not (user and user.is_authenticated and user.is_staff): return False
        if request.method in permissions.SAFE_METHODS or user.is_superuser: return True
        return not user.groups.filter(name='Recruitment Viewer').exists()

def log(request, action, candidate=None, details=None):
    AuditLog.objects.create(action=action, registration_id=candidate.registration_id if candidate else '', details={**(details or {}), 'staff': request.user.username if request.user.is_authenticated else ''})

class CandidateList(generics.ListAPIView):
    serializer_class=CandidateSerializer; permission_classes=[StaffOnly]
    def get_queryset(self):
        qs=Candidate.objects.select_related('resume').prefetch_related('notes').all()
        q=self.request.query_params.get('q','').strip(); status_value=self.request.query_params.get('status','').strip(); role=self.request.query_params.get('role','').strip(); location=self.request.query_params.get('location','').strip()
        if q: qs=qs.filter(Q(full_name__icontains=q)|Q(registration_id__icontains=q)|Q(phone__icontains=q)|Q(email__icontains=q)|Q(key_skills__icontains=q)|Q(preferred_role__icontains=q))
        if status_value: qs=qs.filter(status=status_value)
        if role: qs=qs.filter(preferred_role__icontains=role)
        if location: qs=qs.filter(current_location__icontains=location)
        return qs[:200]

class CandidateDetail(generics.RetrieveUpdateAPIView):
    queryset=Candidate.objects.all(); serializer_class=CandidateSerializer; permission_classes=[StaffOnly]
    def perform_update(self, serializer):
        old=self.get_object().status; obj=serializer.save()
        if old != obj.status: log(self.request,'STATUS_CHANGED',obj,{'from':old,'to':obj.status})

@csrf_protect
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@parser_classes([MultiPartParser,FormParser,JSONParser])
def register(request):
    s=RegistrationSerializer(data=request.data)
    if s.is_valid():
        c=s.save(); log(request,'CANDIDATE_REGISTERED',c); return Response({'success':True,'registrationId':c.registration_id,'message':'Registration received successfully.'},status=status.HTTP_201_CREATED)
    return Response({'success':False,'errors':s.errors},status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def registration_status(request, registration_id):
    c=get_object_or_404(Candidate,registration_id=registration_id.upper())
    return Response({'success':True,'registrationId':c.registration_id,'status':c.status})

class CandidateNotes(generics.ListCreateAPIView):
    serializer_class=NoteSerializer; permission_classes=[StaffOnly]
    def get_queryset(self): return CandidateNote.objects.filter(candidate_id=self.kwargs['candidate_id'])
    def perform_create(self,s):
        c=get_object_or_404(Candidate,id=self.kwargs['candidate_id']); obj=s.save(candidate=c,created_by=self.request.user.username); log(self.request,'NOTE_ADDED',c)

class InterviewListCreate(generics.ListCreateAPIView):
    serializer_class=InterviewSerializer; permission_classes=[StaffOnly]
    def get_queryset(self): return Interview.objects.filter(candidate_id=self.kwargs['candidate_id'])
    def perform_create(self,s):
        c=get_object_or_404(Candidate,id=self.kwargs['candidate_id']); s.save(candidate=c); log(self.request,'INTERVIEW_SCHEDULED',c)
class ReferralListCreate(generics.ListCreateAPIView):
    serializer_class=ReferralSerializer; permission_classes=[StaffOnly]
    def get_queryset(self): return Referral.objects.filter(candidate_id=self.kwargs['candidate_id'])
    def perform_create(self,s):
        c=get_object_or_404(Candidate,id=self.kwargs['candidate_id']); s.save(candidate=c); log(self.request,'REFERRAL_CREATED',c)
class PlacementCreate(generics.CreateAPIView):
    serializer_class=PlacementSerializer; permission_classes=[StaffOnly]
    def perform_create(self,s):
        c=get_object_or_404(Candidate,id=self.kwargs['candidate_id']); s.save(candidate=c); log(self.request,'PLACEMENT_CREATED',c)

@api_view(['GET'])
@permission_classes([StaffOnly])
def resume_download(request, candidate_id):
    c=get_object_or_404(Candidate,id=candidate_id)
    if not hasattr(c,'resume'): return Response({'detail':'Resume not found.'},status=404)
    return FileResponse(c.resume.file.open('rb'), as_attachment=True, filename=c.resume.original_name)

@api_view(['GET'])
@permission_classes([StaffOnly])
def staff_dashboard(request):
    counts={'candidates':Candidate.objects.count(),'new_resumes':Candidate.objects.filter(status='NEW').count(),'to_contact':Candidate.objects.filter(status='CONTACTED').count(),'interviews':Candidate.objects.filter(status='INTERVIEW').count(),'placements':Placement.objects.count(),'referrals':Referral.objects.count(),'selected':Candidate.objects.filter(status='SELECTED').count(),'joined':Candidate.objects.filter(status='JOINED').count()}
    pipeline={key:Candidate.objects.filter(status=key).count() for key,_ in Candidate.STATUS_CHOICES}
    recent=Candidate.objects.select_related('resume').prefetch_related('notes').all()[:20]
    roles=list(Candidate.objects.values_list('preferred_role',flat=True).distinct().order_by('preferred_role')[:100])
    locations=list(Candidate.objects.values_list('current_location',flat=True).distinct().order_by('current_location')[:100])
    return Response({'user':{'username':request.user.username,'name':request.user.get_full_name() or request.user.username,'role':('Admin' if request.user.is_superuser else 'Staff')},'counts':counts,'pipeline':pipeline,'recent':CandidateSerializer(recent,many=True).data,'roles':roles,'locations':locations})

@api_view(['GET'])
@permission_classes([StaffOnly])
def audit_activity(request):
    return Response([{'action':a.action,'registration_id':a.registration_id,'details':a.details,'created_at':a.created_at} for a in AuditLog.objects.all()[:50]])
