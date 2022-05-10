''' module to update weather record files in the database
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    Copyright: 2022
'''
import warnings
import datetime
import pandas as pd
from seis_weather_database import WeatherDb
from seis_settings import DATA_FILES_WEATHER, FilesWeatherTable, WeatherTable

# ignore warning velocity =  dist / time in method update_vo_distance
warnings.filterwarnings("ignore", category=RuntimeWarning)


class Weather:
    ''' class for reading and parsing weather information and store the data
        in the production database
    '''
    weather_base_folder = DATA_FILES_WEATHER
    weather_db = WeatherDb()

    @classmethod
    def read_store_weather(cls):
        for filename in cls.weather_base_folder.glob('*.*'):
            if not filename.is_file() or filename.suffix.lower() != '.csv':
                continue

            weather_file = FilesWeatherTable(*[None]*2)

            weather_file.file_name = filename.name
            weather_file.file_date = (
                datetime.datetime.fromtimestamp(filename.stat().st_mtime)
            )
            file_id = cls.weather_db.update_weather_file(weather_file)

            if file_id == -1:
                continue

            weather_df = pd.read_csv(
                    filename, skiprows=1,
                    usecols=[0, 1, 2, 3, 10, 14, 17],
                    names=[
                        'date_time', 'wind_speed', 'gust', 'pulse_count',
                        'counter_value', 'input_voltage', 'temperature'
                    ]
                )
            weather_df.date_time = pd.to_datetime(weather_df.date_time)

            weather_records = []
            for _, weather_row in weather_df.iterrows():
                weather_record = WeatherTable(*[None]*8)
                weather_record.file_id = file_id
                weather_record.date_time = weather_row.date_time.to_pydatetime()
                weather_record.wind_speed = weather_row.wind_speed
                weather_record.gust = weather_row.gust
                weather_record.pulse_count = weather_row.pulse_count
                weather_record.counter_value = weather_row.counter_value
                weather_record.input_voltage = weather_row.input_voltage
                weather_record.temperature = weather_row.temperature
                weather_records.append(weather_record)

            if weather_records:
                cls.weather_db.update_weather_records(weather_records)


if __name__ == '__main__':
    weather_db = WeatherDb()
    weather_db.create_table_weather_files()
    weather_db.create_table_weather_data()
    Weather().read_store_weather()
