import pandas as pd
import numpy as np
import os

def create_sample_csv():
    """Generates a sample OHLCV CSV file for testing."""
    if not os.path.exists('data/raw'):
        os.makedirs('data/raw')
        
    dates = pd.to_datetime(pd.date_range(start='2023-01-01', periods=500, freq='D'))
    price = 100
    
    data = []
    for date in dates:
        open_price = price + np.random.uniform(-1, 1)
        high = open_price + np.random.uniform(0, 2)
        low = open_price - np.random.uniform(0, 2)
        close = np.random.uniform(low, high)
        volume = np.random.randint(100000, 5000000)
        data.append([date, open_price, high, low, close, volume])
        price = close

    df = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df.to_csv('data/raw/SAMPLE.csv', index=False)
    print("Created 'data/raw/SAMPLE.csv' for testing.")

if __name__ == '__main__':
    create_sample_csv()