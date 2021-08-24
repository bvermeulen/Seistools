''' Read noise test and store to database
'''
import sys
from pathlib import Path
from seis_settings import RcvrTable
from seis_quantum_database import QuantumDb

rcv_db = QuantumDb()

class Rcv:

    @classmethod
    def read_rcvr(cls, rcvr_file):
        with open(rcvr_file, 'rt') as f:
            rcvr_lines = f.readlines()

        rcvr_points = []
        index = 1
        elevation = 0
        for rcvr_line in rcvr_lines:
            if rcvr_line[0:1] == 'R':
                line = int(float(rcvr_line[4:11]))
                station = int(float(rcvr_line[14:21]))
                easting = float(rcvr_line[46:55])
                northing = float(rcvr_line[55:65])

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
