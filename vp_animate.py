''' vp_plot mapping of vp locations
'''
import sys
import datetime
import matplotlib.pyplot as plt
from vp_settings import MapTypes, plt_settings
from vp_utils import MapTools
from vp_database import VpDb

FIGSIZE = (7, 7)
EDGECOLOR = 'black'
ZOOM = 10
MARKERSIZE = 0.2
cmap = 'coolwarm'
evening_close = datetime.time(13, 0, 0)

vp_db = VpDb()
maptools = MapTools()

class PlotMap:
    ''' method to setup map and plot vp's
    '''
    def __init__(self, attribute, start_time, end_time, time_interval,
                 maptype=MapTypes.no_background):
        self.attribute = attribute
        self.maptype = maptype
        self.run_time = start_time
        self.end_time = end_time
        self.time_interval = time_interval
        self.animation_started = False
        self.date_gid = None

        self.vp_df = vp_db.get_vp_data_by_time(self.run_time, self.end_time)

        self.fig, self.ax = plt.subplots(figsize=FIGSIZE)
        area_bnd_gpd = maptools.get_area()
        area_bnd_gpd = maptools.convert_to_map(area_bnd_gpd, self.maptype)
        area_bnd_gpd.plot(ax=self.ax, facecolor='none', edgecolor=EDGECOLOR)

        connect = self.fig.canvas.mpl_connect
        connect('button_press_event', self.on_click)
        connect('key_press_event', self.on_key)

        extent_map = self.ax.axis()
        plot_area = (extent_map[0], extent_map[2], extent_map[1], extent_map[3])

        if self.maptype == MapTypes.local:
            maptools.add_basemap_local(self.ax)

        elif self.maptype == MapTypes.osm:
            maptools.add_basemap_osm(self.ax, plot_area, ZOOM)

        else:
            pass

        self.ax.axis(extent_map)
        self.background = self.fig.canvas.copy_from_bbox(self.fig.bbox)

        if self.attribute != 'none':
            maptools.add_colorbar(self.fig, cmap,
                                  plt_settings[self.attribute]['min'],
                                  plt_settings[self.attribute]['max'],
                                 )
            self.ax.set_title(
                f'Block 42: {plt_settings[self.attribute]["title_attribute"]}')

        else:
            self.ax.set_title(f'Block 42')

        self.date_text_x, self.date_text_y = (0.75, 1.2)

    def on_click(self, event):
        print(f'on click: {event.button}')

    def on_key(self, event):
        print(f'on key: {event.key}')
        if not self.animation_started:
            self.plot_animate()

    def plot_animate(self):
        minimum = plt_settings[self.attribute]['min']
        maximum = plt_settings[self.attribute]['max']

        self.animation_started = True
        while self.run_time < self.end_time:
            self.delete_from_map()

            vp_int_df = self.vp_df[(self.vp_df['time_break'] >= self.run_time) &
                                   (self.vp_df['time_break'] < self.run_time +
                                    self.time_interval)]

            if self.run_time.time() > evening_close:
                self.change_date_and_store_background()

            vp_gdf = maptools.get_vp_gpd(vp_int_df)
            vp_gdf = maptools.convert_to_map(vp_gdf, self.maptype)
            self.run_time += self.time_interval

            if vp_gdf.empty:
                continue

            if self.attribute == 'none':
                vp_gdf.plot(ax=self.ax, color='black', markersize=MARKERSIZE)

            else:
                vp_gdf.plot(
                    ax=self.ax,
                    column=self.attribute,
                    cmap=cmap,
                    vmin=minimum,
                    vmax=maximum,
                    markersize=MARKERSIZE
                )

            self.date_gid = plt.text(self.date_text_x, self.date_text_y,
                                     self.run_time.strftime("%d-%b-%Y %H:%M"),
                                     transform=self.ax.transAxes)
            self.line_gid = plt.text(self.date_text_x, self.date_text_y - 0.1,
                                     vp_gdf.iloc[0]['line'],
                                     transform=self.ax.transAxes)
            self.blit()

    def change_date_and_store_background(self):
        self.run_time = datetime.datetime.combine(
            self.run_time.date() + datetime.timedelta(1), datetime.time(3, 0, 0))

        # self.background = self.fig.canvas.copy_from_bbox(self.fig.bbox)

        # for plot_object in reversed(self.ax.collections):
        #     plot_object.remove()

    def delete_from_map(self):
        try:
            self.date_gid.remove()
            self.line_gid.remove()

        except (ValueError, AttributeError):
            pass

    def blit(self):
        self.fig.canvas.restore_region(self.background)
        plt.draw()
        self.fig.canvas.blit(self.fig.bbox)

    @staticmethod
    def show():
        plt.show()


if __name__ == '__main__':
    start = datetime.datetime(2019, 12, 1, 8, 0, 0)
    end = datetime.datetime(2020, 1, 12, 0, 0, 0)
    interval = datetime.timedelta(seconds=1800)

    maptype = 'no_background'
    if len(sys.argv) == 3:
        maptype = sys.argv[2]
        attribute = sys.argv[1]

    elif len(sys.argv) == 2:
        attribute = sys.argv[1]

    else:
        attribute = 'none'

    if maptype.lower() == 'local':
        maptype = MapTypes.local

    elif maptype.lower() == 'osm':
        maptype = MapTypes.osm

    else:
        maptype = MapTypes.no_background

    attribute = attribute.lower()
    if attribute not in [attr for attr in plt_settings]:
        attribute = 'none'

    plot = PlotMap(attribute, start, end, interval, maptype=maptype)
    plot.show()
