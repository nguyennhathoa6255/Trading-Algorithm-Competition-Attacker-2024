import pandas as pd
import numpy as np
from datetime import datetime, date

class Portfolio:
    '''
        Khởi tạo portfolio
    '''
    def __init__(self, starting_cash, ticker_list, df_percentage):
        self.initial_cash = starting_cash
        self.cash = starting_cash
        self.ticker_list = ticker_list
        self.stock_df = self.create_stock_df(ticker_list=ticker_list)
        self.transaction_list = self.create_transaction_list()
        self.update_percentage(df_percentage=df_percentage)
        self.init_buy_power();

    def create_stock_df(self, ticker_list):
        ticker_list_len = len(ticker_list) 
        data = {
            'ticker': ticker_list,
            'percentage': ['']*ticker_list_len,
            'weight': [0.0]*ticker_list_len,
            'buy_power': [0]*ticker_list_len,
            'holding': [False]*ticker_list_len,
            'current_price': [0]*ticker_list_len,
            'last_date_sell': ['']*ticker_list_len,
            'last_date_buy': ['']*ticker_list_len,
            'pending_money': [0]*ticker_list_len,
            'quantity': [0]*ticker_list_len
        }
        stock_df = pd.DataFrame(data)
        return stock_df
    
    def update_percentage(self, df_percentage):
        self.stock_df['percentage'] = (df_percentage['weight'].values * 100)
        self.stock_df['weight'] = df_percentage['weight'].values
        
    
    def create_transaction_list(self):
        data = {
            'time': [],
            'ticker': [],
            'price': [],
            'quantity': [],
            'action': []
        }      
        transaction_list = pd.DataFrame(data)
        return transaction_list
    
    def init_buy_power(self):
        for index, it in self.stock_df.iterrows():
            ticker_percentage = self.stock_df.loc[index]['weight']
            new_buy_power = self.cash*ticker_percentage
            # print(new_buy_power)
            self.stock_df.at[index, 'buy_power'] = new_buy_power
    '''
        Kết thúc khởi tạo portfolio
    '''
    
    '''
        ************
        Utility functions
    '''
    def add_transaction(self, time: str, ticker: str, price: int, quantity: int, action: str):
        new_transaction = {
            'time': time,
            'ticker': ticker,
            'price': price,
            'quantity': quantity,
            'action': action,
        }
        # Phương thức append
        self.transaction_list = self.transaction_list._append(new_transaction, ignore_index=True)
        
    def calculate_holding_stock_values(self):
        '''
            - Tính tổng giá trị cổ phiếu đang nắm giữ
        '''
        value = 0
        for index, it in self.stock_df.iterrows():
            if it['holding']:
                # ticker = it['ticker']
                value += it['current_price']*it['quantity']
        # print('Current holding stock value', value)
        return value
                
    '''
    def update_buy_power(self):
        pending_money = self.stock_df['pending_money'].sum()
        holding_stock_value = self.calculate_holding_stock_values()
        
        total_buy_power = pending_money + holding_stock_value + self.cash
        for index, it in self.stock_df.iterrows():
            ticker_percentage = self.stock_df.loc[index]['weight']
            new_buy_power = total_buy_power*ticker_percentage
            self.stock_df.at[index, 'buy_power'] = new_buy_power
    '''
    
        
    def check_pending_money(self, current_date):
        '''
            - Cập nhật tiền của cp bán từ phiên trước
        '''
        for index, it in self.stock_df.iterrows():
            last_date_sell = it['last_date_sell']
            if last_date_sell != '':
                date_difference = (current_date-last_date_sell).days
                if (date_difference >= 2):
                    self.cash += it['pending_money']
                    self.stock_df.at[index, 'pending_money'] = 0

        
    def validate_buy(self, signal_row):
        # self.update_buy_power()
        signal = signal_row['signal']
        ticker = signal_row['ticker']
        index_of_ticker = self.stock_df[self.stock_df['ticker'] == ticker].index[0]
        self.stock_df.at[index_of_ticker, 'current_price'] = signal_row['close']
        
        # Kiểm tra cổ phiếu đã có đang nắm giữ hay chưa
        if self.stock_df.at[index_of_ticker, 'holding']:
            # print(f'Co phieu dang nam giu {ticker}, khong the mua')
            return # Thoát hàm
        
        
        # Kiểm tra luật T+2
        signal_date = signal_row['time']
        last_transaction_date = self.stock_df.at[index_of_ticker, 'last_date_sell']
        if last_transaction_date != '':
            date_difference = (signal_date - last_transaction_date).days
            # print('difference days: ', date_difference)
            if date_difference < 2:
                # print(f'Không thể mua do luật T+ {ticker}')
                return # Thoát hàm
            
        ### Kiểm tra số tiền đang có (không tính pending) có đủ để
        #   số mua lượng cổ phiếu dự kiên hay không
        stock_price = signal_row['close']
        tickers_buy_power = self.stock_df.at[index_of_ticker, 'buy_power']
        n_of_tickerToBuy = np.floor(tickers_buy_power/stock_price)

        if n_of_tickerToBuy < 100:
            return
        
        n_ToBuy_100 = (n_of_tickerToBuy - (n_of_tickerToBuy%100))

        estimate_money = n_ToBuy_100 * stock_price
        # if self.cash < estimate_money:
        #     # print(f'Khong du tien {ticker}, khong the mua')
        #     return # Thoat ham, vi khong du tien
        
        # Ghi lai lich su mua
        self.add_transaction(time=signal_date, ticker=ticker, price=stock_price, quantity=n_ToBuy_100, action=signal)
        
        # Cap nhat trang thai co phieu trong portfolio
        self.stock_df.at[index_of_ticker, 'quantity'] = n_ToBuy_100
        self.stock_df.at[index_of_ticker, 'holding'] = True
        self.stock_df.at[index_of_ticker, 'last_date_buy'] = signal_date
        self.cash -= estimate_money
        self.stock_df.at[index_of_ticker, 'buy_power'] -= estimate_money
        # print('Thuc hien mua co phieu ', ticker)
        
        # There no need to update buy power when a ticker is bought
        # self.update_buy_power()
            
    def validate_sell(self, signal_row):
        signal = signal_row['signal']
        ticker = signal_row['ticker']

        index_of_ticker = self.stock_df[self.stock_df['ticker'] == ticker].index[0]
        # Cập nhật giá của cổ phiếu tại ngày đang xét cho dù có đưa ra giao dịch hay không
        self.stock_df.at[index_of_ticker, 'current_price'] = signal_row['close']
        
        # Kiểm tra cổ phiếu có đang được nắm giữ hay không
        if not self.stock_df.at[index_of_ticker, 'holding']:
        # [self.stock_df['ticker'] == ticker]].index, 'holding']:
            # print(f'Khong nam giu co phieu nay {ticker}, khong the ban')
            return # Thoát hàm
        
        # Kiểm tra luật T+2
        signal_date = signal_row['time']
        last_transaction_date = self.stock_df.at[index_of_ticker, 'last_date_buy']
        if last_transaction_date != '':
            # print('date1 ', signal_date)
            # print('date2 ', last_transaction_date)
            
            date_difference = (signal_date - last_transaction_date).days
            if (date_difference < 2):
                # print(f'Không thể bán do luật T+ {ticker}')
                return # Thoát hàm
                
        stock_price = signal_row['close']
        # Ghi lich su ban
        n_of_stock_toSell = self.stock_df.at[index_of_ticker, 'quantity']
        self.add_transaction(time=signal_date, ticker=ticker, price=stock_price, quantity=n_of_stock_toSell, action=signal)
        # print(f'Thuc hien ban co phieu {ticker}')
        
        # update portfolio
        self.stock_df.at[index_of_ticker, 'quantity'] = 0 # Ban het
        self.stock_df.at[index_of_ticker, 'holding'] = False 
        pending_money = n_of_stock_toSell*stock_price
        self.stock_df.at[index_of_ticker, 'pending_money'] = pending_money
        self.stock_df.at[index_of_ticker, 'last_date_sell'] = signal_date
        self.stock_df.at[index_of_ticker, 'buy_power'] += pending_money
        # self.update_buy_power()


    '''
        @ Hàm quyết định giao dịch
        - input: một dòng tín hiệu (ticker, time, close(price), signal)
        - Đầu tiên cập nhật tiền và cổ phiếu vào đầu phiên giao dịch
        - Dựa trên loại tín hiệu để quyết định loại giao dịch
    '''
    def validate_transaction(self, signal_row):
        self.check_pending_money(signal_row['time'])
        signal = signal_row['signal']
        if (signal == 'Buy'):
            self.validate_buy(signal_row=signal_row)
        if (signal == 'Sell'):
            self.validate_sell(signal_row=signal_row)
         
    
    def show_porfolio(self):
        print('==============PORTFOLIO================')
        
        print('*Stocks\n', self.stock_df)
        # self.show_transaction_history()
        total_revenue = self.calculate_holding_stock_values() + self.cash_prop + self.get_pending_money()
        print('*Total revenue: ', total_revenue)
        print('*Holding value',self.calculate_holding_stock_values())
        print('*Cash',self.cash)
        print('*Pending money', self.get_pending_money())
    
        print('=======================================')
        
    def show_transaction_history(self):
        print('*Transaction history\n', self.transaction_list)
        
    def testList(self):
        transList = self.transaction_list
        result = transList[transList['ticker'] == 'aaa']
        print(result)
        
    def get_pending_money(self):
        return self.stock_df['pending_money'].sum()
    
    def daily_performance(self):
        return (self.cash + self.calculate_holding_stock_values() + self.get_pending_money())/self.initial_cash
    
    def portfolio_performance(self):
        performance_per_ticker = pd.DataFrame(columns=['ticker', 'performance'])
        # print('performance per ticker')
        # print(performance_per_ticker)
        
        for ticker, tickerTransSet in self.transaction_list.groupby('ticker'):
            tickerTransSet.sort_values('time', ascending=True)
            tickerTransSet.reset_index(drop=True, inplace=True)
            # print('****Transaction set*****')
            # print(tickerTransSet)
            trading_log = []
            for index, row in tickerTransSet.iterrows():
                if index == 0:
                    continue
                if row['action'] == 'Sell':
                    buy_price = tickerTransSet.loc[index-1, 'price']
                    sell_price = row['price']
                    profit = (sell_price - buy_price)/buy_price
                    trading_log.append(profit)
            
            # Them hieu suat cua co phieu dang nam giu
            for index, row in self.stock_df.iterrows():
                if (self.stock_df.loc[index, 'holding']) and (self.stock_df.at[index, 'ticker'] == ticker):
                    current_price = self.stock_df.loc[index, 'current_price']
                    last_buy_price = tickerTransSet.at[len(tickerTransSet)-1, 'price']
                    profit = (current_price-last_buy_price)/last_buy_price
                    trading_log.append(profit)

            # Calculate cumulative return
            cumulative_return = 0
            if len(tickerTransSet) > 0:
                cumulative_return = np.prod(np.array(trading_log) + 1) - 1
            
            # performance_per_ticker.loc[len(performance_per_ticker)] = [ticker, ticker_performance]
            performance_per_ticker.loc[len(performance_per_ticker)] = [ticker, cumulative_return]
            
            # Tinh hieu suat toan danh muc
            df_merge = pd.merge(performance_per_ticker, self.stock_df[['ticker', 'weight']], on='ticker', how='left')
            portfolio_performance = (df_merge['weight'] * df_merge['performance']).sum()
        return portfolio_performance, performance_per_ticker 
    
    # Getter cho thuộc tính
    @property
    def portfolio_stock_df(self):
        return self.stock_df
    
    @property
    def cash_prop(self):
        return self.cash
    
    '''
        ************
        End Utility functions
    '''
        
'''
    Kết thúc định nghĩa class Portfolio
'''


