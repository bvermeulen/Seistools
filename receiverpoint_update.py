''' Read noise test and store to database
'''
import sys
from shapely.geometry import Point
from pyproj import Proj
from seis_settings import RcvrTable
import seis_database

EPSG_PSD93 = (
    '+proj=utm +zone=40 +ellps=clrk80 +towgs84=-180.624,-225.516,173.919,'
    '-0.81,-1.898,8.336,16.71006 +units=m +no_defs')
utm_40n_psd93 = Proj(EPSG_PSD93)
rcv_db = seis_database.RcvDb()

class Rcv:

    @classmethod
    def read_rcvr(cls, rcvr_file):
        with open(rcvr_file, 'rt') as f:
            rcvr_lines = f.readlines()

        rcvr_points = []
        index = 1
        elevation = 0
        for rcvr_line in rcvr_lines:
            latitude = float(rcvr_line[120:129])
            longitude = float(rcvr_line[131:141])

            converted_point = Point(utm_40n_psd93(longitude, latitude))
            rcvr_points.append(
                RcvrTable(
                    line=int(rcvr_line[1:18].split()[0]),
                    station=int(rcvr_line[1:18].split()[1]),
                    rcvr_index=index,
                    easting=converted_point.x,
                    northing=converted_point.y,
                    elevation=elevation
                )
            )

        rcv_db.update_rcvr_point_records(rcvr_points)


def main(file_name):
    rcv_db.create_table_rcvr_points()
    rcv = Rcv()
    rcv.read_rcvr(file_name)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('give the file with receiver coordinates')
        exit()

    main(sys.argv[1])
