"""PyQt shell for vp_attributes
author: Bruno Vermeulen
email: bvermeulen@hotmail.com
© 2023 howdimain
admin@howdiweb.nl
"""

import sys
import time
import datetime
import re
from functools import partial
import warnings
from pathlib import Path
from seis_plots_module import DbUtils, VpAttributes, VpActivity, NodeAttributes
from PyQt6 import uic, QtWidgets
from PyQt6.QtCore import QDate, QObject, QThread, pyqtSignal, pyqtSlot, QTimer
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from seis_utils import status_message_generator
from seis_settings import PROJECT_PATH, PLOT_RESULTS, VIBRATORS, vp_plt_settings


matplotlib.use("QtAgg")
warnings.filterwarnings("ignore", category=UserWarning)
RIGHT_ARROW_SYMBOL = "\u25b6"
LEFT_ARROW_SYMBOL = "\u25c0"
REFRESH_SYMBOL = "\u27f3"
TIMER_DELAY = 750
STATUS_DELAY = 0.750
destination_folder_description = "Saved plots are stored in: "
base_database = Path(PROJECT_PATH.parent)
qcb_empty_style = """
    QCheckBox::indicator {padding: 2px; width: 14px; height: 14px; color: grey; border: 2px solid grey; border-radius: 4px;} 
    QCheckBox::indicator:checked {image: url(seis_plots_images/check.png);} 
    QCheckBox {padding: 2px 2px; color: black; background-color: transparent;}
"""
qcb_color_style = """
    QCheckBox::indicator {{padding: 2px; width: 14px; height: 14px; border: 2px solid lightblue; border-radius: 4px;}} 
    QCheckBox::indicator:checked {{image: url(seis_plots_images/check-color.png);}} 
    QCheckBox {{padding: 2px 2px; color: lightblue; background-color: {color};}}
"""


class MplCanvas(FigureCanvas):
    def __init__(self, fig):
        super().__init__(fig)


class SeisAttrWorker(QObject):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    database = pyqtSignal(str)

    @pyqtSlot(object, object, object)
    def run(self, project, production_date, vp_mask):
        db_utils = DbUtils(database=project) if project else DbUtils()
        self.database.emit(db_utils.database_name)
        figure_dict = {}
        self.progress.emit("Wait")
        time.sleep(STATUS_DELAY)
        self.progress.emit("LoadVp")
        time.sleep(STATUS_DELAY)
        vp_df = db_utils.get_data_by_date("VP", production_date)
        ep_df = db_utils.get_data_by_date("EP", production_date)
        activity_type = vp_plt_settings["vib_activity"]["activity_type"]

        if not vp_df.empty:
            vp_plot_attributes = VpAttributes(vp_df, production_date, vp_mask)
            match activity_type:
                case "EP":
                    ep_plot_activity = VpActivity(ep_df, production_date, activity_type)

                case "VP":
                    ep_plot_activity = VpActivity(vp_df, production_date, activity_type)

                case _:
                    print(f"invalid option: {activity_type}")

            self.progress.emit("VpAttr")
            figure_dict["VpAttr"] = vp_plot_attributes.plot_vp_data()
            time.sleep(STATUS_DELAY)
            self.progress.emit("VpHist")
            figure_dict["VpHist"] = vp_plot_attributes.plot_histogram_data()
            time.sleep(STATUS_DELAY)
            self.progress.emit("VpErr")
            figure_dict["VpErr"] = vp_plot_attributes.plot_error_data()
            time.sleep(STATUS_DELAY)
            self.progress.emit("ActAll")
            figure_dict["ActAll"] = ep_plot_activity.plot_vps_by_interval()
            time.sleep(STATUS_DELAY)
            self.progress.emit("ActEach")
            figure_dict["ActEach"] = ep_plot_activity.plot_vps_by_vibe()
            time.sleep(STATUS_DELAY)

        else:
            self.progress.emit("NoVpData")
            time.sleep(STATUS_DELAY)

        self.progress.emit("LoadNode")
        time.sleep(STATUS_DELAY)
        node_df = db_utils.get_data_by_date("NODE", production_date)
        if not node_df.empty:
            node_plot_attributes = NodeAttributes(node_df, production_date)
            self.progress.emit("NodeAttr")
            figure_dict["NodeAttr"] = node_plot_attributes.plot_node_data()
            time.sleep(STATUS_DELAY)

        else:
            self.progress.emit("NoNodeData")
            time.sleep(STATUS_DELAY)

        self.progress.emit("Done")
        self.finished.emit(figure_dict)


class PyqtViewControl(QtWidgets.QMainWindow):
    """PyQt view and control"""

    request_seis_attributes = pyqtSignal(object, object, object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(Path(__file__).parent / "seis_plots.ui", self)
        self.plot_dict = {
            "VpAttr": {
                "index": 1,
                "canvas": None,
                "rb": self.RB_Type_01,
                "layout": self.FormLayoutType_01,
                "save": self.ActionSaveType_01,
                "file_name": "vp_attributes",
                "fig": None,
            },
            "VpHist": {
                "index": 2,
                "canvas": None,
                "rb": self.RB_Type_02,
                "layout": self.FormLayoutType_02,
                "save": self.ActionSaveType_02,
                "file_name": "vp_histograms",
                "fig": None,
            },
            "VpErr": {
                "index": 3,
                "canvas": None,
                "rb": self.RB_Type_03,
                "layout": self.FormLayoutType_03,
                "save": self.ActionSaveType_03,
                "file_name": "vp_error_bars",
                "fig": None,
            },
            "ActAll": {
                "index": 4,
                "canvas": None,
                "rb": self.RB_Type_04,
                "layout": self.FormLayoutType_04,
                "save": self.ActionSaveType_04,
                "file_name": "vp_activity_all",
                "fig": None,
            },
            "ActEach": {
                "index": 5,
                "canvas": None,
                "rb": self.RB_Type_05,
                "layout": self.FormLayoutType_05,
                "save": self.ActionSaveType_05,
                "file_name": "vp_activity_each",
                "fig": None,
            },
            "NodeAttr": {
                "index": 6,
                "canvas": None,
                "rb": self.RB_Type_06,
                "layout": self.FormLayoutType_06,
                "save": self.ActionSaveType_06,
                "file_name": "node_attributes",
                "fig": None,
            },
        }
        self.ActionQuit.triggered.connect(self.quit)
        self.ActionDefaultDatabase.triggered.connect(
            partial(self.select_database, default=True)
        )
        self.ActionSelectDatabase.triggered.connect(
            partial(self.select_database, default=False)
        )
        self.ActionDestinationFolder.triggered.connect(self.select_destination_folder)
        self.ActionSaveAll.triggered.connect(partial(self.save_plot, "All"))
        self.DateEdit.dateChanged.connect(self.select_date)
        for key, value in self.plot_dict.items():
            value["rb"].clicked.connect(partial(self.show_plot, value["index"] - 1))
            value["save"].triggered.connect(partial(self.save_plot, key))

        self.PB_Next.setText(RIGHT_ARROW_SYMBOL)
        self.PB_Prev.setText(LEFT_ARROW_SYMBOL)
        self.PB_Refresh.setText(REFRESH_SYMBOL)
        self.PB_Next.clicked.connect(self.next_date)
        self.PB_Prev.clicked.connect(self.previous_date)
        self.PB_Refresh.clicked.connect(self.refresh)
        self.vib_checkboxes = []
        for vib in range(VIBRATORS):
            v_checkbox = QtWidgets.QCheckBox(f"V{vib + 1}", self.SelectionFrame)
            v_checkbox.setStyleSheet(qcb_empty_style)
            v_checkbox.setChecked(True)
            v_checkbox.toggled.connect(self.handle_vib_toggle)
            self.vib_checkboxes.append(v_checkbox)
            self.SelectionFrameLayout.addWidget(v_checkbox)

        self.v_label = QtWidgets.QLabel("Total: ")
        self.SelectionFrameLayout.addWidget(self.v_label)
        self.vib_mask = [False for _ in range(VIBRATORS)]
        self.figure_dict = {}
        self.production_date = None
        self.progress_key = None
        self.project = None
        self.database_name = None
        self.destination_folder = Path(PLOT_RESULTS)
        self.RB_Type_01.setChecked(True)
        self.StatusHeaderLabel.setText("Status")
        self.StatusDatabaseLabel.setText("")
        self.StatusDestinationLabel.setText(
            "".join([destination_folder_description, str(self.destination_folder)])
        )
        self.StatusLabel.setText("")
        self.DateEdit.setDate(datetime.datetime.now().date())

    def run_plot_thread(self):
        if not self.production_date:
            return

        self.thread = QThread()
        self.worker = SeisAttrWorker()
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.update_canvas_data)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.get_progress_key)
        self.worker.database.connect(self.get_database_name)
        self.request_seis_attributes.connect(self.worker.run)
        self.request_seis_attributes.emit(
            self.project, self.production_date, self.vib_mask
        )
        self.enable_disable_buttons(enabled=False)
        self.thread.start()
        self.progress_key = "Wait"
        self.progress_generator = status_message_generator(self.progress_key)
        next(self.progress_generator)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress_message)
        self.timer.start(TIMER_DELAY)

    def update_canvas_data(self, figure_dict):
        self.enable_disable_buttons(enabled=True)
        self.update_progress_message()
        self.timer.stop()

        for key, value in self.plot_dict.items():
            value["fig"] = figure_dict.get(key)
            if value["canvas"]:
                value["canvas"].hide()
                value["layout"].removeWidget(value["canvas"])
                value["canvas"] = None

            if value["fig"]:
                value["canvas"] = MplCanvas(value["fig"])
                value["layout"].addWidget(value["canvas"])

        if fig := self.plot_dict["VpAttr"]["fig"]:
            handles, vib_labels = fig.axes[0].get_legend_handles_labels()
            self.handle_vib_colors(handles, vib_labels)

        else:
            self.clear_vib_checkboxes()

    def handle_vib_toggle(self, _):
        for i, v_checkbox in enumerate(self.vib_checkboxes):
            self.vib_mask[i] = False if v_checkbox.isChecked() else True

    def handle_vib_colors(self, handles, labels):
        vib_colors = [handle.get_color() for handle in handles]
        set_label_totals = False
        for cb_index in range(VIBRATORS):
            label_index = next(
                (i for i, s in enumerate(labels[:-1]) if int(s[1:3]) == cb_index + 1),
                None,
            )
            if label_index is not None:
                self.vib_checkboxes[cb_index].setStyleSheet(
                    qcb_color_style.format(color=vib_colors[label_index])
                )
                self.vib_checkboxes[cb_index].setText(labels[label_index])
                set_label_totals = True

            else:
                self.vib_checkboxes[cb_index].setStyleSheet(qcb_empty_style)
                self.vib_checkboxes[cb_index].setChecked(False)
                self.vib_checkboxes[cb_index].setText(f"V{cb_index + 1}")

        self.v_label.setText(
            f"Total: {re.search(r"\((.*)\)",labels[-1]).group(1)}"
            if set_label_totals
            else "Total: "
        )

    def clear_vib_checkboxes(self):
        for cb_index in range(VIBRATORS):
            self.vib_checkboxes[cb_index].setStyleSheet(qcb_empty_style)
            self.vib_checkboxes[cb_index].setChecked(True)
            self.vib_checkboxes[cb_index].setText(f"V{cb_index + 1}")
            self.vib_mask[cb_index] = False
            self.v_label.setText("Total: ")

    def enable_disable_buttons(self, enabled=False):
        self.DateEdit.setEnabled(enabled)
        self.PB_Next.setEnabled(enabled)
        self.PB_Prev.setEnabled(enabled)
        self.PB_Refresh.setEnabled(enabled)

    def get_progress_key(self, key):
        self.progress_key = key

    def update_progress_message(self):
        status_message = self.progress_generator.send(self.progress_key)
        self.StatusLabel.setText(status_message)

    def get_database_name(self, name):
        self.database_name = name
        self.StatusDatabaseLabel.setText(self.database_name)

    def select_plot(self):
        for val in self.plot_dict.values():
            if val["rb"].isChecked():
                plot_type_index = val["index"] - 1
                break
        self.show_plot(plot_type_index)

    def select_date(self):
        new_date = self.DateEdit.date().toPyDate()
        if not self.production_date:
            self.production_date = new_date
            return

        self.production_date = new_date
        self.StatusHeaderLabel.setText(
            ": ".join(["Status", self.production_date.strftime("%d %b %Y")])
        )
        self.clear_vib_checkboxes()
        self.run_plot_thread()
        self.select_plot()

    def previous_date(self):
        if self.production_date:
            self.production_date -= datetime.timedelta(days=1)
            self.DateEdit.setDate(QDate(self.production_date))

    def next_date(self):
        if self.production_date:
            self.production_date += datetime.timedelta(days=1)
            self.DateEdit.setDate(QDate(self.production_date))

    def refresh(self):
        self.run_plot_thread()

    def show_plot(self, plot_index: int):
        if not self.production_date:
            return
        self.stackedWidget.setCurrentIndex(plot_index)

    def select_database(self, default=True):
        if default:
            self.project = None

        else:
            database = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Open file",
                str(base_database),
                "SQLite files (*.sqlite3 *.sqlite);; All (*.*)",
            )
            self.project = Path(database[0])

    def select_destination_folder(self):
        destination_folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select destination folder", directory=PLOT_RESULTS.parent.as_posix()
        )
        if destination_folder:
            self.destination_folder = Path(destination_folder)
        self.StatusDestinationLabel.setText(
            "".join([destination_folder_description, str(self.destination_folder)])
        )

    def save_plot(self, plot_key):
        base_file_name = "".join([self.production_date.strftime("%y%m%d"), "_"])
        for key, value in self.plot_dict.items():
            if not (fig := value["fig"]):
                continue

            if key == "VpAttr":
                handles, labels = fig.axes[0].get_legend_handles_labels()
                fig.legend(
                    handles,
                    labels,
                    loc="upper right",
                    frameon=True,
                    fontsize="small",
                    framealpha=1,
                    markerscale=40,
                )

            file_name = self.destination_folder / "".join(
                [base_file_name, value.get("file_name"), ".png"]
            )
            if plot_key == "All" or key == plot_key:
                fig.savefig(file_name)

    def quit(self):
        sys.exit()


def start_app():
    app = QtWidgets.QApplication([])
    view_control = PyqtViewControl()
    view_control.show()
    app.exec()


if __name__ == "__main__":
    start_app()
