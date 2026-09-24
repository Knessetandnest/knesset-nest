from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    dependencies=[('candidates','0001_initial')]
    operations=[migrations.CreateModel(name='CandidateNote',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('note',models.TextField()),('created_by',models.CharField(blank=True,max_length=150)),('created_at',models.DateTimeField(auto_now_add=True)),('candidate',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='notes',to='candidates.candidate'))],options={'ordering':['-created_at']})]
