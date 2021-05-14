''' settings and data structures for vp app
'''
from pathlib import Path
import datetime
from dataclasses import dataclass

IVMS_FOLDER = Path(r'.\\data_files\\IVMS')
DRIVER_TRAINING = Path(r'.\\data_files\\IVMS\\driver_training_db.xlsx')
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
    file_name: str = None
    file_date: datetime.datetime = None


@dataclass
class IvmsTripReport:
    id_file: int = None
    id_vehicle: int = None
    report_date: datetime.datetime = None
    driving_time: datetime.time = None
    standing_time: datetime.time = None
    duration: datetime.time = None
    idle_time: datetime.time = None
    distance: float = None
    avg_speed: float = None
    max_speed: float = None


@dataclass
class IvmsFileRag:
    filename: str = None
    file_date: datetime.datetime = None


@dataclass
class IvmsRag:
    rag_report: datetime.datetime = None
    id_file: int = None
    id_driver: int = None
    distance: float = None
    driving_time: datetime.time = None
    harsh_accel: int = None
    harsh_brake: int = None
    highest_speed: float = None
    overspeeding_time: float = None
    seatbelt_violation_time: datetime.time = None
    accel_violation_score: float = None
    decel_violation_score: float = None
    seatbelt_violation_score: float = None
    overspeeding_violation_score: float = None
    total_score: float = None
