''' patch to convert text file to csv
    use this when it cannot be done with excel
    due to the number of rows
'''
import re
from pathlib import Path
import csv

input_text_file = input('Please give the input file: ')
input_text_file = Path(input_text_file)
output_csv_file = input_text_file.parent / ''.join([input_text_file.stem, '.csv'])

with open(input_text_file, 'rt') as f_txt:
    with open(output_csv_file, 'wt', newline='') as f_csv:
        counter = 1
        csv_writer = csv.writer(f_csv, delimiter=',')
        for text_line in f_txt:
            csv_elements = re.split('\s+', text_line)
            csv_writer.writerow(csv_elements)
            print(f' Processing: {counter:-10}', end='\r')
            counter += 1
