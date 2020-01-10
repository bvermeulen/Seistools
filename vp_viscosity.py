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
        cls.vaps_records_df = vp_database.VpDb().get_vp_data_by_date(production_date)

    @classmethod
    def plot_vaps_data(cls):
        ax0 = [None for i in range(6)]
        ax1 = [None for i in range(6)]
        fig1, (
            (ax0[0], ax1[0]), (ax0[1], ax1[1]),
            ) = plt.subplots(nrows=2, ncols=2, figsize=(8, 8))

        # plt.subplots_adjust(hspace=10)

        plt_index = 0
        for key, plt_setting in plt_settings.items():
            cls.total_records = 1
            if key in ['avg_stiffness', 'avg_viscosity']:
                ax0[plt_index] = cls.plot_attribute(ax0[plt_index], key, plt_setting)
                ax1[plt_index] = cls.plot_density(ax1[plt_index], key, plt_setting)
                plt_index += 1

        fig1.tight_layout()
        plt.show()

    @classmethod
    def plot_attribute(cls, axis, key, setting):
        axis.set_title(setting['title_attribute'])
        axis.set_ylabel(setting['y-axis_label_attribute'])
        axis.set_xlabel('Index')
        axis.set_ylim(bottom=setting['min'], top=setting['max'])

        for vib in range(1, FLEETS + 1):
            vib_data = cls.vaps_records_df[
                cls.vaps_records_df['vibrator'] == vib][key].to_list()

            if vib_data:
                records = [i for i in range(
                    cls.total_records, cls.total_records + len(vib_data))]
                cls.total_records += len(vib_data)
                vib_data = np.array(vib_data)
                axis.plot(records, vib_data, label=vib)

        # axis.legend(loc='upper right')

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

        for vib in range(1, FLEETS + 1):
            vib_data = cls.vaps_records_df[
                cls.vaps_records_df['vibrator'] == vib][key].to_list()

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
