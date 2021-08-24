''' display node attributes
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    Copyright: 2021
'''
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seis_utils
from seis_nuseis_database import NuseisDb
from seis_settings import MARKERSIZE_NODE, TOL_COLOR, nuseis_plt_settings

SMALL_SIZE = 8
plt.rc('xtick', labelsize=SMALL_SIZE)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('axes', labelsize=SMALL_SIZE)
FIGSIZE = (12, 5.3)


class NodeAttributes:

    def __init__(self, production_date):
        self.production_date = production_date

    def select_data(self):
        self.node_records_df = NuseisDb().get_node_data_by_date(
            self.production_date
        )

    def plot_node_data(self):
        ax0 = [None for i in range(4)]
        ax1 = [None for i in range(4)]
        fig, (
            (ax0[0], ax1[0], ax0[1], ax1[1]),
            (ax0[2], ax1[2], ax0[3], ax1[3]),
        ) = plt.subplots(nrows=2, ncols=4, figsize=FIGSIZE)
        fig.suptitle(
            f'Daily tests for NuSeis: '
            f'{self.production_date.strftime("%d %b %Y")}', fontweight='bold'
        )

        for i_plt, (key, plt_setting) in enumerate(nuseis_plt_settings.items()):
            if key in ['resistance', 'thd', 'noise', 'tilt']:
                ax0[i_plt] = self.plot_attribute(ax0[i_plt], key, plt_setting)
                ax1[i_plt] = self.plot_histogram(ax1[i_plt], key, plt_setting)

        fig.tight_layout()
        plt.show()

    def plot_attribute(self, axis, key, setting):
        axis.set_title(setting['title_attribute'])
        axis.set_ylabel(setting['y-axis_label_attribute'])
        axis.set_ylim(bottom=setting['min'], top=setting['max'])

        node_data = np.array(self.node_records_df[key].to_list())

        if node_data.size > 0:
            axis.plot(
                range(len(node_data)), node_data, '.', markersize=MARKERSIZE_NODE
            )
            if setting['tol_min'] is not None:
                axis.axhline(setting['tol_min'], color=TOL_COLOR, linewidth=0.5)

            if setting['tol_max'] is not None:
                axis.axhline(setting['tol_max'], color=TOL_COLOR, linewidth=0.5)

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

        node_data = np.array(self.node_records_df[key].to_list())

        if node_data.size > 0:
            try:
                node_density_data = stats.kde.gaussian_kde(node_data)
                axis.plot(x_values, setting['interval'] * node_density_data(x_values))

            except np.linalg.LinAlgError:
                node_data = [dirac_function(x) for x in range(len(x_values))]
                axis.plot(x_values, node_data)

        return axis

    def plot_histogram(self, axis, key, setting):
        '''  method to plot the attribute histogram.
        '''
        axis.set_title(setting['title_density'])
        axis.set_ylabel(setting['y-axis_label_density'])
        node_data = np.array(self.node_records_df[key].to_list())
        if node_data.size > 0:
            axis.hist(
                node_data, histtype='step', bins=setting['bins'],
                range=(setting['min'], setting['max'])
            )
            if setting['tol_min'] is not None:
                axis.axvline(setting['tol_min'], color=TOL_COLOR, linewidth=0.5)

            if setting['tol_max'] is not None:
                axis.axvline(setting['tol_max'], color=TOL_COLOR, linewidth=0.5)

            axis.axvline(
                node_data.mean(), linestyle='dashed', color='black', linewidth=0.7)

            d = 0 if node_data.mean() > 1000 else 2
            axis.text(
                0.98, 0.98, f'Mean: {node_data.mean():.{d}f}', size='smaller',
                horizontalalignment='right', verticalalignment='top',
                transform=axis.transAxes)

        return axis

if __name__ == "__main__":

    while True:
        production_date = seis_utils.get_production_date()
        if production_date == -1:
            break

        node_attr = NodeAttributes(production_date)
        node_attr.select_data()
        node_attr.plot_node_data()
