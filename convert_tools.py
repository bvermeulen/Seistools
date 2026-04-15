"""
Module for conversion tools for WGS84, UTM and local
note the module maintains consistency in x, y; easting, northing; and
longitude, latitude, where x is the first and y is the second argument
grid conversion is project dependent
"""

import os
import re
import json
from pathlib import Path
from dataclasses import dataclass
import numpy as np
from shapely.geometry import Point
from pyproj import Proj


degree_symbol = "\u00b0"

match os.name:
    case "nt":
        convert_config_file = (
            Path.home() / "AppData/Roaming/SeistoolsConfig" / "convert_config.json"
        )
    case "posix":
        convert_config_file = (
            Path.home() / ".config/SeistoolsConfig" / "convert_config.json"
        )
    case other:
        assert False, f"{os.name} is not implemented"

with open(convert_config_file, "rt") as f:
    config = json.load(f)

title = config["title"]
prefix = config["prefix"]
origin = config["origin"]
projection = config["projection"]
utm_zone = projection["utm_zone"]
local_name = projection["local_name"]


@dataclass
class GridOrigin:
    azimuth: float = origin["azimuth"]
    line: int = origin["line"]
    station: int = origin["station"]
    x: float = origin["x"]
    y: float = origin["y"]
    interval: float = origin["interval"]
    sl_direction: int = origin.get("sl", 1)


class ConvertTools:
    proj_local = Proj(projection["local_proj"])
    proj_utm = Proj(projection["utm_proj"])

    @staticmethod
    def transformation() -> tuple[float, float]:
        """transformation from interval to their corresponding x,  y components
        based on azimuth
        """
        azimuth = np.pi / 180 * GridOrigin().azimuth
        sin_azm = np.sin(azimuth)
        cos_azm = np.cos(azimuth)
        return sin_azm, cos_azm

    @staticmethod
    def strip_lon_lat(longitude: str, latitude: str) -> tuple[re.Match, re.Match]:
        lon = re.match(
            r'^\s*(\d{1,3})[\s\u00B0]\s*(\d{1,2})[\s\']\s*(\d{1,2}|\d{1,2}\.\d*)[\s"]{0,1}\s*([EWew])\s*$',
            longitude,
        )
        lat = re.match(
            r'^\s*(\d{1,3})[\s\u00B0]\s*(\d{1,2})[\s\']\s*(\d{1,2}|\d{1,2}\.\d*)[\s"]{0,1}\s*([NSns])\s*$',
            latitude,
        )
        return lon, lat

    def convert_dms_to_dec_degree(
        self, longitude: str, latitude: str
    ) -> tuple[float, float]:
        lon, lat = self.strip_lon_lat(longitude, latitude)
        if lon and lat:
            lat_d = float(lat.group(1))
            lat_m = float(lat.group(2))
            lat_s = float(lat.group(3))
            lat_ns = lat.group(4).upper()

            lon_d = float(lon.group(1))
            lon_m = float(lon.group(2))
            lon_s = float(lon.group(3))
            lon_ew = lon.group(4).upper()

            # check correct ranges
            if not (0 <= lat_d < 180) or not (0 <= lon_d < 180):
                return -1, -1

            if not (0 <= lat_m < 60) or not (0 <= lon_m < 60):
                return -1, -1

            if not (0 <= lat_s < 60) or not (0 <= lon_s < 60):
                return -1, -1

            if not (lat_ns in ["N", "S"]) or not (lon_ew in ["E", "W"]):
                return -1, -1

            latitude = lat_d + lat_m / 60 + lat_s / 3600
            latitude = latitude if lat_ns.upper() == "N" else latitude * -1

            longitude = lon_d + lon_m / 60 + lon_s / 3600
            longitude = longitude if lon_ew.upper() == "E" else longitude * -1

            return longitude, latitude

        else:
            return -1, -1

    @staticmethod
    def convert_dec_degree_to_dms(longitude: float, latitude: float) -> tuple[str, str]:
        if not (-180 < latitude <= 180) or not (-180 < longitude <= 180):
            return "-", "-"

        else:
            if latitude >= 0:
                lat_ns = "N"

            else:
                lat_ns = "S"

            latitude = abs(latitude)
            lat_d = int(latitude)
            lat_m = (latitude - lat_d) * 60
            lat_s = (lat_m % 1) * 60
            lat_m = int(lat_m)
            if int(round(lat_s, 3)) == 60:
                lat_m += 1
                lat_s = 0
            lat = f"{lat_d:3d}{degree_symbol} {lat_m:02d}' {lat_s:2.3f}\" {lat_ns}"

            if longitude >= 0:
                lon_ew = "E"

            else:
                lon_ew = "W"

            longitude = abs(longitude)
            lon_d = abs(int(longitude))
            lon_m = (longitude - lon_d) * 60
            lon_s = (lon_m % 1) * 60
            lon_m = int(lon_m)
            if int(round(lon_s, 3)) == 60:
                lon_m += 1
                lon_s = 0
            lon = f"{lon_d:3d}{degree_symbol} {lon_m:02d}' {lon_s:2.3f}\" {lon_ew}"

            return lon, lat

    def utm_to_wgs84(self, easting: float, northing: float) -> tuple[float, float]:
        converted_point = Point(self.proj_utm(easting, northing, inverse=True))
        return converted_point.x, converted_point.y

    def local_to_wgs84(self, easting: float, northing: float) -> tuple[float, float]:
        converted_point = Point(self.proj_local(easting, northing, inverse=True))
        return converted_point.x, converted_point.y

    def wgs84_to_utm(self, longitude: float, latitude: float) -> tuple[float, float]:
        converted_point = Point(self.proj_utm(longitude, latitude))
        return converted_point.x, converted_point.y

    def wgs84_to_local(self, longitude: float, latitude: float) -> tuple[float, float]:
        converted_point = Point(self.proj_local(longitude, latitude))
        return converted_point.x, converted_point.y

    def local_to_utm(self, easting: float, northing: float) -> tuple[float, float]:
        # local to wgs84 lon, lat
        converted_point = Point(self.proj_local(easting, northing, inverse=True))
        # wgs84 lon, lat to utm
        converted_point = Point(self.proj_utm(converted_point.x, converted_point.y))
        return converted_point.x, converted_point.y

    def utm_to_local(self, easting: float, northing: float) -> tuple[float, float]:
        # utm to wgs84 lon, lat
        converted_point = Point(self.proj_utm(easting, northing, inverse=True))
        # wgs84 lon, lat to local
        converted_point = Point(self.proj_local(converted_point.x, converted_point.y))
        return converted_point.x, converted_point.y

    def grid_local(self, line, station):
        # grid to local easting, northing
        orgn = GridOrigin()
        sin_azm, cos_azm = self.transformation()
        # step 1 move to origin with respect to the line number
        new_origin_x = (line - orgn.line) * cos_azm * orgn.interval + orgn.x
        new_origin_y = (
            -orgn.sl_direction * (line - orgn.line) * sin_azm * orgn.interval + orgn.y
        )
        # step 2 calculate x, y with respect to the new origin
        easting = (station - orgn.station) * sin_azm * orgn.interval + new_origin_x
        northing = (station - orgn.station) * cos_azm * orgn.interval + new_origin_y
        return easting, northing

    def local_grid(self, easting, northing):
        # local easting, northing to grid
        orgn = GridOrigin()
        sin_azm, cos_azm = self.transformation()
        x1 = (easting - orgn.x) * sin_azm + (northing - orgn.y) * cos_azm
        y1 = (easting - orgn.x) * cos_azm - orgn.sl_direction * (
            northing - orgn.y
        ) * sin_azm
        station = round(x1 / orgn.interval + orgn.station, 0)
        line = round(y1 / orgn.interval + orgn.line, 0)
        return line, station
