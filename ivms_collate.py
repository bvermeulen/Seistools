import os
import re
import shutil
from pathlib import Path
import seis_utils
from ivms_settings import IVMS_FOLDER

rag_folder = IVMS_FOLDER / 'RAG'

def get_prefix(name):
    if m := re.match(f'^.+(\d\d)-(\d\d)-(\d\d\d\d)$', name):
        return m.group(3) + m.group(2) + m.group(1)


def main():
    for foldername, _, filenames in os.walk(IVMS_FOLDER):
        if prefix := get_prefix(foldername):
            foldername = Path(foldername)
            for filename in filenames:
                if 'RAG Report' in filename:
                    new_filename = ' - '.join([prefix, filename])
                    shutil.copyfile(foldername / filename, rag_folder / new_filename)
                    print(f'created: {rag_folder / new_filename}')

if __name__ == '__main__':
    main()
