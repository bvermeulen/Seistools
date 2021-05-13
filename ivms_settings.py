''' settings and data structures for vp app
'''
from pathlib import Path
import datetime
from dataclasses import dataclass

IVMS_FOLDER = Path(r'.\\data_files\\IVMS')
DRIVER_TRAINING = Path(r'.\\data_files\\IVMS\\driver_db.xlsx')
DATABASE = r'ivms_db.sqlite3'


@dataclass
class IvmsVehicle:
    asset_descr: str
    registration: str
    make: str
    model: str
    year_manufacture: str
    chassis_number: str
    date_ras: datetime.datetime


@dataclass
class IvmsDriver:
    contractor: int = None
    employee_no: int = None
    ivms_id: int = None
    name: str = None
    dob: datetime.datetime = None
    mobile: str = None
    hse_passport: str = None
    site_name: str = None
    ROP_license: str = None
    date_issue_license: datetime.datetime = None
    date_expiry_license: datetime.datetime = None
    PDO_permit: str = None
    date_expiry_permit: datetime.datetime = None
    vehicle_light: str = None
    vehicle_heavy: str = None
    date_dd01: datetime.datetime = None
    date_dd02: datetime.datetime = None
    date_dd03: datetime.datetime = None
    date_dd04: datetime.datetime = None
    date_dd05: datetime.datetime = None
    date_dd06: datetime.datetime = None
    date_dd06_due: datetime.datetime = None
    date_assessment_day: datetime.datetime = None
    date_assessment_night: datetime.datetime = None
    date_assessment_rough: datetime.datetime = None
    assessment_comment: str = None
    training_comment: str = None


@dataclass
class IvmsFileTripReport:
    file_name: str
    file_date: datetime.datetime


@dataclass
class IvmsTripReport:
    id_file: int
    id_vehicle: int
    report_date: datetime.datetime
    driving_time: datetime.time
    standing_time: datetime.time
    duration: datetime.time
    idle_time: datetime.time
    distance: float
    avg_speed: float
    max_speed: float


@dataclass
class IvmsFileRag:
    file_name: str
    file_date: datetime.datetime


@dataclass
class IvmsRag:
    id_file: int
    id_driver: int
    distance: float
    driving_time: datetime.time
    harsh_accel: int
    harsh_brake: int
    seatbelt_violation_time: datetime.time
    highest_speed: float
    overspeeding_time: float
    accel_violation_score: float
    decel_violation_score: float
    seatbelt_violation_score: float
    overspeeding_violation_score: float
    total_score: float
