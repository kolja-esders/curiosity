from django.db import models
from django.utils import timezone
from datetime import date

class Rate(models.Model):
    platform = models.CharField(max_length=16)
    trading_pair = models.CharField(max_length=16, default='BTC-EUR')
    time = models.DateTimeField(db_index=True)
    high = models.FloatField()
    low = models.FloatField()
    open = models.FloatField()
    close = models.FloatField()
    volume_eur = models.FloatField(null=True)
    volume_btc = models.FloatField(null=True)
    volume = models.FloatField(default=0)

class AskPrice(models.Model):
    platform = models.CharField(max_length=16)
    trading_pair = models.CharField(max_length=16, default='BTC-EUR')
    time = models.DateTimeField(db_index=True)
    price_per_unit_eur = models.FloatField()
    volume_btc = models.FloatField(null=True)
    volume_eur = models.FloatField()
    min_volume_btc = models.FloatField(null=True)
    is_express = models.NullBooleanField(null=True)
    volume = models.FloatField(default=0)

    def __str__(self):
        return '[platform={}, pair={}, time={}, price={} €, volume={} €]'.format(self.platform, self.trading_pair, self.time.strftime("%d.%m.%Y %H:%M"), self.price_per_unit_eur, self.volume_eur)

class YubiKey(models.Model):
    value = models.CharField(max_length=50)
    used = models.BooleanField(default=False)

class TradeSession(models.Model):
    amount_eur = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

class Log(models.Model):
    producer = models.CharField(max_length=32)
    msg = models.CharField(max_length=256)
    lvl = models.CharField(max_length=16)
    lvl_id = models.IntegerField(default=1)
    trade_session = models.ForeignKey(TradeSession, null=True, on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(default=timezone.now)

class BankTransaction(models.Model):
    finished = models.BooleanField(default=False)
    amount = models.FloatField()
    desc = models.CharField(max_length=256, default='')
    new_balance = models.FloatField(null=True, default=None)
    unique = models.CharField(max_length=64, default='')
    arrived_on = models.DateField(default=date.today)

class Heartbeat(models.Model):
    origin = models.CharField(max_length=64)
    last_beat_at = models.DateTimeField(default=timezone.now)
