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
    # Fetch 200 minutes worth of candles
    MAX_REQUEST_CHUNK = 200
    # One minute granularity
    GRANULARITY = 60
    # Trading pari
    TRADING_PAIR = 'BTC-EUR'
    # Time delta as a datetime entity
    TIME_DELTA = timedelta(minutes=MAX_REQUEST_CHUNK)
    # Sleep in seconds when encountering a rate limit
    TIMEOUT = 10
    LOCAL_TIMEZONE = pytz.timezone("Europe/Berlin")

    def add_arguments(self, parser):
        parser.add_argument('days', type=int)

    def handle(self, *args, **options):
        if 'days' not in options:
            return -1

        minutes_to_fetch = options['days'] * 24 * 60
        num_chunks = ceil(minutes_to_fetch / self.MAX_REQUEST_CHUNK)
        current_time = datetime.now()

        i = 0
        while i < num_chunks:
            # current_time.microsecond = 0
            start = (current_time - (i + 1) * self.TIME_DELTA).replace(microsecond=0, second=0)
            end = (current_time - i * self.TIME_DELTA).replace(microsecond=0, second=0)

            print('start: ', start.isoformat())
            print('end: ', end.isoformat())

            # while True:
            result = self.client.get_product_historic_rates(self.TRADING_PAIR, start=start.isoformat(), end=end.isoformat(), granularity=self.GRANULARITY)
            print('Received', len(result), 'results')
            if len(result) > 1:
                for r in result:
                    try:
                        r = self.parse_rate(r)
                        r.save()
                    except Exception as e:
                        print(e)
                i += 1
            else:
                time.sleep(self.TIMEOUT)

        self.stdout.write(self.style.SUCCESS('Successfully fetched all rates'))
        return 0

    def parse_rate(self, r):
        rate = Rate()
        rate.platform = 'gdax'

        utc_dt = datetime.utcfromtimestamp(r[0]).replace(tzinfo=pytz.utc)
        rate.time = self.LOCAL_TIMEZONE.normalize(utc_dt.astimezone(self.LOCAL_TIMEZONE))

        rate.high = r[1]
        rate.low = r[2]
        rate.open = r[3]
        rate.close = r[4]
        rate.volume_btc = r[5]
        return rate
