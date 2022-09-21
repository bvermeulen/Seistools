'''
Convert coordinates
'''
import re
from enum import Enum
from convert_tools import ConvertTools

ctools = ConvertTools()

class Conversion(Enum):
    WGS84_PSD93 = 1
    PSD93_WGS84 = 2
    WGS84_UTM = 3
    UTM_WGS84 = 4
    PSD93_UTM = 5
    UTM_PSD93 = 6
    DEC_DMS = 7
    GRID_PSD93 = 8
    PSD93_GRID = 9


class DEGREE_FMT(Enum):
    DECIMAL_DEGREE = 1
    DMS = 2


def input_type_conversion(degree_format=DEGREE_FMT.DECIMAL_DEGREE):
    ''' input choices between type of conversions
    '''
    valid = False
    while not valid:
        prompt = (
            f'Conversion between WGS84, PSD93, UTM\n'
            f'------------------------------------\n'
            f'1: WGS84 ->7 PSD93 ({"decimal" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "DMS"})\n'
            f'2: PSD93 -> WGS84 ({"decimal" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "DMS"})\n'
            f'3: WGS84 -> UTM 40N ({"decimal" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "DMS"})\n'
            f'4: UTM 40N -> WGS84 ({"decimal" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "DMS"})\n'
            f'5: PSD93 -> UTM 40N\n'
            f'6: UTM 40N -> PSD93\n'
            f'7: Lat-Long {"decimal" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "DMS"} -> '
            f'{"DMS" if degree_format == DEGREE_FMT.DECIMAL_DEGREE else "decimal"}\n'
            f'8: 22CO GRID -> PSD93\n'
            f'9: PSD93 -> 22CO GRID\n'
        )
        print(prompt)
        answer = input('Type 1..9 [enter f to change degree format; q to quit]: ')
        if answer in ['q', 'Q', 'quit', 'Quit']:
            exit()

        elif answer in ['f', 'F']:
            if degree_format == DEGREE_FMT.DECIMAL_DEGREE:
                degree_format = DEGREE_FMT.DMS

            else:
                degree_format = DEGREE_FMT.DECIMAL_DEGREE

        try:
            val = int(answer)
            if val in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
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

    elif val == 8:
        return Conversion.GRID_PSD93, degree_format

    elif val == 9:
        return Conversion.PSD93_GRID, degree_format

    else:
        assert False, f'check the code, invalid value {val}'


def input_val1_val2(prompt_string, degree_format=None):
    valid = False
    while not valid:
        answer = input(prompt_string)

        if answer in ['q', 'Q', 'quit', 'Quit']:
            return -1, -1

        if degree_format == DEGREE_FMT.DMS:
            vals = answer.split(',')
            if len(vals) == 2:
                val2, val1 = ctools.convert_dms_to_dec_degree(vals[1], vals[0])
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
        easting, northing = input_val1_val2(f'Easting, Northing (PSD93) [enter q for a new conversion]: ')
        longitude, latitude = ctools.psd93_to_wgs84(easting, northing)

    elif ct == Conversion.UTM_WGS84:
        easting, northing = input_val1_val2(f'Easting, Northing (UTM 40N) [enter q for a new conversion]: ')
        longitude, latitude = ctools.utm40n_to_wgs84(easting, northing)

    else:
        assert False, f'incorrect conversion {ct}'

    continue_input = True
    if easting == -1 and northing == -1:
        continue_input = False

    else:
        if dfmt == DEGREE_FMT.DECIMAL_DEGREE:
            print(
                f'{"Latitude":9} | {"Longitude":9}\n'
                f'{latitude:9.6f} | {longitude:9.6f}\n'
                f'----------------------------------------------------'
            )
        else:
            lon, lat = ctools.convert_dec_degree_to_dms(longitude, latitude)
            print(
                f'{"Latitude":9} | {"Longitude":9}\n'
                f'{lat} | {lon}\n'
                f'----------------------------------------------------'
            )
    return continue_input


def conversion_from_wgs84(ct, dfmt):
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
        return continue_input

    if ct == Conversion.WGS84_PSD93:
        easting, northing = ctools.wgs84_to_psd93(longitude, latitude)
        print(
            f'{"Easting":9} | {"Northing":11} (PSD93)\n'
            f'{easting:9.1f} | {northing:11.1f}\n'
            f'----------------------------------------------------'
        )
    elif ct == Conversion.WGS84_UTM:
        easting, northing = ctools.wgs84_to_utm40n(longitude, latitude)
        print(
            f'{"Easting":9} | {"Northing":11} (UTM 40N)\n'
            f'{easting:9.1f} | {northing:11.1f}\n'
            f'----------------------------------------------------'
        )
    else:
        assert False, f'incorrect conversion {ct}'

    return continue_input


def conversion_proj1_proj2(ct):
    continue_input = True
    if ct == Conversion.PSD93_UTM:
        easting, northing = input_val1_val2(f'Easting, Northing (PSD93) [enter q for a new conversion]: ')
        if easting == -1 and northing == -1:
            continue_input = False
            return continue_input

        easting, northing = ctools.psd93_to_utm40n(easting, northing)
        print(
            f'{"Easting":9} | {"Northing":11} (UTM 40N)\n'
            f'{easting:9.1f} | {northing:11.1f}\n'
            f'----------------------------------------------------'
        )
    elif ct == Conversion.UTM_PSD93:
        easting, northing = input_val1_val2(f'Easting, Northing (UTM 40N) [enter q for a new conversion]: ')
        if easting == -1 and northing == -1:
            continue_input = False
            return continue_input

        easting, northing = ctools.utm40n_to_psd93(easting, northing)
        print(
            f'{"Easting":9} | {"Northing":11} (PSD93)\n'
            f'{easting:9.1f} | {northing:11.1f}\n'
            f'----------------------------------------------------'
        )
    else:
        assert False, f'incorrect conversion {ct}'

    return continue_input


def conversion_dec_dms(ct, dfmt):
    assert ct == Conversion.DEC_DMS, f'incorrect conversion {ct}'

    continue_input = True
    if dfmt == DEGREE_FMT.DECIMAL_DEGREE:
        latitude, longitude = input_val1_val2(
            'Latitude, Longitude (dd.dddd) [enter q for a new conversion]: ',
            degree_format=dfmt
        )
        if latitude != -1 and longitude != -1:
            lon, lat = ctools.convert_dec_degree_to_dms(longitude, latitude)
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
                f'{latitude:9.6f} | {longitude:9.6f}\n'
                f'----------------------------------------------------'
            )

        else:
            continue_input = False

    else:
        assert False, f'incorrect format {dfmt}'

    return continue_input


def conversion_22co_psd93(ct, dfmt):
    assert ct in [Conversion.GRID_PSD93, Conversion.PSD93_GRID], f'incorrect conversion {ct}'

    if ct == Conversion.GRID_PSD93:
        line, station = input_val1_val2(f'line, station (receiver) [enter q for a new conversion]: ')
        if line == -1 and station == -1: return False

        easting, northing = ctools.grid22co_psd93(line, station)
        print(
            f'{"Easting":9} | {"Northing":11} (PSD93)\n'
            f'{easting:9.1f} | {northing:11.1f}\n'
            f'----------------------------------------------------'
        )

    else:
        easting, northing = input_val1_val2(f'easting, northing [enter q for a new conversion]: ')
        if easting == -1 and northing == -1: return False

        line, station = ctools.psd93_grid22co(easting, northing)
        print(
            f'{"Line":8} | {"Station":8} (22CO receiver grid)\n'
            f'{line:8.0f} | {station:8.0f}\n'
            f'----------------------------------------------------'
        )
    return True


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

            elif conversion_type in [Conversion.GRID_PSD93, Conversion.PSD93_GRID]:
                continue_input = conversion_22co_psd93(conversion_type, degree_format)

            else:
                continue_input = False


if __name__ == '__main__':
    conversion_main()
