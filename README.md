# nobitexv2
## install (نصب)
```bash
pip install nobitexv2
```
## example usage (استفاده نمونه)
نمونه استفاده از nobitexv2. اسکریپتی که روزانه با استفاده از moving average سفارشتان market خرید و فروش میذارد.(بازار BTCUSDT)
```python
import time
import requests
from datetime import datetime,timedelta
from nobitexv2 import NobitexV2

nv2=NobitexV2(requests.Session()) # توکن رو از environment variables 'NOBITEX_TOKEN' میگیره

while True:
    # BTCUSDT OHLCV data
    history=nv2.market_udf_history(to=time.time(),
                            from_=(datetime.now()-timedelta(days=10)).timestamp(), # 10 days before
                            symbol='BTCUSDT',
                            resolution='D')
    # closing prices (oldest0 to news)
    closingprices=history['c']
    # last trade price
    last_trade_price=float(nv2.orderbook('BTCUSDT')['lastTradePrice'])
    print("BTCUSDT last trade price:",last_trade_price)
    # select usdt wallet from wallets
    usdt_wallet=[wallet for wallet in nv2.wallets_list()['wallets'] if wallet['currency']=='usdt'][0]
    # usdt balance available to trade
    usdt_balance=float(usdt_wallet['balance'])-float(usdt_wallet['blockedBalance'])
    print("usdt balance available to trade:",usdt_balance)
    if usdt_balance<5.1:
        print('balance less than minimum trade requirement')
        break
    # SMA10 value
    mean=sum(closingprices)/len(closingprices)
    
    trade_amount=usdt_balance*0.5/last_trade_price # 50% of the usdt balance
    # market buy if current price is higher than SMA10
    if last_trade_price>mean:
        print(f"buying {trade_amount} btc")
        nv2.add_spot_order(
            type='buy',
            execution='market',
            srcCurrency='btc',
            dstCurrency='usdt',
            amount=trade_amount
        )
    else: # sell otherwise
        print(f"selling {trade_amount} btc")
        nv2.add_spot_order(
            type='sell',
            execution='market',
            srcCurrency='btc',
            dstCurrency='usdt',
            amount=trade_amount
        )
    
    # iterate after a day
    time.sleep(timedelta(days=1).total_seconds())
```
## implementation progress [nobitex docs](https://apidocs.nobitex.ir/)
مواردی که 🟩 گذاشته شده پیاده سازی شده اند. 🟧 ناقص. 🟥 پیاده سازی نشده
|بخش|وضیعت|
|---|---|
|اطلاعات بازار (عمومی) |🟩|
|اطلاعات کاربر  |🟧|
|معامله در بازار اسپات |🟩|
|معامله در بازار تعهدی |🟥|
|برداشت |🟥|
|وب‌سوکت (آزمایشی)|🟥|
|دفتر آدرس و حالت برداشت امن|🟥|
|امنیت|🟥|
|احراز هویت|🟥|
|سود و زیان|🟥|
|طرح معرفی دوستان|🟥|
|سایر|🟥|