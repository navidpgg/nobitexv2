import requests
import urllib
from urllib.parse import urljoin
import os

def _remove_nones_dict(data: dict) -> dict:
    return {k: v for k, v in data.items() if v is not None}

def _join_urls(base_url, *paths):
    url = base_url
    for path in paths:
        url = urljoin(url.rstrip('/') + '/', path.lstrip('/'))
    return url

def _get_from_environment_variable(var_name):
    token = os.environ.get(var_name)
    if token is None:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
    return token

class NobitexV2:
    def __init__(self,
                 session:requests.Session,
                 token:str=None,
                 bot_name:str=None,
                 base_url='https://apiv2.nobitex.ir/',
                 test_token=True):
        """nobitex client

        Args:
            session (requests.Session): session
            token (str, optional): Nobitex token. If none tries to retreive it from the environment variables `NOBITEX_TOKEN` if this fails raises EnvironmentError. Defaults to None.
            bot_name (str, optional): Nobitex docs recommend setting this value. See https://apidocs.nobitex.ir/#intro-ua. Defaults to None.
            base_url (str, optional): base url. Defaults to 'https://apiv2.nobitex.ir/'.
            test_token (bool): if true makes a call to user_profile(). in case if the token is invalid raises requests.exceptions.HTTPError: 401 Client Error: Unauthorized for...
        """
        self.session = session
        token = _get_from_environment_variable("NOBITEX_TOKEN") if token is None else token
        self.session.headers.update({
            'Authorization': f"Token {token}",
        })
        if bot_name:
            self.session.headers.update({
                "User-Agent":f"TraderBot/{bot_name}"
            })
        self.base_url=base_url
        
        if test_token:
            self.user_profile() # gives 401 Unauthorized error if token is invalid
            
    #region public market info (no token required)
    def orderbook(self, symbol:str='BTCIRT'):
        """برای دریافت لیست سفارش‌ها یا همان اردربوک بازارهای مختلف، از این درخواست استفاده نمایید:
        https://apidocs.nobitex.ir/#orderbook-v3"""
        url=_join_urls(self.base_url,f'v3/orderbook/{symbol}')
        response=self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def orderbook_all(self):
        """ در صورت تمایل به دریافت لیست سفارشات همه بازارها به صورت یکجا از مقدار all برای symbol استفاده نمایید.
        
        https://apidocs.nobitex.ir/#orderbook-v3"""
        url=_join_urls(self.base_url,f'v3/orderbook/all')
        response=self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def depth(self, symbol:str='BTCUSDT'):
        """برای دریافت داده‌های نمودار عمق، یا همان اردربوک بازارهای مختلف، از این درخواست استفاده نمایید:
        
        https://apidocs.nobitex.ir/#54977c5fca"""
        url=_join_urls(self.base_url,f'/v2/depth/{symbol}')
        response=self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def trades(self,symbol:str='BCHIRT'):
        """برای دریافت لیست معاملات از این نوع درخواست استفاده نمایید:
        
        https://apidocs.nobitex.ir/#3fe8d57657"""
        url=_join_urls(self.base_url,f'/v2/trades/{symbol}')
        response=self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def market_stats(self, 
                     srcCurrency='btc',
                     dstCurrency='rls'):
        """برای دریافت آخرین آمار بازار نوبیتکس از این نوع درخواست استفاده نمایید:

        https://apidocs.nobitex.ir/#6ae2dae4a2"""
        url=_join_urls(self.base_url,'/market/stats')
        data=dict(srcCurrency=srcCurrency,dstCurrency=dstCurrency)
        data=_remove_nones_dict(data)
        response=self.session.get(url,data=data)
        response.raise_for_status()
        return response.json()
    
    def market_udf_history(self,
                           to:int,
                           from_:int,
                           symbol="BTCIRT",
                           resolution="D",
                           countback=None,
                           page=None):
        """برای دریافت آمار OHLC نوبیتکس از این نوع درخواست استفاده نمایید:
        
        https://apidocs.nobitex.ir/#ohlc"""
        url=_join_urls(self.base_url,'/market/udf/history')
        data=dict(to=int(to),symbol=symbol,resolution=resolution,countback=countback,page=page)
        data['from']=int(from_)
        data=_remove_nones_dict(data)
        query_string = urllib.parse.urlencode(data)
        full_url = url + '?' + query_string
        response=self.session.get(full_url)
        response.raise_for_status()
        return response.json()
    #endregion
    
    #region user info
    def user_profile(self):
        """این api، اطلاعات پروفایل شما، کارت بانکی، حساب بانکی، موارد تایید شده(ایمیل، شماره تلفن، موبایل ...)، تنظمیات مربوط به پروفایل(فی تراکنش، فی مبادلات usdt و ...) و خلاصه آمار مبادلات شما را برمیگرداند.
        
        https://apidocs.nobitex.ir/#user-profile"""
        url=_join_urls(self.base_url,'/users/profile')
        response=self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def create_address(self,
                       currency,
                       wallet=None,
                       network=None):
        """برای تولید آدرس بلاکچین از این نوع درخواست استفاده نمایید:
        
        https://apidocs.nobitex.ir/#87af031464"""
        url=_join_urls(self.base_url,'/users/wallets/generate-address')
        data=dict(currency=currency,wallet=wallet,network=network)
        data=_remove_nones_dict(data)
        response=self.session.post(url,data=data)
        response.raise_for_status()
        return response.json()
    
    def user_limitations(self):
        """کاربران در نوبیتکس بر اساس سطح کاربری خود، محدودیت هایی در برداشت، واریز و مبادلات خود دارند. هر کاربر نسبت به نیاز خود و میزان مبادلاتی که دارد میتواند با ارائه مدارک مورد نیاز ، سطح کاربری خود را پس از احراز هویت و تایید مدراک، ارتقا دهد. اطلاعات نمایش داده شده در خروجی api شامل همین محدودیت ها میباشد:
        
        https://apidocs.nobitex.ir/#e2ecdd60d4"""
        url=_join_urls(self.base_url,'/users/limitations')
        response=self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def balance(self,
                currency):
        """برای دریافت موجودی کیف پول های خود در نوبیتکس (شامل کیف پول ریالی و کیف پول های رمز ارزی) از این نوع درخواست استفاده نمایید:
        
        https://apidocs.nobitex.ir/#55645b2c6d"""
        url=_join_urls(self.base_url,'/users/wallets/balance')
        data=dict(currency=currency)
        response=self.session.post(url,data=data)
        response.raise_for_status()
        return response.json()

    def wallets_list(self):
        """https://apidocs.nobitex.ir/#1100025d2c"""
        url=_join_urls(self.base_url,'/users/wallets/list')
        response=self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def wallets_list_choice(self,
                            currencies:str,
                            type_):
        """https://apidocs.nobitex.ir/#1ff004071d"""
        url=_join_urls(self.base_url,'/v2/wallets')
        data=dict(currencies=currencies,type=type_)
        response=self.session.get(url,data=data)
        response.raise_for_status()
        return response.json()
    
    #endregion
    
    #region spot trade
    def add_spot_order(self,
                    type=None,
                    execution=None,
                    srcCurrency=None,
                    dstCurrency=None,
                    amount=None,
                    price=None):
        """ثبت سفارش الزاماً به معنی انجام معامله نیست و بسته به نوع و قیمت سفارش و وضعیت لحظه‌ای بازار ممکن است معامله انجام شود یا نشود. با درخواست «مشاهده وضعیت سفارش» می‌توانید از وضعیت سفارش خود مطلع شوید.
        
        https://apidocs.nobitex.ir/#e12b63a512"""
        url=_join_urls(self.base_url,'/market/orders/add')
        data=dict(type=type,srcCurrency=srcCurrency,dstCurrency=dstCurrency,amount=amount,price=price,execution=execution)
        data=_remove_nones_dict(data)
        response=self.session.post(url,data=data)
        response.raise_for_status()
        return response.json()
    
    def order_status(self,
                     id,
                     client_order_id=None):
        """برای دریافت وضعیت سفارش از این نوع درخواست استفاده نمایید:
        
        https://apidocs.nobitex.ir/#e12b63a512"""
        url=_join_urls(self.base_url,'/market/orders/status')
        data=dict(id=id,clientOrderId=client_order_id)
        data=_remove_nones_dict(data)
        response=self.session.post(url,data=data)
        response.raise_for_status()
        return response.json()
    
    def orders_list(self,
                    status=None,
                    type_=None,
                    execution=None,
                    tradeType=None,
                    srcCurrency=None,
                    dstCurrency=None,
                    details=None,
                    fromId=None,):
        """برای دریافت فهرست سفارش‌های خود، از این درخواست استفاده نمایید.
        
        https://apidocs.nobitex.ir/#a2ce8ff7e3"""
        url=_join_urls(self.base_url,'/market/orders/list')
        data=dict(status=status,
                  type=type_,
                  execution=execution,
                  tradeType=tradeType,
                  srcCurrency=srcCurrency,
                  dstCurrency=dstCurrency,
                  details=details,
                  fromId=fromId)
        data=_remove_nones_dict(data)
        response=self.session.post(url,data=data)
        response.raise_for_status()
        return response.json()
    
    def update_order_status(self,
                            order,
                            status):
        """برای تغییر وضعیت یک سفارش (لغو یا فعال‌سازی) از این نوع درخواست استفاده نمایید:
        
        https://apidocs.nobitex.ir/#4a50e713bf"""
        url=_join_urls(self.base_url,'/market/orders/update-status')
        data=dict(status=status,
                  order=order)
        data=_remove_nones_dict(data)
        response=self.session.post(url,data=data)
        response.raise_for_status()
        return response.json()
    
    def cancel_orders_status(self,
                             hours=None,
                             execution=None,
                             tradeType=None,
                             srcCurrency=None,
                             dstCurrency=None):
        """برای لغو دسته‌جمعی سفارشات فعال از این نوع درخواست استفاده نمایید:
        
        https://apidocs.nobitex.ir/#2a3bc4fdc6"""
        url=_join_urls(self.base_url,'/market/orders/cancel-old')
        data=dict(hours=hours,
                  execution=execution,
                  tradeType=tradeType,
                  srcCurrency=srcCurrency,
                  dstCurrency=dstCurrency)
        data=_remove_nones_dict(data)
        response=self.session.post(url,data=data)
        response.raise_for_status()
        return response.json()
    
    def trades_list(self,
                    srcCurrency=None,
                    dstCurrency=None,
                    fromId=None):
        """برای دریافت فهرست معاملات ۳ روز اخیر خود، از این درخواست استفاده نمایید.
        
        https://apidocs.nobitex.ir/#1cf6f6c643"""
        url=_join_urls(self.base_url,'/market/trades/list')
        data=dict(fromId=fromId,dstCurrency=dstCurrency,srcCurrency=srcCurrency)
        data=_remove_nones_dict(data)
        query_string = urllib.parse.urlencode(data)
        full_url = url + '?' + query_string
        response=self.session.get(full_url)
        response.raise_for_status()
        return response.json()
    #endregion

if __name__=="__main__":
    # exmaple usage
    
    import time
    from datetime import datetime,timedelta
    
    nv2=NobitexV2(requests.Session())
    
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