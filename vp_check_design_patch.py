''' this module checks the vps that are sent to processing and stored in the database
    with the sps design vps
    input: sps source design
    output: sps source with a column add with count how many times the vp has been
        acquired
    pre-condition:
        - check is done on a block by block basis
        - vps sent to processing must be stored in the database

    patch: filtered on lines 4556 mod 4
'''
import sys
import numpy as np
import csv
from pathlib import Path
import seis_utils
from seis_sps_database import SpsDb


class Src:

    @classmethod
    def check_design_sps(cls, sps_design_file, block_name):
        linepoints = SpsDb().get_all_line_points(block_name)

        progress_message = seis_utils.progress_message_generator(
            f'check design sps for {sps_design_file.name}                 ')

        with open(sps_design_file, mode='rt') as sps_design:
            sps_lines = sps_design.readlines()

        csv_output_file = sps_design_file.with_suffix('.csv')
        with open(csv_output_file, 'w', newline='') as csvfile:
            csv_write = csv.writer(csvfile, delimiter=',')
            for sps_line in sps_lines:
                sps_line = sps_line.replace('\n', '')
                line, point = cls.parse_line(sps_line)
                if line == -1 or point == -1:
                    continue

                if (line - 4556) % 4 == 0:
                    linepoint = line * 10_000 + point
                    count = np.count_nonzero(linepoints == linepoint)
                    csv_elements = sps_line.split()
                    csv_elements.append(count)
                    csv_write.writerow(csv_elements)

                next(progress_message)

    @staticmethod
    def parse_line(row):
        try:
            line = int(float(row[5:11]))
            point = int(float(row[15:21]))
            return line, point

        except ValueError:
            return -1, -1


def main(sps_design_file_raw, block_name):
    sps_design_file = Path(sps_design_file_raw)
    Src().check_design_sps(sps_design_file, block_name)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('give the design SPS source file and block name')
        exit()

    main(sys.argv[1], sys.argv[2])
