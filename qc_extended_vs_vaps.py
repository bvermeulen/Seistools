''' program to run extended QC parsing module
    using various options: sequential, multiprocessing, threading
'''
import multiprocessing as mp
from pathlib import Path
import pandas as pd
from qc_extended import ExtendedQc
from qc_vaps import Vaps
from Utils.plogger import Logger, timed
from pprint import pprint

# Logging setup
logformat = '%(asctime)s:%(levelname)s:%(message)s'
Logger.set_logger(Path('./logs/vp_extended_qc.log'), logformat, 'INFO')
logger = Logger.getlogger()

def log_message(message):
    print(message)
    logger.info(message)

extended_qc_files = [
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB01.txt'),
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB02.txt'),
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB03.txt'),
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB04.txt'),
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB05.txt'),
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB07.txt'),
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB08.txt'),
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB09.txt'),
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB10.txt'),
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB11.txt'),
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB12.txt'),
    Path('./data_files/211006 - check VAPS/20210920/210920_VIB13.txt'),
]
vaps_file = Path('./data_files/211006 - check VAPS/jd21263dpg.txt')
excel_output_file = Path('./data_files/211006 - check VAPS/jd21263dpg.xlsx')


@timed(logger, print_log=True)
def extended_qc(file_name):
    log_message(f'run extended qc for: {file_name}')
    ext_qc = ExtendedQc(file_name)
    ext_qc.read_extended_qc()
    return ext_qc.avg_peak_df


@timed(logger, print_log=True)
def run_pool():
    log_message('start pool ...')
    cpus = mp.cpu_count()
    log_message(f'cpu\'s: {cpus}')
    with mp.Pool(cpus - 1) as pool:
        results = pool.map(extended_qc, extended_qc_files)

    # combine results in a dataframe
    extended_qc_df = None
    if results:
        extended_qc_df = results[0]
        for result in results[1:]:
            extended_qc_df = pd.concat(
                [result, extended_qc_df], ignore_index=True
            )
    return extended_qc_df


def main():
    extended_qc_df = run_pool()
    vaps = Vaps(vaps_file)
    vaps.read_vaps()
    vaps_df = vaps.avg_peak_df

    df_merge_df = pd.merge(extended_qc_df, vaps_df, on=['time_break', 'vibrator'], how='inner')
    df_merge_df = df_merge_df.sort_values('time_break')
    df_merge_df.to_excel(excel_output_file)


if __name__ == '__main__':
    main()
