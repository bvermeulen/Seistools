"""
    PyQt application for conversion of coordinates for a local project coordinate system
    @ 2022, 2025 howdimain; bruno.vermeulen@hotmail.com
"""

import sys
from enum import Enum
from pathlib import Path
from PyQt6 import uic, QtWidgets
from convert_tools import ConvertTools, title, prefix, local_name, utm_zone


class ConvertChoice(Enum):
    wgs84_local = 1
    local_wgs84 = 2
    wgs84_utm = 3
    utm_wgs84 = 4
    local_utm = 5
    utm_local = 6
    lon_lat = 7
    grid_local = 8
    local_grid = 9


class FormatChoice(Enum):
    Degrees = 1
    DMS = 2


convert = ConvertTools()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(Path(__file__).parent / "convert_main.ui", self)
        self.actionQuit.triggered.connect(self.action_quit)
        self.actionDegrees.triggered.connect(
            lambda x: self.action_format(FormatChoice.Degrees)
        )
        self.actionDMS.triggered.connect(lambda x: self.action_format(FormatChoice.DMS))
        self.pb5_local_utm.clicked.connect(
            lambda x: self.action_float_float(ConvertChoice.local_utm)
        )
        self.pb6_utm_local.clicked.connect(
            lambda x: self.action_float_float(ConvertChoice.utm_local)
        )
        self.pb8_grid_local.clicked.connect(
            lambda x: self.action_float_float(ConvertChoice.grid_local)
        )
        self.pb9_local_grid.clicked.connect(
            lambda x: self.action_float_float(ConvertChoice.local_grid)
        )
        self.action_connect()
        self.title_label.setText(title)
        self.pb1_wgs84_local.setText(f"WGS84 -> {local_name}")
        self.pb2_local_wgs84.setText(f"{local_name} -> WGS84")
        self.pb3_wgs84_utm.setText(f"WGS84 -> UTM {utm_zone}")
        self.pb4_utm_wgs84.setText(f"UTM {utm_zone} -> WGS84")
        self.pb5_local_utm.setText(f"{local_name} -> UTM {utm_zone}")
        self.pb6_utm_local.setText(f"UTM {utm_zone} -> {local_name}")
        self.pb7_lon_lat.setText(f"Lon-Lat")
        self.pb8_grid_local.setText(f"{prefix} grid -> {local_name}")
        self.pb9_local_grid.setText(f"{local_name} -> {prefix} grid")

    def action_format(self, format_choice):
        match format_choice:
            case FormatChoice.Degrees:
                self.actionDegrees.setChecked(True)
                self.actionDMS.setChecked(False)
                self.menuFormat.setTitle("Degrees")

            case FormatChoice.DMS:
                self.actionDegrees.setChecked(False)
                self.actionDMS.setChecked(True)
                self.menuFormat.setTitle("DMS")

            case _:
                assert False, "check format choice"

        self.action_connect()

    def action_connect(self):
        self.pb1_wgs84_local.disconnect()
        self.pb2_local_wgs84.disconnect()
        self.pb3_wgs84_utm.disconnect()
        self.pb4_utm_wgs84.disconnect()
        self.pb7_lon_lat.disconnect()

        if self.actionDegrees.isChecked():
            self.pb1_wgs84_local.clicked.connect(
                lambda x: self.action_float_float(ConvertChoice.wgs84_local)
            )
            self.pb2_local_wgs84.clicked.connect(
                lambda x: self.action_float_float(ConvertChoice.local_wgs84)
            )
            self.pb3_wgs84_utm.clicked.connect(
                lambda x: self.action_float_float(ConvertChoice.wgs84_utm)
            )
            self.pb4_utm_wgs84.clicked.connect(
                lambda x: self.action_float_float(ConvertChoice.utm_wgs84)
            )
            self.pb7_lon_lat.clicked.connect(
                lambda x: self.action_float_DMS(ConvertChoice.lon_lat)
            )

        elif self.actionDMS.isChecked():
            self.pb1_wgs84_local.clicked.connect(
                lambda x: self.action_DMS_float(ConvertChoice.wgs84_local)
            )
            self.pb2_local_wgs84.clicked.connect(
                lambda x: self.action_float_DMS(ConvertChoice.local_wgs84)
            )
            self.pb3_wgs84_utm.clicked.connect(
                lambda x: self.action_DMS_float(ConvertChoice.wgs84_utm)
            )
            self.pb4_utm_wgs84.clicked.connect(
                lambda x: self.action_float_DMS(ConvertChoice.utm_wgs84)
            )
            self.pb7_lon_lat.clicked.connect(
                lambda x: self.action_DMS_float(ConvertChoice.lon_lat)
            )

        else:
            assert False, "check Degrees/ DMS"

    def action_float_float(self, convert_choice):
        match convert_choice:
            case ConvertChoice.wgs84_local:
                dlg = DialogFloatFloat(
                    self,
                    convert_choice,
                    f"WGS84 to {local_name}",
                    "Longitude",
                    "Latitude",
                    "Easting",
                    "Northing",
                )
            case ConvertChoice.local_wgs84:
                dlg = DialogFloatFloat(
                    self,
                    convert_choice,
                    f"{local_name} to WGS84",
                    "Easting",
                    "Northing",
                    "Longitude",
                    "Latitude",
                )
            case ConvertChoice.wgs84_utm:
                dlg = DialogFloatFloat(
                    self,
                    convert_choice,
                    f"WGS84 to UTM {utm_zone}",
                    "Longitude",
                    "Latitude",
                    "Easting",
                    "Northing",
                )
            case ConvertChoice.utm_wgs84:
                dlg = DialogFloatFloat(
                    self,
                    convert_choice,
                    f"UTM {utm_zone} to WGS84",
                    "Easting",
                    "Northing",
                    "Longitude",
                    "Latitude",
                )
            case ConvertChoice.local_utm:
                dlg = DialogFloatFloat(
                    self,
                    convert_choice,
                    f"{local_name} to UTM {utm_zone}",
                    "Easting",
                    "Northing",
                    "Easting",
                    "Northing",
                )
            case ConvertChoice.utm_local:
                dlg = DialogFloatFloat(
                    self,
                    convert_choice,
                    f"UTM {utm_zone} to {local_name}",
                    "Easting",
                    "Northing",
                    "Easting",
                    "Northing",
                )
            case ConvertChoice.grid_local:
                dlg = DialogFloatFloat(
                    self,
                    convert_choice,
                    f"{prefix} grid to {local_name}",
                    "Line",
                    "Station",
                    "Easting",
                    "Northing",
                )
            case ConvertChoice.local_grid:
                dlg = DialogFloatFloat(
                    self,
                    convert_choice,
                    f"{local_name} to {prefix} grid",
                    "Easting",
                    "Northing",
                    "Line",
                    "Station",
                )
            case _:
                assert False, "Check action_float_float"

        dlg.exec()

    def action_DMS_float(self, convert_choice):
        match convert_choice:
            case ConvertChoice.wgs84_local:
                dlg = DialogDMSFloat(
                    self,
                    convert_choice,
                    f"WGS84 to {local_name}",
                    "Longitude",
                    "Latitude",
                    "Easting",
                    "Northing",
                )
            case ConvertChoice.wgs84_utm:
                dlg = DialogDMSFloat(
                    self,
                    convert_choice,
                    f"WGS84 to UTM {utm_zone}",
                    "Longitude",
                    "Latitude",
                    "Easting",
                    "Northing",
                )
            case ConvertChoice.lon_lat:
                dlg = DialogDMSFloat(
                    self,
                    convert_choice,
                    "DMS to Degrees",
                    "Longitude",
                    "Latitude",
                    "Longitude",
                    "Latitude",
                )
            case _:
                assert False, "Check action_DMS_float"

        dlg.exec()

    def action_float_DMS(self, convert_choice):
        match convert_choice:
            case ConvertChoice.local_wgs84:
                dlg = DialogFloatDMS(
                    self,
                    convert_choice,
                    f"{local_name} to WGS84",
                    "Easting",
                    "Northing",
                    "Longitude",
                    "Latitude",
                )
            case ConvertChoice.utm_wgs84:
                dlg = DialogFloatDMS(
                    self,
                    convert_choice,
                    f"UTM {utm_zone} to WGS84",
                    "Easting",
                    "Northing",
                    "Longitude",
                    "Latitude",
                )
            case ConvertChoice.lon_lat:
                dlg = DialogFloatDMS(
                    self,
                    convert_choice,
                    "Degrees to DMS",
                    "Longitude",
                    "Latitude",
                    "Longitude",
                    "Latitude",
                )
            case _:
                assert False, "Check action_float_DMS"

        dlg.exec()

    def action_quit(self):
        self.close()
        sys.exit()


class DialogFloatFloat(QtWidgets.QDialog):
    def __init__(self, parent, conversion, title, input1, input2, output1, output2):
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / "convert_dlg_float_float.ui", self)
        self.TitleText.setText(title)
        self.TextInput_1.setText(input1)
        self.TextInput_2.setText(input2)
        self.TextOutput_1.setText(output1)
        self.TextOutput_2.setText(output2)
        self.pb_exit.clicked.connect(self.action_exit)
        self.pb_convert.clicked.connect(lambda x: self.action_convert(conversion))

    def action_convert(self, convert_choice):
        self.lineEditOutput_1.setText("")
        self.lineEditOutput_2.setText("")
        try:
            val1 = float(self.lineEditInput_1.text())
            val2 = float(self.lineEditInput_2.text())

        except ValueError:
            return

        match convert_choice:
            case ConvertChoice.wgs84_local:
                val1, val2 = convert.wgs84_to_local(val1, val2)
                f_fmt = ".2f"

            case ConvertChoice.local_wgs84:
                val1, val2 = convert.local_to_wgs84(val1, val2)
                f_fmt = ".6f"

            case ConvertChoice.wgs84_utm:
                val1, val2 = convert.wgs84_to_utm(val1, val2)
                f_fmt = ".2f"

            case ConvertChoice.utm_wgs84:
                val1, val2 = convert.utm_to_wgs84(val1, val2)
                f_fmt = ".6f"

            case ConvertChoice.local_utm:
                val1, val2 = convert.local_to_utm(val1, val2)
                f_fmt = ".2f"

            case ConvertChoice.utm_local:
                val1, val2 = convert.utm_to_local(val1, val2)
                f_fmt = ".2f"

            case ConvertChoice.grid_local:
                val1, val2 = convert.grid_local(val1, val2)
                f_fmt = ".2f"

            case ConvertChoice.local_grid:
                val1, val2 = convert.local_grid(val1, val2)
                f_fmt = ".0f"

            case _:
                assert False, "Check DiaglogFloatFloat"

        self.lineEditOutput_1.setText(f"{val1:{f_fmt}}")
        self.lineEditOutput_2.setText(f"{val2:{f_fmt}}")

    def action_exit(self):
        self.close()


class DialogDMSFloat(QtWidgets.QDialog):
    def __init__(self, parent, conversion, title, input1, input2, output1, output2):
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / "convert_dlg_DMS_float.ui", self)
        self.TitleText.setText(title)
        self.TextInput_1.setText(input1)
        self.TextInput_2.setText(input2)
        self.TextOutput_1.setText(output1)
        self.TextOutput_2.setText(output2)
        self.pb_exit.clicked.connect(self.action_exit)
        self.pb_convert.clicked.connect(lambda x: self.action_convert(conversion))

    def action_convert(self, convert_choice):
        self.lineEditOutput_1.setText("")
        self.lineEditOutput_2.setText("")
        val1 = self.lineEditInput_1.text() if self.lineEditInput_1.text() else "0"
        val2 = self.lineEditInput_2.text() if self.lineEditInput_2.text() else "0"
        val3 = self.lineEditInput_3.text() if self.lineEditInput_3.text() else "0"
        val4 = self.lineEditInput_4.text() if self.lineEditInput_4.text() else "E"
        val5 = self.lineEditInput_5.text() if self.lineEditInput_5.text() else "0"
        val6 = self.lineEditInput_6.text() if self.lineEditInput_6.text() else "0"
        val7 = self.lineEditInput_7.text() if self.lineEditInput_7.text() else "0"
        val8 = self.lineEditInput_8.text() if self.lineEditInput_8.text() else "N"

        val1 = "".join([val1, "\u00B0", val2, "'", val3, '"', val4])
        val2 = "".join([val5, "\u00B0", val6, "'", val7, '"', val8])
        val1, val2 = convert.convert_dms_to_dec_degree(val1, val2)
        if val1 == -1 and val2 == -1:
            return

        match convert_choice:
            case ConvertChoice.wgs84_local:
                val1, val2 = convert.wgs84_to_local(val1, val2)
                f_fmt = ".2f"

            case ConvertChoice.wgs84_utm:
                val1, val2 = convert.wgs84_to_utm(val1, val2)
                f_fmt = ".2f"

            case ConvertChoice.lon_lat:
                f_fmt = ".6f"

            case _:
                assert False, "Check class DialogDMSFloat"

        self.lineEditOutput_1.setText(f"{val1:{f_fmt}}")
        self.lineEditOutput_2.setText(f"{val2:{f_fmt}}")

    def action_exit(self):
        self.close()


class DialogFloatDMS(QtWidgets.QDialog):
    def __init__(self, parent, conversion, title, input1, input2, output1, output2):
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / "convert_dlg_float_DMS.ui", self)
        self.TitleText.setText(title)
        self.TextInput_1.setText(input1)
        self.TextInput_2.setText(input2)
        self.TextOutput_1.setText(output1)
        self.TextOutput_2.setText(output2)
        self.pb_exit.clicked.connect(self.action_exit)
        self.pb_convert.clicked.connect(lambda x: self.action_convert(conversion))

    def action_convert(self, convert_choice):
        self.lineEditOutput_1.setText("")
        self.lineEditOutput_2.setText("")
        self.lineEditOutput_3.setText("")
        self.lineEditOutput_4.setText("")
        self.lineEditOutput_5.setText("")
        self.lineEditOutput_6.setText("")
        self.lineEditOutput_7.setText("")
        self.lineEditOutput_8.setText("")
        try:
            val1 = float(self.lineEditInput_1.text())
            val2 = float(self.lineEditInput_2.text())

        except ValueError:
            return

        match convert_choice:
            case ConvertChoice.local_wgs84:
                val1, val2 = convert.local_to_wgs84(val1, val2)

            case ConvertChoice.utm_wgs84:
                val1, val2 = convert.utm_to_wgs84(val1, val2)

            case ConvertChoice.lon_lat:
                pass

            case _:
                assert False, "Check class DialogFloatDMS"

        val1, val2 = convert.convert_dec_degree_to_dms(val1, val2)
        lon, lat = convert.strip_lon_lat(val1, val2)
        if lon and lat:
            self.lineEditOutput_1.setText(f"{float(lon.group(1)):.0f}")
            self.lineEditOutput_2.setText(f"{float(lon.group(2)):.0f}")
            self.lineEditOutput_3.setText(f"{float(lon.group(3)):.2f}")
            self.lineEditOutput_4.setText(f"{lon.group(4)}")
            self.lineEditOutput_5.setText(f"{float(lat.group(1)):.0f}")
            self.lineEditOutput_6.setText(f"{float(lat.group(2)):.0f}")
            self.lineEditOutput_7.setText(f"{float(lat.group(3)):.2f}")
            self.lineEditOutput_8.setText(f"{lat.group(4)}")

        else:
            return

    def action_exit(self):
        self.close()


def start_app():
    app = QtWidgets.QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()


if __name__ == "__main__":
    start_app()
