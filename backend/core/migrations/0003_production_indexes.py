from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0002_jobopportunity")]
    operations = [
        migrations.AddIndex(model_name="jobopportunity", index=models.Index(fields=["is_published", "closing_date"], name="core_job_pub_close_idx")),
        migrations.AddIndex(model_name="jobopportunity", index=models.Index(fields=["company"], name="core_job_company_idx")),
    ]
