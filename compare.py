import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import date
from sys import argv
from dotenv import load_dotenv
from os import environ
from os.path import join, dirname

args = argv

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except:
    pass

TIMESPANS = {"minute", "hour", "day", "week", "month", "quarter", "year"}

flag_mapping = {
    "--symbol": "-s",
    "--ticker": "-s",
    "--time": "-t",
    "--multiplier": "-m",
    "--datetime": "-x",
    "--adjusted": "-a",
    "--desc": "-d",
    "--descending": "-d",
    "--limit": "-l",
    "--key": "-k",
    "--filepath": "-k"
}

flags = ["-s", "-t", "-m", "-x", "-a", "-d", "-l", "-k"]
for f in flags:
    flag_mapping[f] = f

all_keys = flag_mapping.keys()

class StockCompare():
    def __init__(self):
        self.symbols = None
        self.timeStart = None
        self.timeEnd = None
        self.multipiler = None
        self.timespan = None
        self.adjusted = True
        self.sort = "asc"
        self.limit = None
        self.key = environ.get("POLYGON_KEY")
        self.function_mapping = {
            "-s": self.set_symbols,
            "-t": self.set_date,
            "-m": self.set_multiplier,
            "-x": self.set_timespan,
            "-a": self.set_adjusted,
            "-d": self.set_descending,
            "-l": self.set_limit,
            "-k": self.set_key
        }

    def polygon_request(self, symbol):
        try:
            url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{self.multiplier}/{self.timespan}/{self.timeStart}/{self.timeEnd}?adjusted={str(self.adjusted).lower()}&sort={self.sort}&apiKey={self.key}'
            r = requests.get(url)
            return r.json()
        except:
            print(f"Error: {symbol} not a valid ticker symbol or query is otherwise invalid.")
            self.symbols.remove(symbol)
    
    def extract_results(self, json):
        if not json["ticker"]:
            return [], []
        results = json['results']
        size = len(results)
        datetimes = np.empty(size, dtype="object")
        prices = np.zeros(size)
        for i, result in enumerate(results):
            datetimes[i] = pd.to_datetime(date.fromtimestamp(int(result['t'])/1000))
            prices[i] = int(result['c'])
        return datetimes, prices

    def compare(self):
        if not self.symbols:
            return
        stockdata = np.empty(3, dtype="object")
        stockdata[0] = np.empty(len(self.symbols), dtype="object")
        stockdata[1] = np.empty(len(self.symbols), dtype="object")
        stockdata[2] = np.asarray(self.symbols)
        for i, symbol in enumerate(self.symbols):
            response = self.polygon_request(symbol)
            datetimes, prices = self.extract_results(response)
            stockdata[0][i] = datetimes
            stockdata[1][i] = prices
        for i in range(len(self.symbols)):
            plt.plot(stockdata[0][i], stockdata[1][i], label=stockdata[2][i])
        plt.legend()
        plt.show(block=True)

    def set_symbols(self):
        global args
        if args[0] not in all_keys:
            self.symbols = []
        while args[0] not in all_keys:
            self.symbols.append(str(args[0]).upper())
            args = args[1:]

    def set_date(self):
        global args
        count = 0
        if not args[0] in all_keys:
            try:
                self.timeStart = int(pd.to_datetime(args[0]).timestamp() * 1000)
            except:
                print(f"Improperly formatted datetime string {args[0]}. Try YYYY/MM/DD HH:MM format.")
                self.timeStart = None
            count += 1
        if not args[1] in all_keys:
            try:
                self.timeEnd = int(pd.to_datetime(args[1]).timestamp() * 1000)
            except:
                print(f"Improperly formatted datetime string {args[1]}. Try YYYY/MM/DD HH:MM format.")
                self.timeEnd = None
            count += 1
        args = args[count:]

    def set_multiplier(self):
        global args
        if not args[0] in all_keys:
            try:
                self.multiplier = int(float(args[0]))
            except:
                print("Argument for multiplier cannot be converted to an integer, please input an integer.")
            args = args[1:]

    def set_timespan(self):
        global args
        if not args[0] in all_keys:
            lower_arg = args[0].lower()
            if lower_arg in TIMESPANS:
                self.timespan = lower_arg
            else:
                print("Please include one of the following for datetime (-x) argument: ", end="")
                [print(x, end=" ") for x in list(TIMESPANS)]
            args = args[1:]

    def set_adjusted(self):
        self.adjusted = False

    def set_descending(self):
        self.sort = "desc"

    def set_limit(self):
        global args
        if not args[0] in all_keys:
            try:
                self.limit = int(float(args[0]))
            except:
                print("Argument for multiplier cannot be converted to an integer, please input an integer.")
            args = args[1:]

    def set_key(self):
        global args
        if not args[0] in all_keys:
            self.key = args[0]
            args = args[1:]
        
# input("Press enter to continue...")
c = StockCompare()
while(args):
    arg = args[0]
    if arg in flag_mapping.keys() and flag_mapping[arg] in flags:
        flag = flag_mapping[arg]
        args = args[1:]
        c.function_mapping[flag]()
    else:
        args = args[1:]
c.compare()
    
    
