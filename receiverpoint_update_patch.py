''' Read noise test and store to database
'''
import sys
from pathlib import Path
from seis_settings import RcvrTable
import seis_database

rcv_db = seis_database.RcvDb()
bl_origin = (435_778.45, 2_443_331.25)
bl_grid = (1000.0, 3760.0)
spacing = 12.5

class Rcv:

    @classmethod
    def read_rcvr(cls, rcvr_file):
        with open(rcvr_file, 'rt') as f:
            rcvr_lines = f.readlines()

        rcvr_points = []
        index = 1
        elevation = 0
        for rcvr_line in rcvr_lines:
            if rcvr_line[1:2] == 'Q':
                line = int(rcvr_line[24:35])
                station = int(rcvr_line[36:47])
                easting = bl_origin[0] + (line - bl_grid[0]) * spacing
                northing = bl_origin[1] + (station - bl_grid[1]) * spacing

                rcvr_points.append(
                    RcvrTable(
                        line=line,
                        station=station,
                        rcvr_index=index,
                        easting=easting,
                        northing=northing,
                        elevation=elevation
                    )
                )

            else:
                pass

        rcv_db.update_rcvr_point_records(rcvr_points)


def main(file_name):
    file_name = Path(file_name)
    rcv_db.create_table_rcvr_points()
    rcv = Rcv()
    rcv.read_rcvr(file_name)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('give the file with receiver coordinates')
        exit()

    main(sys.argv[1])
