''' utility functions for vp application
'''
import datetime
from geopandas import GeoDataFrame, GeoSeries
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
from PIL import Image
import contextily as ctx
from vp_settings import (
    AREA_EASTING_MIN, AREA_EASTING_MAX, AREA_NORTHING_MIN, AREA_NORHING_MAX,
    MapTypes, EPSG_UTM_40N, EPSG_WGS84, EPSG_OSM,
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

class MapTools:

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

    @staticmethod
    def convert_to_map(df, maptype):
        if maptype == MapTypes.osm and not df.empty:
            df = df.to_crs(f'epsg:{EPSG_OSM}')

        else:
            pass

        return df

    @staticmethod
    def add_basemap_osm(
            ax, plot_area, zoom,
            url='http://tile.stamen.com/terrain/{z}/{x}/{y}.png'):

        basemap, extent = ctx.bounds2img(*plot_area, zoom=zoom, url=url)
        ax.imshow(basemap, extent=extent, interpolation='bilinear')

    @staticmethod
    def add_basemap_local(ax):
        MAP_FILE = r'BackgroundMap/3D_31256.jpg'
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
