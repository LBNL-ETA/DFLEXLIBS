import requests
import pandas as pd

def get_CFH_rate(url):
    r = requests.get(url)
    price_dict = r.json()
    interval_prices = price_dict.get('prices')
    start_str = price_dict.get('timeOfFirstPriceLocal')
    start_ts = pd.Timestamp(start_str)
    interval_prices.insert(0, {'duration':'00:00:00'})
    df = pd.DataFrame(interval_prices)
    df.duration = pd.to_timedelta(df.duration)
    df['end_time'] = start_ts + df.duration.cumsum()
    hourly_df = df.set_index('end_time').resample('60T').bfill().reset_index()
    hourly_df['start_time'] = hourly_df['end_time'] - hourly_df['end_time'].diff()
    hourly_df = hourly_df.drop(index = 0)
    return hourly_df.set_index('start_time')