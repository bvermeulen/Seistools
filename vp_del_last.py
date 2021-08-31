'''
  delete last vaps file from the database
'''
from seis_vibe_database import VpDb
from seis_settings import DATA_FILES_VAPS

def main():
    # delete the last record in the database
    vaps_db = VpDb()
    filename = vaps_db.delete_last_file_id()
    if filename == -1:
        print('There are no records ...')

    # remove the file
    file = DATA_FILES_VAPS / filename
    try:
        file.unlink()
        print(f'{file.name} has been deleted ...')

    except OSError as e:
        print(f'Error: {file} : {e.strerror}')


if __name__ == '__main__':
      main()

