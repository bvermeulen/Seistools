''' this module checks the vps that are sent to processing and stored in the database
    with the sps design vps
    input: planned sources file (csv)
    output: sps source with a column add with count how many times the vp has been
        acquired
    pre-condition:
        - check is done on a block by block basis
        - vps sent to processing must be stored in the database
'''
import sys
import numpy as np
import csv
from pathlib import Path
import seis_utils
from seis_sps_database import SpsDb


class Src:

    @classmethod
    def check_design_sps(cls, planned_vp_file, block_name):
        linepoints = SpsDb().get_all_line_points(block_name)

        progress_message = seis_utils.progress_message_generator(
            f'check design sps for {planned_vp_file.name}                 ')

        with open(planned_vp_file, mode='rt') as csv_input:
            planned_vps = csv.reader(csv_input)

            csv_output_file = (
                planned_vp_file.parent /
                Path(''.join([planned_vp_file.stem, '_count', planned_vp_file.suffix]))
            )
            with open(csv_output_file, 'w', newline='') as csv_output:
                csv_write = csv.writer(csv_output, delimiter=',')

                # write the header
                csv_write.writerow(next(planned_vps) + ['count'])

                for planned_vp in planned_vps:
                    line, point = cls.parse_line([planned_vp])
                    if line == -1 or point == -1:
                        continue

                    linepoint = line * 10_000 + point
                    count = np.count_nonzero(linepoints == linepoint)

                    planned_vp.append(str(count))
                    csv_write.writerow(planned_vp)

                    next(progress_message)

    @staticmethod
    def parse_line(row):
        try:
            line = int(row[0][0])
            point = int(row[0][1])
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
