''' program to run extended QC parsing module
    using various options: sequential, multiprocessing, threading
'''
import multiprocessing as mp
import threading
import queue
from pathlib import Path
from dataclasses import dataclass
from vp_extended_qc import ExtendedQc
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
    # Path('./data_files/211006 - check VAPS/20210920/210920_VIB08.txt'),
    # Path('./data_files/211006 - check VAPS/20210920/210920_VIB09.txt'),
    # Path('./data_files/211006 - check VAPS/20210920/210920_VIB10.txt'),
    # Path('./data_files/211006 - check VAPS/20210920/210920_VIB11.txt'),
    # Path('./data_files/211006 - check VAPS/20210920/210920_VIB12.txt'),
    # Path('./data_files/211006 - check VAPS/20210920/210920_VIB13.txt'),
]


@timed(logger, print_log=True)
def extended_qc_pool(file_name):
    log_message(f'run extended qc for: {file_name}')
    ext_qc = ExtendedQc(file_name)
    ext_qc.read_extended_qc()
    return ext_qc.avg_peak_df


@timed(logger, print_log=True)
def extended_qc_thread_or_process(file_name, results_queue):
    log_message(f'run extended qc for: {file_name}')
    ext_qc = ExtendedQc(file_name)
    ext_qc.read_extended_qc()
    results_queue.put(ext_qc.avg_peak_df)


@timed(logger, print_log=True)
def run_sequential():
    results = []
    log_message('start sequential ...')
    results_queue = queue.Queue()
    for filename in extended_qc_files:
        results.append(extended_qc_pool(filename))

    pprint(results)


@timed(logger, print_log=True)
def run_pool():
    results = []
    log_message('start pool ...')
    cpus = mp.cpu_count()
    log_message(f'cpu\'s: {cpus}')
    with mp.Pool(cpus - 1) as pool:
        results.append(pool.map(extended_qc_pool, extended_qc_files))

    pprint(results)


@timed(logger, print_log=True)
def run_processes():
    log_message('start processes ...')
    processes = []
    results_queue = mp.Queue()
    results = []
    for filename in extended_qc_files:
        processes.append(
            mp.Process(
              target=extended_qc_thread_or_process,
                args=(filename, results_queue,),
            )
        )
        processes[-1].start()

    log_message('all processes have started ...')
    for _ in range(len(extended_qc_files)):
        results.append(results_queue.get())

    # _ = [p.join() for p in processes]

    log_message('all processes have completed ...')
    pprint(results)


@timed(logger, print_log=True)
def run_threading():
    results = []
    log_message('start threading ...')
    threads = []
    results_queue = queue.Queue()
    results = []
    for filename in extended_qc_files:
        threads.append(
            threading.Thread(
                target=extended_qc_thread_or_process,
                args=(filename, results_queue)
            )
        )
        threads[-1].start()

    log_message('all threats have started ...')
    _ = [t.join() for t in threads]

    log_message('all threats have completed ...')
    while not results_queue.empty():
        results.append(results_queue.get())

    pprint(results)


if __name__ == '__main__':
    log_message(f'=================== timed comparisons =================== ')
    run_sequential()
    run_pool()
    run_processes()
    run_threading()
    log_message(f'======================= completed ======================= ')
