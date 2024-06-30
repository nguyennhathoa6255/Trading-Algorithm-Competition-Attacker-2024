# import các thư viện cần thiết
import vnstock as vnst
import pandas as pd
import os
from datetime import datetime, timedelta
import warnings

'''
    Utility functions
    
'''
def subtract_weekdays(start_date_str, days_to_subtract):
    # Chuyển đổi chuỗi ngày đầu vào thành đối tượng datetime
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    # Tăng lên một ngày để khi chạy vòng for thì nó sẽ tính cả ngày bắt đầu
    start_date += timedelta(days=1)
        
    # Duyệt qua các ngày để lùi lại
    for _ in range(days_to_subtract):
        # Lùi lại một ngày từ ngày hiện tại
        start_date -= timedelta(days=1)

        # Kiểm tra xem ngày mới có phải là thứ 7 hoặc chủ nhật không
        while start_date.weekday() in [5, 6]:
            start_date -= timedelta(days=1)

    # Trả về ngày cuối cùng sau khi lùi lại
    return start_date.strftime('%Y-%m-%d')

def basic_filter(df):
    # Lọc theo một vài tiêu chí cơ bản
    df2 = df[(df['roe'] >= 0.17) & (df['earningPerShare'] > 2500) & (df['bookValuePerShare'] > 10000)]
    df2.reset_index(drop=True, inplace=True)
    return df2

def pe_smallerThan_pe_avg(df):
    # Tạo dataframe chứa dữ liệu P/E trung bình theo ngành
    df_pe_byIndustry = df.groupby('industry').agg(
        avg_pe = ('priceToEarning', 'mean')
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        # Thêm giá trị trung bình P/E theo ngành cho cột 'pe_avg' của dataframe
        for index, co in df.iterrows():
            # 'co' is a tuple, so we can get the industry name like this
            industryName = co[11] #column index = 11
            # get the pe average value
            df.at[index, 'pe_avg'] =  df_pe_byIndustry.loc[industryName][0]

    result = df[df['priceToEarning'] < df['pe_avg']]
    return result

def volume_largerThan_100K(df, year):
    # ------ Khối lượng trung bình 20 phiên gần nhất của từng cổ phiếu: Volume trung bình > 100 ngàn
    
    # Tạo một df chứa ticker và trung bình Volume của 20 phiên gần nhất
    df_volume = pd.DataFrame(columns=['ticker','volume_average', 'numSession'])
    end_date = f'{year}-07-01'
    start_date = subtract_weekdays(end_date, 20)
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        for index, co in df.iterrows():
            # Tính tổng volume của 20 phiên gần nhất
            stockHisData = vnst.stock_historical_data(symbol=co['ticker'], start_date=start_date, end_date=end_date, resolution="1D", type="stock", beautify=True, decor=False, source='DNSE')        
            mean_volume = stockHisData['volume'].mean()
            df_volume.loc[len(df_volume)] = [co[0], mean_volume, len(stockHisData)]

    # Thêm cột thông tin về trung bình Volume (volume_average) vào dataframe    
    df_merged = pd.merge(df, df_volume[['ticker', 'volume_average']], on='ticker', how='left')

    # Khối lượng giao dịch 20 phiên gần nhất > 100 ngàn
    df_result = df_merged[df_merged['volume_average'] > 100000]
    df_result.reset_index(drop=True, inplace=True)
    return df_result


def stock_filter_past(year):
    # ---- Chuẩn bị dataframe dữ liệu thô
    # Nhập dữ liệu từ file thông tin đã tải xuống của năm 2018
    # và loại bỏ các cột không cần thiết, các dòng trùng lặp (nếu có)
    # Lấy đường dẫn tuyệt đối của file
    current_directory = os.path.dirname(__file__)
    file_name = f'data_Q3-{year}-mergedIndustry.csv'
    file_path = os.path.join(current_directory, file_name)
    df = pd.read_csv(file_path)
    df.drop('Unnamed: 0', axis=1, inplace=True)
    df.drop_duplicates(subset='ticker', keep='first', inplace=True)
    df_dropColumns = df[['ticker', 'quarter', 'year', 'priceToEarning', 'priceToBook', 'roe',
        'roa', 'earningPerShare', 'bookValuePerShare','epsChange','bookValuePerShareChange', 'industry', 'organName', 'equityOnTotalAsset']]
    
    with warnings.catch_warnings():   
        warnings.simplefilter("ignore", category=pd.errors.SettingWithCopyWarning)
        # Thêm cột giá trị P/E trung bình cho dataframe
        df_dropColumns['pe_avg'] = 0
        df_dropColumns.reset_index(drop=True, inplace=True)
    
    print("Filtering data...")
    filter = pe_smallerThan_pe_avg(df_dropColumns)
    filter = basic_filter(filter)
    result = volume_largerThan_100K(df=filter, year=year)
    print("Complete filter data.")
    return result

def read_df5_local():
    current_directory = os.path.dirname(__file__)
    file_path = os.path.join(current_directory, '5_tickers_local.csv')
    df = pd.read_csv(file_path).head(5)
    return df

def get_5_ticker(year):
    five_ticker = stock_filter_past(year=year).sort_values('priceToEarning', ascending=False).head(5)
    return five_ticker