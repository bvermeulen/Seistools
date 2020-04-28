''' time analysis of vp per day
    calculated number of vp's for each second of day in hashtable
'''
import sys
import datetime
from collections import Counter
import warnings
import numpy as np
import pandas as pd
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

        self.vps_by_interval_df = pd.DataFrame(
            columns=['time'] +
            [f'V{i:02}' for i in range(1, FLEETS + 1)] +
            ['total', 'vps_hour', 'num_vibs']
        )

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

    def add_vps_interval(self, interval, second, vib_list):
        _date = datetime.datetime.combine(
            self.production_date.date(), datetime.time(0, 0, 0))
        _date += datetime.timedelta(seconds=second)

        count_vps = {f'V{vib:02}': vps for vib, vps in Counter(vib_list).items()}
        total = sum(val for _, val in count_vps.items())
        self.vps_by_interval_df = self.vps_by_interval_df.append(
            {
                **{'time': _date},
                **count_vps,
                **{'total': total},
                **{'vps_hour': total * 3600 / interval},
                **{'num_vibs': len(set(vib_list))},
            },
            ignore_index=True)

    def aggregate_vps_by_interval(self, interval):
        ''' aggregate number of vps by interval
            argument:
                interval: integer seconds interval
            returns:
                seconds: list with start second of intervals
                vps_in_interval: list with number of vps in interval
                vibs_in_interval: list of number of vibs operational in interval
        '''
        total_vps = 0
        second = 0
        while second <= seconds_per_day:
            # TODO improve loop, probably over vps_by_second and check if in interval

            # calculate vps in interval and normalise by hour and
            # caluculate vibs operational in interval
            vibs_list = []
            for k, val in self.vps_by_second.items():
                if k in range(second, second + interval):
                    vibs_list += val
                else:
                    pass

            self.add_vps_interval(interval, second, vibs_list)

            total_vps += len(vibs_list)
            second += interval

        if second != seconds_per_day:
            self.add_vps_interval(interval, seconds_per_day, [])

        print(f'\rtotal vps: {total_vps}                                           ')

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
        self.aggregate_vps_by_interval(interval)
        times = self.vps_by_interval_df['time'].to_list()
        ax1.step(times,
                 self.vps_by_interval_df['vps_hour'].to_list(),
                 where='post', markersize=5,
                )
        ax2.step(times,
                 self.vps_by_interval_df['num_vibs'].to_list(),
                 where='post', markersize=5,
                )

        plt.show()

    def results_to_excel(self, file_name):
        self.vps_by_interval_df.to_excel(file_name)

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

        results_file = f'.\\vp_activity_{production_date.strftime("%y%m%d")}.xlsx'
        vp_activity.results_to_excel(results_file)

if __name__ == '__main__':
    main()
