''' utility functions for vp application
'''
import datetime
import pandas as pd
from  osgeo import gdal
from geopandas import GeoDataFrame, GeoSeries
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
from PIL import Image
import contextily as ctx
from vp_settings import (
    AREA_EASTING_MIN, AREA_EASTING_MAX, AREA_NORTHING_MIN, AREA_NORHING_MAX,
    MapTypes, EPSG_UTM_40N, EPSG_OSM, URL_STAMEN, MAP_FILE,
)


def progress_message_generator(message):
    loop_dash = ['\u2014', '\\', '|', '/']
    i = 1
    print_interval = 1
    while True:
        print(
            f'\r{loop_dash[int(i/print_interval) % 4]} {i} {message}', end='')
        i += 1
        yield


def get_line():
    ASK_LINE = 'Enter line number [q - quit]: '

    while True:
        line = input(ASK_LINE)

        if line in ['q', 'Q']:
            return -1

        try:
            line = int(line)
            if 1000 < line < 2000:
                return line

        except ValueError:
            pass


def get_production_date(question='date (YYMMDD) [q - quit]: '):

    while True:
        _date = input(question)

        if _date in ['q', 'Q']:
            return -1

        try:
            return datetime.datetime(
                int(_date[0:2])+2000, int(_date[2:4]), int(_date[4:6]))

        except ValueError:
            pass

def get_animation_dates():
    valid = False
    pause = None
    interval = 0

    while not valid:
        start = get_production_date(question='start date (YYMMDD) [q - quit]: ')
        if start == -1:
            return -1, -1, 0

        end = get_production_date(question='end date (YYMMDD) [q - quit]: ')
        if end == -1:
            return -1, -1, 0


        if end >= start:
            while not valid:
                try:
                    interval = int(input('Enter time interval in minutes: '))
                    end += datetime.timedelta(1)
                    interval = datetime.timedelta(seconds=interval*60)
                    valid = True

                except ValueError:
                    pass

        else:
            print("End date must be greater equal to start date")

        while valid and pause not in ['y', 'Y', 'n', 'N']:
            pause = input('Pause at end of day [y, n]: ')

        if valid and pause in ['y', 'Y']:
            pause = True

        else:
            pause = False

    return start, end, interval, pause


def get_year(day_of_year):
    split_year_at_day = 180
    if day_of_year > split_year_at_day:
        return 2019

    else:
        return 2020


def convert_ecw_to_tiff(file_name):
    src = gdal.Open(file_name)
    output_file = 'map_test.jpg'

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
        area_gpd.crs = f'epsg:{EPSG_UTM_40N}'

        return area_gpd

    @staticmethod
    def get_vp_gpd(vp_df):
        geometry = [Point(xy) for xy in zip(vp_df.easting, vp_df.northing)]
        crs = f'epsg:{EPSG_UTM_40N}'
        return GeoDataFrame(vp_df, crs=crs, geometry=geometry)

    @classmethod
    def concat_gdf(cls, line_gpd):
        cls.combined_gpd = pd.concat([cls.combined_gpd, line_gpd])

    @classmethod
    def save_combined_gpd(cls, attribute):
        cls.combined_gpd = cls.combined_gpd.drop(columns='time_break')
        cls.combined_gpd.to_file(f'lines_{attribute}.shp')

    @staticmethod
    def convert_to_map(df, maptype):
        if maptype == MapTypes.osm and not df.empty:
            df = df.to_crs(f'epsg:{EPSG_OSM}')

        else:
            pass

        return df

    @staticmethod
    def add_basemap_osm(ax, plot_area, zoom, url=URL_STAMEN):
        basemap, extent = ctx.bounds2img(*plot_area, zoom=zoom, url=url)
        ax.imshow(basemap, extent=extent, interpolation='bilinear')

    @staticmethod
    def add_basemap_local(ax):
        Image.MAX_IMAGE_PIXELS = 2_000_000_000

        # read the map image file and set the extent
        fname_jgW = MAP_FILE[:-4] + '.jgW'
        basemap = plt.imread(MAP_FILE)
        cols = basemap.shape[0]
        rows = basemap.shape[1]

        with open(fname_jgW, 'tr') as jgw:
            dx = float(jgw.readline())
            _ = jgw.readline()  # to do with rotation of the map to be ignored
            _ = jgw.readline()  # to do with rotation of the map to be ignored
            dy = float(jgw.readline())
            x_min = float(jgw.readline())
            y_max = float(jgw.readline())

        x_max = x_min + rows * dx
        y_min = y_max + cols * dy

        ax.imshow(basemap, extent=(x_min, x_max, y_min, y_max), interpolation='bilinear')

    @staticmethod
    def add_colorbar(fig, cmap, minimum, maximum):
        ''' plot the colorbar
            https://stackoverflow.com/questions/36008648/colorbar-on-geopandas
        '''
        cax = fig.add_axes([0.92, 0.2, 0.03, 0.7])
        sm = plt.cm.ScalarMappable(cmap=cmap,
                                   norm=plt.Normalize(vmin=minimum, vmax=maximum))
        sm._A = []  #pylint: disable=protected-access
        fig.colorbar(sm, cax=cax)
