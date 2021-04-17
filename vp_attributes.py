''' display vibe attributes
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    Copyright: 2021
'''
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seis_utils
import seis_database
from seis_settings import (
    FLEETS, DATABASE_TABLE, TOL_COLOR, MARKERSIZE_VP, vp_plt_settings
)

SMALL_SIZE = 8
plt.rc('xtick', labelsize=SMALL_SIZE)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('axes', labelsize=SMALL_SIZE)
FIGSIZE = (14, 9)


class VpAttributes:

    def __init__(self, database_table, production_date):
        self.database_table = database_table
        self.production_date = production_date

    def select_data(self):
        self.vp_records_df = seis_database.VpDb().get_vp_data_by_date(
            self.database_table, self.production_date)

    def plot_vp_data(self):
        ax0 = [None for i in range(6)]
        ax1 = [None for i in range(6)]
        fig, (
            (ax0[0], ax1[0], ax0[3], ax1[3]),
            (ax0[1], ax1[1], ax0[4], ax1[4]),
            (ax0[2], ax1[2], ax0[5], ax1[5]),
            ) = plt.subplots(nrows=3, ncols=4, figsize=FIGSIZE)
        fig.suptitle(f'Vib attributes for: {self.production_date.strftime("%d %b %Y")}', fontweight='bold')  #pylint: disable=line-too-long

        for i_plt, (key, plt_setting) in enumerate(vp_plt_settings.items()):
            self.total_records = 1
            if key in ['avg_phase', 'peak_phase', 'avg_dist',
                       'peak_dist', 'avg_force', 'peak_force']:
                ax0[i_plt] = self.plot_attribute(ax0[i_plt], key, plt_setting)
                ax1[i_plt] = self.plot_density(ax1[i_plt], key, plt_setting)

        handles, labels = ax0[0].get_legend_handles_labels()
        fig.legend(
            handles, labels, loc='upper right', frameon=True,
            fontsize='small', framealpha=1, markerscale=40)
        fig.tight_layout()

        plt.show()

    def plot_attribute(self, axis, key, setting):
        axis.set_title(setting['title_attribute'])
        axis.set_ylabel(setting['y-axis_label_attribute'])
        axis.set_xlabel('Index')
        axis.set_ylim(bottom=setting['min'], top=setting['max'])

        plt_tol_lines = True
        for vib in range(1, FLEETS + 1):
            vib_data = self.vp_records_df[
                self.vp_records_df['vibrator'] == vib][key].to_list()

            if vib_data:
                records = [i for i in range(
                    self.total_records, self.total_records + len(vib_data))]
                self.total_records += len(vib_data)
                vib_data = np.array(vib_data)
                label_vib = f'{vib} ({len(records)})'
                axis.plot(
                    records, vib_data, '.', label=label_vib, markersize=MARKERSIZE_VP
                )
                if plt_tol_lines:
                    if setting['tol_min'] is not None:
                        axis.axhline(setting['tol_min'], color=TOL_COLOR, linewidth=0.5)

                    if setting['tol_max'] is not None:
                        axis.axhline(setting['tol_max'], color=TOL_COLOR, linewidth=0.5)
                    plt_tol_lines = False

        return axis

    def plot_density(self, axis, key, setting):
        '''  method to plot the attribute density function. If no density plot can be
             made then plot unity density
        '''
        def dirac_function(x):
            if x == 0:
                return 1
            else:
                return 0

        x_values = np.arange(
            setting['min'],
            setting['max'],
            setting['interval']
        )
        axis.set_title(setting['title_density'])
        axis.set_ylabel(setting['y-axis_label_density'])

        plt_tol_lines = True
        for vib in range(1, FLEETS + 1):
            vib_data = np.array(
                self.vp_records_df[self.vp_records_df['vibrator'] == vib][key].to_list()
            )
            if vib_data.size > 0:
                try:
                    vib_density_data = stats.kde.gaussian_kde(vib_data)
                    axis.plot(
                        x_values, setting['interval'] * vib_density_data(x_values),
                        label=vib
                    )
                except np.linalg.LinAlgError:
                    vib_data = [dirac_function(x) for x in range(len(x_values))]
                    axis.plot(x_values, vib_data, label=vib)

                if plt_tol_lines:
                    if setting['tol_min'] is not None:
                        axis.axvline(setting['tol_min'], color=TOL_COLOR, linewidth=0.5)

                    if setting['tol_max'] is not None:
                        axis.axvline(setting['tol_max'], color=TOL_COLOR, linewidth=0.5)
                    plt_tol_lines = False

        return axis

    def plot_histogram(self, axis, key, setting):
        '''  method to plot the attribute histogram.
        '''
        axis.set_title(setting['title_density'])
        axis.set_ylabel(setting['y-axis_label_density'])

        plt_tol_lines = True
        for vib in range(1, FLEETS + 1):
            vib_data = np.array(
                self.vp_records_df[self.vp_records_df['vibrator'] == vib][key].to_list()
            )
            if vib_data.size > 0:
                axis.hist(
                    vib_data, histtype='step', bins=50,
                    range=(setting['min'], setting['max']), label=vib
                )

                if plt_tol_lines:
                    if setting['tol_min'] is not None:
                        axis.axvline(setting['tol_min'], color=TOL_COLOR, linewidth=0.5)

                    if setting['tol_max'] is not None:
                        axis.axvline(setting['tol_max'], color=TOL_COLOR, linewidth=0.5)
                    plt_tol_lines = False

        return axis


if __name__ == "__main__":

    while True:
        production_date = seis_utils.get_production_date()
        if production_date == -1:
            break

        vp_attr = VpAttributes(DATABASE_TABLE, production_date)
        vp_attr.select_data()
        vp_attr.plot_vp_data()
