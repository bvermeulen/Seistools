#!/usr/bin/env python
""" module to calculate and display vibrator activity over 24 hours time perdio
    calculates number of vp's for each second of day in hashtable and displays in
    user defined interval
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    Copyright: 2021

"""
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
from seis_vibe_database import VpDb
from seis_settings import (
    FLEETS,
    DATABASE_TABLE,
    TOL_COLOR,
    RESULTS_FOLDER,
    vp_plt_settings,
)

SECONDS_PER_DAY = 24 * 3600
warnings.filterwarnings("ignore", category=RuntimeWarning)
register_matplotlib_converters()


class VpActive:
    def __init__(self, production_date):
        """initialise the hashtable"""
        self.production_date = production_date
        self.vps_by_second = {second: [] for second in range(SECONDS_PER_DAY)}
        self.vps_by_interval_list = []
        self.vps_by_interval_df = None

    def select_data(self, database_table, interval):
        self.vp_records_df = VpDb().get_vp_data_by_date(
            database_table, self.production_date
        )

        self.populate_vps_by_second()
        self.aggregate_vps_by_interval(interval)

    def populate_vps_by_second(self):
        progress_message = seis_utils.progress_message_generator(
            f'process records for {self.production_date.strftime("%d-%b-%Y")}'
        )

        for vib in range(1, FLEETS + 1):
            # get time strings and convert to datetime objects
            vib_data = self.vp_records_df[self.vp_records_df["vibrator"] == vib][
                "time_break"
            ]
            if not vib_data.empty:
                vib_data = pd.to_datetime(vib_data, format="ISO8601").to_list()

            else:
                vib_data = []

            for vp_time in vib_data:
                vp_seconds = int(
                    vp_time.time().hour * 3600
                    + vp_time.time().minute * 60
                    + vp_time.time().second
                )
                self.vps_by_second[vp_seconds].append(vib)

                next(progress_message)

    def add_vps_interval(self, interval, second, vib_list):
        _date = datetime.datetime.combine(
            self.production_date.date(), datetime.time(0, 0, 0)
        )
        _date += datetime.timedelta(seconds=second)

        count_vps = {f"V{vib:02}": vps for vib, vps in Counter(vib_list).items()}
        total = sum(val for _, val in count_vps.items())
        self.vps_by_interval_list.append(
            {
                **{"time": _date},
                **count_vps,
                **{"total": total},
                **{"vps_hour": total * 3600 / interval},
                **{"num_vibs": len(set(vib_list))},
            }
        )
        return None

    def aggregate_vps_by_interval(self, interval: int):
        """aggregate number of vps by interval
        interval: integer seconds interval
        """
        progress_message = seis_utils.progress_message_generator(
            f'aggreate VPs for {self.production_date.strftime("%d-%b-%Y")}'
        )
        self.total_vps = 0
        second = 0
        while second < SECONDS_PER_DAY:
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
            self.total_vps += len(vibs_list)
            second += interval
            next(progress_message)

        self.add_vps_interval(interval, SECONDS_PER_DAY, [])
        self.vps_by_interval_df = pd.DataFrame(
            self.vps_by_interval_list,
            columns=(
                ["time"]
                + [f"V{i:02}" for i in range(1, FLEETS + 1)]
                + ["total", "vps_hour", "num_vibs"]
            ),
        )
        print(f"\rtotal vps: {self.total_vps}                                        ")

    def plot_vps_by_interval(self, interval):
        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
        fig.suptitle(
            f'{vp_plt_settings["vib_activity"]["fig_title"]} '
            f'{self.production_date.strftime("%d-%b-%Y")}'  # ({self.total_vps} VPs)'
        )
        time_format = mdates.DateFormatter("%H:%M")
        times = self.vps_by_interval_df["time"].to_numpy()

        # axis for VPs per hour
        max_val = vp_plt_settings["vib_activity"]["max_vp_hour"]
        intval = vp_plt_settings["vib_activity"]["tick_intval_vp_hour"]
        ax1.set_title(f"VPs per hour - interval {interval / 60:.0f} minutes")
        ax1.set_ylim(bottom=0, top=max_val)
        ax1.yaxis.set_ticks(np.arange(0, max_val + 1, intval))
        ax1.xaxis.set_major_formatter(time_format)
        ax1.grid(axis="y", linewidth=0.5, linestyle="-", zorder=0)
        ax1.step(
            times,
            self.vps_by_interval_df["vps_hour"].to_numpy(),
            where="post",
            zorder=3,
        )
        ax1.axhline(
            vp_plt_settings["vib_activity"]["vp_hour_target"],
            color=TOL_COLOR,
            linewidth=0.5,
        )

        # axis for operational vibs
        max_val = vp_plt_settings["vib_activity"]["max_vibs"]
        intval = vp_plt_settings["vib_activity"]["tick_intval_vibs"]
        ax2.set_title(f"Vibs operational - interval {interval / 60:.0f} minutes")
        ax2.set_ylim(bottom=0, top=max_val)
        ax2.yaxis.set_ticks(np.arange(0, max_val + 1, intval))
        ax2.xaxis.set_major_formatter(time_format)
        ax2.grid(axis="y", linewidth=0.5, linestyle="-", zorder=0)
        vibs = self.vps_by_interval_df["num_vibs"].to_numpy()
        colors = [
            TOL_COLOR
            if nv < vp_plt_settings["vib_activity"]["vibs_target"]
            else "green"
            for nv in vibs
        ]
        width = interval / SECONDS_PER_DAY
        ax2.bar(times, vibs, color=colors, width=width, align="edge", zorder=3)

        fig.tight_layout()
        plt.show()
        plt.close()

    def plot_vps_by_vibe(self, interval):
        ax = [None for i in range(FLEETS)]
        fig, (ax) = plt.subplots(
            nrows=FLEETS, ncols=1, figsize=(7, 12), gridspec_kw={"hspace": 0}
        )
        fig.suptitle(
            f'{vp_plt_settings["vib_activity"]["fig_title"]} '
            f'{self.production_date.strftime("%d-%b-%Y")} ({self.total_vps} VPs)'
        )
        time_format = mdates.DateFormatter("%H:%M")
        times = self.vps_by_interval_df["time"].to_numpy()
        ax[0].set_title(f"VPs per hour - interval {interval / 60:.0f} minutes")
        for vib in range(1, FLEETS + 1):
            ax[FLEETS - vib].set_xticklabels([])
            ax[FLEETS - vib].yaxis.set_ticks(np.arange(0, 200, 50))
            ax[FLEETS - vib].tick_params(axis="both", labelsize=8)
            ax[FLEETS - vib].set_ylabel(f"V{vib}", fontsize=8)
            ax[FLEETS - vib].xaxis.set_major_formatter(time_format)
            ax[FLEETS - vib].set_ylim(bottom=0, top=200)
            ax[FLEETS - vib].grid(axis="y", linewidth=0.5, linestyle="-", zorder=0)
            ax[FLEETS - vib].grid(axis="x", linewidth=0.5, linestyle="-", zorder=0)
            vps = (
                self.vps_by_interval_df[f"V{vib:02}"].fillna(0).to_numpy()
                * 3600
                / interval
            )
            ax[FLEETS - vib].step(times, vps, where="post", linewidth=0.9, zorder=3)

        plt.show()
        plt.close()

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
        vp_activity.select_data(DATABASE_TABLE, interval)
        vp_activity.plot_vps_by_interval(interval)
        vp_activity.plot_vps_by_vibe(interval)

        results_file = (
            RESULTS_FOLDER / f'vp_activity_{production_date.strftime("%y%m%d")}.xlsx'
        )
        vp_activity.results_to_excel(results_file)


if __name__ == "__main__":
    main()
