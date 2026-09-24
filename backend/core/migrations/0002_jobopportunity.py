from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [migrations.CreateModel(name='JobOpportunity', fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('title', models.CharField(max_length=180)), ('company', models.CharField(max_length=180)),
        ('location', models.CharField(max_length=180)), ('employment_type', models.CharField(default='Full-time', max_length=60)),
        ('salary', models.CharField(blank=True, max_length=100)), ('description', models.TextField()),
        ('requirements', models.TextField(blank=True)), ('apply_url', models.URLField(blank=True, help_text='Optional external application link')),
        ('contact_email', models.EmailField(blank=True, help_text='Optional email for applications', max_length=254)),
        ('is_published', models.BooleanField(default=False)), ('closing_date', models.DateField(blank=True, null=True)),
        ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
    ], options={'ordering': ['-created_at']})]
