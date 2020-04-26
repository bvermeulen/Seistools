''' time analysis of vp per day
    calculated number of vp's for each second of day in hashtable
'''
import sys
import datetime
import warnings
import numpy as np
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seis_utils
import seis_database
from seis_settings import FLEETS, DATABASE_TABLE

seconds_per_day = 24 * 3600
warnings.filterwarnings("ignore", category=RuntimeWarning)
register_matplotlib_converters()


class VpActive:

    def __init__(self, production_date):
        ''' initialise the hashtable '''
        self.production_date = production_date
        self.vps_by_second = {second: [] for second in range(seconds_per_day)}

    def select_data(self, database_table):
        self.vp_records_df = seis_database.VpDb().get_data_by_date(
            database_table, self.production_date)

    def populate_vps_by_second(self):
        progress_message = seis_utils.progress_message_generator(
            f'process records for {self.production_date.strftime("%d-%b-%Y")}')

        for vib in range(1, FLEETS + 1):
            vib_data = self.vp_records_df[
                self.vp_records_df['vibrator'] == vib]['time_break'].to_list()
            for vp_time in vib_data:
                vp_seconds = int(
                    vp_time.time().hour * 3600 + vp_time.time().minute * 60 +
                    vp_time.time().second)
                self.vps_by_second[vp_seconds].append(vib)

                next(progress_message)


    def aggregate_vps_by_interval(self, interval):
        ''' aggregate number of vps by interval
            argument:
                interval: integer seconds interval
            returns:
                seconds: list with start second of intervals
                vps_in_interval: list with number of vps in interval
                vibs_in_interval: list of number of vibs operational in interval
        '''
        vps_in_interval = []
        vibs_in_interval = []
        seconds = []
        total_vps = 0
        second = 0

        while second <= seconds_per_day:
            # TODO improve loop, probably over vps_by_second and check if in interval

            # calculate vps in interval and normalise by hour and
            # caluculate vibs operational in interval
            vps = 0
            vibs_operational = set()
            for k, val in self.vps_by_second.items():
                if k in range(second, second + interval):
                    vps += len(val)
                    vibs_operational.update(val)

                else:
                    pass

            seconds.append(second)
            vps_in_interval.append(vps * 3600 / interval)
            vibs_in_interval.append(len(vibs_operational))

            total_vps += vps
            second += interval

        if seconds != seconds_per_day:
            vps_in_interval.append(0)
            vibs_in_interval.append(0)
            seconds.append(seconds_per_day)

        print(f'\rtotal vps: {total_vps}                                           ')
        return seconds, vps_in_interval, vibs_in_interval

    def plot_vps_by_interval(self, interval):

        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12, 8))
        fig.suptitle(f'Vibes activity for {self.production_date.strftime("%d-%b-%Y")}')
        ax1.set_title(f'VPs per hour - interval {interval / 60:.0f} minutes')
        ax2.set_title(f'Vibs operational - interval {interval / 60:.0f} minutes')
        ax1.set_ylim(bottom=0, top=2500)
        ax1.yaxis.set_ticks(np.arange(0, 2501, 500))
        ax2.set_ylim(bottom=0, top=20)
        ax2.yaxis.set_ticks(np.arange(0, 21, 2))
        time_format = mdates.DateFormatter('%H:%M')
        ax1.xaxis.set_major_formatter(time_format)
        ax2.xaxis.set_major_formatter(time_format)

        self.populate_vps_by_second()
        seconds, vps_in_interval, vibs_in_interval = self.aggregate_vps_by_interval(
            interval)

        _date = datetime.datetime.combine(
            self.production_date.date(), datetime.time(0, 0, 0))
        times = [_date + datetime.timedelta(seconds=second) for second in seconds]
        ax1.step(times, vps_in_interval, where='post', markersize=5)
        ax2.step(times, vibs_in_interval, where='post', markersize=5)

        plt.show()

def main():

    interval = 900
    if len(sys.argv) == 2:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            pass

    while True:

        production_date = seis_utils.get_production_date()
        if production_date == -1:
            break

        vp_activity = VpActive(production_date)
        vp_activity.select_data(DATABASE_TABLE)
        vp_activity.plot_vps_by_interval(interval)

if __name__ == '__main__':
    main()
