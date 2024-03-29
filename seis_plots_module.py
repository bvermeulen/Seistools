""" module to provide plot for vibe attributes and activity
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    © 2023 howdimain
    admin@howdiweb.nl
"""
import datetime
from collections import Counter
import numpy as np
import pandas as pd
from scipy import stats
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
from seis_settings import (
    FLEETS,
    DATABASE,
    TOL_COLOR,
    MARKERSIZE_VP,
    MARKERSIZE_NODE,
    vp_plt_settings,
    node_plt_settings,
)
FONTSIZE_6 = 6
FONTSIZE_8 = 8
plt.rc("xtick", labelsize=FONTSIZE_8)
plt.rc("ytick", labelsize=FONTSIZE_8)
plt.rc("axes", labelsize=FONTSIZE_8)
FIGSIZE = (11.6, 8.7)
FIGSIZE_ACTIVITY_ALL = (11.6, 6.0)
FIGSIZE_ERRORS = (12, 6)
DPI_HISTOGRAM = 90
DPI_ERROR = 90
SECONDS_PER_DAY = 24 * 3600
INTERVAL = 900
max_tol_keys = ["avg_phase", "peak_phase", "avg_dist", "peak_dist"]
min_tol_keys = ["avg_force", "peak_force"]


class DbUtils:
    def __init__(self, database=DATABASE):
        self.database = database

    def get_data_by_date(self, type_data, production_date):
        """retrieve data by date"""
        engine = create_engine(f"sqlite:///{self.database}")
        match type_data.upper():
            case "VP":
                file_table = "vaps_files"
                data_table = "vaps_records"
                date_field = "time_break"
            case "NODE":
                file_table = 'node_quantum_files'
                data_table = "node_quantum_attributes"
                date_field = "test_time"
            case other:
                assert False, f'{type_data} is invalid, must be "VP" or "NODE"'

        # return an empty dataframe if production date is not within the date range of the uploaded data.
        # filename for vaps must be in format <YY><DOY>, and for node <YY><MM><DD>
        try:
            with engine.connect() as con:
                file_names = [row[0] for row in con.execute(f"select file_name from {file_table} order by file_name asc")]
                if not file_names:
                    return pd.DataFrame()
                min_date = (
                    datetime.datetime.strptime(file_names[0][2:7], '%y%j').date() if type_data.upper() == "VP"
                    else datetime.datetime.strptime(file_names[0][0:6], '%y%m%d').date()
                )
                max_date = (
                    datetime.datetime.strptime(file_names[-1][2:7], '%y%j').date() if type_data.upper() == "VP"
                    else datetime.datetime.strptime(file_names[-1][0:6], '%y%m%d').date()
                )
                if not (min_date <= production_date <= max_date):
                    return pd.DataFrame()
        except Exception as e:
            # on error just continue without checking the dates
            pass

        # extract data
        try:
            sql_string = (
                f"SELECT * FROM {data_table} WHERE "
                f'DATE({date_field}) = \'{production_date.strftime("%Y-%m-%d")}\';'
            )
            return pd.read_sql_query(sql_string, con=engine)

        except Exception as e:
            print(f"Error: {e} for {engine}")
            return pd.DataFrame()

    @property
    def database_name(self):
        return self.database.name


class VpAttributes:
    """methods to plot attributes"""

    def __init__(self, vp_records_df, production_date):
        self.production_date = production_date
        self.vp_records_df = vp_records_df
        self.total_vps = self.vp_records_df.shape[0]

    def plot_vp_data(self, figsize=FIGSIZE, dpi=100):
        ax0 = [None for _ in range(6)]
        ax1 = [None for _ in range(6)]
        fig, (
            (ax0[0], ax1[0], ax0[3], ax1[3]),
            (ax0[1], ax1[1], ax0[4], ax1[4]),
            (ax0[2], ax1[2], ax0[5], ax1[5]),
        ) = plt.subplots(nrows=3, ncols=4, figsize=figsize, dpi=dpi)
        fig.suptitle(
            f'Vib attributes for: {self.production_date.strftime("%d %b %Y")} ({self.total_vps} VPs)',
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
        plt.close()
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

    def plot_histogram_data(self, figsize=FIGSIZE, dpi=DPI_HISTOGRAM):
        gs_kw = {"hspace": 0.15, "wspace": 0.20}
        fig, ax = plt.subplots(
            nrows=FLEETS,
            ncols=6,
            figsize=figsize,
            dpi=dpi,
            gridspec_kw=gs_kw,
        )
        fig.suptitle(
            f'Vib attributes for: {self.production_date.strftime("%d %b %Y")} ({self.total_vps} VPs)',
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

        plt.close()
        return fig

    def plot_histograms(self, axis, key, setting):
        """method to plot the attribute histogram in a single axis per vibrator"""
        plt_tol_lines = True
        for vib in range(1, FLEETS + 1):
            vib_data = np.array(
                self.vp_records_df[self.vp_records_df["vibrator"] == vib][key].to_list()
            )
            if vib_data.size > 0:
                if key in max_tol_keys:
                    data_in_spec = vib_data[vib_data <= setting["tol_max"]]
                    data_out_spec = vib_data[vib_data > setting["tol_max"]]

                elif key in min_tol_keys:
                    data_in_spec = vib_data[vib_data >= setting["tol_min"]]
                    data_out_spec = vib_data[vib_data < setting["tol_min"]]

                axis[vib - 1].hist(
                    [data_in_spec, data_out_spec],
                    histtype="stepfilled",
                    align="right",
                    bins=25,
                    color=["green", "red"],
                    range=(setting["min"], setting["max"]),
                    label=vib + 1,
                )
            if plt_tol_lines:
                if setting["tol_min"] is not None:
                    axis[vib - 1].axvline(
                        setting["tol_min"] + 1, color=TOL_COLOR, linewidth=1.0
                    )

                if setting["tol_max"] is not None:
                    axis[vib - 1].axvline(
                        setting["tol_max"] + 1, color=TOL_COLOR, linewidth=1.0
                    )

            axis[vib - 1].set_xlim(left=setting["min"], right=setting["max"])
            if vib != FLEETS:
                axis[vib - 1].set_xticklabels([])
                axis[vib - 1].set_xticks([])

            axis[vib - 1].set_yticks([])
            axis[vib - 1].set_yticklabels([])
            if key == "avg_phase":
                axis[vib - 1].set_ylabel(f"V{vib}", fontsize=FONTSIZE_8)

        axis[0].set_title(key, fontsize=FONTSIZE_8)
        return axis

    def plot_error_data(self, figsize=FIGSIZE_ERRORS, dpi=DPI_ERROR):
        gs_kw = {"wspace": 0.55}
        fig, ax = plt.subplots(
            nrows=1,
            ncols=6,
            figsize=figsize,
            dpi=dpi,
            gridspec_kw=gs_kw,
        )
        fig.suptitle(
            f'Vib attributes for: {self.production_date.strftime("%d %b %Y")} ({self.total_vps} VPs)',
            fontweight="bold",
        )
        for ax_index, (key, plt_setting) in enumerate(vp_plt_settings.items()):
            color = "grey"
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

            ax[ax_index] = self.plot_error_bars(ax[ax_index], key, plt_setting)

            # add border around the ax
            bbox = ax[ax_index].get_tightbbox(fig.canvas.get_renderer())
            x0, y0, width, height = bbox.transformed(fig.transFigure.inverted()).bounds
            xpad = 0.01
            ypad = 0.01
            fig.add_artist(
                plt.Rectangle(
                    (x0 - xpad, y0 - ypad),
                    width + 2 * xpad,
                    height + 2 * ypad,
                    edgecolor=color,
                    linewidth=1,
                    fill=False,
                )
            )
        return fig

    def plot_error_bars(self, axis, key, setting):
        y_step = 0.20
        bar_height = 0.19
        y_vals = np.arange(1, FLEETS + 1) * y_step
        y_labels = [None for _ in range(FLEETS)]
        for vib in range(1, FLEETS + 1):
            vib_data = np.array(
                self.vp_records_df[self.vp_records_df["vibrator"] == vib][key].to_list()
            )
            if key in max_tol_keys:
                data_out_spec = vib_data[vib_data > setting["tol_max"]]
                x_label = f"Limit < {setting['tol_max'] + 1}"

            elif key in min_tol_keys:
                data_out_spec = vib_data[vib_data < setting["tol_min"]]
                x_label = f"Limit > {setting['tol_min'] - 1}"

            else:
                assert False, f"incorrect key: {key}"

            if (size := vib_data.size) > 0:
                out_spec_percentage = data_out_spec.size / size * 100

                axis.barh(
                    y_vals[FLEETS - vib],
                    out_spec_percentage,
                    align="center",
                    height=bar_height,
                    color="red",
                )
                axis.barh(
                    y_vals[FLEETS - vib],
                    100 - out_spec_percentage,
                    align="center",
                    height=bar_height,
                    left=out_spec_percentage,
                    color="green",
                )

                axis.text(
                    104,
                    y_vals[FLEETS - vib],
                    f"{out_spec_percentage:5.1f}%",
                    fontsize=FONTSIZE_6,
                )
            y_labels[FLEETS - vib] = f"V{vib}"

        axis.xaxis.set_major_formatter(mtick.PercentFormatter(100.0))
        axis.set_xlim(left=0, right=120)
        max_y = FLEETS * y_step + bar_height * 0.6
        axis.set_ylim(0, max_y)
        axis.set_xlabel(x_label, fontsize=FONTSIZE_6)
        axis.xaxis.set_label_coords(0.4, -0.08)
        axis.set_xticks([0, 100])
        axis.set_yticks([])
        for side in ["top", "right", "bottom", "left"]:
            axis.spines[side].set_visible(False)
        axis.yaxis.set_tick_params(length=0)
        axis.set_yticks(y_vals, y_labels, fontsize=FONTSIZE_6)
        axis.set_title(f"        {key}", fontsize=FONTSIZE_6, loc="left")

        return axis


class VpActivity:
    """methods to plot vibrator acticity"""

    def __init__(self, vp_records_df, production_date):
        self.vp_records_df = vp_records_df
        self.production_date = production_date
        self.vps_by_second = {second: [] for second in range(SECONDS_PER_DAY)}
        self.vps_by_interval_list = []
        self.vps_by_interval_df = None
        self.populate_vps_by_second()
        self.aggregate_vps_by_interval()

    def populate_vps_by_second(self):
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

    def add_vps_interval(self, interval, second, vib_list):
        _date = datetime.datetime.combine(self.production_date, datetime.time(0, 0, 0))
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

    def aggregate_vps_by_interval(self, interval: int = INTERVAL):
        """aggregate number of vps by interval
        interval: integer seconds interval
        """
        self.total_vps = 0
        second = 0
        while second < SECONDS_PER_DAY:
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

        self.add_vps_interval(interval, SECONDS_PER_DAY, [])
        self.vps_by_interval_df = pd.DataFrame(
            self.vps_by_interval_list,
            columns=(
                ["time"]
                + [f"V{i:02}" for i in range(1, FLEETS + 1)]
                + ["total", "vps_hour", "num_vibs"]
            ),
        )

    def plot_vps_by_interval(self, interval: int = INTERVAL):
        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=FIGSIZE_ACTIVITY_ALL)
        fig.suptitle(
            f'{vp_plt_settings["vib_activity"]["fig_title"]} '
            f'{self.production_date.strftime("%d-%b-%Y")} ({self.total_vps} VPs)',
            fontweight="bold",
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
        plt.close()
        return fig

    def plot_vps_by_vibe(self, interval: int = INTERVAL):
        ax = [None for _ in range(FLEETS)]
        fig, ax = plt.subplots(
            nrows=FLEETS, ncols=1, figsize=FIGSIZE, gridspec_kw={"hspace": 0.10}
        )
        fig.suptitle(
            f'{vp_plt_settings["vib_activity"]["fig_title"]} '
            f'{self.production_date.strftime("%d-%b-%Y")} ({self.total_vps} VPs)',
            fontweight="bold",
        )
        time_format = mdates.DateFormatter("%H:%M")
        times = self.vps_by_interval_df["time"].to_numpy()
        ax[0].set_title(f"VPs per hour - interval {interval / 60:.0f} minutes")
        for vib in range(1, FLEETS + 1):
            ax[vib - 1].yaxis.set_ticks(np.arange(0, 200, 50))
            ax[vib - 1].set_xticklabels([])
            ax[vib - 1].tick_params(axis="both", labelsize=8)
            ax[vib - 1].set_ylabel(f"V{vib}", fontsize=8)
            ax[vib - 1].set_ylim(bottom=0, top=200)
            ax[vib - 1].xaxis.set_major_formatter(time_format)
            ax[vib - 1].grid(axis="y", linewidth=0.5, linestyle="-", zorder=0)
            ax[vib - 1].grid(axis="x", linewidth=0.5, linestyle="-", zorder=0)
            vps = (
                self.vps_by_interval_df[f"V{vib:02}"].fillna(0).to_numpy()
                * 3600
                / interval
            )
            ax[vib - 1].step(times, vps, where="post", linewidth=0.9, zorder=3)

        plt.close()
        return fig


class NodeAttributes:
    def __init__(self, node_records_df, production_date):
        self.node_records_df = node_records_df
        self.production_date = production_date

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
        plt.close()
        return fig

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

