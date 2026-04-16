from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0002_applicationaudit"),
    ]

    operations = [
        migrations.CreateModel(
            name="MailboxEmail",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("external_id", models.CharField(max_length=255, unique=True, verbose_name="Внешний ID письма")),
                ("message_id", models.CharField(blank=True, default="", max_length=255, verbose_name="Message-ID")),
                ("subject", models.CharField(blank=True, default="", max_length=500, verbose_name="Тема")),
                ("sender_name", models.CharField(blank=True, default="", max_length=255, verbose_name="Имя отправителя")),
                ("sender_email", models.EmailField(blank=True, max_length=255, verbose_name="Email отправителя")),
                ("recipients", models.TextField(blank=True, default="", verbose_name="Получатели")),
                ("cc", models.TextField(blank=True, default="", verbose_name="Копия")),
                ("date", models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="Дата письма")),
                ("body_text", models.TextField(blank=True, default="", verbose_name="Текст письма")),
                ("body_html", models.TextField(blank=True, default="", verbose_name="HTML письма")),
                ("preview", models.TextField(blank=True, default="", verbose_name="Превью")),
                ("is_read", models.BooleanField(default=False, verbose_name="Прочитано")),
                ("is_important", models.BooleanField(default=False, verbose_name="Важное")),
                ("in_inbox", models.BooleanField(default=False, verbose_name="Во входящих")),
                ("in_sent", models.BooleanField(default=False, verbose_name="В отправленных")),
                ("in_trash", models.BooleanField(default=False, verbose_name="В корзине")),
                ("primary_folder", models.CharField(default="inbox", max_length=32, verbose_name="Основная папка")),
                ("raw_flags", models.JSONField(blank=True, default=list, verbose_name="IMAP flags")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Дата обновления")),
            ],
            options={
                "verbose_name": "Письмо",
                "verbose_name_plural": "Почта",
                "ordering": ["-date", "-id"],
            },
        ),
    ]
