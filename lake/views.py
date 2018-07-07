from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from .models import Rate, AskPrice, BankTransaction, Log, Heartbeat
from datetime import datetime, timedelta

def calc_profit_pct(btc_price, gdax_price):
    TRANSACTION_COST = 15
    SEPA_FEE_GDAX = 0.15
    MARKET_FEE_BITCOIN_DE = 0.004

    delta = gdax_price - btc_price
    raw_arbitrage = gdax_price - btc_price - TRANSACTION_COST - SEPA_FEE_GDAX
    pct = raw_arbitrage / btc_price

    return (pct - MARKET_FEE_BITCOIN_DE) * 100

def calc_profit_pct_eth(btc_price, gdax_price):
    TRANSACTION_COST = 2
    SEPA_FEE_GDAX = 0.15
    MARKET_FEE_BITCOIN_DE = 0.004
    raw_arbitrage = gdax_price - btc_price - TRANSACTION_COST - SEPA_FEE_GDAX
    pct = raw_arbitrage / btc_price

    return (pct - MARKET_FEE_BITCOIN_DE) * 100


def index(request):
    """
    View function for home page of site.
    """

    # Assets

    # last_transaction = BankTransaction.objects.filter(finished=True).last()
    # if last_transaction:
        # available = last_transaction.new_balance
    # else:
        # available = 0

    # on_sepa_result = BankTransaction.objects.filter(finished=False).aggregate(Sum('amount'))['amount__sum']
    # on_sepa = round(on_sepa_result, 2) if on_sepa_result else 0.0

    # Live BTC
    gdax_cur = AskPrice.objects.filter(platform='gdax', trading_pair='BTC-EUR').order_by('-id')[0]
    btc_cur = AskPrice.objects.filter(platform='bitcoin.de', trading_pair='BTC-EUR').order_by('-id')[0]
    gdax_cur_price = gdax_cur.price_per_unit_eur
    btc_cur_price = btc_cur.price_per_unit_eur

    delta = gdax_cur_price - btc_cur_price
    profit_pct = calc_profit_pct(btc_cur_price, gdax_cur_price)

    # Live ETH
    gdax_cur_eth = AskPrice.objects.filter(platform='gdax', trading_pair='ETH-EUR').order_by('-id')[0]
    btc_cur_eth = AskPrice.objects.filter(platform='bitcoin.de', trading_pair='ETH-EUR').order_by('-id')[0]
    gdax_cur_price_eth = gdax_cur_eth.price_per_unit_eur
    btc_cur_price_eth = btc_cur_eth.price_per_unit_eur

    delta_eth = gdax_cur_price_eth - btc_cur_price_eth
    profit_pct_eth = calc_profit_pct_eth(btc_cur_price_eth, gdax_cur_price_eth)

    # Intraday

    intraday_result = AskPrice.objects.raw("""
            SELECT a1.id, a2.id, a1.time AS time, a1.price_per_unit_eur AS gdax_price, a2.price_per_unit_eur AS btc_price FROM lake_askprice a1
            INNER JOIN lake_askprice a2
            WHERE a1.trading_pair = 'BTC-EUR' AND a2.trading_pair='BTC-EUR' AND a1.platform='gdax' AND a2.platform='bitcoin.de' AND a1.time = a2.time AND a1.time >= date('now')
            ORDER BY a1.time ASC;
            """
    )
    intra_gdax_asks = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': a.gdax_price} for a in intraday_result]
    intra_btc_asks = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': a.btc_price} for a in intraday_result]
    intra_profits_pct= [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': calc_profit_pct_eth(a.btc_price, a.gdax_price)} for a in intraday_result]


    intraday_result_eth = AskPrice.objects.raw("""
            SELECT a1.id, a2.id, a1.time AS time, a1.price_per_unit_eur AS gdax_price, a2.price_per_unit_eur AS btc_price FROM lake_askprice a1
            INNER JOIN lake_askprice a2
            WHERE a1.trading_pair = 'ETH-EUR' AND a2.trading_pair='ETH-EUR' AND a1.platform='gdax' AND a2.platform='bitcoin.de' AND a1.time = a2.time AND a1.time >= date('now')
            ORDER BY a1.time ASC;
            """
    )
    intra_gdax_asks_eth = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': a.gdax_price} for a in intraday_result_eth]
    intra_btc_asks_eth = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': a.btc_price} for a in intraday_result_eth]
    intra_profits_pct_eth = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': calc_profit_pct_eth(a.btc_price, a.gdax_price)} for a in intraday_result_eth]

    # BTC: All time

    result = AskPrice.objects.raw("""
            SELECT a1.id, a2.id, a1.time AS time, a1.price_per_unit_eur AS gdax_price, a2.price_per_unit_eur AS btc_price FROM lake_askprice a1
            INNER JOIN lake_askprice a2
            WHERE a1.trading_pair='BTC-EUR' AND a1.platform='gdax' AND a2.trading_pair='BTC-EUR' AND a2.platform='bitcoin.de' AND a1.time = a2.time
            GROUP BY strftime('%Y-%m-%dT%H', a1.time)
            ORDER BY a1.time ASC;
            """
    )
    gdax_asks = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': a.gdax_price} for a in result]
    btc_asks = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': a.btc_price} for a in result]
    deltas = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': a.gdax_price - a.btc_price} for a in result]
    profits_pct = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': calc_profit_pct(a.btc_price, a.gdax_price)} for a in result]

    # ETH: All time

    result = AskPrice.objects.raw("""
            SELECT a1.id, a2.id, a1.time AS time, a1.price_per_unit_eur AS gdax_price, a2.price_per_unit_eur AS btc_price FROM lake_askprice a1
            INNER JOIN lake_askprice a2
            WHERE a1.trading_pair='ETH-EUR' AND a1.platform='gdax' AND a2.trading_pair='ETH-EUR' AND a2.platform='bitcoin.de' AND a1.time = a2.time
            GROUP BY strftime('%Y-%m-%dT%H', a1.time)
            ORDER BY a1.time ASC;
            """
    )

    gdax_asks_eth = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': a.gdax_price} for a in result]
    btc_asks_eth = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': a.btc_price} for a in result]
    deltas_eth = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': a.gdax_price - a.btc_price} for a in result]
    profits_pct_eth = [{'x': a.time.strftime('%Y-%m-%dT%H:%M:00Z'), 'y': calc_profit_pct(a.btc_price, a.gdax_price)} for a in result]

    return render(
        request,
        'index.html',
        context={'gdax_asks': gdax_asks, 'btc_asks': btc_asks, 'gdax_asks_eth': gdax_asks_eth, 'btc_asks_eth': btc_asks_eth, 'gdax_cur_price': gdax_cur_price, 'btc_cur_price': btc_cur_price, 'delta': delta, 'profits_pct': profits_pct, 'profits_pct_eth': profits_pct_eth,  'profit_pct': profit_pct, 'deltas': deltas, 'deltas_eth': deltas_eth, 'intra_gdax_asks': intra_gdax_asks, 'intra_btc_asks': intra_btc_asks, 'intra_profits_pct': intra_profits_pct, 'btc_cur_price_eth': btc_cur_price_eth, 'gdax_cur_price_eth': gdax_cur_price_eth, 'profit_pct_eth': profit_pct_eth, 'delta_eth': delta_eth, 'intra_gdax_asks_eth': intra_gdax_asks_eth, 'intra_btc_asks_eth': intra_btc_asks_eth, 'intra_profits_pct_eth': intra_profits_pct_eth}
    )

def trade(request):
    return render(
        request,
        'trade.html',
        context={},
    )

def settings(request):
    return render(
        request,
        'settings.html',
        context={},
    )

def stats(request):
    return render(
        request,
        'stats.html',
        context={},
    )

def logs(request):
    min_chasqui_lvl = request.GET['chasqui_lvl'] if 'chasqui_lvl' in request.GET else 1
    min_medici_lvl = request.GET['medici_lvl'] if 'medici_lvl' in request.GET else 1

    try:
        chasqui_beat = Heartbeat.objects.get(origin='chasqui')
        chasqui_status = 'stopped' if (timezone.now() - chasqui_beat.last_beat_at) > timedelta(minutes=6) else 'running'
    except Heartbeat.DoesNotExist:
        chasqui_status = 'missing'

    try:
        medici_beat = Heartbeat.objects.get(origin='medici')
        medici_status = 'stopped' if (timezone.now() - medici_beat.last_beat_at) > timedelta(minutes=6) else 'running'
    except Heartbeat.DoesNotExist:
        medici_status = 'missing'

    medici_logs = Log.objects.filter(producer='BankClient', lvl_id__gte=min_medici_lvl).order_by('-id')[:10]
    chasqui_logs = Log.objects.filter(producer='Notifier', lvl_id__gte=min_chasqui_lvl).order_by('-id')[:10]

    return render(
        request,
        'logs.html',
        context={'medici_logs': medici_logs, 'chasqui_logs': chasqui_logs, 'chasqui_status': chasqui_status, 'medici_status': medici_status},
    )
