import MetaTrader5 as mt
from datetime import datetime
import pandas as pd
import pytz

Login=1075557
Password="Forex@123"
Server="VantageInternational-Demo"


def login (Login,Password,Server):
    try:
        mt.initialize()
        mt.login(Login,Password,Server)
    except Exception as e:
        print("An error occurred while login:", str(e))



def get_data(symbol, timeframe):
    try:
        if timeframe=='TIMEFRAME_M1':
            timeframe=mt.TIMEFRAME_M1
        elif timeframe=='TIMEFRAME_M2':
            timeframe=mt.TIMEFRAME_M2
        elif timeframe=='TIMEFRAME_M5':
            timeframe=mt.TIMEFRAME_M5
        elif timeframe=='TIMEFRAME_M15':
            timeframe=mt.TIMEFRAME_M15

        # mt.TIMEFRAME_M1
        start_date = datetime.now(pytz.timezone("Etc/UTC")) - pd.DateOffset(days=1)
        end_date = datetime.now(pytz.timezone("Etc/UTC")).replace(hour=datetime.now().hour, minute=datetime.now().minute, second=0, microsecond=0)
        OHLC_DATA = pd.DataFrame(mt.copy_rates_range(symbol, timeframe, start_date, end_date)).tail(3)
        OHLC_DATA['time'] = pd.to_datetime(OHLC_DATA['time'], unit='s')

        return OHLC_DATA
    except Exception as e:
        print("An error occurred while fetching data:", str(e))


def get_open_position():
    try:
        result=mt.positions_get()
        print(result)
        return result
    except Exception as e:
        print("An error occurred while fetching open position:", str(e))


def current_ask(symbol):

    return mt.symbol_info_tick(symbol).ask

def current_bid(symbol):
    return mt.symbol_info_tick(symbol).bid


def mt_buy(symbol,lot,MagicNumber):
    try:
        price = mt.symbol_info_tick(symbol).ask
        point = mt.symbol_info(symbol).point
        request = {
            "action": mt.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt.ORDER_TYPE_BUY,
            "price": price,
            "magic": MagicNumber,
            "comment": "python buy order",
            "type_time": mt.ORDER_TIME_GTC,
            "type_filling": mt.ORDER_FILLING_IOC,
        }
        result = mt.order_send(request)
        print("result: ",result)
    except Exception as e:
        print(" error occurred while placing buy order:", str(e))






def mt_short(symbol,lot,MagicNumber):
    try:
        price = mt.symbol_info_tick(symbol).bid
        point = mt.symbol_info(symbol).point
        request = {
            "action": mt.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt.ORDER_TYPE_SELL,
            "price": price,
            "magic": MagicNumber,
            "comment": "python sell order",
            "type_time": mt.ORDER_TIME_GTC,
            "type_filling": mt.ORDER_FILLING_IOC,
        }
        result = mt.order_send(request)
        print("result: ", result)
    except Exception as e:
        print(" error occurred while placing sell order:", str(e))

def mt_close_buy(symbol,lot,orderid):
    try:
        price = mt.symbol_info_tick(symbol).bid
        request = {
            "action": mt.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt.ORDER_TYPE_SELL,
            "position":orderid,
            "price": price,
            "comment": "python  close buy ",
            "type_time": mt.ORDER_TIME_GTC,
            "type_filling": mt.ORDER_FILLING_IOC,
        }
        result = mt.order_send(request)
        print(result)
    except Exception as e:
        print(" error occurred while closing buy order:", str(e))


def mt_close_sell(symbol,lot,orderid):
    try:
        price = mt.symbol_info_tick(symbol).ask
        request = {
            "action": mt.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt.ORDER_TYPE_BUY,
            "position": orderid,
            "price": price,
            "comment": "python  close sell ",
            "type_time": mt.ORDER_TIME_GTC,
            "type_filling": mt.ORDER_FILLING_IOC,
        }
        result = mt.order_send(request)
        print(result)
    except Exception as e:
        print(" error occurred while closing sell order:", str(e))







# def get_data(symbol,timeframe=mt.TIMEFRAME_M1):
#     start_date = datetime(2024, 1, 29)
#     end_date = datetime.now()
#     timezone = pytz.timezone("Etc/UTC")
#
#     OHLC_DATA =pd.DataFrame(mt.copy_rates_range(symbol,timeframe,start_date,datetime(2024, 1, 29, hour = 17,minute=31, tzinfo=timezone))).tail(3)
#     OHLC_DATA['time'] = pd.to_datetime(OHLC_DATA['time'], unit='s')
#     OHLC_DATA.to_csv("checking.csv")


