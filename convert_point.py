'''
Convert coordinates
'''
import re
from enum import Enum
from typing import Type
from shapely.geometry import Point
from pyproj import Proj

EPSG_PSD93 = (
    '+proj=utm +zone=40 +ellps=clrk80 +towgs84=-180.624,-225.516,173.919,'
    '-0.81,-1.898,8.336,16.71006 +units=m +no_defs')
utm_40n_psd93 = Proj(EPSG_PSD93)
utm_40n = Proj('epsg:32640')


class Conversion(Enum):
    WGS84_PSD93 = 1
    PSD93_WGS84 = 2
    WGS84_UTM = 3
    UTM_WGS84 = 4
    PSD93_UTM = 5
    UTM_PSD93 = 6
    DEC_DMS = 7


class DEGREE_FMT(Enum):
    DECIMAL_DEGREE = 1
    DMS = 2


def convert_dms_to_dec_degree(answer:str):
    try:
        latitude, longitude = answer.split(',')

    except ValueError:
        return -1, -1

    lat = re.match(r'^\s*(\d{1,3})[\s\u00B0]\s*(\d{1,2})[\s\']\s*(\d{1,2}|\d{1,2}\.\d*)[\s"]{0,1}\s*([NSns])\s*$', latitude)
    lon = re.match(r'^\s*(\d{1,3})[\s\u00B0]\s*(\d{1,2})[\s\']\s*(\d{1,2}|\d{1,2}\.\d*)[\s"]{0,1}\s*([EWew])\s*$', longitude)
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

        return latitude, longitude

    else:
        return -1, -1


def convert_dec_degree_to_dms(latitude: float, longitude: float):
    if not (0 <= latitude < 180) or not (0 <= longitude < 180):
        return '-', '-'

    else:
        if latitude > 0:
            lat_ns = 'N'

        else:
            lat_ns = 'S'

        latitude = abs(latitude)
        lat_d = int(latitude)
        lat_m = (latitude - lat_d) * 60
        lat_s = (lat_m % 1) * 60
        lat_m = int(lat_m)
        if int(round(lat_s, 6)) == 60:
            lat_m += 1
            lat_s = 0
        lat = f'{lat_d:3d}\u00B0 {lat_m:02d}\' {lat_s:2.3f}" {lat_ns}'

        if longitude > 0:
            lon_ew = 'E'

        else:
            lon_ew = 'W'

        longitude = abs(longitude)
        lon_d = abs(int(longitude))
        lon_m = (longitude - lon_d) * 60
        lon_s = (lon_m % 1) * 60
        lon_m = int(lon_m)
        if int(round(lon_s, 6)) == 60:
            lon_m += 1
            lon_s = 0
        lon = f'{lon_d:3d}\u00B0 {lon_m:02d}\' {lon_s:2.3f}" {lon_ew}'

        return lat, lon

def input_type_conversion(degree_format=DEGREE_FMT.DECIMAL_DEGREE):
    ''' input choices between type of conversions
    '''
    valid = False
    while not valid:
        prompt = (
            f'Conversion between WGS84, PSD93, UTM\n'
            f'------------------------------------\n'
            f'1: WGS84 -> PSD93 ({"decimal" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "DMS"})\n'
            f'2: PSD93 -> WGS84 ({"decimal" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "DMS"})\n'
            f'3: WGS84 -> UTM 40N ({"decimal" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "DMS"})\n'
            f'4: UTM 40N -> WGS84 ({"decimal" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "DMS"})\n'
            f'5: PSD93 -> UTM 40N\n'
            f'6: UTM 40N -> PSD93\n'
            f'7: Lat-Long {"decimal" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "DMS"} -> '
            f'{"DMS" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "decimal"}'
        )
        print(prompt)
        answer = input('Type 1..7 [enter f to change degree format; q to quit]: ')
        if answer in ['q', 'Q', 'quit', 'Quit']:
            exit()

        elif answer in ['f', 'F']:
            if degree_format == DEGREE_FMT.DECIMAL_DEGREE:
                degree_format = DEGREE_FMT.DMS

            else:
                degree_format = DEGREE_FMT.DECIMAL_DEGREE

        try:
            val = int(answer)
            if val in [1, 2, 3, 4, 5, 6, 7]:
                valid = True

        except ValueError:
            pass

    print('-'*34)
    if val == 1:
        return Conversion.WGS84_PSD93, degree_format

    elif val == 2:
        return Conversion.PSD93_WGS84, degree_format

    elif val == 3:
        return Conversion.WGS84_UTM, degree_format

    elif val == 4:
        return Conversion.UTM_WGS84, degree_format

    elif val == 5:
        return Conversion.PSD93_UTM, degree_format

    elif val == 6:
        return Conversion.UTM_PSD93, degree_format

    elif val == 7:
        return Conversion.DEC_DMS, degree_format

    else:
        assert False, f'check the code, invalid value {val}'


def input_val1_val2(prompt_string, degree_format=None):
    valid = False
    while not valid:
        answer = input(prompt_string)

        if answer in ['q', 'Q', 'quit', 'Quit']:
            return -1, -1

        if degree_format == DEGREE_FMT.DMS:
            val1, val2 = convert_dms_to_dec_degree(answer)
            if not (val1 == -1 and val2 == -1):
                valid = True

        else:
            # try to split on comma seperated values and space
            try:
                val1, val2 = [
                    float(val) for val in re.split(r',|\s|;', answer) if val]

                if degree_format == DEGREE_FMT.DECIMAL_DEGREE:
                    if (-180 < val1 <= 180) and (-180 < val2 <= 180):
                       valid = True

                else:
                    valid = True

            except (IndexError, ValueError):
                pass

    return val1, val2


def conversion_to_wgs84(ct, dfmt):
    if ct == Conversion.PSD93_WGS84:
        projection = utm_40n_psd93
        proj_str = 'PSD93'

    elif ct == Conversion.UTM_WGS84:
        projection = utm_40n
        proj_str = 'UTM 40N'

    else:
        assert False, f'incorrect conversion {ct}'

    continue_input = True
    easting, northing = input_val1_val2(f'Easting, Northing ({proj_str}) [enter q for a new conversion]: ')
    if easting == -1 and northing == -1:
        continue_input = False

    else:
        converted_point = Point(projection(easting, northing, inverse=True))
        if dfmt == DEGREE_FMT.DECIMAL_DEGREE:
            print(
                f'{"Latitude":9} | {"Longitude":9}\n'
                f'{converted_point.y:9,.5f} | {converted_point.x:9,.5f}\n'
                f'----------------------------------------------------'
            )
        else:
            lat, lon = convert_dec_degree_to_dms(converted_point.y, converted_point.x)
            print(
                f'{"Latitude":9} | {"Longitude":9}\n'
                f'{lat} | {lon}\n'
                f'----------------------------------------------------'
            )
    return continue_input


def conversion_from_wgs84(ct, dfmt):
    if ct == Conversion.WGS84_PSD93:
        projection = utm_40n_psd93
        proj_str = 'PSD93'

    elif ct == Conversion.WGS84_UTM:
        projection = utm_40n
        proj_str = 'UTM 40N'

    else:
        assert False, f'incorrect conversion {ct}'

    continue_input = True
    if dfmt == DEGREE_FMT.DECIMAL_DEGREE:
        latitude, longitude = input_val1_val2(
            'Latitude, Longitude (dd.dddd) [enter q for a new conversion]: ',
            degree_format=dfmt
        )
    elif dfmt == DEGREE_FMT.DMS:
        latitude, longitude = input_val1_val2(
            'Latitude, Longitude (ddd mm ss[.ddd] [NS], ddd mm ss[.ddd] [EW]) '
            '[enter q for a new conversion]: ',
            degree_format=dfmt,
        )
    if latitude == -1 and longitude == -1:
        continue_input = False

    else:
        converted_point = Point(projection(longitude, latitude))
        print(
            f'{"Easting":9} | {"Northing":11} ({proj_str})\n'
            f'{converted_point.x:9,.1f} | {converted_point.y:11,.1f}\n'
            f'----------------------------------------------------'
        )
    return continue_input


def conversion_proj1_proj2(ct):
    if ct == Conversion.PSD93_UTM:
        proj1 = utm_40n_psd93
        proj2 = utm_40n
        proj1_str = 'PSD93'
        proj2_str = 'UTM 40N'

    elif ct == Conversion.UTM_PSD93:
        proj1 = utm_40n
        proj2 = utm_40n_psd93
        proj1_str = 'UTM 40N'
        proj2_str = 'PSD93'

    else:
        assert False, f'incorrect conversion {ct}'

    continue_input = True
    easting, northing = input_val1_val2(f'Easting, Northing ({proj1_str}) [enter q for a new conversion]: ')
    if easting == -1 and northing == -1:
        continue_input = False

    else:
        # proj1 to lat, long
        converted_point = Point(proj1(easting, northing, inverse=True))
        # lat, long to proj2
        converted_point = Point(proj2(converted_point.x, converted_point.y))
        print(
            f'{"Easting":9} | {"Northing":11} ({proj2_str})\n'
            f'{converted_point.x:9,.1f} | {converted_point.y:11,.1f}\n'
            f'----------------------------------------------------'
        )
    return continue_input


def conversion_dec_dms(ct, dfmt):
    if ct != Conversion.DEC_DMS:
        assert False, f'incorrect conversion {ct}'

    continue_input = True
    if dfmt == DEGREE_FMT.DECIMAL_DEGREE:
        latitude, longitude = input_val1_val2(
            'Latitude, Longitude (dd.dddd) [enter q for a new conversion]: ',
            degree_format=dfmt
        )
        if latitude != -1 and longitude != -1:
            lat, lon = convert_dec_degree_to_dms(latitude, longitude)
            print(
                f'{"Latitude":9} | {"Longitude":9}\n'
                f'{lat} | {lon}\n'
                f'----------------------------------------------------'
            )
        else:
            continue_input = False

    elif dfmt == DEGREE_FMT.DMS:
        latitude, longitude = input_val1_val2(
            'Latitude, Longitude (ddd mm ss[.ddd] [NS], ddd mm ss[.ddd] [EW]) '
            '[enter q for a new conversion]: ',
            degree_format=dfmt,
        )
        if latitude != -1 and longitude != -1:
            print(
                f'{"Latitude":9} | {"Longitude":9}\n'
                f'{latitude:9,.5f} | {longitude:9,.5f}\n'
                f'----------------------------------------------------'
            )

        else:
            continue_input = False

    else:
        assert False, f'incorrect format {dfmt}'

    return continue_input


def conversion_main():
    degree_format = DEGREE_FMT.DECIMAL_DEGREE

    while True:
        conversion_type, degree_format = input_type_conversion(degree_format)

        continue_input = True
        while continue_input:
            if conversion_type in [Conversion.PSD93_WGS84, Conversion.UTM_WGS84]:
                continue_input = conversion_to_wgs84(conversion_type, degree_format)

            elif conversion_type in [Conversion.WGS84_PSD93, Conversion.WGS84_UTM]:
                continue_input = conversion_from_wgs84(conversion_type, degree_format)

            elif conversion_type in [Conversion.UTM_PSD93, Conversion.PSD93_UTM]:
                continue_input = conversion_proj1_proj2(conversion_type)

            elif conversion_type == Conversion.DEC_DMS:
                continue_input = conversion_dec_dms(conversion_type, degree_format)

            else:
                continue_input = False


if __name__ == '__main__':
    conversion_main()
