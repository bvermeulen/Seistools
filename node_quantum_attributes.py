""" display node attributes
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    Copyright: 2021
"""
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seis_utils
from seis_quantum_database import QuantumDb
from seis_settings import MARKERSIZE_NODE, TOL_COLOR, node_plt_settings

SMALL_SIZE = 8
plt.rc("xtick", labelsize=SMALL_SIZE)
plt.rc("ytick", labelsize=SMALL_SIZE)
plt.rc("axes", labelsize=SMALL_SIZE)
FIGSIZE = (12, 8)


class NodeAttributes:
    def __init__(self, production_date):
        self.production_date = production_date

    def select_data(self):
        self.node_records_df = QuantumDb().get_node_data_by_date(self.production_date)

    def plot_node_data(self):
        ax0 = [None for i in range(8)]
        ax1 = [None for i in range(8)]
        fig, (
            (ax0[0], ax1[0], ax0[1], ax1[1]),
            (ax0[2], ax1[2], ax0[3], ax1[3]),
            (ax0[4], ax1[4], ax0[5], ax1[5]),
            (ax0[6], ax1[6], ax0[7], ax1[7]),
        ) = plt.subplots(nrows=4, ncols=4, figsize=FIGSIZE)
        fig.suptitle(
            f"Daily tests for Quantum: "
            f'{self.production_date.strftime("%d %b %Y")} '
            f"({self.node_records_df.shape[0]} nodes)",
            fontweight="bold",
        )
        ax0[7].remove()
        ax1[7].remove()

        for i_plt, (key, plt_setting) in enumerate(node_plt_settings.items()):
            if key in [
                "frequency",
                "damping",
                "sensitivity",
                "resistance",
                "thd",
                "noise",
                "tilt",
            ]:
                ax0[i_plt] = self.plot_attribute(ax0[i_plt], key, plt_setting)
                ax1[i_plt] = self.plot_histogram(ax1[i_plt], key, plt_setting)

        fig.tight_layout()
        plt.show()

    def plot_attribute(self, axis, key, setting):
        axis.set_title(setting["title_attribute"])
        axis.set_ylabel(setting["y-axis_label_attribute"])
        axis.set_ylim(bottom=setting["min"], top=setting["max"])

        node_data = np.array(self.node_records_df[key].to_list())
        if key == "damping":
            node_data *= 100.0

        if node_data.size > 0:
            axis.plot(range(len(node_data)), node_data, ".", markersize=MARKERSIZE_NODE)
            if setting["tol_min"] is not None:
                axis.axhline(setting["tol_min"], color=TOL_COLOR, linewidth=0.5)

            if setting["tol_max"] is not None:
                axis.axhline(setting["tol_max"], color=TOL_COLOR, linewidth=0.5)

        return axis

    def plot_density(self, axis, key, setting):
        """method to plot the attribute density function. If no density plot can be
        made then plot unity density
        """
        x_values = np.arange(setting["min"], setting["max"], setting["interval"])
        axis.set_title(setting["title_density"])
        axis.set_ylabel(setting["y-axis_label_density"])

        node_data = np.array(self.node_records_df[key].to_list())
        if key == "damping":
            node_data *= 100.0

        if (node_count := node_data.size) > 0:
            try:
                density_vals = stats.gaussian_kde(node_data, bw_method=0.5).evaluate(
                    x_values
                )
                density_vals /= density_vals.sum()
                scale_factor = node_count / setting["interval"]

            except np.linalg.LinAlgError:
                # KDE fails is all elements in the vib_data array have the same value
                # In this case run below fallback
                half_intval = 0.5 * setting["interval"]
                val = node_data.mean()
                density_vals = np.where(
                    (x_values > val - half_intval) & (x_values < val + half_intval),
                    1,
                    0,
                )
                scale_factor = node_count

            axis.plot(x_values, scale_factor * density_vals)

        if setting["tol_min"] is not None:
            axis.axvline(setting["tol_min"], color=TOL_COLOR, linewidth=0.5)

        if setting["tol_max"] is not None:
            axis.axvline(setting["tol_max"], color=TOL_COLOR, linewidth=0.5)

        axis.axvline(node_data.mean(), linestyle="dashed", color="black", linewidth=0.7)
        return axis

    def plot_histogram(self, axis, key, setting):
        """method to plot the attribute histogram."""
        axis.set_title(setting["title_density"])
        axis.set_ylabel(setting["y-axis_label_density"])
        node_data = np.array(self.node_records_df[key].to_list())
        if key == "damping":
            node_data *= 100.0

        if node_data.size > 0:
            axis.hist(
                node_data,
                histtype="step",
                bins=50,
                range=(setting["min"], setting["max"]),
            )
            d = 0 if node_data.mean() > 1000 else 2
            axis.text(
                0.98,
                0.98,
                f"Mean: {node_data.mean():.{d}f}",
                size="smaller",
                horizontalalignment="right",
                verticalalignment="top",
                transform=axis.transAxes,
            )

        if setting["tol_min"] is not None:
            axis.axvline(setting["tol_min"], color=TOL_COLOR, linewidth=0.5)

        if setting["tol_max"] is not None:
            axis.axvline(setting["tol_max"], color=TOL_COLOR, linewidth=0.5)

        axis.axvline(node_data.mean(), linestyle="dashed", color="black", linewidth=0.7)
        return axis


if __name__ == "__main__":
    while True:
        production_date = seis_utils.get_production_date()
        if production_date == -1:
            break

        node_attr = NodeAttributes(production_date)
        node_attr.select_data()
        node_attr.plot_node_data()
