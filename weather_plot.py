import  matplotlib.pyplot as plt
from pathlib import Path
import datetime
import numpy as np
import pandas as pd
from seis_weather_database import WeatherDb

FILTER_THRESHOLD_WIND = 20  # 10
FILTER_THRESHOLD_GUST = 30  # 10
csv_file_full = Path('D:/Onedrive/Desktop/wind_data_full.csv')
csv_file_daily = Path('D:/Onedrive/Desktop/wind_data_daily.csv')


d1 = datetime.datetime(2022, 5, 1)
d2 = datetime.datetime(2022, 12, 31)
weather_db = WeatherDb()
weather_df = weather_db.get_weather_data_by_dates(d1, d2)

previous_wind_speed = 0
previous_wind_gust = 0
wind_gust_series = weather_df['wind_gust'].to_numpy()
wind_speed_series = weather_df['wind_speed'].to_numpy()
new_wind_gust_series = []
new_wind_speed_series = []
for index, wind in enumerate(zip(wind_speed_series, wind_gust_series)):
    wind_speed, wind_gust = wind
    if index == 0:
        previous_wind_speed = wind_speed
        previous_wind_gust = wind_gust
    else:
        if abs(wind_speed - previous_wind_speed) < FILTER_THRESHOLD_WIND:
            previous_wind_speed = wind_speed
        else:
            wind_speed = previous_wind_speed

        if abs(wind_gust - previous_wind_gust) < FILTER_THRESHOLD_GUST:
            previous_wind_gust = wind_gust
        else:
            wind_gust = previous_wind_gust

    new_wind_speed_series.append(wind_speed)
    new_wind_gust_series.append(wind_gust)

wind_speed_series = np.array(new_wind_speed_series)
wind_gust_series = np.array(new_wind_gust_series)

weather_df['wind_speed'] = wind_speed_series
weather_df['wind_gust'] = wind_gust_series
weather_df['date_time'] = pd.to_datetime(weather_df['date_time'])
weather_df.to_csv(csv_file_daily)

df = weather_df.groupby([weather_df['date_time'].dt.date])['temperature'].min().reset_index()
x = df['date_time'].to_numpy()
min_temp_series = df['temperature'].to_numpy()

df = weather_df.groupby([weather_df['date_time'].dt.date])['temperature'].max().reset_index()
max_temp_series = df['temperature'].to_numpy()

df = weather_df.groupby([weather_df['date_time'].dt.date])['wind_speed'].max().reset_index()
max_wind_speed_series = df['wind_speed'].to_numpy()

df = weather_df.groupby([weather_df['date_time'].dt.date])['wind_gust'].max().reset_index()
max_wind_gust_series = df['wind_gust'].to_numpy()

weather_daily_df = pd.DataFrame({
    'date': x,
    'min_temp': min_temp_series,
    'max_temp': max_temp_series,
    'wind_speed': max_wind_speed_series,
    'wind_gust': max_wind_gust_series
})

weather_daily_df.to_csv(csv_file_daily)

fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(15, 10))
ax1.plot(x, max_wind_speed_series)
ax1.plot(x, max_wind_gust_series)
ax2.plot(x, max_temp_series)
ax2.plot(x, min_temp_series)
plt.show()
