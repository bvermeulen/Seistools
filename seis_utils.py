""" utility functions for vp application
"""
import warnings
import sys
import datetime
import numpy as np
from ntplib import NTPClient
from progress.bar import Bar
from seis_settings import EXPIRY_DATE

warnings.simplefilter(action="ignore", category=FutureWarning)


def set_progress_bar(max_value, filename, skip_factor):
    return Bar(
        f"reading {max_value:,} records " f"from {filename}",
        max=int(1 / skip_factor * max_value),
        suffix="%(percent)d%%",
    )


def progress_message_generator(message):
    print()
    loop_dash = ["\u2014", "\\", "|", "/"]
    i = 1
    print_interval = 1
    while True:
        print(f"\r{loop_dash[int(i/print_interval) % 4]} {i} {message}", end="")
        i += 1
        yield


def status_message_generator(key):
    MODULUS = 10
    status_lines = {
        "Wait": "Please wait ...",
        "Load": "Load data",
        "VpAttr": "VP attributes",
        "VpHist": "VP histograms",
        "VpErr": "VP error bars",
        "ActAll": "Activity all",
        "ActEach": "Activity each",
        "Done": "Done",
        "Error": "Error getting data",
    }
    current_key = None
    progress_dots = "."
    progress_done = "...   done"
    count = 0
    status_message = ""
    while True:
        if key == current_key:
            if key not in ["Wait", "Done"]:
                status_message = "\n".join(status_message.split("\n")[:-1])
                status_message = "\n".join(
                    [
                        status_message,
                        "".join(
                            [status_lines[current_key], progress_dots * (count + 1)]
                        ),
                    ]
                )
                count = (count + 1) % MODULUS

        else:
            if key not in ["Wait", "Done", "Error"]:
                if current_key not in ["Wait", "Done"]:
                    status_message = "\n".join(status_message.split("\n")[:-1])
                    status_message = "\n".join(
                        [
                            status_message,
                            "".join([status_lines[current_key], progress_done]),
                            "".join([status_lines[key], progress_dots]),
                        ]
                    )

                else:
                    status_message = "\n".join(
                        [status_message, "".join([status_lines[key], progress_dots])]
                    )

                count = 0

            elif key == "Wait":
                status_message = "".join([status_message, status_lines[key]])

            elif key == "Done":
                status_message = "\n".join(status_message.split("\n")[:-1])
                status_message = "\n".join(
                    [
                        status_message,
                        "".join([status_lines[current_key], progress_done]),
                        status_lines[key],
                    ]
                )
                status_message = "\n".join(status_message.split("\n")[1:])

            elif key == "Error":
                status_message = status_lines[key]

            else:
                assert False, f"Key {key} is invalid"

            current_key = key

        received = yield status_message
        key = key if received is None else received


def get_line():
    ASK_LINE = "Enter line number [q - quit]: "

    while True:
        line = input(ASK_LINE)

        if line[0].lower() == "q":
            return -1

        try:
            line = int(line)
            if 1000 < line < 2000:
                return line

        except ValueError:
            pass


def check_expiry_date():
    client = NTPClient()
    response = client.request("europe.pool.ntp.org", version=3)
    date_today = datetime.datetime.fromtimestamp(response.tx_time).date()
    if date_today > EXPIRY_DATE:
        input(f'error, your license has expired on {EXPIRY_DATE.strftime("%d %b %Y")}')
        sys.exit()

    elif date_today + datetime.timedelta(days=15) > EXPIRY_DATE:
        print(
            f'warning, your license will expire on {EXPIRY_DATE.strftime("%d %b %Y")}'
        )


def get_production_date(question="date (YYMMDD) [q - quit]: "):
    while True:
        _date = input(question)

        if _date[0].lower() == "q":
            return -1

        try:
            return datetime.datetime(
                int(_date[0:2]) + 2000, int(_date[2:4]), int(_date[4:6])
            )

        except ValueError:
            pass


def get_animation_dates():
    valid = False
    pause = None
    interval = 0

    while not valid:
        start = get_production_date(question="start date (YYMMDD) [q - quit]: ")
        if start == -1:
            return -1, -1, 0, True

        end = get_production_date(question="end date (YYMMDD) [q - quit]: ")
        if end == -1:
            return -1, -1, 0, True

        if end >= start:
            while not valid:
                try:
                    interval = int(input("Enter time interval in minutes: "))
                    end += datetime.timedelta(1)
                    interval = datetime.timedelta(seconds=interval * 60)
                    valid = True

                except ValueError:
                    pass

        else:
            print("End date must be greater equal to start date")

        while valid and pause not in ["y", "Y", "n", "N"]:
            pause = input("Pause at end of day [y, n]: ")

        if valid and pause in ["y", "Y"]:
            pause = True

        else:
            pause = False

    return start, end, interval, pause


def get_year(day_of_year):
    current_date = datetime.datetime.now()
    year = current_date.year
    month = current_date.month

    if month < 7:
        if day_of_year < 190:
            return year
        else:
            return year - 1

    else:
        if day_of_year > 170:
            return year
        else:
            return year + 1


def set_val(value, dtype):
    try:
        if dtype == "str":
            return str(int(value))

        elif dtype == "int":
            return int(value)

        elif dtype == "float":
            return float(value)

        elif dtype == "bool":
            return bool(value)

        elif dtype == "date":
            try:
                return value.strftime("%Y-%m-%d")

            except AttributeError:
                return np.datetime_as_string(value, unit="D")

        elif dtype == "time":
            try:
                return value.strftime("%H:%M:%S")

            except AttributeError:
                return value

        else:
            return value

    except (TypeError, ValueError):
        return value
