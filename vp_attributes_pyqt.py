""" PyQt shell for vp_attributes
"""
import sys
from pathlib import Path
import datetime
import warnings
from vp_attributes import VpAttributes
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDate, QObject, QThread, pyqtSignal, pyqtSlot
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

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
        print(f"start thread for {production_date}")
        self.progress.emit("please wait ...")
        vp_attr.production_date = production_date
        vp_attr.select_data()
        self.progress.emit("please wait ... vp date")
        fig_vp_data = vp_attr.plot_vp_data()
        self.progress.emit("please wait ... vp hist")
        fig_hist_data = vp_attr.plot_histogram_data()
        self.progress.emit("done")
        self.finished.emit(fig_vp_data, fig_hist_data)
        print("thread completed\n")


class DateDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Select date ...")
        self.setGeometry(
            parent.pos().x() + dialogue_rel_position[0],
            parent.pos().y() + dialogue_rel_position[1],
            date_widget_size[0] + 10,
            date_widget_size[1] + 10,
        )
        self.date_widget = QtWidgets.QCalendarWidget(self)
        self.date_widget.setGeometry(5, 5, date_widget_size[0], date_widget_size[1])
        self.date_widget.clicked[QDate].connect(self.clicked)

    def clicked(self):
        self.accept()

    @property
    def date(self):
        return self.date_widget.selectedDate().toPyDate()


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
        self.RB_VpData.setChecked(True)

        self.DateEdit.setDate(
            (datetime.datetime.now() + datetime.timedelta(days=1)).date()
        )
        self.DateLineEdit.setText("")
        self.StatusLineEdit.setText("")

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
        self.worker.progress.connect(self.progress_message)
        self.request_vp_attributes.connect(self.worker.run)
        self.thread.start()
        self.request_vp_attributes.emit(self.vp_attr, self.production_date)
        self.enable_disable_buttons(enabled=False)

    def progress_message(self, message):
        self.StatusLineEdit.setText(message)

    def update_canvas_data(self, fig_vp_data, fig_hist_data):
        print(f"{fig_vp_data = }, {fig_hist_data = }")
        self.FormVpDataLayout.removeWidget(self.canvas_widget_data)
        self.FormVpHistLayout.removeWidget(self.canvas_widget_hist)
        self.canvas_widget_data = MplCanvas(fig_vp_data)
        self.canvas_widget_hist = MplCanvas(fig_hist_data)
        self.FormVpDataLayout.addWidget(self.canvas_widget_data)
        self.FormVpHistLayout.addWidget(self.canvas_widget_hist)
        self.enable_disable_buttons(enabled=True)

    def select_plot(self):
        if self.RB_VpData.isChecked():
            self.show_vp_data()

        elif self.RB_Histograms.isChecked():
            self.show_hist()

    def select_date(self):
        new_date = self.DateEdit.date().toPyDate()
        if not self.production_date:
            self.production_date = new_date
            return

        self.production_date = new_date
        self.DateLineEdit.setText(self.production_date.strftime("%d-%b-%Y"))
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
