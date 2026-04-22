from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("yookassa_integration", "0003_invoice_project_integration"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="comment",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="contact_phone",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name="invoice",
            name="onec_payment_document_id",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="invoice",
            name="service_id",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
