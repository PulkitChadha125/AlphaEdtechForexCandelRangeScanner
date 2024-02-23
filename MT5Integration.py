import MetaTrader5 as mt
from datetime import datetime, timedelta
import pandas as pd
import pytz
import traceback
# Login=1075557
# Password="Forex@123"
# Server="VantageInternational-Demo"
def write_to_order_logs(message):
    with open('MachineLogs.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')

def login (Login,Password,Server):
    try:
        mt.initialize()
        mt.login(Login,Password,Server)
    except Exception as e:
        print("An error occurred while login:", str(e))

def get_mtm():
    try:
        # Assuming get_open_position() returns the list of TradePosition objects
        open_positions = get_open_position()

        # Calculate the combined PnL
        combined_pnl = sum(position.profit for position in open_positions)



        # Display the combined PnL
        print("Combined PnL:", combined_pnl)

        return combined_pnl

    except Exception as e:
        print("An error occurred while fetching open position:", str(e))


def convert_to_broker_time():
    # Define time zones
    ist_timezone = pytz.timezone('Asia/Kolkata')  # Indian Standard Time
    current_time_ist = datetime.now(ist_timezone)
    print(current_time_ist)
    broker_time_difference = timedelta(hours=-3, minutes=-30)
    broker_time = current_time_ist + broker_time_difference

    return broker_time

def getdata_ver2(symbol, timeframe):
    try:
        if timeframe=='TIMEFRAME_M1':
            timeframe=mt.TIMEFRAME_M1
        elif timeframe=='TIMEFRAME_M2':
            timeframe=mt.TIMEFRAME_M2
        elif timeframe=='TIMEFRAME_M5':
            timeframe=mt.TIMEFRAME_M5
        elif timeframe=='TIMEFRAME_M15':
            timeframe=mt.TIMEFRAME_M15

        start_date = datetime.now(pytz.timezone("Etc/UTC")) - pd.DateOffset(days=1)
        print("start_date 2: ",start_date)

        OHLC_DATA = pd.DataFrame(mt.copy_rates_from(symbol, timeframe, start_date, 5000)).tail(3)
        OHLC_DATA['time'] = pd.to_datetime(OHLC_DATA['time'], unit='s')
        OHLC_DATA.to_csv("data.csv")

    except Exception as e:
        print("An error occurred while fetching data:", str(e))
        traceback.print_exc()

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

        candle_data = mt.copy_rates_from_pos(symbol, mt.TIMEFRAME_M5, 0, 1)

        return candle_data
    except Exception as e:
        print("An error occurred while fetching data:", str(e))
        traceback.print_exc()

def checking ():
    candle_data = mt.copy_rates_from_pos("XAUUSD", mt.TIMEFRAME_M5, 0, 1)
    print("candle_data: ",candle_data)
    timestamp = candle_data[0][0]
    print("Unix Timestamp:", timestamp)
    human_readable_time = datetime.fromtimestamp(timestamp, pytz.timezone("Europe/Athens"))
    print("Human Readable Time:", human_readable_time)









# def get_data(symbol, timeframe):
#
#     try:
#         if timeframe=='TIMEFRAME_M1':
#             timeframe=mt.TIMEFRAME_M1
#         elif timeframe=='TIMEFRAME_M2':
#             timeframe=mt.TIMEFRAME_M2
#         elif timeframe=='TIMEFRAME_M5':
#             timeframe=mt.TIMEFRAME_M5
#         elif timeframe=='TIMEFRAME_M15':
#             timeframe=mt.TIMEFRAME_M15
#
#
#
#
#         end_date = datetime.now(pytz.timezone("Etc/UTC")).replace(hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second, microsecond=0)
#         end_date_utc = datetime.now(pytz.timezone("Etc/UTC"))
#
#         start_date = end_date_utc.astimezone(
#             pytz.timezone("Europe/Athens")) - timedelta(hours=5)
#         end_date_gmt2 = end_date_utc.astimezone(
#             pytz.timezone("Europe/Athens"))  # Replace "Europe/Athens" with the desired timezone
#
#         # Convert end_date to GMT+3
#         end_date_gmt3 = end_date_utc.astimezone(
#             pytz.timezone("Europe/Istanbul"))  # Replace "Europe/Istanbul" with the desired timezone
#
#         # print("end_date (UTC): ", end_date_utc)
#         print("start_date (GMT+2): ", start_date)
#         print("end_date (GMT+2): ", end_date_gmt2)
#         print("end_date (GMT+3): ", end_date_gmt3)
#
#
#         OHLC_DATA = pd.DataFrame(mt.copy_rates_range(symbol, timeframe, start_date, end_date_gmt3))
#         OHLC_DATA['time'] = pd.to_datetime(OHLC_DATA['time'], unit='s')
#         OHLC_DATA.to_csv("data.csv")
#         return OHLC_DATA
#     except Exception as e:
#         print("An error occurred while fetching data:", str(e))
#         traceback.print_exc()


def get_open_position():
    try:
        result=mt.positions_get()

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

        write_to_order_logs(result)
    except Exception as e:
        print(" error occurred while placing buy order:", str(e))
        write_to_order_logs(str(e))






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
        write_to_order_logs(result)
    except Exception as e:
        print(" error occurred while placing sell order:", str(e))
        write_to_order_logs(str(e))

def mt_close_buy(symbol,lot,orderid,timestamp):
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
        orderlog = f"{timestamp} {result}"
        print(orderlog)
        write_to_order_logs(orderlog)
    except Exception as e:
        print(" error occurred while closing buy order:", str(e))
        write_to_order_logs(str(e))


def mt_close_sell(symbol,lot,orderid,timestamp):
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
        orderlog = f"{timestamp} {result}"
        print(orderlog)
        write_to_order_logs(orderlog)
    except Exception as e:
        print(" error occurred while closing sell order:", str(e))
        write_to_order_logs(str(e))







# def get_data(symbol,timeframe=mt.TIMEFRAME_M1):
#     start_date = datetime(2024, 1, 29)
#     end_date = datetime.now()
#     timezone = pytz.timezone("Etc/UTC")
#
#     OHLC_DATA =pd.DataFrame(mt.copy_rates_range(symbol,timeframe,start_date,datetime(2024, 1, 29, hour = 17,minute=31, tzinfo=timezone))).tail(3)
#     OHLC_DATA['time'] = pd.to_datetime(OHLC_DATA['time'], unit='s')
#     OHLC_DATA.to_csv("checking.csv")


