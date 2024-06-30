import pandas as pd
import numpy as np
import vnstock as vn
from configparser import ConfigParser


transactions_df = pd.DataFrame({
    'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
    'Stock': ['AAPL', 'GOOGL', 'MSFT', 'AAPL'],
    'Action': ['Buy', 'Buy', 'Sell', 'Sell'],
    'Quantity': [100,200,500,300],
    'Price': [150, 2500, 200, 160]
})

recent_prices_df = pd.DataFrame({
    'Stock': ['AAPL', 'GOOGL', 'MSFT'],
    'Price': [155, 2600, 210]
})

portfolio_df = pd.DataFrame({
    'Stock': ['AAPL', 'GOOGL'],
    'Quantity': [100, 200]
})

def get_recent_price(stock_name):
    recent_price = recent_prices_df.loc[recent_prices_df['Stock'] == stock_name, 'Price'].values[0]
    return recent_price

def calculate_daily_returns(transactions_df, recent_prices_df):
    merged_df = pd.merge(transactions_df, recent_prices_df, on='Stock', how='left')
    merged_df['Daily Return'] = merged_df.groupby('Stock')['Price'].pct_change()
    daily_returns_df = merged_df[['Date', 'Stock', 'Daily Return']]
    return daily_returns_df

def cal_portfolio_daily_return(transactions_df,recent_prices_df, portfolio_df):
    daily_returns_df = calculate_daily_returns(transactions_df, recent_prices_df)
    merged_df = pd.merge(daily_returns_df, portfolio_df, on='Stock', how='inner')
    merged_df['Weighted Return'] = merged_df['Daily Return'] * merged_df['Quantity']
    total_weighted_return = merged_df['Weighted Return'].sum()
    total_portfolio_quantity = merged_df['Quantity'].sum()
    mean_return = total_weighted_return / total_portfolio_quantity
    return mean_return

def cal_port_current_value(portfolio_df, current_prices):
    initial_value = 123

    for asset, quantity in portfolio_df.items():
        price = current_prices.get(asset, 0)
        asset_value = price*quantity
        current_value += asset_value
    return current_value

def record_action(portfolio_df, transactions_df):
    for index, action in transactions_df.interrows():
        date = transactions_df['Date']
        stock = transactions_df['Stock']
        action = transactions_df['Action']
        quantity = transactions_df['Quantity']
        price = transactions_df['Price']

        stock_row = portfolio_df.loc[portfolio_df['Stock']== stock]

        if action == 'Buy':
            if not stock_row.empty:
                portfolio_df.loc[portfolio_df['Stock'] == stock, 'Quantity'] += quantity
            else:
                portfolio_df = portfolio_df.append({'Stock': stock, 'Quantity': quantity, 'Price': price}, ignore_index = True)
        elif action == 'Sell':
            if not stock_row.empty:
                portfolio_df.loc[portfolio_df['Stock']== stock, 'Quantity']-= quantity
                if portfolio_df.loc[portfolio_df['Stock'] == stock, 'Quantity'].values[0] <= 0:
                    portfolio_df = portfolio_df[portfolio_df['Stock'] != stock]
        return portfolio_df

def buy_stock(stock, quantity):
    '''
    quantity
    price
    order
    stock
    '''
    print(f"Buying {quantity} shares of {stock}")


def sell_stock(stock, quantity):
    '''
    quantity
    price
    order
    stock
    '''
    print(f"Selling {quantity} shares of {stock}")

def read_config(file_path='config/config.ini'):
    config = ConfigParser()
    config.read(file_path)
    return config['main']

def execute_orders():
    config = read_config()
    client_id = config['CLIENT_ID']
    redirect_url = config['REDIRECT_URL']
    json_path = config['JSON_PATH']
    account_number = config['ACCOUNT_NUMBER']

    buy_stock('AAPL', 100)
    sell_stock('GOOGL', 200)

if __name__ == "__main__":
    execute_orders()