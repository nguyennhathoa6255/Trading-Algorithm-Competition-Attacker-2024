# Nhập các thư viện cần thiết trong quá trình thực hiện
import vnstock as vnst
import pandas as pd
import numpy as np
import cvxpy as cp
from datetime import datetime, timedelta
import warnings

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

def get_combined_df(list_stock, trading_year):    
    symbols = list_stock
    end_date = f"{trading_year}-01-01"
    start_date = subtract_weekdays(end_date, 180)
    historical_data = {}

    for symbol in symbols:
        historical_data[symbol] = vnst.stock_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            # type=type
        )

    # Gộp các DataFrame trong danh sách theo cột 'close'
    df_combined = pd.concat([historical_data[symbol]['close'] for symbol in symbols], axis=1)

    # Đặt tên cột mới
    df_combined.columns = symbols
    return df_combined

def covariance_matrix(corr_matrix, volatility):
    n = len(volatility)
    cov_matrix = np.zeros((n, n))
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        for i in range(n):
            for j in range(n):
                cov_matrix[i, j] = corr_matrix.iloc[i, j] * volatility[i] * volatility[j]  # Changed corr_matrix[i, j] to corr_matrix.iloc[i, j]
    return cov_matrix

def objective(x, cov_matrix):
    return cp.quad_form(x, cov_matrix)

def cal_weight(df_combined, list_stock):
    days_return_3days = df_combined / df_combined.shift(3) - 1
    days_return_3days.dropna(inplace=True)
    # returns_20 = days_return_3days.head(20).mean()
    # returns_60 = days_return_3days.tail(60).mean()
    volatility = np.std(days_return_3days.tail(20))
    corr_matrix = df_combined.corr()

    cov_matrix = covariance_matrix(corr_matrix, volatility)
    num_assets = cov_matrix.shape[0]
    x = cp.Variable(num_assets)
    objective_func = cp.Minimize(cp.quad_form(x, cov_matrix))
    constraints = [
        cp.sum(x) == 1,  # a + b + c + d + e = 1
        x >= 0.05,  # a, b, c, d, e >= 0.05
        # cp.matmul(returns_20.values, x) >= 0,  # Lớn hơn hoặc bằng 0
        # cp.matmul(returns_60.values, x) >= 0  # Lớn hơn hoặc bằng 0
    ]
    problem = cp.Problem(objective_func, constraints)
    weight_df = problem.solve()
    weight_df = pd.DataFrame({'ticker': list_stock,'weight': x.value}).round(4)
    weight_df = weight_df.map(lambda x: 0.00 if x == -0.00 else x)
    return weight_df


