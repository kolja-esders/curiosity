from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from lake.models import Rate, AskPrice, Heartbeat
from lake.lib.log import Log
from datetime import datetime, timedelta
from lxml import html
from botocore.exceptions import ClientError
import gdax
import time
import pytz
import http
import boto3

class Command(BaseCommand):
    ME = 'Notifier'
    CLIENT_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3205.0 Safari/537.36'}
    CLIENT_HEADER_ETH = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3205.0 Safari/537.36', 'x-requested-with': 'XMLHttpRequest'}
    BASE_URL = 'www.bitcoin.de'
    # Resource for asks
    BTC_OFFER_RESOURCE = '/de/btceur/home/reload-trades?type=offer'
    ETH_OFFER_RESOURCE = '/de/etheur/loadMarketOffers?type=offer'
    # Time between fetching orders
    SLEEP_TIME_SECS = 60
    # Critical volume needed for a trade to be valid
    CRITICAL_VOLUME_EUR = 5000.0
    # GDAX public client
    GDAX_CLIENT = gdax.PublicClient()
    # Threshold above which a notification should be send
    NOTIFICATION_THRESHOLD_PCT = 0.07
    NOTIFICATION_EMAIL_PAUSE_MIN = 30

    bitcoin_conn = None
    last_notification_email = None

    def __init__(self):
        self.email_client = boto3.client('ses', region_name='eu-west-1')
        self._sender = os.environ['NOTIFICATION_SENDER']
        self._recipient = os.environ['NOTIFICATION_RECIPIENT']
        self._charset = 'UTF-8'
        self.create_btc_conn()

    def handle(self, *args, **options):
        last_gdax_ask_btc = None
        last_gdax_ask_eth = None
        last_bitcoin_de_ask_btc = None
        while True:
            bitcoin_ask_btc = self.get_bitcoin_ask('BTC')
            if bitcoin_ask_btc is not None:
                bitcoin_ask_btc.save()
                last_bitcoin_de_ask_btc = bitcoin_ask_btc
                Log.info(self.ME, 'Fetched new ask: {}'.format(last_bitcoin_de_ask_btc))

            bitcoin_ask_eth = self.get_bitcoin_ask('ETH')
            if bitcoin_ask_eth is not None:
                bitcoin_ask_eth.save()
                last_bitcoin_de_ask_eth = bitcoin_ask_eth
                Log.info(self.ME, 'Fetched new ask: {}'.format(last_bitcoin_de_ask_eth))

            gdax_ask_btc = self.get_gdax_ask('BTC-EUR')
            if gdax_ask_btc is not None:
                gdax_ask_btc.save()
                last_gdax_ask_btc = gdax_ask_btc
                Log.info(self.ME, 'Fetched new ask: {}'.format(last_gdax_ask_btc))

            gdax_ask_eth = self.get_gdax_ask('ETH-EUR')
            if gdax_ask_eth is not None:
                gdax_ask_eth.save()
                last_gdax_ask_eth = gdax_ask_eth
                Log.info(self.ME, 'Fetched new ask: {}'.format(last_gdax_ask_eth))

            pct_profit = self.calc_profit_pct_btc(last_gdax_ask_btc, last_bitcoin_de_ask_btc)
            allowed_to_send_email = self.last_notification_email is None or (datetime.now() - self.last_notification_email).seconds // 60 > self.NOTIFICATION_EMAIL_PAUSE_MIN

            if pct_profit > self.NOTIFICATION_THRESHOLD_PCT and allowed_to_send_email:
                success = self.send_notification_email(last_gdax_ask_btc, last_bitcoin_de_ask_btc, pct_profit)
                if success:
                    self.last_notification_email = datetime.now()

            # TODO: Fix. Should really fire every minute and not sleep for 60s.
            self.heartbeat()
            time.sleep(60)

        return 0

    def heartbeat(self):
        hb, created = Heartbeat.objects.get_or_create(origin='chasqui')
        hb.last_beat_at = timezone.now()
        hb.save()

    def get_gdax_ask(self, pair):
        try:
            gdax_order_book = self.GDAX_CLIENT.get_product_order_book(pair, level=1)
            return self.parse_gdax_order_book(gdax_order_book, pair)
        except Exception as e:
            Log.warn(self.ME, 'Unable to fetch new ask from gdax.com: {}'.format(e))

        return None

    def create_btc_conn(self):
        if self.bitcoin_conn:
            self.bitcoin_conn.close()
        self.bitcoin_conn = http.client.HTTPSConnection(self.BASE_URL)

    def get_bitcoin_ask(self, coin):
        try:
            if coin == 'BTC':
                self.bitcoin_conn.request('GET', self.BTC_OFFER_RESOURCE, None, self.CLIENT_HEADER)
                resp = self.bitcoin_conn.getresponse()
                if resp.status == 200:
                    asks = html.fragments_fromstring(resp.read())
                    for a in asks:
                        ask = self.parse_ask_btc(a)
                        if (self.valid(ask)):
                            return ask
                else:
                    Log.warn(self.ME, 'Unable to fetch new ask from bitcoin.de: [status={}, reason={}]'.format(resp.status, resp.reason))
            elif coin == 'ETH':
                self.bitcoin_conn.request('GET', self.ETH_OFFER_RESOURCE, None, self.CLIENT_HEADER_ETH)
                resp = self.bitcoin_conn.getresponse()
                if resp.status == 200:
                    asks = html.fragments_fromstring(resp.read())
                    for a in asks:
                        ask = self.parse_ask_eth(a)
                        if (self.valid(ask)):
                            return ask
                else:
                    Log.warn(self.ME, 'Unable to fetch new ask from bitcoin.de: [status={}, reason={}]'.format(resp.status, resp.reason))
        except Exception as e:
            Log.warn(self.ME, 'Unable to fetch new ask from bitcoin.de: {}'.format(e))
            self.create_btc_conn()

        return None

    def calc_profit_pct_btc(self, gdax, bitcoin_de):
        TRANSACTION_COST = 15
        SEPA_FEE_GDAX = 0.15
        MARKET_FEE_BITCOIN_DE = 0.004
        raw_arbitrage = gdax.price_per_unit_eur - bitcoin_de.price_per_unit_eur - TRANSACTION_COST - SEPA_FEE_GDAX
        pct = raw_arbitrage / bitcoin_de.price_per_unit_eur

        return pct - MARKET_FEE_BITCOIN_DE

    def calc_profit_pct_eth(self, gdax, bitcoin_de):
        TRANSACTION_COST = 2
        SEPA_FEE_GDAX = 0.15
        MARKET_FEE_BITCOIN_DE = 0.004
        raw_arbitrage = gdax.price_per_unit_eur - bitcoin_de.price_per_unit_eur - TRANSACTION_COST - SEPA_FEE_GDAX
        pct = raw_arbitrage / bitcoin_de.price_per_unit_eur

        return pct - MARKET_FEE_BITCOIN_DE

    def valid(self, ask):
        # return ask.volume_eur >= self.CRITICAL_VOLUME_EUR
        return ask.is_express;

    def parse_ask_eth(self, a):
        ask = AskPrice()
        ask.platform = 'bitcoin.de'
        ask.trading_pair = 'ETH-EUR'
        ask.time = datetime.now().replace(tzinfo=pytz.utc, microsecond=0, second=0)
        ask.is_express = len(a.cssselect('img[data-express]')) > 0
        ask.price_per_unit_eur = float(a.get('data-critical-price'))
        ask.volume = float(a.get('data-amount'))
        ask.volume_eur = round(ask.volume * ask.price_per_unit_eur, 2)
        return ask

    def parse_ask_btc(self, a):
        ask = AskPrice()
        ask.platform = 'bitcoin.de'
        ask.trading_pair = 'BTC-EUR'
        ask.time = datetime.now().replace(tzinfo=pytz.utc, microsecond=0, second=0)
        ask.is_express = len(a.cssselect('img[data-express]')) > 0
        ask.price_per_unit_eur = float(a.get('data-critical-price'))
        ask.volume = float(a.get('data-critical-amount'))
        ask.volume_eur = round(ask.volume * ask.price_per_unit_eur, 2)
        return ask

    def parse_gdax_order_book(self, ob, pair):
        ask = AskPrice()
        ask.platform = 'gdax'
        ask.trading_pair = pair
        ask.time = datetime.now().replace(tzinfo=pytz.utc, microsecond=0, second=0)
        ask.price_per_unit_eur = float(ob['asks'][0][0])
        ask.volume = float(ob['asks'][0][1])
        ask.volume_eur = round(ask.volume * ask.price_per_unit_eur, 2)
        return ask

    def send_notification_email(self, gdax, bitcoin_de, profit_pct):
        try:
            email = EmailBuilder.build_notification_email(gdax, bitcoin_de, profit_pct)
            response = self.email_client.send_email(
                Destination={
                    'ToAddresses': [
                        self._recipient,
                    ],
                },
                Message={
                    'Body': {
                        'Text': {
                            'Charset': self._charset,
                            'Data': email['text']
                        },
                    },
                    'Subject': {
                        'Charset': self._charset,
                        'Data': email['subject']
                    },
                },
                Source=self._sender,
            )
            Log.info(self.ME, 'Just sent a notification email. Profit: {} %.'.format(profit_pct))
        except Exception as e:
            Log.error(self.ME, 'Unable to send notification email: {}'.format(e))
            return False

        return True

class EmailBuilder:

    @staticmethod
    def build_notification_email(gdax, bitcoin_de, profit_pct):
        pct = round(profit_pct * 100, 2)

        email = {
            'subject': 'Curiosity notification: {}€ -> {}€ ({}%)'.format(bitcoin_de.price_per_unit_eur, gdax.price_per_unit_eur, pct),
            'text': ''
        }

        return email

