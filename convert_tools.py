''' module for conversion tools for WGS84, UTM 40N and PSD93
    note the module maintains consistency in x, y; easting, northing; and
    longitude, latitude, where x is the first and y is the second argument
'''
import re
from shapely.geometry import Point
from pyproj import Proj


degree_symbol = '\u00B0'


class ConvertTools:

    EPSG_PSD93 = (
        '+proj=utm +zone=40 +ellps=clrk80 +towgs84=-180.624,-225.516,173.919,'
        '-0.81,-1.898,8.336,16.71006 +units=m +no_defs')
    psd93 = Proj(EPSG_PSD93)
    utm40n = Proj('epsg:32640')

    @staticmethod
    def convert_dms_to_dec_degree(longitude: str, latitude: str) -> tuple[float, float]:

        lon = re.match(r'^\s*(\d{1,3})[\s\u00B0]\s*(\d{1,2})[\s\']\s*(\d{1,2}|\d{1,2}\.\d*)[\s"]{0,1}\s*([EWew])\s*$', longitude)
        lat = re.match(r'^\s*(\d{1,3})[\s\u00B0]\s*(\d{1,2})[\s\']\s*(\d{1,2}|\d{1,2}\.\d*)[\s"]{0,1}\s*([NSns])\s*$', latitude)
        if lat and lon:
            lat_d = float(lat.group(1))
            lat_m = float(lat.group(2))
            lat_s = float(lat.group(3))
            lat_ns = lat.group(4)

            lon_d = float(lon.group(1))
            lon_m = float(lon.group(2))
            lon_s = float(lon.group(3))
            lon_ew = lon.group(4)

            # check correct ranges
            if not (0 <= lat_d < 180) or not (0 <= lon_d < 180):
                return -1, -1

            if not (0 <= lat_m < 60) or not (0 <= lon_m < 60):
                return -1, -1

            if not (0 <= lat_s < 60) or not (0 <= lon_s < 60):
                return -1, -1

            latitude = lat_d + lat_m / 60 + lat_s /3600
            latitude = latitude if lat_ns.upper() == 'N' else latitude * -1

            longitude = lon_d + lon_m / 60 + lon_s /3600
            longitude = longitude if lon_ew.upper() == 'E' else longitude * -1

            return longitude, latitude

        else:
            return -1, -1

    @staticmethod
    def convert_dec_degree_to_dms(longitude: float, latitude: float) -> tuple[float, float]:
        if not (-180 < latitude <= 180) or not (-180 < longitude <= 180):
            return '-', '-'

        else:
            if latitude >= 0:
                lat_ns = 'N'

            else:
                lat_ns = 'S'

            latitude = abs(latitude)
            lat_d = int(latitude)
            lat_m = (latitude - lat_d) * 60
            lat_s = (lat_m % 1) * 60
            lat_m = int(lat_m)
            if int(round(lat_s, 3)) == 60:
                lat_m += 1
                lat_s = 0
            lat = f'{lat_d:3d}{degree_symbol} {lat_m:02d}\' {lat_s:2.3f}" {lat_ns}'

            if longitude >= 0:
                lon_ew = 'E'

            else:
                lon_ew = 'W'

            longitude = abs(longitude)
            lon_d = abs(int(longitude))
            lon_m = (longitude - lon_d) * 60
            lon_s = (lon_m % 1) * 60
            lon_m = int(lon_m)
            if int(round(lon_s, 3)) == 60:
                lon_m += 1
                lon_s = 0
            lon = f'{lon_d:3d}{degree_symbol} {lon_m:02d}\' {lon_s:2.3f}" {lon_ew}'

            return lon, lat

    def utm40n_to_wgs84(self, easting: float, northing: float) -> tuple[float, float]:
        converted_point = Point(self.utm40n(easting, northing, inverse=True))
        return converted_point.x, converted_point.y

    def psd93_to_wgs84(self, easting: float, northing: float) -> tuple[float, float]:
        converted_point = Point(self.psd93(easting, northing, inverse=True))
        return converted_point.x, converted_point.y

    def wgs84_to_utm40n(self, longitude: float, latitude: float) -> tuple[float, float]:
        converted_point = Point(self.utm40n(longitude, latitude))
        return converted_point.x, converted_point.y

    def wgs84_to_psd93(self, longitude: float, latitude: float) -> tuple[float, float]:
        converted_point = Point(self.psd93(longitude, latitude))
        return converted_point.x, converted_point.y

    def psd93_to_utm40n(self, easting: float, northing: float) -> tuple[float, float]:
        # psd93 to wgs84 lon, lat
        converted_point = Point(self.psd93(easting, northing, inverse=True))
        # wgs84 lon, lat to utm40n
        converted_point = Point(self.utm40n(converted_point.x, converted_point.y))
        return converted_point.x, converted_point.y

    def utm40n_to_psd93(self, easting: float, northing: float) -> tuple[float, float]:
        # utm40n to wgs84 lon, lat
        converted_point = Point(self.utm40n(easting, northing, inverse=True))
        # wgs84 lon, lat to psd93
        converted_point = Point(self.psd93(converted_point.x, converted_point.y))
        return converted_point.x, converted_point.y
