''' utility functions for vp application
'''
import datetime

def progress_message_generator(message):
    loop_dash = ['\u2014', '\\', '|', '/']
    i = 1
    print_interval = 1
    while True:
        print(
            f'\r{loop_dash[int(i/print_interval) % 4]} {i} {message}', end='')
        i += 1
        yield


def get_production_date():
    ASK_DATE = 'date (YYMMDD) [q - quit]: '

    while True:
        _date = input(ASK_DATE)

        if _date in ['q', 'Q']:
            return -1

        try:
            return datetime.datetime(
                int(_date[0:2])+2000, int(_date[2:4]), int(_date[4:6]))
        except ValueError:
            pass

def get_year(day_of_year):
    split_year_at_day = 180
    if day_of_year > split_year_at_day:
        return 2019

    else:
        return 2020
