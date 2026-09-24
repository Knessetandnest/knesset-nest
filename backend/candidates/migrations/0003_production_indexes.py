from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("candidates", "0002_candidate_note")]
    operations = [
        migrations.AddIndex(model_name="candidate", index=models.Index(fields=["status", "created_at"], name="cand_status_created_idx")),
        migrations.AddIndex(model_name="candidate", index=models.Index(fields=["phone"], name="cand_phone_idx")),
        migrations.AddIndex(model_name="candidate", index=models.Index(fields=["current_location"], name="cand_location_idx")),
    ]
