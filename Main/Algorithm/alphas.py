
import pandas as pd
import numpy as np
import vnstock as vn
import calculation as cal

class Alphas():
    # Pattern of Weakness
    # Weakness A
    '''
    - down bar
    - high volume
    - medium or low spread
    - close: middle-third or bottom-third
    '''
    def is_weakness_a_signal(data):
        if (data['bar_type'] == 'down-bar') and \
            (data['OBV_label']=='high') and \
            ((data['label_spread'] == 'low') or (data['label_spread']=='medium')) and \
            ((data['close_bar_label'] == 'middle-third') or (data['close_bar_label']=='bottom-third')):
            return True
        else:
            return False

    # No Demand - Weakness B
        '''
        - up bar
        - volume: low or high
        - spread: low
        - close: bottom-third and middle-third
        '''
    def is_no_demand_signal(data):
        if (data['bar_type'] == 'up-bar') and \
            ((data['OBV_label']=='high') or (data['OBV_label']=='low')) and \
            (data['label_spread'] == 'low') and \
            ((data['close_bar_label'] == 'bottom-third') or data['close_bar_label'] == 'middle-third'):
            return True
        else:
            return False
        

    # Up-trust - Pseudo Up-trust
        '''
        - up bar or down bar 
        - high spread
        - close: bottom-third
        - high or low volume
        '''

    def is_up_trust_signal(data):
        if ((data['OBV_label']=='high') or (data['OBV_label']=='low')) and \
            (data['label_spread'] == 'high') and \
            ((data['close_bar_label'] == 'bottom-third') ):
            return True
        else:
            return False

    # Stop volume
        '''
        - up bar
        - high spread
        - high volume 
        '''
    def is_stop_volume_signal(data):
        if (data['bar_type']=='up-bar') and \
            (data['OBV_label']=='high') and \
            (data['label_spread'] == 'high'):
            return True
        else:
            return False
        
    # Power pattern

    # Power A
        '''
        - up bar
        - medium spread
        - medium or high volume
        - close: top-third
        '''
    def is_power_A_signal(data):
        if (data['bar_type'] == 'up-bar') and \
            (data['label_spread'] == 'medium') and \
            ((data['OBV_label']=='medium') or (data['OBV_label'] == 'low')) and \
            (data['close_bar_label'] == 'top-third'):
            return True
        else:
            return False
        
    # Power B - Lack of order
        '''
        - down bar 
        - low spread 
        - low or high volume
        - close: top-third or bottom-third
        '''
    def is_power_B_signal(data):
        if (data['bar_type'] == 'down-bar') and \
            (data['label_spread'] == 'low') and \
            ((data['OBV_label']=='low') or (data['OBV_label'] == 'high')) and \
            ((data['close_bar_label'] == 'top-third') or (data['close_bar_label'] == 'bottom-third')):
            return True
        else:
            return False

    # Reverse Up-Trust - Pseudo Up-trust
        '''
        - up bar or down bar 
        - high spread
        - close: bottom-third
        - high and low volume
        '''
    def is_reverse_up_trust_signal(data):
        if ((data['bar_type'] == 'down-bar') or (data['bar_type']) == 'up-bar') and \
            (data['label_spread'] == 'high') and \
            ((data['OBV_label']=='low') or (data['OBV_label'] == 'high')) and \
            (data['close_bar_label'] == 'bottom-third'):
            return True
        else:
            return False
        
    # Stopped Volume
        '''
        - down bar
        - low spread
        - close: middle-third
        - high volume
        '''
    def is_stopped_volume_signal(data):
        if (data['bar_type'] == 'down-bar') and \
            (data['label_spread'] == 'low') and \
            (data['OBV_label'] == 'high') and \
            (data['close_bar_label'] == 'middle-third'):
            return True
        else:
            return False

    def get_rsi_signal(data):
        if data['RSI'] > 0.7:
            return False
        elif data['RSI'] < 0.3:
            return True   

    def ssma(data, period, sensitivity):
        sma = np.mean(data[:period])  # Tính toán moving average ban đầu
        ssma_values = [sma]  # Danh sách để lưu trữ giá trị SSMA
    
        for i in range(period, len(data)):
            # Tính toán độ nhạy cảm (sensitivity factor)
            sensitivity_factor = (i / period) ** sensitivity
            
            # Cập nhật giá trị SSMA bằng cách áp dụng độ nhạy cảm vào moving average
            ssma = sma + sensitivity_factor * (data[i] - sma)
            
            # Thêm giá trị SSMA vào danh sách
            ssma_values.append(ssma)
            
            # Cập nhật giá trị moving average cho vòng lặp tiếp theo
            sma = ssma
    
        return ssma_values

    def determine_signal(row):
        if (Alphas.is_weakness_a_signal(row) or Alphas.is_no_demand_signal(row) or Alphas.is_up_trust_signal(row) or Alphas.is_stop_volume_signal(row)) and (Alphas.get_rsi_signal(row)==  True):
            return 'Sell'
        elif (Alphas.is_power_A_signal(row) or Alphas.is_power_B_signal(row) or Alphas.is_reverse_up_trust_signal(row) or Alphas.is_stopped_volume_signal(row)) and (Alphas.get_rsi_signal(row) == False):
            return 'Buy'
        else:
            return 'Hold'
    
