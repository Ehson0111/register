from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chatService", "0002_alter_chatmessage_sender_role_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatroom",
            name="is_ai",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="chatmessage",
            name="sender_role",
            field=models.CharField(
                choices=[
                    ("manager", "Manager"),
                    ("admin", "Admin"),
                    ("telegram_client", "Telegram Client"),
                    ("ai_assistant", "AI Assistant"),
                ],
                max_length=20,
            ),
        ),
    ]
