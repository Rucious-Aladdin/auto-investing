# Aladdin crytocurrency investing version 1.7
# last update : 2021.03.13

# 1.0 version 2020.12.29
# Larry williams' Volitality Break-out Strategy
# moving average score + average noise ratio(ma20) target volatility = 4%, goal of CAGR: 100% up.

# 1.1 version 2021.1.1
# reduced target volatility 4% to 3.5%

# 1.2 version 2021.1.20
# noise threshold reset due to concerns about reduced returns due to increased market noise

# 1.3 version 2020.1.25
# changed to use the 3~20-day moving average line from the existing 3, 5, 10, 20 moving average line

# 1.4 version 2020.1.27
# optimized code

# 1.5 version 2021.02.19
# addition of repeated selling funtion of virtual currency due to extreme selling error

# 1.6 version 2021.02.20
# change of minimum purchase amount due to purchase amount restriction measures

# 1.7 version 2021.03.13
# Set not to buy when the target price is more than 1.5% from the expected purchase price

import pyupbit
import datetime
import time

with open("pyupbit.txt") as f:
    lines = f.readlines()
    access_key = lines[0].strip()
    secret_key = lines[1].strip()
    upbit = pyupbit.Upbit(access_key, secret_key)

def get_target_price(ticker):
    df = pyupbit.get_ohlcv(ticker, count = 23)
    yesterday = df.iloc[-2]
    noise_sum = 0
    today = df.iloc[-1]

    for num in range(1,21):
        noise_df = df.iloc[(-1*num) + 1]
        gap_hl = noise_df["high"] - noise_df["low"]
        gap_oc = abs(noise_df["open"]-noise_df["close"])
        noise_idx = 1 - gap_oc / gap_hl

        if noise_idx < 0.00001:
            noise_idx = 0

        noise_sum += noise_idx 

    target = today['open'] + (yesterday["high"] - yesterday["low"]) * (noise_sum / 20)
    current_price = pyupbit.get_current_price(ticker)
    rst = upbit.get_balance(ticker)

    nse_rto = round(noise_sum * 5, 2)

    print(ticker, " current price: ", format(int(current_price), ","), " won", sep = '')
    print(ticker, " target price: ", format(int(target), ","), " won", sep ='')
    print(ticker, " noise ratio: ", nse_rto, "%", sep = '')

    return noise_sum / 20, target, rst

def get_bet_ratio(ticker):
    current_price = pyupbit.get_current_price(ticker)
    count = 0
    df = pyupbit.get_ohlcv(ticker,interval = "day", count = 23)
    close = df["close"]
    yesterday = df.iloc[-2]
    volatility =  (yesterday["high"] - yesterday["low"])/ yesterday['close']

    vol_idx = 1 if volatility < 0.035 else 0.035 / volatility

    for num in range(3,21):
        ma_series = close.rolling(window = num).mean()
        if current_price > ma_series[-1]:
            count += 1

    return ( count / 18 ) * vol_idx

def get_initial_account():

    krw = upbit.get_balance(ticker = "KRW")
    KRW, default = upbit.get_balances()
    i=0
    initial_acc = krw

    while i < 6:
            
        try:
            initial_acc += (float(KRW[i]["balance"]) * float(KRW[i]["avg_buy_price"]))
            i += 1    
        except:
            pass
            i += 1

    return initial_acc

def sell():
    rst_BTC = upbit.get_balance(ticker = "KRW-BTC")
    rst_ETH = upbit.get_balance(ticker = "KRW-ETH")
    rst_BCH = upbit.get_balance(ticker = "KRW-BCH")
    rst_LTC = upbit.get_balance(ticker = "KRW-LTC")
    rst_EOS = upbit.get_balance(ticker = "KRW-EOS")

    while True:
        
        if rst_BTC != None:
            upbit.sell_market_order("KRW-BTC", rst_BTC)
        if rst_ETH != None:
            upbit.sell_market_order("KRW-ETH", rst_ETH)
        if rst_BCH != None:
            upbit.sell_market_order("KRW-BCH", rst_BCH)
        if rst_LTC != None:
            upbit.sell_market_order("KRW-LTC", rst_LTC)
        if rst_EOS != None:
            upbit.sell_market_order("KRW-EOS", rst_EOS)

        time.sleep(0.5)

        rst_BTC = upbit.get_balance(ticker = "KRW-BTC")
        rst_ETH = upbit.get_balance(ticker = "KRW-ETH")
        rst_BCH = upbit.get_balance(ticker = "KRW-BCH")
        rst_LTC = upbit.get_balance(ticker = "KRW-LTC")
        rst_EOS = upbit.get_balance(ticker = "KRW-EOS")

        if rst_BTC == None and rst_ETH == None and rst_BCH == None and rst_LTC == None and rst_EOS == None:
            print("completed selling all coins")
            time.sleep(1)
            break
        else:
            print("Not all coins have been sold, resale execution")
            time.sleep(1)

now = datetime.datetime.now()

if datetime.datetime(now.year, now.month, now.day, now.hour, now.minute) < datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(hours = 9, minutes = 5):
    mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(hours = 9, minutes = 5)
else:
    mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days = 1, hours = 9, minutes = 5)

acc_bal = get_initial_account() * 0.2 - 1
print("initial KRW balance: ", acc_bal*5)

noise_BTC, tar_BTC, rst_BTC = get_target_price("KRW-BTC") #Bitcoin
noise_ETH, tar_ETH, rst_ETH = get_target_price("KRW-ETH") #Ethereum
noise_BCH, tar_BCH, rst_BCH = get_target_price("KRW-BCH") #Ripple
noise_LTC, tar_LTC, rst_LTC = get_target_price("KRW-LTC") #LightCoin
noise_EOS, tar_EOS, rst_EOS = get_target_price("KRW-EOS") #Eos

time.sleep(0.5)

print("code is working normally")
print("initial settings complete...")
print("next rebalancing time:", mid)

count = 0

if rst_BTC != None:
    hold_BTC = True
else:
    hold_BTC = False

if rst_ETH != None:
    hold_ETH = True
else:
    hold_ETH = False

if rst_BCH != None:
    hold_BCH = True
else:
    hold_BCH = False

if rst_LTC != None:
    hold_LTC = True
else:
    hold_LTC = False

if rst_EOS != None:
    hold_EOS = True
else:
    hold_EOS = False

while True:

    try:
        now = datetime.datetime.now()
        
        if mid < now < mid + datetime.timedelta(seconds = 60): 
            mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days = 1, hours = 9, minutes = 5)

            sell()
            print("now time:", now)

            noise_BTC, tar_BTC, rst_BTC = get_target_price("KRW-BTC") #Bitcoin
            noise_ETH, tar_ETH, rst_ETH = get_target_price("KRW-ETH") #Ethereum
            noise_BCH, tar_BCH, rst_BCH = get_target_price("KRW-BCH") #Ripple
            noise_LTC, tar_LTC, rst_LTC = get_target_price("KRW-LTC") #LightCoin
            noise_EOS, tar_EOS, rst_EOS = get_target_price("KRW-EOS") #Eos

            hold_BTC = False
            hold_ETH = False
            hold_BCH = False
            hold_LTC = False
            hold_EOS = False
            
            time.sleep(2)

            acc_bal = upbit.get_balance(ticker = "KRW") * 0.2 - 1
            print("renewing account balances and target price...")
            print("next rebalancing time: ", mid)
            rst_KRW = upbit.get_balance("KRW")
            print("KRW: ", rst_KRW)

            time.sleep(10)

        cur_BTC = pyupbit.get_current_price("KRW-BTC")
        cur_ETH = pyupbit.get_current_price("KRW-ETH")
        cur_BCH = pyupbit.get_current_price("KRW-BCH")
        cur_LTC = pyupbit.get_current_price("KRW-LTC")
        cur_EOS = pyupbit.get_current_price("KRW-EOS")

        time.sleep(0.2)

        rst_BTC = upbit.get_balance("KRW-BTC")
        rst_ETH = upbit.get_balance("KRW-ETH")
        rst_BCH = upbit.get_balance("KRW-BCH")
        rst_LTC = upbit.get_balance("KRW-LTC")
        rst_EOS = upbit.get_balance("KRW-EOS")

        count += 1

        if cur_BTC > tar_BTC and rst_BTC == None and noise_BTC < 0.65 and (tar_BTC / cur_BTC) < 1.015 and hold_BTC != True:
            bet_BTC = get_bet_ratio("KRW-BTC")
            ive_BTC = acc_bal * bet_BTC
            #if ive_BTC < 100000:
            #    ive_BTC = 100001
            upbit.buy_market_order("KRW-BTC", ive_BTC)
            print("Buying BTC", ive_BTC, "won")
            hold_BTC = True

            time.sleep(5)

        if cur_ETH > tar_ETH and rst_ETH == None and noise_ETH < 0.65 and (tar_ETH / cur_ETH) < 1.015 and hold_ETH != True:
            bet_ETH = get_bet_ratio("KRW-ETH")
            ive_ETH = acc_bal * bet_ETH
            #if ive_ETH < 100000:
            #    ive_ETH = 100001
            upbit.buy_market_order("KRW-ETH", ive_ETH)
            print("Buying ETH", ive_ETH, "won")
            hold_ETH = True
            time.sleep(5)
                
        if cur_BCH > tar_BCH and rst_BCH == None and noise_BCH < 0.65 and (tar_BCH / cur_BCH) < 1.015 and hold_BCH != True:
            bet_BCH = get_bet_ratio("KRW-BCH")
            ive_BCH = acc_bal * bet_BCH
            #if ive_BCH < 100000:
            #    ive_BCH = 100001
            upbit.buy_market_order("KRW-BCH", ive_BCH)
            print("Buying BCH", ive_BCH, "won")
            hold_BCH = True

            time.sleep(5)
            
        if cur_LTC > tar_LTC and rst_LTC == None and noise_LTC < 0.65 and (tar_LTC / cur_LTC) < 1.015 and hold_LTC != True:
            bet_LTC = get_bet_ratio("KRW-LTC")
            ive_LTC = acc_bal * bet_LTC
            #if ive_LTC < 100000:
            #    ive_LTC = 100001
            upbit.buy_market_order("KRW-LTC", ive_LTC)
            print("Buying LTC", ive_LTC, "won")
            hold_LTC = True

            time.sleep(5)
            
        if cur_EOS > tar_EOS and rst_EOS == None and noise_EOS < 0.65 and (tar_EOS / cur_EOS) < 1.015 and hold_EOS != True:
            bet_EOS = get_bet_ratio("KRW-EOS")
            ive_EOS = acc_bal * bet_EOS
            upbit.buy_market_order("KRW-EOS", ive_EOS)
            print("Buying EOS", ive_EOS, "won")
            hold_EOS = True

            time.sleep(0.1)
        
        if count == 8000:
            print("code is working normally")
            print(datetime.datetime.now())
            print("BTC: ",cur_BTC)
            print("ETH: ",cur_ETH)
            print("BCH: ",cur_BCH)
            print("LTC: ",cur_LTC)
            print("EOS: ",cur_EOS)
            count = 0

    except:
        print("error occured")

    time.sleep(0.7)