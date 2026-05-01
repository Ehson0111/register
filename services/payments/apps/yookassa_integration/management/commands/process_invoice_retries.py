import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from ...invoice_sync_v2 import retry_due_invoice_sync
from ...models import Invoice


class Command(BaseCommand):
    help = "Processes pending 1C invoice/payment retries."

    def add_arguments(self, parser):
        parser.add_argument(
            "--loop",
            action="store_true",
            help="Keep polling for due retries instead of running once.",
        )

    def handle(self, *args, **options):
        loop = options["loop"]
        interval = settings.INVOICE_RETRY_WORKER_INTERVAL_SECONDS

        while True:
            processed = self._process_due_invoices()
            if not loop:
                self.stdout.write(self.style.SUCCESS(f"Processed {processed} invoice(s)."))
                return

            self.stdout.write(f"[{timezone.now().isoformat()}] processed {processed} invoice(s)")
            time.sleep(interval)

    def _process_due_invoices(self):
        now = timezone.now()
        invoices = Invoice.objects.filter(
            onec_sync_status=Invoice.SyncStatus.ERROR,
            next_retry_at__isnull=False,
            next_retry_at__lte=now,
        ).order_by("next_retry_at", "id")

        processed = 0
        for invoice in invoices:
            try:
                retry_due_invoice_sync(invoice)
                processed += 1
            except Exception as exc:
                invoice.mark_retry(error_text=str(exc), onec=True)
                invoice.save()
        return processed
