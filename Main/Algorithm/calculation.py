# import libraries
import pandas as pd
import numpy as np
import vnstock as vn

class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    #load_data
    def load_data(ticker, year):
        START = f"{year}-01-01"
        END = f"{year+1}-02-01"
        data = vn.stock_historical_data(ticker, START, END)    
        return data

    #lable volume
    def label_values(a):
        if pd.isnull(a):
            return a
        elif a < 0.75:
            return 'low'
        elif 0.75 <= a <= 1.25:
            return 'medium'
        else:
            return 'high'

    #Bar
    def compare_close_prices(row):
        t = row['close']
        t_minus_1 = row['close_t_minus_1']
        if t > t_minus_1:
            return 'up-bar'
        else:
            return 'down-bar'

    #lable spread
    def label_spread(a):
        if 0 < a < 0.3: return 'low'
        elif 0.3 <= a <= 0.7: return 'medium'
        else: return 'high'

    #Close bar
    def label_close_bar(data):
        q1 = data['low'] + (data['high'] - data['low'])/3
        q2 = data['low'] + 2*((data['high'] - data['low'])/3)
        if data['close'] < q1:
            return 'bottom-third'
        elif q1 <= data['close'] <= q2:
            return 'middle-third'
        else:
            return 'top-third'
