from django.db import migrations, models
class Migration(migrations.Migration):
    initial=True
    dependencies=[]
    operations=[migrations.CreateModel(name='AuditLog',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('action',models.CharField(max_length=120)),('registration_id',models.CharField(blank=True,max_length=40)),('details',models.JSONField(blank=True,default=dict)),('created_at',models.DateTimeField(auto_now_add=True))],options={'ordering':['-created_at']})]
