import time
import traceback
import pandas as pd
from pathlib import Path
import MT5Integration as trade
from datetime import datetime, timedelta, timezone
import pytz

# timezone = pytz.timezone("Etc/UTC")
result_dict = {}


vantage_timezone ="GMT"
exceness="Etc/UTC"

timezoneused=exceness

def pip_converter():
    pass


def get_user_settings():
    global result_dict
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}

        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            symbol_dict = {
                'TimeFrame': row['TimeFrame'],
                'CandleRange': row['CandleRange'],
                'AveragingStep': row['AveragingStep'],
                'MagicNumber': row['MagicNumber'],
                'TargetRangePercentage': row['TargetRangePercentage'],
                'AveragingStepCount': 0,
                'NextTradeVal': 0,
                'NumberOfTrades': row['NumberOfTrades'],
                'Quantity': row['Quantity'],
                'InitialQuantity': row['Quantity'],
                'NextOrderQty': 0,
                'QuantityMultiplier': row['QuantityMultiplier'],
                'RangePercentage': row['RangePercentage'],
                'Stoploss': row['Stoploss'],
                'USESL': row['USESL'],
                'InitialTrade': None,
                'previous_target_val': 0,
                'target_val': 0,
                'ActivateSl': False,
                'Sl_Val': 0,
                'updated_high': 0,
                'updated_low': 0,
                'perval': 0,
                'fixed_low_sell': 0,
                'fixed_high_buy': 0,
                'ExitTime': None,
                'TradingStatus': row['TradingStatus'],

            }
            result_dict[row['Symbol']] = symbol_dict
        print(result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))


get_user_settings()

def get_mt5_credentials():
    credentials = {}
    try:
        df = pd.read_csv('MT5Credentials.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials


credentials_dict = get_mt5_credentials()
Login = credentials_dict.get('Login')
Password = credentials_dict.get('Password')
Server = credentials_dict.get('Server')
switch = credentials_dict.get('UseRisk')
print(switch)
MaxLoss = float(credentials_dict.get('MaxLoss'))
MaxProfit = float(credentials_dict.get('MaxProfit'))
print("StartTime: ", credentials_dict.get('StartTime'))
print("Stoptime: ", credentials_dict.get('Stoptime'))
trade.login(Login, Password, Server)
start_date = datetime.now(timezone.utc) - timedelta(days=1)
end_date = datetime.now(timezone.utc).replace(hour=17, minute=31, second=0, microsecond=0)


def takeprofit_calculation(updated_price, tradetype, previous_target_value):
    try:
        if tradetype is None:
            return previous_target_value

        if tradetype == "SHORT":
            if updated_price >= previous_target_value:
                previous_target_value = updated_price
        if tradetype == "BUY":
            if updated_price <= previous_target_value:
                previous_target_value = updated_price
        return previous_target_value
    except Exception as e:
        print("Error happened in target calculation", str(e))


def close_all_buy_orders(trade_positions, symbol):
    try:
        for position in trade_positions:
            ticket_value = position.ticket
            symbol_value = position.symbol
            volume_value = position.volume
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if symbol == symbol_value:
                orderlog = f"{timestamp} Target Executed For buy Trade @ {symbol_value} @ {volume_value} order no ={ticket_value}"
                print(orderlog)
                write_to_order_logs(orderlog)
                trade.mt_close_buy(symbol=symbol_value, lot=volume_value, orderid=ticket_value, timestamp=timestamp)
    except Exception as e:
        print("Error happened in Closing buy position", str(e))


def close_all_sell_orders(trade_positions, symbol):
    try:
        for position in trade_positions:

            ticket_value = position.ticket
            symbol_value = position.symbol
            volume_value = position.volume

            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")

            if symbol == symbol_value:
                orderlog = f"{timestamp} Target Executed For buy Trade @ {symbol_value} @ {volume_value} order no ={ticket_value}"
                print(orderlog)
                write_to_order_logs(orderlog)
                trade.mt_close_sell(symbol=symbol_value, lot=volume_value, orderid=ticket_value, timestamp=timestamp)
    except Exception as e:
        print("Error happened in Closing sell position", str(e))




# trade.get_data(symbol="AMZN",timeframe="TIMEFRAME_M5")

def main_strategy():
    global result_dict
    try:
        for symbol, params in result_dict.items():
            time_frame = params['TimeFrame']
            candle_range = float(params['CandleRange'])
            averaging_step = float(params['AveragingStep'])
            NumberOfTrades = int(params['NumberOfTrades'])
            symr = trade.get_data(symbol=symbol, timeframe=time_frame)
            open=float(symr[0][1])
            high =float(symr[0][2])
            low =float(symr[0][3])
            close =float(symr[0][4])

            candletime  = symr[0][0]
            print(candletime)
            print(timezoneused)
            candletime = datetime.fromtimestamp(candletime, pytz.timezone(timezoneused))
            diff_to_high = abs(close - high)
            diff_to_low = abs(close - low)
            value_to_compare = high - low
            # print("Loop Started")
            print("Symbol = ", symbol)
            print("Time: ",candletime)
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            current_time_gmt = datetime.now(pytz.timezone("GMT"))
            start_time_str = credentials_dict.get('StartTime')
            start_time = datetime.strptime(start_time_str, "%H:%M")
            start_time = start_time.replace(year=current_time_gmt.year, month=current_time_gmt.month,
                                            day=current_time_gmt.day)
            start_time = start_time.replace(tzinfo=pytz.timezone(timezoneused))


            if (
                    start_time>candletime and
                    params['TradingStatus'] == "ENABLE" and
                    float(value_to_compare) >= candle_range and
                    params['InitialTrade'] == None and
                    diff_to_high < diff_to_low and
                    params['ExitTime'] != candletime
            ):
                # open sell
                params['InitialTrade'] = "SHORT"
                params['AveragingStepCount'] = params['AveragingStepCount'] + 1
                params['NextTradeVal'] = close + averaging_step
                params['NextOrderQty'] = float(params['Quantity']) * float(params['QuantityMultiplier'])
                params['updated_high'] = float(high)
                params['fixed_low_sell'] = float(low)
                params['previous_target_val'] = params['updated_high']
                params['perval'] = params['updated_high'] - params['fixed_low_sell']
                params['target_val'] = params['perval'] * float(params['TargetRangePercentage']) * 0.01
                params['target_val'] = params['updated_high'] - params['target_val']
                orderlog = f"{timestamp} Short order executed for {symbol} for lotsize= {params['Quantity']}  @ {close} ,Step = {params['AveragingStepCount']},Target1 = {params['target_val']} "
                print(orderlog)
                write_to_order_logs(orderlog)
                trade.mt_short(symbol=symbol, lot=float(params['Quantity']), MagicNumber=int(params['MagicNumber']))

            if (
                    start_time > candletime and
                    params['TradingStatus'] == "ENABLE" and
                    float(value_to_compare) >= candle_range and
                    params['InitialTrade'] == None and
                    diff_to_high > diff_to_low and
                    params['ExitTime'] != candletime
            ):
                # open buy
                params['InitialTrade'] = "BUY"
                params['AveragingStepCount'] = params['AveragingStepCount'] + 1
                params['NextTradeVal'] = close - averaging_step
                params['NextOrderQty'] = float(params['Quantity']) * float(params['QuantityMultiplier'])
                params['updated_low'] = float(low)
                params['fixed_high_buy'] = float(high)
                params['previous_target_val'] = params['updated_low']
                params['perval'] = params['fixed_high_buy'] - params['updated_low']
                params['target_val'] = params['perval'] * float(params['TargetRangePercentage']) * 0.01
                params['target_val'] = params['updated_low'] + params['target_val']
                orderlog = f"{timestamp} Buy order executed for {symbol} for lotsize= {params['Quantity']}  @ {close} ,Step = {params['AveragingStepCount']},Target1 ={params['target_val']} "
                print(orderlog)
                write_to_order_logs(orderlog)
                trade.mt_buy(symbol=symbol, lot=float(params['Quantity']), MagicNumber=int(params['MagicNumber']))

            if (
                    params['TradingStatus'] == "ENABLE" and
                    params['TradingStatus'] == "ENABLE" and
                    params['InitialTrade'] == "BUY" and
                    close <= float(params['NextTradeVal']) and
                    float(params['NextTradeVal']) > 0 and
                    params['AveragingStepCount'] < NumberOfTrades
            ):
                params['AveragingStepCount'] = params['AveragingStepCount'] + 1
                params['NextTradeVal'] = close - averaging_step
                params['Quantity'] = params['NextOrderQty']
                params['NextOrderQty'] = float(params['Quantity']) * float(params['QuantityMultiplier'])
                params['updated_low'] = float(low)
                params['previous_target_val'] = params['updated_low']
                params['perval'] = params['fixed_high_buy'] - params['updated_low']
                params['target_val'] = params['perval'] * params['TargetRangePercentage'] * 0.01
                params['target_val'] = params['updated_low'] + params['target_val']
                if params['AveragingStepCount'] == NumberOfTrades:
                    params['ActivateSl'] = True
                    params['Sl_Val'] = close - averaging_step
                orderlog = f"{timestamp} Buy order executed for {symbol} for lotsize= {params['Quantity']}  @ {close} ,Step = {params['AveragingStepCount']},Target ={params['target_val']} "
                print(orderlog)
                write_to_order_logs(orderlog)
                trade.mt_buy(symbol=symbol, lot=float(params['Quantity']), MagicNumber=int(params['MagicNumber']))

            if (
                    params['TradingStatus'] == "ENABLE" and
                    params['TradingStatus'] == "ENABLE" and
                    params['InitialTrade'] == "SHORT" and
                    close >= float(params['NextTradeVal']) and
                    float(params['NextTradeVal']) > 0 and
                    params['AveragingStepCount'] < NumberOfTrades
            ):
                params['AveragingStepCount'] = params['AveragingStepCount'] + 1
                params['NextTradeVal'] = close + averaging_step
                params['Quantity'] = params['NextOrderQty']
                params['NextOrderQty'] = float(params['Quantity']) * float(params['QuantityMultiplier'])
                params['updated_high'] = float(high)
                params['previous_target_val'] = params['updated_high']
                params['perval'] = params['updated_high'] - params['fixed_low_sell']
                params['target_val'] = params['perval'] * params['TargetRangePercentage'] * 0.01
                params['target_val'] = params['updated_high'] - params['target_val']
                if params['AveragingStepCount'] == NumberOfTrades:
                    params['ActivateSl'] = True
                    params['Sl_Val'] = close + averaging_step
                orderlog = f"{timestamp} Short order executed for {symbol} for lotsize= {params['Quantity']}  @ {close} ,Step = {params['AveragingStepCount']},Target ={params['target_val']}"
                print(orderlog)
                write_to_order_logs(orderlog)
                trade.mt_short(symbol=symbol, lot=float(params['Quantity']), MagicNumber=int(params['MagicNumber']))

            #   target calculation
            if params['InitialTrade'] == "SHORT":
                params['updated_high'] = float(
                    takeprofit_calculation(updated_price=high, tradetype=params['InitialTrade'],
                                           previous_target_value=params['previous_target_val']))
                params['previous_target_val'] = params['updated_high']
                params['perval'] = params['updated_high'] - params['fixed_low_sell']
                params['target_val'] = params['perval'] * params['TargetRangePercentage'] * 0.01
                params['target_val'] = params['updated_high'] - params['target_val']

            if params['InitialTrade'] == "BUY":
                params['updated_low'] = float(
                    takeprofit_calculation(updated_price=low, tradetype=params['InitialTrade'],
                                           previous_target_value=params['previous_target_val']))
                params['previous_target_val'] = params['updated_low']
                params['perval'] = params['fixed_high_buy'] - params['updated_low']
                params['target_val'] = params['perval'] * params['TargetRangePercentage'] * 0.01
                params['target_val'] = params['updated_low'] + params['target_val']

            #         target and stoploss execution
            if (params['TradingStatus'] == "ENABLE" and
                    params['TradingStatus'] == "ENABLE" and
                    params['InitialTrade'] == "SHORT" and
                    close <= float(params['target_val']) and
                    float(params['target_val']) > 0
            ):
                params['InitialTrade'] = None
                params['target_val'] = 0
                params['Sl_Val'] = 0
                params['Quantity'] = float(params['InitialQuantity'])
                params['ExitTime'] = candletime
                params['AveragingStepCount'] = 0
                orderlog = f"{timestamp} Target Executed For Short Trade All Position Exited @ {symbol} @ price {close}, high: {params['updated_high']}, low: {params['fixed_low_sell']} "
                params['updated_low'] = 0
                params['fixed_high_buy'] = 0
                params['updated_high'] = 0
                params['fixed_low_sell'] = 0
                print(orderlog)
                write_to_order_logs(orderlog)
                open_positions = trade.get_open_position()
                close_all_sell_orders(open_positions, symbol)

            if (
                    params['TradingStatus'] == "ENABLE" and
                    params['ActivateSl'] == True and
                    params['InitialTrade'] == "SHORT" and
                    close >= float(params['Sl_Val']) and
                    float(params['Sl_Val']) > 0
            ):
                params['InitialTrade'] = None
                params['target_val'] = 0
                params['Sl_Val'] = 0
                params['ExitTime'] = candletime
                params['AveragingStepCount'] = 0
                params['Quantity'] = float(params['InitialQuantity'])
                orderlog = f"{timestamp} Stoploss Executed For Short Trade All Position Exited @ {symbol} @ price {close} "
                params['updated_low'] = 0
                params['fixed_high_buy'] = 0
                params['updated_high'] = 0
                params['fixed_low_sell'] = 0
                print(orderlog)
                write_to_order_logs(orderlog)
                open_positions = trade.get_open_position()
                close_all_sell_orders(open_positions, symbol)

            if (
                    params['TradingStatus'] == "ENABLE" and
                    params['InitialTrade'] == "BUY" and
                    close >= float(params['target_val']) and
                    float(params['target_val']) > 0
            ):
                params['InitialTrade'] = None
                params['target_val'] = 0
                params['Sl_Val'] = 0
                params['ExitTime'] = candletime
                params['AveragingStepCount'] = 0
                params['Quantity'] = float(params['InitialQuantity'])
                orderlog = f"{timestamp} Target Executed For Buy Trade All Position Exited @ {symbol} @ price {close}, high: {params['fixed_high_buy']}, low: {params['updated_low']} "
                params['updated_low'] = 0
                params['fixed_high_buy'] = 0
                params['updated_high'] = 0
                params['fixed_low_sell'] = 0
                print(orderlog)
                write_to_order_logs(orderlog)
                open_positions = trade.get_open_position()
                close_all_buy_orders(open_positions, symbol)

            if (
                    params['TradingStatus'] == "ENABLE" and
                    params['ActivateSl'] == True and
                    params['InitialTrade'] == "BUY" and
                    close <= float(params['Sl_Val']) and
                    float(params['Sl_Val']) > 0
            ):
                params['InitialTrade'] = None
                params['target_val'] = 0
                params['Sl_Val'] = 0
                params['ExitTime'] = candletime
                params['AveragingStepCount'] = 0
                params['Quantity'] = float(params['InitialQuantity'])
                orderlog = f"{timestamp} Stoploss Executed For Buy Trade All Position Exited @ {symbol} @ price {close} "
                params['updated_low'] = 0
                params['fixed_high_buy'] = 0
                params['updated_high'] = 0
                params['fixed_low_sell'] = 0
                print(orderlog)
                write_to_order_logs(orderlog)
                open_positions = trade.get_open_position()
                close_all_buy_orders(open_positions, symbol)

            combined_pnl = float(trade.get_mtm())

            if switch == "TRUE" and combined_pnl >= MaxProfit:
                orderlog = f"{timestamp} Max Profit acheived closing all open position no more trade will be taken {combined_pnl}"
                print(orderlog)
                write_to_order_logs(orderlog)
                open_positions = trade.get_open_position()
                close_all_buy_orders(open_positions, symbol)
                open_positions = trade.get_open_position()
                close_all_sell_orders(open_positions, symbol)
                for symbol, VARAM in result_dict.items():
                    VARAM['TradingStatus'] = "DISABLE"

            if switch == "TRUE" and combined_pnl <= MaxLoss:
                orderlog = f"{timestamp} Max loss acheived closing all open position no more trade will be taken {combined_pnl} "
                print(orderlog)
                write_to_order_logs(orderlog)
                open_positions = trade.get_open_position()
                close_all_buy_orders(open_positions, symbol)

                open_positions = trade.get_open_position()
                close_all_sell_orders(open_positions, symbol)

                for symbol, VARAM in result_dict.items():
                    VARAM['TradingStatus'] = "DISABLE"






    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()


def write_to_order_logs(message):
    with open('MachineLogs.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')
#
# trade.getdata_ver2(symbol="XAUUSD", timeframe="TIMEFRAME_M5")
# trade.get_data(symbol="XAUUSD", timeframe="TIMEFRAME_M5")
#


# trade.mt_buy(symbol="EURUSD",lot=0.01,MagicNumber=12345)
# trade.mt_close_sell(symbol="EURUSD",lot=0.01,orderid=64504309)
while True:
    main_strategy()









