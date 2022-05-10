from seis_weather_database import WeatherDb
import  matplotlib.pyplot as plt
import datetime
intval = 15
d1 = datetime.datetime(2021, 12, 1)
d2 = datetime.datetime(2022, 3, 12)
weather_db = WeatherDb()
weather_df = weather_db.get_weather_data_by_dates(d1, d2)
x = weather_df['date_time'].to_list()[::intval]
y1 = weather_df['temperature'].to_list()[::intval]
y2 = weather_df['wind_speed'].to_list()[::intval]
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(15, 10))
ax1.plot(x, y1)
ax2.plot(x, y2)
plt.show()
