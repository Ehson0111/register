from django.db import migrations, models
import django.db.models.deletion


def seed_deal_stages(apps, schema_editor):
    Deal = apps.get_model("contacts", "Deal")
    DealStage = apps.get_model("contacts", "DealStage")
    defaults = [
        {"name": "Новая", "order": 10, "color": "#3b82f6", "is_default": True},
        {"name": "Квалификация", "order": 20, "color": "#8b5cf6", "is_default": False},
        {"name": "Переговоры", "order": 30, "color": "#f59e0b", "is_default": False},
        {"name": "Согласование", "order": 40, "color": "#06b6d4", "is_default": False},
        {"name": "Закрыто", "order": 50, "color": "#10b981", "is_default": False},
    ]
    for payload in defaults:
        DealStage.objects.get_or_create(name=payload["name"], defaults=payload)
    default_stage = DealStage.objects.filter(is_default=True).order_by("order", "id").first()
    if default_stage:
        Deal.objects.filter(stage__isnull=True).update(stage=default_stage)


class Migration(migrations.Migration):

    dependencies = [
        ("contacts", "0003_contactcompanydetails_contact_inn"),
    ]

    operations = [
        migrations.CreateModel(
            name="DealStage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="Stage Name")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Order")),
                ("color", models.CharField(default="#2563eb", max_length=20, verbose_name="Color")),
                ("is_default", models.BooleanField(default=False, verbose_name="Default Stage")),
            ],
            options={
                "verbose_name": "Deal Stage",
                "verbose_name_plural": "Deal Stages",
                "ordering": ["order", "id"],
            },
        ),
        migrations.AddField(
            model_name="deal",
            name="stage",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="deals",
                to="contacts.dealstage",
                verbose_name="Stage",
            ),
        ),
        migrations.RunPython(seed_deal_stages, migrations.RunPython.noop),
    ]
