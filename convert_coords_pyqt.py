import sys
from enum import Enum
from pathlib import Path
from PyQt5 import uic, QtWidgets
from convert_tools import ConvertTools


class ConvertChoice(Enum):
    wgs84_psd93 = 1
    psd93_wgs84 = 2
    wgs84_utm40 = 3
    utm40_wgs84 = 4
    psd93_utm40 = 5
    utm40_psd93 = 6
    lon_lat = 7
    grid_psd93 = 8
    psd93_grid = 9


class FormatChoice(Enum):
    Degrees = 1
    DMS = 2


convert = ConvertTools()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(Path(__file__).parent / 'convert_main.ui', self)
        self.actionQuit.triggered.connect(self.action_quit)
        self.actionDegrees.triggered.connect(lambda x: self.action_format(FormatChoice.Degrees))
        self.actionDMS.triggered.connect(lambda x: self.action_format(FormatChoice.DMS))
        self.pb5_psd93_utm40.clicked.connect(lambda x: self.action_float_float(ConvertChoice.psd93_utm40))
        self.pb6_utm40_psd93.clicked.connect(lambda x: self.action_float_float(ConvertChoice.utm40_psd93))
        self.pb8_grid_psd93.clicked.connect(lambda x: self.action_float_float(ConvertChoice.grid_psd93))
        self.pb9_psd93_grid.clicked.connect(lambda x: self.action_float_float(ConvertChoice.psd93_grid))
        self.action_connect()

    def action_format(self, format_choice):
        match format_choice:
            case FormatChoice.Degrees:
                self.actionDegrees.setChecked(True)
                self.actionDMS.setChecked(False)
                self.menuFormat.setTitle('Degrees')

            case FormatChoice.DMS:
                self.actionDegrees.setChecked(False)
                self.actionDMS.setChecked(True)
                self.menuFormat.setTitle('DMS')

            case _:
                assert False, "check format choice"

        self.action_connect()

    def action_connect(self):
        self.pb1_wgs84_psd93.disconnect()
        self.pb2_psd93_wgs84.disconnect()
        self.pb3_wgs84_utm40.disconnect()
        self.pb4_utm40_wgs84.disconnect()
        self.pb7_lon_lat.disconnect()

        if self.actionDegrees.isChecked():
            self.pb1_wgs84_psd93.clicked.connect(lambda x: self.action_float_float(ConvertChoice.wgs84_psd93))
            self.pb2_psd93_wgs84.clicked.connect(lambda x: self.action_float_float(ConvertChoice.psd93_wgs84))
            self.pb3_wgs84_utm40.clicked.connect(lambda x: self.action_float_float(ConvertChoice.wgs84_utm40))
            self.pb4_utm40_wgs84.clicked.connect(lambda x: self.action_float_float(ConvertChoice.utm40_wgs84))
            self.pb7_lon_lat.clicked.connect(lambda x: self.action_float_DMS(ConvertChoice.lon_lat))

        elif self.actionDMS.isChecked():
            self.pb1_wgs84_psd93.clicked.connect(lambda x: self.action_DMS_float(ConvertChoice.wgs84_psd93))
            self.pb2_psd93_wgs84.clicked.connect(lambda x: self.action_float_DMS(ConvertChoice.psd93_wgs84))
            self.pb3_wgs84_utm40.clicked.connect(lambda x: self.action_DMS_float(ConvertChoice.wgs84_utm40))
            self.pb4_utm40_wgs84.clicked.connect(lambda x: self.action_float_DMS(ConvertChoice.utm40_wgs84))
            self.pb7_lon_lat.clicked.connect(lambda x: self.action_DMS_float(ConvertChoice.lon_lat))

        else:
            assert False, "check Degrees/ DMS"

    def action_float_float(self, convert_choice):
        match convert_choice:
            case ConvertChoice.wgs84_psd93:
                dlg = DialogFloatFloat(
                    self, convert_choice, 'WGS84 to PSD93', 'Longitude', 'Latitude',
                    'Easting', 'Northing'
                )
            case ConvertChoice.psd93_wgs84:
                dlg = DialogFloatFloat(
                    self, convert_choice, 'PSD93 to WGS84', 'Easting', 'Northing',
                    'Longitude', 'Latitude'
                )
            case ConvertChoice.wgs84_utm40:
                dlg = DialogFloatFloat(
                    self, convert_choice, 'WGS84 to UTM 40N', 'Longitude', 'Latitude',
                    'Easting', 'Northing'
                )
            case ConvertChoice.utm40_wgs84:
                dlg = DialogFloatFloat(
                    self, convert_choice, 'UTM 40N to WGS84', 'Easting', 'Northing',
                    'Longitude', 'Latitude'
                )
            case ConvertChoice.psd93_utm40:
                dlg = DialogFloatFloat(
                    self, convert_choice, 'PSD93 to UTM 40N', 'Easting', 'Northing',
                    'Easting', 'Northing'
                )
            case ConvertChoice.utm40_psd93:
                dlg = DialogFloatFloat(
                    self, convert_choice, 'UTM 40N to PSD93', 'Easting', 'Northing',
                    'Easting', 'Northing'
                )
            case ConvertChoice.grid_psd93:
                dlg = DialogFloatFloat(
                    self, convert_choice, '22CO grid to PSD93', 'Line', 'Station',
                    'Easting', 'Northing'
                )
            case ConvertChoice.psd93_grid:
                dlg = DialogFloatFloat(
                    self, convert_choice, 'PSD93 to 22CO grid', 'Easting', 'Northing',
                    'Line', 'Station'
                )
            case _:
                assert False, "Check action_float_float"

        dlg.exec_()

    def action_DMS_float(self, convert_choice):
        match convert_choice:
            case ConvertChoice.wgs84_psd93:
                dlg = DialogDMSFloat(
                    self, convert_choice, 'WGS84 to PSD93', 'Longitude', 'Latitude',
                    'Easting', 'Northing'
                )
            case ConvertChoice.wgs84_utm40:
                dlg = DialogDMSFloat(
                    self, convert_choice, 'WGS84 to UTM 40N', 'Longitude', 'Latitude',
                    'Easting', 'Northing'
                )
            case ConvertChoice.lon_lat:
                dlg = DialogDMSFloat(
                    self, convert_choice, 'DMS to Degrees', 'Longitude', 'Latitude',
                    'Longitude', 'Latitude'
                )
            case _:
                assert False, "Check action_DMS_float"

        dlg.exec_()

    def action_float_DMS(self, convert_choice):
        match convert_choice:
            case ConvertChoice.psd93_wgs84:
                dlg = DialogFloatDMS(
                    self, convert_choice, 'PSD93 to WGS84', 'Easting', 'Northing',
                    'Longitude', 'Latitude'
                )
            case ConvertChoice.utm40_wgs84:
                dlg = DialogFloatDMS(
                    self, convert_choice, 'UTM 40N to WGS84', 'Easting', 'Northing',
                    'Longitude', 'Latitude'
                )
            case ConvertChoice.lon_lat:
                dlg = DialogFloatDMS(
                    self, convert_choice, 'Degrees to DMS', 'Longitude', 'Latitude',
                    'Longitude', 'Latitude'
                )
            case _:
                assert False, "Check action_float_DMS"

        dlg.exec_()

    def action_quit(self):
        self.close()
        sys.exit()


class DialogFloatFloat(QtWidgets.QDialog):
    def __init__(self, parent, conversion, title, input1, input2, output1, output2):
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / 'convert_dlg_float_float.ui', self)
        self.TitleText.setText(title)
        self.TextInput_1.setText(input1)
        self.TextInput_2.setText(input2)
        self.TextOutput_1.setText(output1)
        self.TextOutput_2.setText(output2)
        self.pb_exit.clicked.connect(self.action_exit)
        self.pb_convert.clicked.connect(lambda x: self.action_convert(conversion))

    def action_convert(self, convert_choice):
        self.lineEditOutput_1.setText('')
        self.lineEditOutput_2.setText('')
        try:
            val1 = float(self.lineEditInput_1.text())
            val2 = float(self.lineEditInput_2.text())

        except ValueError:
            return

        match convert_choice:
            case ConvertChoice.wgs84_psd93:
                val1, val2 = convert.wgs84_to_psd93(val1, val2)
                f_fmt = '.2f'

            case ConvertChoice.psd93_wgs84:
                val1, val2 = convert.psd93_to_wgs84(val1, val2)
                f_fmt = '.6f'

            case ConvertChoice.wgs84_utm40:
                val1, val2 = convert.wgs84_to_utm40n(val1, val2)
                f_fmt = '.2f'

            case ConvertChoice.utm40_wgs84:
                val1, val2 = convert.utm40n_to_wgs84(val1, val2)
                f_fmt = '.6f'

            case ConvertChoice.psd93_utm40:
                val1, val2 = convert.psd93_to_utm40n(val1, val2)
                f_fmt = '.2f'

            case ConvertChoice.utm40_psd93:
                val1, val2 = convert.utm40n_to_psd93(val1, val2)
                f_fmt = '.2f'

            case ConvertChoice.grid_psd93:
                val1, val2 = convert.grid22co_psd93(val1, val2)
                f_fmt = '.2f'

            case ConvertChoice.psd93_grid:
                val1, val2 = convert.psd93_grid22co(val1, val2)
                f_fmt = '.0f'

            case _:
                assert False, "Check DiaglogFloatFloat"

        self.lineEditOutput_1.setText(f'{val1:{f_fmt}}')
        self.lineEditOutput_2.setText(f'{val2:{f_fmt}}')

    def action_exit(self):
        self.close()


class DialogDMSFloat(QtWidgets.QDialog):
    def __init__(self, parent, conversion, title, input1, input2, output1, output2):
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / 'convert_dlg_DMS_float.ui', self)
        self.TitleText.setText(title)
        self.TextInput_1.setText(input1)
        self.TextInput_2.setText(input2)
        self.TextOutput_1.setText(output1)
        self.TextOutput_2.setText(output2)
        self.pb_exit.clicked.connect(self.action_exit)
        self.pb_convert.clicked.connect(
            lambda x: self.action_convert(conversion))

    def action_convert(self, convert_choice):
        self.lineEditOutput_1.setText('')
        self.lineEditOutput_2.setText('')
        val1 = self.lineEditInput_1.text()
        val2 = self.lineEditInput_2.text() if self.lineEditInput_2.text() else '0'
        val3 = self.lineEditInput_3.text() if self.lineEditInput_3.text() else '0'
        val4 = self.lineEditInput_4.text()
        val5 = self.lineEditInput_5.text() if self.lineEditInput_5.text() else '0'
        val6 = self.lineEditInput_6.text() if self.lineEditInput_6.text() else '0'

        val1 = ''.join([val1, '\u00B0', val2,'\'', val3, '\"', 'E'])
        val2 = ''.join([val4, '\u00B0', val5,'\'', val6, '\"', 'N'])
        val1, val2 = convert.convert_dms_to_dec_degree(val1, val2)
        if val1 == -1 and val2 == -1:
            return

        match convert_choice:
            case ConvertChoice.wgs84_psd93:
                val1, val2 = convert.wgs84_to_psd93(val1, val2)
                f_fmt = '.2f'

            case ConvertChoice.wgs84_utm40:
                val1, val2 = convert.wgs84_to_utm40n(val1, val2)
                f_fmt = '.2f'

            case ConvertChoice.lon_lat:
                f_fmt = '.6f'

            case _:
                assert False, "Check class DialogDMSFloat"

        self.lineEditOutput_1.setText(f'{val1:{f_fmt}}')
        self.lineEditOutput_2.setText(f'{val2:{f_fmt}}')

    def action_exit(self):
        self.close()


class DialogFloatDMS(QtWidgets.QDialog):
    def __init__(self, parent, conversion, title, input1, input2, output1, output2):
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / 'convert_dlg_float_DMS.ui', self)
        self.TitleText.setText(title)
        self.TextInput_1.setText(input1)
        self.TextInput_2.setText(input2)
        self.TextOutput_1.setText(output1)
        self.TextOutput_2.setText(output2)
        self.pb_exit.clicked.connect(self.action_exit)
        self.pb_convert.clicked.connect(
            lambda x: self.action_convert(conversion))

    def action_convert(self, convert_choice):
        self.lineEditOutput_1.setText('')
        self.lineEditOutput_2.setText('')
        self.lineEditOutput_3.setText('')
        self.lineEditOutput_4.setText('')
        self.lineEditOutput_5.setText('')
        self.lineEditOutput_6.setText('')
        self.lineEditOutput_7.setText('')
        self.lineEditOutput_8.setText('')
        try:
            val1 = float(self.lineEditInput_1.text())
            val2 = float(self.lineEditInput_2.text())

        except ValueError:
            return

        match convert_choice:
            case ConvertChoice.psd93_wgs84:
                val1, val2 = convert.psd93_to_wgs84(val1, val2)

            case ConvertChoice.utm40_wgs84:
                val1, val2 = convert.utm40n_to_wgs84(val1, val2)

            case ConvertChoice.lon_lat:
                pass

            case _:
                assert False, "Check class DialogFloatDMS"

        val1, val2 = convert.convert_dec_degree_to_dms(val1, val2)
        lon, lat = convert.strip_lon_lat(val1, val2)
        if lon and lat:
            self.lineEditOutput_1.setText(f'{float(lon.group(1)):.0f}')
            self.lineEditOutput_2.setText(f'{float(lon.group(2)):.0f}')
            self.lineEditOutput_3.setText(f'{float(lon.group(3)):.2f}')
            self.lineEditOutput_4.setText(f'{lon.group(4)}')
            self.lineEditOutput_5.setText(f'{float(lat.group(1)):.0f}')
            self.lineEditOutput_6.setText(f'{float(lat.group(2)):.0f}')
            self.lineEditOutput_7.setText(f'{float(lat.group(3)):.2f}')
            self.lineEditOutput_8.setText(f'{lat.group(4)}')

        else:
            return

    def action_exit(self):
        self.close()


def start_app():
    app = QtWidgets.QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    start_app()
