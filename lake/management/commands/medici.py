from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from lake.models import Heartbeat
from lake.lib.bank_client import BankClient
import time

class Command(BaseCommand):
    client = None

    def __init__(self):
        self.client = BankClient()

    def handle(self, *args, **options):
        self.client.login()
        self.client.fetch_most_recent_transaction()

        while True:
            self.heartbeat()
            time.sleep(60 * 5)
            self.client.update_transactions()

    def heartbeat(self):
        hb, created = Heartbeat.objects.get_or_create(origin='medici')
        hb.last_beat_at = timezone.now()
        hb.save()
