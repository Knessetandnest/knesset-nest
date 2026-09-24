from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help='Create standard staff groups for the recruitment console.'
    def handle(self,*args,**kwargs):
        roles={
            'Recruitment Viewer': ['view_candidate','view_resume','view_candidatenote','view_interview','view_referral','view_placement'],
            'Recruiter': ['view_candidate','add_candidatenote','view_candidatenote','add_interview','view_interview','add_referral','view_referral','add_placement','view_placement','change_candidate'],
            'Recruitment Manager': ['view_candidate','add_candidatenote','change_candidatenote','view_candidatenote','add_interview','change_interview','view_interview','add_referral','change_referral','view_referral','add_placement','change_placement','view_placement','change_candidate'],
        }
        for name,codenames in roles.items():
            group,_=Group.objects.get_or_create(name=name)
            perms=Permission.objects.filter(codename__in=codenames,content_type__app_label='candidates')
            group.permissions.set(perms)
            self.stdout.write(self.style.SUCCESS(f'{name}: {perms.count()} permissions'))
        self.stdout.write(self.style.SUCCESS('Staff roles are ready. Assign users to groups in Django admin.'))
