""" application to parse Extended QC files and extract plot the attributes
"""
import re
from pathlib import Path


def read_line_generator(filename):
    with open(filename, mode="rt") as file_handler:
        while True:
            line = file_handler.readline()
            if not line:
                break
            yield line


def parse_line(line):
    ...


filename = Path("./data_files/230629_VIB08.txt")
read_line = read_line_generator(filename)
lines = ""
for _ in range(10):
    line = next(read_line).rstrip("\n")
    print(line)
    lines = "\n".join([lines, line])

print(lines)
