#### Xử lỹ lỗi import module
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'StockFiltering'))
sys.path.append(os.path.join(current_dir, 'Algorithm'))

# ####### Nhập các thư viện và module
import pandas as pd
import warnings
from StockFiltering import stock_filter_past as stfp
from Class.portfolioClass import Portfolio
from Algorithm import calculation as cal , weight as wi
from Algorithm import alphas as alp


for trading_year in range(2019, 2022):
    
    ###### Lấy danh sách signals của 5 mã cổ phiếu
    ticker_list = stfp.get_5_ticker(year=trading_year-1)['ticker'].to_list()

    ###### Thiết lập phần trăm danh mục dựa trên weight
    df_combined =  wi.get_combined_df(ticker_list, trading_year)
    weight_df = wi.cal_weight(df_combined, ticker_list)
    weight_df.head()
    
    ###### Khởi tạo portfolio
    my_portfolio = Portfolio(starting_cash=1000000000, ticker_list=ticker_list, df_percentage=weight_df)
    print("### Trading year: ", trading_year)
    print('Initial Portfolio')
    my_portfolio.show_porfolio()

    ###### Tạo dataframe tín hiệu ######
    signal_df = pd.DataFrame(columns=['index', 'time', 'open', 'high', 'low', 'close', 'volume', 'ticker',
                                    'on-balance_volume', 'OBV_label', 'close_t_minus_1', 'bar_type', 'para',
                                    'label_spread', 'close_bar_label', 'signal'])

    for ticker in ticker_list:
        data = cal.DataProcessor.load_data(ticker=ticker, year=trading_year)
        # data = data.set_index('time')
        #Tính trung bình 20 phiên gần nhất
        mean_20 = data['volume'].rolling(window=20).mean()

        #Tính on-balance volume\n",
        data['on-balance_volume'] = data['volume']/mean_20
        data['OBV_label'] = data['on-balance_volume'].apply(cal.DataProcessor.label_values)

        #Giá đóng cửa ngày t-1
        data['close_t_minus_1'] = data['close'].shift(1)
        data['bar_type'] = data.apply(cal.DataProcessor.compare_close_prices, axis=1)
        data['para'] =abs(data['close'] - data['open'])/(data['high'] - data['low'])
        data['label_spread'] = data['para'].apply(cal.DataProcessor.label_spread)
        data['close_bar_label'] = data.apply(cal.DataProcessor.label_close_bar, axis=1)
            
        #tính RSI
        data['delta'] = data['close'] - data['close'].shift(1)
        data['gains'] = data['delta'].where(data['delta'] > 0, 0)
        data['losses'] = -data['delta'].where(data['delta'] < 0, 0)
        data['avg_gain'] = data['gains'].rolling(window=14).mean()
        data['avg_loss'] = data['losses'].rolling(window=14).mean()
        data['rs'] = data['avg_gain'] / data['avg_loss']
        data['RSI'] = 1 - (1 / (1 + data['rs']))

        data['signal'] = data.apply(alp.Alphas.determine_signal, axis=1)
        # data = data[data['signal'] != 'Hold']
        data.reset_index(inplace=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            signal_df = pd.concat([signal_df, data], ignore_index=True)
    signal_df.sort_values(by='time')
    ##########

    ####### Thực hiện xét tín hiệu để giao dịch
    date_performances_df = pd.DataFrame(columns=['date', 'performance']);
    for date, group in signal_df.groupby('time'):
        # print(f'**time {date}')
        for index, row in group.iterrows():
            my_portfolio.validate_transaction(signal_row=row)
        date_performance = my_portfolio.daily_performance()
        date_performances_df.loc[len(date_performances_df)] = [date, date_performance]
        # print('**')
        
    date_performances_df.to_csv(f'Visualization_{trading_year}.csv', index=False)

    print('============== After trading ================')
    my_portfolio.show_porfolio()
    
    portfolio_performance, per_per_tick = my_portfolio.portfolio_performance()
    print('*Total performance', round(portfolio_performance*100, 2), '%')
    print('*List performance per ticker')
    print(per_per_tick)