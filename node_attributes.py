''' display node attributes
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    Copyright: 2021
'''
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seis_utils
import seis_database
from seis_settings import MARKERSIZE_NODE, node_plt_settings


class NodeAttributes:

    @classmethod
    def select_data(cls, production_date):
        cls.node_records_df = seis_database.RcvDb().get_node_data_by_date(production_date)

    @classmethod
    def plot_node_data(cls):
        ax0 = [None for i in range(9)]
        ax1 = [None for i in range(9)]
        fig1, (
                (ax0[0], ax1[0]), (ax0[1], ax1[1]), (ax0[2], ax1[2]),
                (ax0[3], ax1[3]), (ax0[4], ax1[4]),
            ) = plt.subplots(nrows=5, ncols=2, figsize=(8, 8))

        fig2, (
                (ax0[5], ax1[5]), (ax0[6], ax1[6]), (ax0[7], ax1[7]),
            ) = plt.subplots(nrows=3, ncols=2, figsize=(8, 8))

        # plt.subplots_adjust(hspace=10)

        for i_plt, (key, plt_setting) in enumerate(node_plt_settings.items()):
            if key in ['frequency', 'damping', 'sensitivity', 'resistance',
                       'thd', 'battery', 'noise', 'tilt']:
                ax0[i_plt] = cls.plot_attribute(ax0[i_plt], key, plt_setting)
                ax1[i_plt] = cls.plot_density(ax1[i_plt], key, plt_setting)

        handles, labels = ax0[0].get_legend_handles_labels()
        fig1.legend(
            handles, labels, loc='upper right', frameon=True,
            fontsize='small', framealpha=1, markerscale=40)
        fig1.tight_layout()

        fig2.legend(
            handles, labels, loc='upper right', frameon=True,
            fontsize='small', framealpha=1, markerscale=40)
        fig2.tight_layout()

        plt.show()

    @classmethod
    def plot_attribute(cls, axis, key, setting):
        axis.set_title(setting['title_attribute'])
        axis.set_ylabel(setting['y-axis_label_attribute'])
        axis.set_ylim(bottom=setting['min'], top=setting['max'])

        node_data = np.array(cls.node_records_df[key].to_list())

        if node_data.size > 0:
            axis.plot(
                range(len(node_data)), node_data, '.', markersize=MARKERSIZE_NODE
            )

        return axis

    @classmethod
    def plot_density(cls, axis, key, setting):
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

        node_data = np.array(cls.node_records_df[key].to_list())

        if node_data.size > 0:
            try:
                node_density_data = stats.kde.gaussian_kde(node_data)
                axis.plot(x_values, node_density_data(x_values))

            except np.linalg.LinAlgError:
                node_data = [dirac_function(x) for x in range(len(x_values))]
                axis.plot(x_values, node_data)

        return axis


if __name__ == "__main__":
    node_attr = NodeAttributes()

    while True:
        production_date = seis_utils.get_production_date()
        if production_date == -1:
            break

        node_attr.select_data(production_date)
        node_attr.plot_node_data()
