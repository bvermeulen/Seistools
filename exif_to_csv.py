'''
    little app to get picture exif data to csv
'''
import sys
from datetime import datetime
import json
from pathlib import Path
import pandas as pd
from picture_exif import Exif

base_folder = Path(r'D:\PDO\Central Oman 2022\11a Drone\Drone_scouting')
exif = Exif()


def progress_message_generator(message):
    loop_dash = ['\u2014', '\\', '|', '/']
    i = 1
    print_interval = 1
    while True:
        print(
            f'\r{loop_dash[int(i/print_interval) % 4]} {i} {message}', end='')
        i += 1
        yield


def main():
    if len(sys.argv) < 2:
        print('error: provide picture folder name')
        exit()

    else:
        picture_folder = sys.argv[1]

    progress_message = progress_message_generator(
        f'processing pictures in folder: {picture_folder}'
    )

    files = Path(base_folder / picture_folder).glob('*.JPG')
    csv_file = '.'.join([str(Path(base_folder / picture_folder)), 'csv'])
    print(csv_file)
    csv_df = pd.DataFrame(
        columns=[
            'file_name', 'date_time', 'label', 'longitude', 'latitude', 'altitude',
            'camera_make', 'camera_model', 'file_path', 'file_size',
        ]
    )

    for i, file in enumerate(files):
        file_name = str(file)
        pm, fm = exif.get_pic_meta(file_name)
        _, gps_values = exif.convert_gps(
            json.loads(pm.gps_latitude),
            json.loads(pm.gps_longitude),
            json.loads(pm.gps_altitude)
        )
        csv_df.loc[csv_df.shape[0]] = [
            fm.file_name,
            pm.date_picture,
            '_'.join([f'{i+1:02}', datetime.strftime(pm.date_picture, '%H:%M:%S')]),
            gps_values[1],
            gps_values[0],
            gps_values[2],
            pm.camera_make,
            pm.camera_model,
            fm.file_path,
            fm.file_size,
        ]

        next(progress_message)

    csv_df = csv_df.sort_values(by=['date_time'], ascending=True)
    csv_df.to_csv(csv_file, index=False)

if __name__ == '__main__':
    main()
