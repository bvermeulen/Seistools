''' vp_plot mapping of vp locations
'''
import sys
import matplotlib.pyplot as plt
from vp_settings import MapTypes, plt_settings
from vp_utils import MapTools
from vp_database import VpDb

FIGSIZE = (7, 7)
EDGECOLOR = 'black'
ZOOM = 10
MARKERSIZE = 0.2
cmap = 'coolwarm'

vp_db = VpDb()
maptools = MapTools()

class PlotMap:
    ''' method to setup map and plot vp's
    '''
    @classmethod
    def setup_map(cls, attribute, maptype=MapTypes.no_background):
        cls.attribute = attribute
        cls.maptype = maptype

        cls.fig, cls.ax = plt.subplots(figsize=FIGSIZE)
        area_bnd_gpd = maptools.get_area()
        area_bnd_gpd.plot(ax=cls.ax, facecolor='none', edgecolor=EDGECOLOR)

        extent_map = cls.ax.axis()
        plot_area = (extent_map[0], extent_map[2], extent_map[1], extent_map[3])

        if cls.maptype == MapTypes.local:
            maptools.add_basemap_local(cls.ax)

        elif cls.maptype == MapTypes.osm:
            maptools.add_basemap_osm(cls.ax, plot_area, ZOOM)

        else:
            pass

        cls.ax.axis(extent_map)
        cls.background = cls.fig.canvas.copy_from_bbox(cls.fig.bbox)

        maptools.add_colorbar(cls.fig, cmap,
                              plt_settings[cls.attribute]['min'],
                              plt_settings[cls.attribute]['max'],
                             )
        cls.ax.set_title(f'Block 42: {plt_settings[cls.attribute]["title_attribute"]}')

    @classmethod
    def plot_attribute(cls, line):
        vp_df = vp_db.get_vp_data_by_line(line)
        vp_gdf = maptools.get_vp_gpd(vp_df)

        minimum = plt_settings[cls.attribute]['min']
        maximum = plt_settings[cls.attribute]['max']

        vp_gdf.plot(
            ax=cls.ax,
            column=cls.attribute,
            cmap=cmap,
            vmin=minimum,
            vmax=maximum,
            markersize=MARKERSIZE
        )

        cls.blit()

    @classmethod
    def blit(cls):
        cls.fig.canvas.restore_region(cls.background)
        plt.draw()
        cls.fig.canvas.blit(cls.fig.bbox)

    @staticmethod
    def show():
        plt.show()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        attribute = sys.argv[1]

    else:
        attribute = 'elevation'

    plot = PlotMap()
    plot.setup_map(attribute, maptype=MapTypes.no_background)
    lines = [1001, 1010, 1008, 1028, 1007, 1004, 1002, 1003, 1009]
    for line in lines:
        plot.plot_attribute(line)

    plot.show()
