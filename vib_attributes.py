# display vibe statistics
from update_vaps import VpDb, VapsTable
import pandas as pd

fleets = 5

class VpAttributes:

    vib_attributes = {
        'index': [],
        'vibrator': [],
        'avg_phase': [],
        'peak_phase': [],
        'avg_dist': [],
        'peak_dist': [],
        'avg_force': [],
        'peak_force': [],
    }

    @classmethod
    def select_data(cls, production_date):
        vp_db = VpDb()
        cls.vaps_records = vp_db.retrieve_vaps_data_by_date(production_date)

        for index, record in enumerate(cls.vaps_records):
            cls.vib_attributes['index'].append(index)
            cls.vib_attributes['vibrator'].append(record.vibrator)
            cls.vib_attributes['avg_phase'].append(record.avg_phase)
            cls.vib_attributes['peak_phase'].append(record.peak_phase)
            cls.vib_attributes['avg_dist'].append(record.avg_dist)
            cls.vib_attributes['peak_dist'].append(record.peak_dist)
            cls.vib_attributes['avg_force'].append(record.avg_force)
            cls.vib_attributes['peak_force'].append(record.peak_force)

    @classmethod
    def plot_vaps_data(cls):
        fig1, ((ax0, ax1), (ax2, ax3), (ax4, ax5),
            ) = plt.subplots(nrows=3, ncols=2, figsize=(8, 8))
        plt.subplots_adjust(hspace=10)
        ax0, ax1 = cls.plot_attribute(ax0, ax1, [
            'peak_phase', 'Peak phase', 0, 20])
        # ax2, ax3 = cls.plot_peak_dist(ax2, ax3)
        # ax4, ax5 = cls.plot_peak_phase(ax4, ax5)

        fig2, ((ax6, ax7), (ax8, ax9), (ax10, ax11),
            ) = plt.subplots(nrows=3, ncols=2, figsize=(8, 8))
        plt.subplots_adjust(hspace=10)
        # ax6, ax7 = cls.plot_peak_phase(ax6, ax7)
        # ax8, ax9 = cls.plot_peak_dist(ax8, ax9)
        # ax10, ax11 = cls.plot_peak_phase(ax10, ax11)


    @classmethod
    def plot_attribute(cls, axis1, axis2, config):
        for vib in range(1, fleets + 1):
            vib_axis = []
            vib_data = []
            for record in cls.vib_attributes[]
                vib_axis.append()


if __name__ == "__main__":
    vp_attr = VpAttributes()

    vp_attr.select_date(prod_date)

