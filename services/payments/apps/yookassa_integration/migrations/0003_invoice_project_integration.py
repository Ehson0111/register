from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("yookassa_integration", "0002_invoice"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="contact_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="invoice",
            name="contact_id",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="contact_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="invoice",
            name="crm_retry_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="invoice",
            name="crm_sync_status",
            field=models.CharField(choices=[("pending", "Ожидает синхронизации"), ("synced", "Синхронизирован"), ("error", "Ошибка синхронизации")], default="pending", max_length=20),
        ),
        migrations.AddField(
            model_name="invoice",
            name="deal_id",
            field=models.PositiveIntegerField(default=0, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="invoice",
            name="deal_title",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="invoice",
            name="last_crm_error",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="last_onec_error",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="next_retry_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="onec_document_id",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="invoice",
            name="onec_invoice_number",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="invoice",
            name="onec_retry_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="invoice",
            name="onec_sync_status",
            field=models.CharField(choices=[("pending", "Ожидает синхронизации"), ("synced", "Синхронизирован"), ("error", "Ошибка синхронизации")], default="pending", max_length=20),
        ),
        migrations.AddField(
            model_name="invoice",
            name="pay_link_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="payment_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="service_name",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
