from segpy.reader import create_reader
from segpy.writer import write_segy

with open('hilin.sgy', 'rb') as segy_in_file:
    # The seg_y_dataset is a lazy-reader, so keep the file open throughout.
    seg_y_dataset = create_reader(segy_in_file)  # Non-standard Rev 1 little-endian

    print(seg_y_dataset.num_traces())

    for i, val in enumerate(seg_y_dataset.trace_samples(4)):
        print(f'{i:4}: {float(val):10.4f}')


    # # Write the seg_y_dataset out to another file, in big-endian format
    # with open('hilin_big.sgy', 'wb') as segy_out_file:
    #     write_segy(segy_out_file, seg_y_dataset)  #  Standard Rev 1 big-endian