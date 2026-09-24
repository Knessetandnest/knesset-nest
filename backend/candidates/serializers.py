from django.urls import reverse
from rest_framework import serializers
from .models import Candidate, Resume, CandidateNote, Interview, Referral, Placement

class ResumeSerializer(serializers.ModelSerializer):
    class Meta: model=Resume; fields=['id','original_name','uploaded_at']

class CandidateSerializer(serializers.ModelSerializer):
    resume=ResumeSerializer(read_only=True)
    notes=serializers.SerializerMethodField()
    def get_notes(self,obj):
        return NoteSerializer(obj.notes.all(),many=True).data
    class Meta:
        model=Candidate
        fields=['id','registration_id','full_name','phone','email','current_location','highest_qualification','experience','key_skills','preferred_role','preferred_work_location','expected_salary','status','consent','created_at','updated_at','resume','notes']
        read_only_fields=['id','registration_id','created_at','updated_at']

class CandidateListSerializer(CandidateSerializer):
    class Meta(CandidateSerializer.Meta):
        fields=CandidateSerializer.Meta.fields

class RegistrationSerializer(serializers.ModelSerializer):
    resume=serializers.FileField(write_only=True,required=True)
    class Meta:
        model=Candidate
        fields=['full_name','phone','email','current_location','highest_qualification','experience','key_skills','preferred_role','preferred_work_location','expected_salary','consent','resume']
    def validate_consent(self,v):
        if not v: raise serializers.ValidationError('Consent is required.')
        return v
    def validate_resume(self,f):
        if f.size>5*1024*1024: raise serializers.ValidationError('Resume must be 5 MB or smaller.')
        if not f.name.lower().endswith(('.pdf','.doc','.docx')): raise serializers.ValidationError('Only PDF, DOC or DOCX files are allowed.')
        return f
    def create(self,validated_data):
        resume=validated_data.pop('resume')
        candidate=Candidate.objects.create(registration_id='TEMP',**validated_data)
        candidate.registration_id=f"KN-{candidate.created_at.year}-{candidate.id:05d}"
        candidate.save(update_fields=['registration_id'])
        Resume.objects.create(candidate=candidate,file=resume,original_name=resume.name)
        return candidate

class NoteSerializer(serializers.ModelSerializer):
    class Meta: model=CandidateNote; fields=['id','candidate','note','created_by','created_at']; read_only_fields=['id','candidate','created_by','created_at']
class InterviewSerializer(serializers.ModelSerializer):
    class Meta: model=Interview; fields='__all__'; read_only_fields=['id','created_at','candidate']
class ReferralSerializer(serializers.ModelSerializer):
    class Meta: model=Referral; fields='__all__'; read_only_fields=['id','created_at','candidate']
class PlacementSerializer(serializers.ModelSerializer):
    class Meta: model=Placement; fields='__all__'; read_only_fields=['id','created_at','candidate']
