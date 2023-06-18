""" PyQt shell for vp_attributes
"""
# TODO add vib acitivity, save figures, select database
import sys
import time
import datetime
import warnings
from pathlib import Path
from vp_plots_module import DbUtils, VpAttributes, VpActivity
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDate, QObject, QThread, pyqtSignal, pyqtSlot, QTimer
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from seis_utils import status_message_generator

matplotlib.use("Qt5Agg")
warnings.filterwarnings("ignore", category=UserWarning)
RIGHT_ARROW_SYMBOL = "\u25B6"
LEFT_ARROW_SYMBOL = "\u25C0"
TIMER_DELAY = 1000


class MplCanvas(FigureCanvas):
    def __init__(self, fig):
        super().__init__(fig)


class VpAttrWorker(QObject):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)

    @pyqtSlot(object, object)
    def run(self, project, production_date):
        db_utils = DbUtils(database=project) if project else DbUtils()
        figure_dict = {}
        self.progress.emit("Wait")
        self.progress.emit("Load")
        vp_df = db_utils.get_vp_data_by_date(production_date)
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

        self.actionQuit.triggered.connect(self.quit)
        self.DateEdit.dateChanged.connect(self.select_date)
        self.RB_VpData.clicked.connect(self.show_vp_data)
        self.RB_Histograms.clicked.connect(self.show_hist)
        self.RB_Activity_All.clicked.connect(self.show_activity_all)
        self.RB_Activity_Each.clicked.connect(self.show_activity_each)
        self.PB_Next.setText(RIGHT_ARROW_SYMBOL)
        self.PB_Prev.setText(LEFT_ARROW_SYMBOL)
        self.PB_Next.clicked.connect(self.next_date)
        self.PB_Prev.clicked.connect(self.previous_date)
        self.production_date = None
        self.canvas_vp_data = None
        self.canvas_vp_hist = None
        self.canvas_dict = {}
        self.figure_dict = {}
        self.progress_key = None
        self.project = None
        self.RB_VpData.setChecked(True)
        self.StatusHeaderLabel.setText("Status")
        self.StatusLabel.setText("")
        # set the initial date to tomorrow, so date is changed when selecting
        # today
        self.DateEdit.setDate(
            (datetime.datetime.now() + datetime.timedelta(days=1)).date()
        )

    def enable_disable_buttons(self, enabled=False):
        self.DateEdit.setEnabled(enabled)
        self.PB_Next.setEnabled(enabled)
        self.PB_Prev.setEnabled(enabled)

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

    def get_progress_key(self, key):
        self.progress_key = key

    def update_progress_message(self):
        status_message = self.progress_generator.send(self.progress_key)
        self.StatusLabel.setText(status_message)

    def update_canvas_data(self, figure_dict):
        self.figure_dict = figure_dict
        self.FormVpDataLayout.removeWidget(self.canvas_dict.get("VpAttr"))
        self.FormVpHistLayout.removeWidget(self.canvas_dict.get("VpHist"))
        self.FormVpActAllLayout.removeWidget(self.canvas_dict.get("ActAll"))
        self.FormVpActEachLayout.removeWidget(self.canvas_dict.get("ActEach"))
        self.canvas_dict["VpAttr"] = MplCanvas(self.figure_dict.get("VpAttr"))
        self.canvas_dict["VpHist"] = MplCanvas(self.figure_dict.get("VpHist"))
        self.canvas_dict["ActAll"] = MplCanvas(self.figure_dict.get("ActAll"))
        self.canvas_dict["ActEach"] = MplCanvas(self.figure_dict.get("ActEach"))
        self.FormVpDataLayout.addWidget(self.canvas_dict.get("VpAttr"))
        self.FormVpHistLayout.addWidget(self.canvas_dict.get("VpHist"))
        self.FormVpActAllLayout.addWidget(self.canvas_dict.get("ActAll"))
        self.FormVpActEachLayout.addWidget(self.canvas_dict.get("ActEach"))
        self.enable_disable_buttons(enabled=True)
        self.update_progress_message()
        self.timer.stop()

    def select_plot(self):
        if self.RB_VpData.isChecked():
            self.show_vp_data()

        elif self.RB_Histograms.isChecked():
            self.show_hist()

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

    def show_vp_data(self):
        if not self.production_date:
            return
        self.stackedWidget.setCurrentIndex(0)

    def show_hist(self):
        if not self.production_date:
            return
        self.stackedWidget.setCurrentIndex(1)

    def show_activity_all(self):
        if not self.production_date:
            return
        self.stackedWidget.setCurrentIndex(2)

    def show_activity_each(self):
        if not self.production_date:
            return
        self.stackedWidget.setCurrentIndex(3)

    def quit(self):
        sys.exit()


def start_app():
    app = QtWidgets.QApplication([])
    view_control = PyqtViewControl()
    view_control.show()
    app.exec()


if __name__ == "__main__":
    start_app()
