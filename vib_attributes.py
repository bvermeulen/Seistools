# display vibe statistics
import datetime
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from update_vaps import VpDb

fleets = 5

class VpAttributes:

    @classmethod
    def select_data(cls, production_date):
        vp_db = VpDb()
        cls.vaps_records_df = vp_db.get_vaps_data_by_date(production_date)

    @classmethod
    def plot_vaps_data(cls):
        fig1, ((ax0, ax1), (ax2, ax3), (ax4, ax5),
            ) = plt.subplots(nrows=3, ncols=2, figsize=(8, 8))
        plt.subplots_adjust(hspace=10)

        # plot peak distortion
        settings = {
            'key':'peak_dist',
            'title': 'Peak Distorion',
            'y-axis_title': 'Percentage',
            'y-axis_min': 0,
            'y-axis_max': 60,
            'y-axis_int': 1,
        }
        ax0 = cls.plot_attribute(ax0, settings)

        settings['title'] = 'Peak Distortion Density'
        settings['y-axis_title'] = ''
        ax1 = cls.plot_density(ax1, settings)

        # ax2, ax3 = cls.plot_peak_dist(ax2, ax3)
        # ax4, ax5 = cls.plot_peak_phase(ax4, ax5)

        fig2, ((ax6, ax7), (ax8, ax9), (ax10, ax11),
            ) = plt.subplots(nrows=3, ncols=2, figsize=(8, 8))
        plt.subplots_adjust(hspace=10)
        # ax6, ax7 = cls.plot_peak_phase(ax6, ax7)
        # ax8, ax9 = cls.plot_peak_dist(ax8, ax9)
        # ax10, ax11 = cls.plot_peak_phase(ax10, ax11)

        fig1.tight_layout()
        plt.show()

    @classmethod
    def plot_attribute(cls, axis, settings):
        key = settings['key']
        axis.set_title(settings['title'])
        axis.set_ylabel(settings['y-axis_title'])
        axis.set_xlabel('Record index')
        axis.set_ylim(bottom=settings['y-axis_min'], top=settings['y-axis_max'])

        for vib in range(1, fleets + 1):
            vib_axis = cls.vaps_records_df[
                cls.vaps_records_df['vibrator']==vib].index.to_list()
            vib_data = cls.vaps_records_df[
                cls.vaps_records_df['vibrator']==vib][key].to_list()

            if vib_data:
                vib_data = np.array(vib_data)
                axis.plot(vib_axis, vib_data, label=vib)

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

        axis.set_title(settings['title'])
        axis.set_ylabel(settings['y-axis_title'])

        for vib in range(1, fleets + 1):
            vib_data = cls.vaps_records_df[
                cls.vaps_records_df['vibrator']==vib][settings['key']].to_list()

            if not vib_data:
                continue

            try:
                vib_density_data = stats.kde.gaussian_kde(vib_data)
                axis.plot(x_values, vib_density_data(x_values), label=vib)

            except (np.linalg.LinAlgError):
                vib_data = [dirac_function(x) for x in range(len(x_values))]
                axis.plot(x_values, vib_data, label=vib)

            axis.legend(loc='upper right')

        return axis


if __name__ == "__main__":
    vp_attr = VpAttributes()

    production_date = datetime.datetime(2019, 12, 23)
    vp_attr.select_data(production_date)
    vp_attr.plot_vaps_data()
