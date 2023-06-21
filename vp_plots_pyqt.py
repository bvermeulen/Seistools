""" PyQt shell for vp_attributes
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    © 2023 howdimain
    admin@howdiweb.nl
"""
import sys
import time
import datetime
from functools import partial
import warnings
from pathlib import Path
from vp_plots_module import DbUtils, VpAttributes, VpActivity
from PyQt6 import uic, QtWidgets
from PyQt6.QtCore import QDate, QObject, QThread, pyqtSignal, pyqtSlot, QTimer
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from seis_utils import status_message_generator

matplotlib.use("QtAgg")
warnings.filterwarnings("ignore", category=UserWarning)
RIGHT_ARROW_SYMBOL = "\u25B6"
LEFT_ARROW_SYMBOL = "\u25C0"
TIMER_DELAY = 750
destination_folder_description = "Saved plots are stored in: "
base_database = Path("D:\\OneDrive\\Work\\PDO\\")


class MplCanvas(FigureCanvas):
    def __init__(self, fig):
        super().__init__(fig)


class VpAttrWorker(QObject):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    database = pyqtSignal(str)

    @pyqtSlot(object, object)
    def run(self, project, production_date):
        db_utils = DbUtils(database=project) if project else DbUtils()
        self.database.emit(db_utils.database_name)
        figure_dict = {}
        self.progress.emit("Wait")
        self.progress.emit("Load")
        vp_df = db_utils.get_vp_data_by_date(production_date)
        if vp_df.empty:
            self.progress.emit("Error")
            self.finished.emit(figure_dict)
            return

        vp_plot_attributes = VpAttributes(vp_df, production_date)
        vp_plot_activity = VpActivity(vp_df, production_date)
        self.progress.emit("VpAttr")
        figure_dict["VpAttr"] = vp_plot_attributes.plot_vp_data()
        self.progress.emit("VpHist")
        figure_dict["VpHist"] = vp_plot_attributes.plot_histogram_data()
        self.progress.emit("ActAll")
        figure_dict["ActAll"] = vp_plot_activity.plot_vps_by_interval()
        time.sleep(1.0)
        self.progress.emit("ActEach")
        figure_dict["ActEach"] = vp_plot_activity.plot_vps_by_vibe()
        time.sleep(1.0)
        self.progress.emit("Done")
        self.finished.emit(figure_dict)


class PyqtViewControl(QtWidgets.QMainWindow):
    """PyQt view and control"""

    request_vp_attributes = pyqtSignal(object, object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(Path(__file__).parent / "vp_plots.ui", self)
        self.plot_dict = {
            "VpAttr": {
                "index": 1,
                "canvas": None,
                "rb": self.RB_VpType_01,
                "layout": self.FormLayoutVpType_01,
                "save": self.ActionSaveVpType_01,
                "file_name": "vp_attributes",
                "fig": {},
            },
            "VpHist": {
                "index": 2,
                "canvas": None,
                "rb": self.RB_VpType_02,
                "layout": self.FormLayoutVpType_02,
                "save": self.ActionSaveVpType_02,
                "file_name": "vp_histograms",
                "fig": {},
            },
            "ActAll": {
                "index": 3,
                "canvas": None,
                "rb": self.RB_VpType_03,
                "layout": self.FormLayoutVpType_03,
                "save": self.ActionSaveVpType_03,
                "file_name": "vp_activity_all",
                "fig": {},
            },
            "ActEach": {
                "index": 4,
                "canvas": None,
                "rb": self.RB_VpType_04,
                "layout": self.FormLayoutVpType_04,
                "save": self.ActionSaveVpType_04,
                "file_name": "vp_activity_each",
                "fig": {},
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
        self.PB_Next.clicked.connect(self.next_date)
        self.PB_Prev.clicked.connect(self.previous_date)
        self.figure_dict = {}
        self.production_date = None
        self.progress_key = None
        self.project = None
        self.database_name = None
        self.destination_folder = Path(sys.path[0])
        self.RB_VpType_01.setChecked(True)
        self.StatusHeaderLabel.setText("Status")
        self.StatusDatabaseLabel.setText("")
        self.StatusDestinationLabel.setText(
            "".join([destination_folder_description, str(self.destination_folder)])
        )
        self.StatusLabel.setText("")
        # set the initial date to tomorrow, so date is changed when selecting
        # today
        self.DateEdit.setDate(
            (datetime.datetime.now() + datetime.timedelta(days=1)).date()
        )

    def run_plot_thread(self):
        if not self.production_date:
            return

        self.thread = QThread()
        self.worker = VpAttrWorker()
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.update_canvas_data)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.get_progress_key)
        self.worker.database.connect(self.get_database_name)
        self.request_vp_attributes.connect(self.worker.run)
        self.request_vp_attributes.emit(self.project, self.production_date)
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

        if not figure_dict:
            return

        for key, value in self.plot_dict.items():
            value["fig"] = figure_dict.get(key)
            if value["canvas"]:
                value["layout"].removeWidget(value["canvas"])

            value["canvas"] = MplCanvas(value["fig"])
            value["layout"].addWidget(value["canvas"])

    def enable_disable_buttons(self, enabled=False):
        self.DateEdit.setEnabled(enabled)
        self.PB_Next.setEnabled(enabled)
        self.PB_Prev.setEnabled(enabled)

    def get_progress_key(self, key):
        self.progress_key = key

    def get_database_name(self, name):
        self.database_name = name
        self.StatusDatabaseLabel.setText(self.database_name)

    def update_progress_message(self):
        status_message = self.progress_generator.send(self.progress_key)
        self.StatusLabel.setText(status_message)

    def select_plot(self):
        for val in self.plot_dict.values():
            if val["rb"].isChecked():
                plot_type_index = val["index"] - 1
                break
        self.show_plot(plot_type_index)

    def select_date(self):
        new_date = self.DateEdit.date().toPyDate()
        # initial DateEdit date is set to tomorrow and self.production_date as None
        # below check avoids starting the long thread making plots immediately at the
        # start of the application
        if not self.production_date:
            self.production_date = new_date
            return

        self.production_date = new_date
        self.StatusHeaderLabel.setText(
            ": ".join(["Status", self.production_date.strftime("%d %b %Y")])
        )
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
            self, "Select destination folder"
        )
        if destination_folder:
            self.destination_folder = Path(destination_folder)
        self.StatusDestinationLabel.setText(
            "".join([destination_folder_description, str(self.destination_folder)])
        )

    def save_plot(self, plot_key):
        base_file_name = "".join([self.production_date.strftime("%y%m%d"), "_"])
        for key, value in self.plot_dict.items():
            if not value["fig"]:
                break

            file_name = self.destination_folder / "".join(
                [base_file_name, value.get("file_name"), ".png"]
            )
            if plot_key == "All" or key == plot_key:
                value["fig"].savefig(file_name)

    def quit(self):
        sys.exit()


def start_app():
    app = QtWidgets.QApplication([])
    view_control = PyqtViewControl()
    view_control.show()
    app.exec()


if __name__ == "__main__":
    start_app()
