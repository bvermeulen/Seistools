""" utility functions for vp application
"""
import warnings
import sys
import datetime
import numpy as np
import pandas as pd
from ntplib import NTPClient
from progress.bar import Bar
from osgeo import gdal
from geopandas import GeoDataFrame, GeoSeries
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
from PIL import Image
import contextily as ctx
from seis_settings import (
    AREA_EASTING_MIN,
    AREA_EASTING_MAX,
    AREA_NORTHING_MIN,
    AREA_NORHING_MAX,
    MapTypes,
    EPSG_UTM_40N,
    EPSG_OSM,
    URL_STAMEN,
    MAP_FILE,
    EXPIRY_DATE,
)

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

        if line in ["q", "Q"]:
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

        if _date in ["q", "Q"]:
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


def convert_ecw_to_tiff(file_name):
    src = gdal.Open(file_name)
    output_file = "map_test.jpg"

    src = gdal.Translate(output_file, src)


class MapTools:
    combined_gpd = GeoDataFrame()

    @staticmethod
    def get_area():
        p1 = (AREA_EASTING_MIN, AREA_NORHING_MAX)
        p2 = (AREA_EASTING_MAX, AREA_NORHING_MAX)
        p3 = (AREA_EASTING_MAX, AREA_NORTHING_MIN)
        p4 = (AREA_EASTING_MIN, AREA_NORTHING_MIN)
        area_polygon = Polygon([p1, p2, p3, p4])
        area_gpd = GeoDataFrame(geometry=GeoSeries(area_polygon))
        area_gpd.crs = f"epsg:{EPSG_UTM_40N}"

        return area_gpd

    @staticmethod
    def get_vp_gpd(vp_df):
        geometry = [Point(xy) for xy in zip(vp_df.easting, vp_df.northing)]
        crs = f"epsg:{EPSG_UTM_40N}"
        return GeoDataFrame(vp_df, crs=crs, geometry=geometry)

    @classmethod
    def concat_gdf(cls, line_gpd):
        cls.combined_gpd = pd.concat([cls.combined_gpd, line_gpd])

    @classmethod
    def save_combined_gpd(cls, attribute):
        cls.combined_gpd = cls.combined_gpd.drop(columns="time_break")
        cls.combined_gpd.to_file(f"lines_{attribute}.shp")

    @staticmethod
    def convert_to_map(df, maptype):
        if maptype == MapTypes.osm and not df.empty:
            df = df.to_crs(f"epsg:{EPSG_OSM}")

        else:
            pass

        return df

    @staticmethod
    def add_basemap_osm(ax, plot_area, zoom, url=URL_STAMEN):
        basemap, extent = ctx.bounds2img(*plot_area, zoom=zoom, url=url)
        ax.imshow(basemap, extent=extent, interpolation="bilinear")

    @staticmethod
    def add_basemap_local(ax):
        Image.MAX_IMAGE_PIXELS = 2_000_000_000

        # read the map image file and set the extent
        fname_jgW = MAP_FILE[:-4] + ".jgW"
        basemap = plt.imread(MAP_FILE)
        cols = basemap.shape[0]
        rows = basemap.shape[1]

        with open(fname_jgW, "tr") as jgw:
            dx = float(jgw.readline())
            _ = jgw.readline()  # to do with rotation of the map to be ignored
            _ = jgw.readline()  # to do with rotation of the map to be ignored
            dy = float(jgw.readline())
            x_min = float(jgw.readline())
            y_max = float(jgw.readline())

        x_max = x_min + rows * dx
        y_min = y_max + cols * dy

        ax.imshow(
            basemap, extent=(x_min, x_max, y_min, y_max), interpolation="bilinear"
        )

    @staticmethod
    def add_colorbar(fig, cmap, minimum, maximum):
        """plot the colorbar
        https://stackoverflow.com/questions/36008648/colorbar-on-geopandas
        """
        cax = fig.add_axes([0.92, 0.2, 0.03, 0.7])
        sm = plt.cm.ScalarMappable(
            cmap=cmap, norm=plt.Normalize(vmin=minimum, vmax=maximum)
        )
        sm._A = []  # pylint: disable=protected-access
        fig.colorbar(sm, cax=cax)
