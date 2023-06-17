""" display vibe attributes
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    Copyright: 2023
"""
import numpy as np
from scipy import stats
import matplotlib

matplotlib.use("Qt5Agg")

import matplotlib.pyplot as plt
import seis_utils
from seis_vibe_database import VpDb
from seis_settings import (
    FLEETS,
    DATABASE_TABLE,
    TOL_COLOR,
    MARKERSIZE_VP,
    vp_plt_settings,
)

SMALL_SIZE = 8
plt.rc("xtick", labelsize=SMALL_SIZE)
plt.rc("ytick", labelsize=SMALL_SIZE)
plt.rc("axes", labelsize=SMALL_SIZE)
FIGSIZE = (14, 9)
FIGSIZE_HISTOGRAM = (8, 20)
DPI_HISTOGRAM = 90


class VpAttributes:
    def __init__(self):
        self.database_table = DATABASE_TABLE
        self._production_date = None
        self.dpi = 100

    @property
    def production_date(self):
        return self._production_date

    @production_date.setter
    def production_date(self, val):
        self._production_date = val

    def select_data(self):
        self.vp_records_df = VpDb().get_vp_data_by_date(
            self.database_table, self._production_date
        )

    def plot_vp_data(self, figsize=FIGSIZE, dpi=100):
        ax0 = [None for _ in range(6)]
        ax1 = [None for _ in range(6)]
        fig, (
            (ax0[0], ax1[0], ax0[3], ax1[3]),
            (ax0[1], ax1[1], ax0[4], ax1[4]),
            (ax0[2], ax1[2], ax0[5], ax1[5]),
        ) = plt.subplots(nrows=3, ncols=4, figsize=figsize, dpi=dpi)
        fig.suptitle(
            f'Vib attributes for: {self._production_date.strftime("%d %b %Y")}',
            fontweight="bold",
        )
        for key, plt_setting in vp_plt_settings.items():
            match key:
                case "avg_phase":
                    ax_index = 0
                case "peak_phase":
                    ax_index = 3
                case "avg_dist":
                    ax_index = 1
                case "peak_dist":
                    ax_index = 4
                case "avg_force":
                    ax_index = 2
                case "peak_force":
                    ax_index = 5
                case other:
                    continue
            self.total_records = 0
            ax0[ax_index] = self.plot_attribute(ax0[ax_index], key, plt_setting)
            ax1[ax_index] = self.plot_density_combined(ax1[ax_index], key, plt_setting)
            # ax1[ax_index] = self.plot_histograms_combined(ax1[ax_index], key, plt_setting)

        # add total vp's as extra label in the legend
        ax0[0].plot([], [], " ", label=f"Ttl ({self.total_records:,})")
        handles, labels = ax0[0].get_legend_handles_labels()
        fig.legend(
            handles,
            labels,
            loc="upper right",
            frameon=True,
            fontsize="small",
            framealpha=1,
            markerscale=40,
        )
        fig.tight_layout()
        return fig

    def plot_histogram_data(self, figsize=FIGSIZE_HISTOGRAM, dpi=DPI_HISTOGRAM):
        gs_kw = {"hspace": 0.15, "wspace": 0.20}
        fig, ax = plt.subplots(
            nrows=FLEETS,
            ncols=6,
            figsize=figsize,
            dpi=dpi,
            gridspec_kw=gs_kw,
        )
        fig.suptitle(
            f'Vib attributes for: {self._production_date.strftime("%d %b %Y")}',
            fontweight="bold",
        )
        for key, plt_setting in vp_plt_settings.items():
            match key:
                case "avg_phase":
                    ax_index = 0
                case "peak_phase":
                    ax_index = 1
                case "avg_dist":
                    ax_index = 2
                case "peak_dist":
                    ax_index = 3
                case "avg_force":
                    ax_index = 4
                case "peak_force":
                    ax_index = 5
                case other:
                    continue

            ax[:, ax_index] = self.plot_histograms(ax[:, ax_index], key, plt_setting)

        return fig

    def plot_attribute(self, axis, key, setting):
        axis.set_title(setting["title_attribute"])
        axis.set_ylabel(setting["y-axis_label_attribute"])
        axis.set_xlabel("Index")
        axis.set_ylim(bottom=setting["min"], top=setting["max"])

        plt_tol_lines = True
        for vib in range(1, FLEETS + 1):
            vib_data = self.vp_records_df[self.vp_records_df["vibrator"] == vib][
                key
            ].to_list()

            if vib_data:
                records = [
                    i
                    for i in range(
                        self.total_records, self.total_records + len(vib_data)
                    )
                ]
                self.total_records += len(vib_data)
                vib_data = np.array(vib_data)
                label_vib = f"{vib} ({len(records)})"
                axis.plot(
                    records, vib_data, ".", label=label_vib, markersize=MARKERSIZE_VP
                )
                if plt_tol_lines:
                    if setting["tol_min"] is not None:
                        axis.axhline(setting["tol_min"], color=TOL_COLOR, linewidth=0.5)

                    if setting["tol_max"] is not None:
                        axis.axhline(setting["tol_max"], color=TOL_COLOR, linewidth=0.5)
                    plt_tol_lines = False

        return axis

    def plot_density_combined(self, axis, key, setting):
        """method to plot the attribute density function combined in one axis."""
        x_values = np.arange(setting["min"], setting["max"], setting["interval"])
        axis.set_title(setting["title_density"])
        axis.set_ylabel(setting["y-axis_label_density"])
        plt_tol_lines = True

        for vib in range(1, FLEETS + 1):
            vib_data = np.array(
                self.vp_records_df[self.vp_records_df["vibrator"] == vib][key].to_list()
            )
            if (vp_count := vib_data.size) > 0:
                try:
                    density_vals = stats.gaussian_kde(vib_data, bw_method=0.5).evaluate(
                        x_values
                    )
                    density_vals /= density_vals.sum()
                    scale_factor = vp_count / setting["interval"]
                    # unable to explain why below is necessary but it seems to work
                    if key in ["avg_phase"]:
                        scale_factor *= setting["interval"]

                except np.linalg.LinAlgError:
                    # KDE fails is all elements in the vib_data array have the same value
                    # In this case run below fallback
                    half_intval = 0.5 * setting["interval"]
                    val = vib_data.mean()
                    density_vals = np.where(
                        (x_values > val - half_intval) & (x_values < val + half_intval),
                        1,
                        0,
                    )
                    scale_factor = vp_count

                axis.plot(x_values, scale_factor * density_vals, label=vib)

                if plt_tol_lines:
                    if setting["tol_min"] is not None:
                        axis.axvline(setting["tol_min"], color=TOL_COLOR, linewidth=0.5)

                    if setting["tol_max"] is not None:
                        axis.axvline(setting["tol_max"], color=TOL_COLOR, linewidth=0.5)
                    plt_tol_lines = False

        return axis

    def plot_histograms_combined(self, axis, key, setting):
        """method to plot the attribute histograms combined in one axis"""
        axis.set_title(setting["title_density"])
        axis.set_ylabel(setting["y-axis_label_density"])

        plt_tol_lines = True
        for vib in range(1, FLEETS + 1):
            vib_data = np.array(
                self.vp_records_df[self.vp_records_df["vibrator"] == vib][key].to_list()
            )
            if vib_data.size > 0:
                axis.hist(
                    vib_data,
                    histtype="step",
                    bins=50,
                    range=(setting["min"], setting["max"]),
                    label=vib,
                )

                if plt_tol_lines:
                    if setting["tol_min"] is not None:
                        axis.axvline(setting["tol_min"], color=TOL_COLOR, linewidth=0.5)

                    if setting["tol_max"] is not None:
                        axis.axvline(setting["tol_max"], color=TOL_COLOR, linewidth=0.5)
                    plt_tol_lines = False

        return axis

    def plot_histograms(self, axis, key, setting):
        """method to plot the attribute histogram in a single axis per vibrator"""
        plt_tol_lines = True
        for vib in range(1, FLEETS + 1):
            vib_data = np.array(
                self.vp_records_df[self.vp_records_df["vibrator"] == vib][key].to_list()
            )

            if vib_data.size > 0:
                if key in ["avg_phase", "peak_phase", "avg_dist", "peak_dist"]:
                    data_in_spec = vib_data[vib_data <= setting["tol_max"]]
                    data_out_spec = vib_data[vib_data > setting["tol_max"]]

                elif key in ["avg_force", "peak_force"]:
                    data_in_spec = vib_data[vib_data >= setting["tol_min"]]
                    data_out_spec = vib_data[vib_data < setting["tol_min"]]

                axis[vib - 1].hist(
                    [data_in_spec, data_out_spec],
                    histtype="stepfilled",
                    bins=25,
                    color=["green", "red"],
                    range=(setting["min"], setting["max"]),
                    label=vib + 1,
                )
            if plt_tol_lines:
                if setting["tol_min"] is not None:
                    axis[vib - 1].axvline(
                        setting["tol_min"], color=TOL_COLOR, linewidth=1.0
                    )

                if setting["tol_max"] is not None:
                    axis[vib - 1].axvline(
                        setting["tol_max"], color=TOL_COLOR, linewidth=1.0
                    )

            axis[vib - 1].set_xlim(left=setting["min"], right=setting["max"])
            if vib != FLEETS:
                axis[vib - 1].set_xticklabels([])
                axis[vib - 1].set_xticks([])

            axis[vib - 1].set_yticks([])
            axis[vib - 1].set_yticklabels([])
            if key == "avg_phase":
                axis[vib - 1].set_ylabel(f"V{vib}", fontsize=8)

        axis[0].set_title(key, fontsize=8)
        return axis

    def show_plot(self):
        plt.show()
        plt.close()


if __name__ == "__main__":
    vp_attr = VpAttributes()
    while True:
        production_date = seis_utils.get_production_date()
        if production_date == -1:
            break

        vp_attr.production_date = production_date
        vp_attr.select_data()
        vp_attr.plot_vp_data()
        vp_attr.show_plot()
        vp_attr.plot_histogram_data()
        vp_attr.show_plot()
