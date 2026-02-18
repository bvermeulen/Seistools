"""
conversion app from pss to vaps
@2026 howdimain
bruno.vermeulen@hotmail.com
"""

from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

VAPS_HEADER = """
H26                                                                             
H26 Verbose APS Vibrator Attributes                                             
H26                                                                             
H26 Item  Definition of field       Cols   Format  Min to Max     Default  Units
H26 ----  -------------------       ----   ------  ----------     -------  -----
H26 1     Record identification     1-1    A1      'A'            None     -    
H26 2     Line name                 2-17   4A4     Free           None     -    
H26 3     Point number              18-25  2A4     Free           None     -    
H26 4     Point index               26-26  I1      1-9            1        -    
H26 5     Fleet number              27-27  1-W     Free           None     -    
H26 6     Vibrator number           28-29  I2      Free           None     -    
H26 7     Vibrator drive level      30-32  I3      0-100          None     %    
H26 8     Average phase             33-36  I4      -180 to 180    None     deg  
H26 9     Peak phase                37-40  I4      -180 to 180    None     deg  
H26 10    Average distortion        41-42  I2      0-99           None     %    
H26 11    Peak distortion           43-44  I2      0-99           None     %    
H26 12    Average force             45-46  I2      0-99           None     %    
H26 13    Peak force                47-49  I3      Free           None     %    
H26 14    Average ground stiffness  50-52  I3      Free           None     -    
H26 15    Average ground viscosity  53-55  I3      Free           None     -    
H26 16    Vib. position Easting     56-64  F9.1    Free           None     metre
H26 17    Vib. position Northing    65-74  F10.1   Free           None     metre
H26 18    Vib. position elevation   75-80  F6.1    -999.9 to      None     metre
H26                                                9999.9         None     metre
H26 19    Shot Nb                   82-86  I5      1-99999        None     -    
H26 20    Acquisition Nb            87-88  I2      1-32           None     -    
H26 21    2 Digits Fleet Number     89-90  I2      1-32           None     -    
H26 22    Vib Status Code           91-92  I2      1-98           None     -    
H26 23    Mass 1 Warning            94-94  A1      space or W     None     -    
H26       VE432 users: Magic No.                                                
H26 24    Mass 2 Warning            95-95  A1      space or W     None     -    
H26       VE432 users: Magic No.                                                
H26 25    Mass 3 Warning            96-96  A1      space or W     None     -    
H26       VE432 users: Magic No.                                                
H26 26    Plate 1 Warning           100-100 A1     space or W     None     -    
H26       VE432 users: Magic No.                                                
H26 27    Plate 2 Warning           101-101 A1     space or W     None     -    
H26       VE432 users: Magic No.                                                
H26 28    Plate 3 Warning           102-102 A1     space or W     None     -    
H26       VE432 users: Magic No.                                                
H26 29    Plate 4 Warning           103-103 A1     space or W     None     -    
H26       VE432 users: Magic No.                                                
H26 30    Plate 5 Warning           104-104 A1     space or W     None     -    
H26       VE432 users: Magic No.                                                
H26 31    Plate 6 Warning           105-105 A1     space or W     None     -    
H26       VE432 users: Magic No.                                                
H26 32    Force Overload            106-106 A1     space or F     None     -    
H26 33    Pressure Overload         107-107 A1     space or P     None     -    
H26 34    Mass Overload             108-108 A1     space or M     None     -    
H26 35    Valve Overload            109-109 A1     space or V     None     -    
H26 36    Excitation Overload       110-110 A1     space or E     None     -    
H26 37    Stacking Fold             111-112 I2     1-32           None     -    
H26 38    Computation Domain        113-113 A1     T or F         None     -    
H26 39    Ve432 Version             114-117 A4     Free           None     -    
H26 40    Day of Year               118-120 I3     1-999          None     -    
H26 41    Time hhmmss               121-126 3I2    000000-235959  None     -    
H26 42    HDOP                      127-130 F4.1   1.0-99.9       None     -    
H26 43    Tb Date                   131-150 I20    0 to           None     -    
H26                                         18446744073709551615  None     -    
H26                                                                             
H26 Note :                                                                      
H26    Items 7 to 18 are left blank if no vibrator attributes are available.    
H26    Items 16 to 18 are left blank if GPS failure or bad quality.             
H26                                                                             
H26    Items 23 to 34: To replace warnings by the VE432 Magic Number,           
H26    create a blank file named ApsModified.user408.hci408 in the `/users/     
H26    user408` directory.                                                      
H26                                                                             
H26      1         2         3         4         5         6         7         8         9         0         1         2         3         4         5
H26 56789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
H26                                                                             
"""


class PssConverter:

    def __init__(self, file_name: Path):
        self.file_name = file_name
        self.pss_df = pd.DataFrame()
        self.line: float = 1.0
        self.station: float = 1001.0
        self.index: int = 1
        self.fleet_number: int = 3
        self.vibrator_number: int = 9
        self.drive_level: int = 70
        self.average_phase: int = 1
        self.peak_phase: int = 3
        self.average_distortion: int = 12
        self.peak_distortion: int = 36
        self.average_force: int = 67
        self.peak_force: int = 71
        self.average_stiffness: int = 10
        self.average_viscosity: int = 20
        self.easting: float = 500000.0
        self.northing: float = 2300000.0
        self.elevation: float = 500.0
        self.shot_number: int = 100
        self.acquisition_number: int = 5
        self.fleet_code: int = 3
        self.status_code: int = 15
        self.mass_1: str = "M"
        self.mass_2: str = "M"
        self.mass_3: str = "M"
        self.plate_1: str = "P"
        self.plate_2: str = "P"
        self.plate_3: str = "P"
        self.plate_4: str = "P"
        self.plate_5: str = "P"
        self.plate_6: str = "P"
        self.force_overload: str = "F"
        self.pressure_overload: str = "P"
        self.mass_overload: str = "M"
        self.valve_overload: str = "V"
        self.excitation_overload: str = "E"
        self.stacking_fold: int = 1
        self.computation_domain: str = "T"
        self.ve432_version: str = " PSS"
        self.day_of_year: str = "111"
        self.hhmmss: str = "071012"
        self.hdop: float = 0.8
        self.tb_unix: str = "1234567890100010"
        self.positioning: str = ""

        vaps_file_name = file_name.parent / ("VAPS_" + file_name.stem[4:] + ".txt")
        self.vaps_writer = self.write_vaps_generator(vaps_file_name)
        self.vaps_writer.send(None)
        self.vaps_writer.send(VAPS_HEADER)

    def read_pss(self):
        self.pss_df = pd.read_csv(file)

    def write_vaps_generator(self, vaps_file_name: Path):
        with open(vaps_file_name, mode="wt") as vaps_file:
            while True:
                vaps_line = yield
                vaps_file.write(vaps_line)

    def convert_pss_to_vaps(self):
        for index, row in self.pss_df.iterrows():
            if row["Void"] == "Void":
                continue

            date_txt = row["Date"]
            tdate = datetime.strptime(date_txt, "%m/%d/%Y")
            time_txt = row["Time"]
            ttime = datetime.strptime(time_txt, "%H:%M:%S").time()
            tdatetime = datetime.combine(tdate, ttime).replace(tzinfo=timezone.utc)
            td_doy = tdatetime.utctimetuple().tm_yday
            tb_break = str(int(tdatetime.timestamp())) + f"{int(row["TB Micro"]):03}"

            self.line = row["Line"]
            self.station = row["Station"]
            self.index = 1 # row["EP ID"]
            self.fleet_number = 1
            self.vibrator_number = row["Unit ID"]
            self.drive_level = row["Drive Level"]
            self.average_phase = row["Phase Avg"]
            self.peak_phase = row["Phase Max"]
            self.average_distortion = row["THD Avg"]
            self.peak_distortion = row["THD Max"]
            self.average_force = row["Force Avg"]
            self.peak_force = row["Force Max"]
            self.average_stiffness = row["Avg Stiffness"]
            self.average_viscosity = row["Avg Viscosity"]
            self.easting = row["X"]
            self.northing = row["Y"]
            self.elevation = row["Altitude"]
            self.shot_number = row["EP Count"]
            self.acquisition_number = row["Sweep Number"]
            self.fleet_code = 1
            self.status_code = 1
            self.mass_1 = " "
            self.mass_2 = " "
            self.mass_3 = " "
            self.plate_1 = " "
            self.plate_2 = " "
            self.plate_3 = " "
            self.plate_4 = " "
            self.plate_5 = " "
            self.plate_6 = " "
            self.force_overload = " "
            self.pressure_overload = " "
            self.mass_overload = " "
            self.valve_overload = " "
            self.excitation_overload = " "
            self.stacking_fold = 1
            self.computation_domain = "T"
            self.ve432_version = " PSS"
            self.day_of_year = f"{td_doy:03}"
            self.hhmmss = ttime.strftime("%H%M%S")
            self.hdop = row["HDOP"]
            self.tb_unix = tb_break
            self.positioning = ""

            vaps_line = self.construct_vaps_line()
            self.vaps_writer.send(vaps_line)

    def construct_vaps_line(self) -> str:
        vaps_line = "".join(
            [
                f"{"A":>1}",
                f"{self.line:-16.1f}",
                f"{self.station:-8.1f}",
                f"{self.index:-1}",
                f"{self.fleet_number:-1}",
                f"{self.vibrator_number:-2}",
                f"{self.drive_level:-3}",
                f"{self.average_phase:-4}",
                f"{self.peak_phase:-4}",
                f"{self.average_distortion:-2}",
                f"{self.peak_distortion:-2}",
                f"{self.average_force:-2}",
                f"{self.peak_force:-3}",
                f"{self.average_stiffness:-3}",
                f"{self.average_viscosity:-3}",
                f"{self.easting:-9.1f}",
                f"{self.northing:-10.1f}",
                f"{self.elevation:-6.1f}",
                f"{" ":>1}",
                f"{self.shot_number:-5}",
                f"{self.acquisition_number:-2}",
                f"{self.fleet_code:-2}",
                f"{self.status_code:-2}",
                f"{" ":>1}",
                f"{self.mass_1:1}",
                f"{self.mass_2:1}",
                f"{self.mass_3:1}",
                f"{"   ":>1}",
                f"{self.plate_1:1}",
                f"{self.plate_2:1}",
                f"{self.plate_3:1}",
                f"{self.plate_4:1}",
                f"{self.plate_5:1}",
                f"{self.plate_6:1}",
                f"{self.force_overload:1}",
                f"{self.pressure_overload:1}",
                f"{self.mass_overload:1}",
                f"{self.valve_overload:1}",
                f"{self.excitation_overload:1}",
                f"{self.stacking_fold:-2}",
                f"{self.computation_domain:1}",
                f"{self.ve432_version:4}",
                f"{self.day_of_year:>3}",
                f"{self.hhmmss:>6}",
                f"{self.hdop:-4.1f}",
                f"{self.tb_unix:>20}",
                f"\n",
            ]
        )
        return vaps_line


if __name__ == "__main__":
    base_folder = Path("d:/onedrive/work/epi/omv/omv gnas 2D/qc/vib_node_data/pss")
    file = base_folder / "PSS_20260216.csv"
    pss = PssConverter(file)
    pss.read_pss()
    vaps_line = pss.convert_pss_to_vaps()
    print(f"{pss.construct_vaps_line()=}")
