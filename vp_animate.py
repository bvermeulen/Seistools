''' vp_plot animated mapping of vp locations
    Run:
      python vp_animate <attribute> <maptype>

    Optional:
    attribute: avg_phase, peak_phase, avg_dist, peak_dist, avg_force, peak_force,
               avg_viscosity, avg_stiffness, elevation, none
    maptype: osm (Open street map), local (Local map), none

    Enter start date and end date [YYMMDD] and production time interval in minutes

    start animation by click or any key press
    toggle pause by pressing space bar

    @2020 Bruno Vermeulen
    bruno.vermeulen@hotmail.com
'''
import sys
import datetime
import matplotlib.pyplot as plt
from vp_settings import GMT_OFFSET, MapTypes, plt_settings
from vp_utils import MapTools, get_animation_dates
from vp_database import VpDb

FIGSIZE = (7, 7)
EDGECOLOR = 'black'
ZOOM = 10
MARKERSIZE = 0.2
STATUS_POSISTION = (0.75, 1.1)
GMT_START_TIME = 3
TITLE = 'Block 42'
cmap = 'coolwarm'
evening_close = datetime.time(13, 0, 0)

vp_db = VpDb()
maptools = MapTools()

class PlotMap:
    ''' method to setup map and plot vp's
    '''
    def __init__(self, attribute, start_time, end_time, time_interval, pause,
                 maptype=MapTypes.no_background):
        self.attribute = attribute
        self.maptype = maptype
        self.run_time = start_time
        self.end_time = end_time
        self.time_interval = time_interval
        self.pause_at_end_of_day = pause
        self.animation_started = False
        self.pause = False
        self.date_gid = None
        self.attr_min = plt_settings[self.attribute]['min']
        self.attr_max = plt_settings[self.attribute]['max']
        self.time_stamp = ''
        self.line = ''

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
            maptools.add_colorbar(self.fig, cmap, self.attr_min, self.attr_max)
            self.ax.set_title(
                f'{TITLE}: {plt_settings[self.attribute]["title_attribute"]}')

        else:
            self.ax.set_title(f'{TITLE}')

    def on_click(self, _):
        if not self.animation_started:
            self.animation_started = True
            self.plot_animate()

    def on_key(self, event):
        if not self.animation_started:
            self.animation_started = True
            self.plot_animate()

        if event.key == ' ':
            self.pause = not self.pause
            self.plot_animate()

    def plot_animate(self):

        while self.run_time < self.end_time and not self.pause:
            self.delete_from_map()

            vp_int_df = self.vp_df[(self.vp_df['time_break'] >= self.run_time) &
                                   (self.vp_df['time_break'] < self.run_time +
                                    self.time_interval)]
            if not vp_int_df.empty:

                vp_gdf = maptools.get_vp_gpd(vp_int_df)
                vp_gdf = maptools.convert_to_map(vp_gdf, self.maptype)

                if self.attribute == 'none':
                    vp_gdf.plot(ax=self.ax, color='black', markersize=MARKERSIZE)

                else:
                    vp_gdf.plot(
                        ax=self.ax,
                        column=self.attribute,
                        cmap=cmap,
                        vmin=self.attr_min,
                        vmax=self.attr_max,
                        markersize=MARKERSIZE
                    )

                self.time_stamp = (self.run_time + datetime.timedelta(
                    hours=GMT_OFFSET)).strftime("%d-%b-%Y %H:%M")
                self.line = vp_gdf.iloc[0]['line']

                self.date_gid = plt.text(STATUS_POSISTION[0], STATUS_POSISTION[1],
                                         self.time_stamp,
                                         transform=self.ax.transAxes)
                self.line_gid = plt.text(STATUS_POSISTION[0], STATUS_POSISTION[1] - 0.05,
                                         f'Line: {self.line}',
                                         transform=self.ax.transAxes)
                self.blit()
                plt.pause(0.01)

            self.run_time += self.time_interval
            if self.run_time.time() > evening_close:
                if self.pause_at_end_of_day:
                    self.pause = True
                self.change_date_and_store_background()

    def change_date_and_store_background(self):
        self.run_time = datetime.datetime.combine(
            self.run_time.date() + datetime.timedelta(1),
            datetime.time(GMT_START_TIME, 0, 0))

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

    start, end, interval, pause = get_animation_dates()
    if start == -1:
        exit()

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

    plot = PlotMap(attribute, start, end, interval, pause, maptype=maptype)
    plot.show()
