""" PyQt shell for vp_attributes
"""
import sys
from pathlib import Path
import datetime
import warnings
from vp_attributes import VpAttributes
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDate, QObject, QThread, pyqtSignal, pyqtSlot, QTimer
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from seis_utils import status_message_generator

matplotlib.use("Qt5Agg")
warnings.filterwarnings("ignore", category=UserWarning)
right_arrow_symbol = "\u25B6"
left_arrow_symbol = "\u25C0"
dialogue_rel_position = (700, 150)
date_widget_size = (400, 250)


class MplCanvas(FigureCanvas):
    def __init__(self, fig):
        super().__init__(fig)


class VpAttrWorker(QObject):
    finished = pyqtSignal(object, object)
    progress = pyqtSignal(str)

    @pyqtSlot(object, object)
    def run(self, vp_attr, production_date):
        self.progress.emit("Wait")
        vp_attr.production_date = production_date
        self.progress.emit("Load")
        vp_attr.select_data()
        self.progress.emit("VpAttr")
        fig_vp_data = vp_attr.plot_vp_data()
        self.progress.emit("VpHist")
        fig_hist_data = vp_attr.plot_histogram_data()
        self.progress.emit("Done")
        self.finished.emit(fig_vp_data, fig_hist_data)


class PyqtViewControl(QtWidgets.QMainWindow):
    """PyQt view and control"""

    request_vp_attributes = pyqtSignal(object, object)

    def __init__(self, vp_attributes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(Path(__file__).parent / "vp_attributes.ui", self)

        self.vp_attr = vp_attributes
        self.actionQuit.triggered.connect(self.quit)
        self.DateEdit.dateChanged.connect(self.select_date)
        self.RB_VpData.clicked.connect(self.show_vp_data)
        self.RB_Histograms.clicked.connect(self.show_hist)
        self.PB_Next.setText(right_arrow_symbol)
        self.PB_Prev.setText(left_arrow_symbol)
        self.PB_Next.clicked.connect(self.next_date)
        self.PB_Prev.clicked.connect(self.previous_date)
        self.production_date = None
        self.canvas_vp_data = None
        self.canvas_vp_hist = None
        self.canvas_widget_data = None
        self.canvas_widget_hist = None
        self.progress_key = None
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
        self.request_vp_attributes.emit(self.vp_attr, self.production_date)
        self.enable_disable_buttons(enabled=False)
        self.thread.start()
        self.progress_key = "Wait"
        self.progress_generator = status_message_generator(self.progress_key)
        next(self.progress_generator)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress_message)
        self.timer.start(1000)

    def get_progress_key(self, key):
        self.progress_key = key

    def update_progress_message(self):
        status_message = self.progress_generator.send(self.progress_key)
        self.StatusLabel.setText(status_message)

    def update_canvas_data(self, fig_vp_data, fig_hist_data):
        self.FormVpDataLayout.removeWidget(self.canvas_widget_data)
        self.FormVpHistLayout.removeWidget(self.canvas_widget_hist)
        self.canvas_widget_data = MplCanvas(fig_vp_data)
        self.canvas_widget_hist = MplCanvas(fig_hist_data)
        self.FormVpDataLayout.addWidget(self.canvas_widget_data)
        self.FormVpHistLayout.addWidget(self.canvas_widget_hist)
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

    def quit(self):
        sys.exit()


def start_app():
    app = QtWidgets.QApplication([])
    vp_attributes = VpAttributes()
    view_control = PyqtViewControl(vp_attributes)
    view_control.show()
    app.exec()


if __name__ == "__main__":
    start_app()
