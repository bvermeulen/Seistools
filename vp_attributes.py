# display vibe statistics
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import vp_utils
import vp_database
from vp_settings import FLEETS, plt_settings


class VpAttributes:

    @classmethod
    def select_data(cls, production_date):
        cls.vaps_records_df = vp_database.VpDb().get_vaps_data_by_date(production_date)

    @classmethod
    def plot_vaps_data(cls):
        ax0 = [None for i in range(6)]
        ax1 = [None for i in range(6)]
        fig1, (
            (ax0[0], ax1[0]), (ax0[1], ax1[1]), (ax0[2], ax1[2]),
            ) = plt.subplots(nrows=3, ncols=2, figsize=(8, 8))


        fig2, (
            (ax0[3], ax1[3]), (ax0[4], ax1[4]), (ax0[5], ax1[5]),
            ) = plt.subplots(nrows=3, ncols=2, figsize=(8, 8))

        # plt.subplots_adjust(hspace=10)

        for i_plt, plt_setting in enumerate(plt_settings):
            cls.total_records = 1
            ax0[i_plt] = cls.plot_attribute(ax0[i_plt], plt_setting)
            ax1[i_plt] = cls.plot_density(ax1[i_plt], plt_setting)

        fig1.tight_layout()
        fig2.tight_layout()
        plt.show()

    @classmethod
    def plot_attribute(cls, axis, settings):
        axis.set_title(settings['title_attribute'])
        axis.set_ylabel(settings['y-axis_label_attribute'])
        axis.set_xlabel('Record index')
        axis.set_ylim(bottom=settings['y-axis_min'], top=settings['y-axis_max'])

        for vib in range(1, FLEETS + 1):
            vib_data = cls.vaps_records_df[
                cls.vaps_records_df['vibrator'] == vib][settings['key']].to_list()

            if vib_data:
                records = [i for i in range(
                    cls.total_records, cls.total_records + len(vib_data))]
                cls.total_records += len(vib_data)
                vib_data = np.array(vib_data)
                axis.plot(records, vib_data, label=vib)

        # axis.legend(loc='upper right')

        return axis

    @classmethod
    def plot_density(cls, axis, settings):
        '''  method to plot the attribute density function. If no density plot can be
             made then plot unity density
        '''
        def dirac_function(x):
            if x == 0:
                return 1
            else:
                return 0

        x_values = np.arange(
            settings['y-axis_min'],
            settings['y-axis_max'],
            settings['y-axis_int']
        )

        axis.set_title(settings['title_density'])
        axis.set_ylabel(settings['y-axis_label_density'])

        for vib in range(1, FLEETS + 1):
            vib_data = cls.vaps_records_df[
                cls.vaps_records_df['vibrator'] == vib][settings['key']].to_list()

            if not vib_data:
                continue

            try:
                vib_density_data = stats.kde.gaussian_kde(vib_data)
                axis.plot(x_values, vib_density_data(x_values), label=vib)

            except np.linalg.LinAlgError:
                vib_data = [dirac_function(x) for x in range(len(x_values))]
                axis.plot(x_values, vib_data, label=vib)

            axis.legend(loc='upper right')

        return axis


if __name__ == "__main__":
    vp_attr = VpAttributes()

    while True:
        production_date = vp_utils.get_production_date()
        if production_date == -1:
            break

        else:
            vp_attr.select_data(production_date)
            vp_attr.plot_vaps_data()
