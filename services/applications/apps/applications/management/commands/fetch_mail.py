from django.conf import settings
from django.core.management.base import BaseCommand

from apps.applications.email_parser import YandexMailParser


class Command(BaseCommand):
    help = "Fetch applications from Yandex Mail via IMAP"

    def handle(self, *args, **options):
        parser = YandexMailParser(
            settings.YANDEX_EMAIL,
            settings.YANDEX_PASSWORD,
            imap_host=getattr(settings, 'YANDEX_IMAP_HOST', 'imap.yandex.ru'),
            target_sender=getattr(settings, 'YANDEX_TARGET_SENDER', None),
        )
        result = parser.parse_and_save()
        if 'error' in result:
            self.stderr.write(self.style.ERROR(str(result)))
            return
        self.stdout.write(self.style.SUCCESS(str(result)))

# self.stderr	Стандартный поток ошибок (stderr)