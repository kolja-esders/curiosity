from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from lake.models import Rate
from datetime import datetime, timedelta
from math import ceil
import gdax
import time
import pytz

GDAX_KEY = 'XXX'
GDAX_B64SECRET = 'XXX'
GDAX_PASSPHRASE = 'XXX'

class Command(BaseCommand):
    client = gdax.AuthenticatedClient(GDAX_KEY, GDAX_B64SECRET, GDAX_PASSPHRASE)

    def handle(self, *args, **options):
        return 0
