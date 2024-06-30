# Xử lỹ lỗi import module
import plotly.graph_objects as go
import streamlit as st
from datetime import date
import vnstock as vn
import pandas as pd

import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'StockFiltering'))
sys.path.append(os.path.join(current_dir, 'Algorithm'))
sys.path.append(os.path.join(current_dir, 'Chart'))

# Nhập các thư viện và module
from StockFiltering import stock_filter_past as stfp
from Class.portfolioClass import Portfolio
from Algorithm import calculation as cal
from Algorithm import alphas as alp
from Algorithm import weight as wi

#-------------------------------

st.subheader('Algorithm Visualization - Stack Overflow')

@st.cache_data #Lưu dữ liệu khi tải lên streamlit

def get_year(year):
    if year == 2019:
        stocks = ('VNM','PLX','MSN','VCB','MWG')
    elif year == 2020:
        stocks = ('GAS','TCB','PHR','QNS','NT2')
    elif year == 2021:     
        stocks = ('MWG','PHR','VCG','QNS','FMC')
    return stocks

selected_year = st.selectbox('Select year', [2019,2020,2021])

tab1, tab2, tab3= st.tabs(["Buy and sell signals", "Portfolio performance", "Weight in portfolio"])

with tab1:
    stocks = get_year(selected_year)
    selected_stock = st.selectbox('Select stock', stocks)
    data = cal.DataProcessor.load_data(selected_stock, year=selected_year)

    # stock_list = vn.listing_companies()
    stock_list = pd.DataFrame(vn.listing_companies())
    index = stock_list['ticker'].tolist().index(selected_stock)
    organ_name = stock_list['organName'].iloc[index]


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
    # data.reset_index(inplace=True)
    signal_counts = data['signal'].value_counts()

    #------------

    def plot_buy_sell_signal(data, selected_stock, selected_year):
        fig = go.Figure()

        # Vẽ biểu đồ dựa trên tín hiệu mua bán
        buy_signals = data[data['signal'] == 'Buy']
        sell_signals = data[data['signal'] == 'Sell']
        hold_signals = data[data['signal'] == 'Hold']

        # Lọc dữ liệu theo năm được chọn
        filtered_buy_signals = buy_signals[pd.DatetimeIndex(buy_signals['time']).year == selected_year]
        filtered_sell_signals = sell_signals[pd.DatetimeIndex(sell_signals['time']).year == selected_year]
        # filtered_hold_signals = hold_signals[pd.DatetimeIndex(hold_signals['time']).year == selected_year]

        # Tạo DataFrame mới
        signal_data = {'Buy': [len(filtered_buy_signals)], 'Sell': [len(filtered_sell_signals)]}
        signal_df = pd.DataFrame(signal_data)
        signal_df = signal_df.rename(index={0: 'Quantity'})

        # Vẽ biểu đồ
        fig.add_trace(go.Scatter(x=data['time'], y=data['close'], mode='lines', name='Closing Price'))
        fig.add_trace(go.Scatter(x=filtered_buy_signals['time'], y=filtered_buy_signals['close'], mode='markers', name='Buy', marker=dict(color='green', symbol='triangle-up')))
        fig.add_trace(go.Scatter(x=filtered_sell_signals['time'], y=filtered_sell_signals['close'], mode='markers', name='Sell', marker=dict(color='red', symbol='triangle-down')))

        # Cấu hình biểu đồ
        fig.update_layout(title=f'Buy and sell signals for {selected_stock}: {organ_name}', xaxis_title='Time', yaxis_title='Closing Price')  
        st.write(signal_df)
        return fig

    # Gọi hàm plot_buy_sell_signal với tham số selected_year được truyền từ years
    filtered_fig = plot_buy_sell_signal(data, selected_stock, selected_year)
    st.plotly_chart(filtered_fig, use_container_width=True)

with tab2:

    START = f"{selected_year}-01-01"
    END = f"{selected_year+1}-02-01"
    vnindex = vn.stock_historical_data("VNINDEX", START, END, type="index", source='TCBS')
    vnindex['performance_vnindex'] = 100 * (vnindex['close'] - vnindex['close'].iloc[0]) / (vnindex['close'].iloc[0])
    vnindex1 = vnindex[['time', 'performance_vnindex']]
    vnindex1['time'] = pd.to_datetime(vnindex1['time'])


    date_performances_df = pd.read_csv(f'Chart/Visualization_{selected_year}.csv')
    date_performances_df = date_performances_df.rename(columns={'date' : 'time'})
    date_performances_df['performance'] = (date_performances_df['performance'] - 1) * 100
    date_performances_df['time'] = pd.to_datetime(date_performances_df['time'])
    merge_port_vnindex = pd.merge(date_performances_df, vnindex1, on='time', how="inner")
    # st.write(vnindex1)
    # st.write(date_performances_df)
    # st.write(merge_port_vnindex)
 
    def plot_performance_comparison(df):
        # Tạo figure và các trace cho biểu đồ
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['time'], y=df['performance'], name='Portfolio'))
        fig.add_trace(go.Scatter(x=df['time'], y=df['performance_vnindex'], name='VNINDEX'))

        # Cấu hình layout của biểu đồ
        fig.update_layout(
            title='Portfolio performance vs VNINDEX performance',
            xaxis_title='Time',
            yaxis_title='Performance',
            # legend=dict(x=0, y=1),
            # autosize=False,
            # width=800,
            # height=400
        )
        return fig

    st.plotly_chart(plot_performance_comparison(merge_port_vnindex))


#---Tab3
with tab3:
    col1, col2 = st.columns([0.3, 0.7])
    df_combined =  wi.get_combined_df(get_year(selected_year), selected_year)
    weight_df = wi.cal_weight(df_combined, get_year(selected_year))
    with col1:
        weight_df = weight_df.rename(columns={'percentage':'weight'})
        st.write(weight_df)
    with col2:
        def plot_pie_chart(df):
            # Tạo figure cho biểu đồ Pie Chart
            fig = go.Figure(data=[go.Pie(labels=df['ticker'], values=df['weight'])])
            # Cấu hình layout của biểu đồ
            fig.update_layout(
                title=f'Weight in {selected_year} portfolio',
                autosize=False,
                width=400,
                height=500
            )
            return fig
        st.plotly_chart(plot_pie_chart(weight_df))
#-------------