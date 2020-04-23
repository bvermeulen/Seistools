'''
Convert coordinates
'''
from enum import Enum
from shapely.geometry import Point
from pyproj import Proj

EPSG_PSD93 = (
    '+proj=utm +zone=40 +ellps=clrk80 +towgs84=-180.624,-225.516,173.919,'
    '-0.81,-1.898,8.336,16.71006 +units=m +no_defs')
utm_40n_psd93 = Proj(EPSG_PSD93)

class Conversion(Enum):
    WGS84_PSD93 = 1
    PSD93_WGS84 = 2
    QUIT = 3


def input_val1_val2(prompt_string):
    valid = False
    while not valid:
        answer = input(prompt_string)

        if answer in ['q', 'Q', 'quit', 'Quit']:
            return -1, -1

        # try comma seperated values
        try:
            val1, val2 = [float(val) for val in answer.split(',')]
            valid = True

        except (IndexError, ValueError):
            pass

        # try space seperated values
        try:
            val1, val2 = [float(val) for val in answer.split()]
            valid = True

        except (IndexError, ValueError):
            pass

    return val1, val2


def input_type_conversion():
    ''' input choise between 1) WGS84 -> PSD93 2) PSD93 -> WGS84 or QUIT
        returns: Conversion enum: WGS84_PSD93, PSD93_WGS84, QUIT
    '''
    valid = False
    prompt = (
        'Conversion between WGS84 and PSD93\n'
        '----------------------------------\n'
        '1: WGS84 -> PSD93\n'
        '2: PSD93 -> WGS84'
    )

    while not valid:
        print(prompt)
        answer = input('Type 1 or 2 [enter q to quit]: ')
        if answer in ['q', 'Q', 'quit', 'Quit']:
            return Conversion.QUIT

        try:
            val = int(answer)
            if val in [1, 2]:
                valid = True

        except ValueError:
            pass

    print('-'*34)
    return Conversion.WGS84_PSD93 if val == 1 else Conversion.PSD93_WGS84


def main():
    conversion_type = input_type_conversion()
    if conversion_type == Conversion.QUIT:
        exit()

    while True:
        if conversion_type == Conversion.PSD93_WGS84:
            easting, northing = input_val1_val2('Easting, Northing [enter q to quit]: ')
            if easting == -1:
                exit()

            converted_point = Point(utm_40n_psd93(easting, northing, inverse=True))
            print(
                f'{"Latitude":9} | {"Longitude":9}\n'
                f'{converted_point.y:9,.5f} | {converted_point.x:9,.5f}\n'
                f'----------------------------------------------------'
            )

        elif conversion_type == Conversion.WGS84_PSD93:
            latitude, longitude = input_val1_val2(
                'Latitude, Longitude (dd.dddd) [enter q to quit]: ')
            if latitude == -1:
                exit()

            converted_point = Point(utm_40n_psd93(longitude, latitude))
            print(
                f'{"Easting":9} | {"Northing":11}\n'
                f'{converted_point.x:9,.1f} | {converted_point.y:11,.1f}\n'
                f'----------------------------------------------------'
            )

        else:
            pass


if __name__ == '__main__':
    main()
