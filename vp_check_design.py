"""
    This module checks recorded VPs stored in the SPS table in the database
    with designed VPs. Repeated VPs are counted and a design_flag is set
    if a VP was in the original design. The output is a CSV file.
    arguments:
        Two arguments must be given to the program:
        - file name containing the design VPs and must have at least the
          following fields (separated by one or more spaces):
            column1, line, point, index
            (only line, point and index are used as columns 2, 3 and 4)
        - name of the sps table in the database
    output:
        - CSV file with recorded VPs with the following fields (separated
          by comma):
            line, point, easting, northing, elevation, count, design_flag
        - count is the number of times a VP has been repeated
        - design_flag is True if a VP was in the design, False if not
    pre-condition:
        - check is done on a block by block basis
        - recorded vps must be stored in the database in the sps table

    © 2023 Howdimain
    bruno.vermeulen@hotmail.com
"""
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from seis_sps_database import SpsDb


def write_message(message_id, message_var=None):
    message_var = message_var if message_var else ""
    match message_id:
        case "db_sps":
            message_text = "Getting the recorded VP records for "
        case "source_design":
            message_text = "Getting the SPS source design records from file: "
        case "crosscheck":
            message_text = "Crosscheck acquired VPs with design"
        case "csv_out":
            message_text = f"Writing VP count CSV file: "
        case "done":
            print("Done.")
            return
        case "error":
            print(f"Error: {message_var}")
            return
        case other:
            print(f"Invalid message: {message_var}.")
            return

    print("".join([message_text, f"{message_var} ..."]))


def check_design_sps(sps_design_file, block_name):
    """
    Function to check the final SPS source records with the
    designed VPs. A count is made for repeated VPs. Compensation
    for skips that are in the final SPS but obviously not the
    design are added to the output CSV file
    """
    # create the output CSV file
    sps_extended_file = sps_design_file.parent / Path(
        "".join([sps_design_file.stem, "_count", ".csv"])
    )

    # get the sps records from the database
    write_message("db_sps", f"'{block_name}'")
    sps_df = SpsDb().get_all_line_points(block_name)
    if sps_df.empty:
        write_message(
            "error", f"SPS table for '{block_name}' is empty, load these first"
        )
        exit()

    sps_df["count"] = pd.Series(np.ones(sps_df.size))
    sps_df = sps_df.groupby(["line", "point"], as_index=False).aggregate(
        {
            "line": "last",
            "point": "last",
            "easting": "mean",
            "northing": "mean",
            "elevation": "mean",
            "count": "sum",
        }
    )
    sps_df[["line", "point", "count"]] = sps_df[["line", "point", "count"]].astype(int)

    # get the source design records from file
    write_message("source_design", f"'{sps_design_file}'")
    try:
        sps_design_df = pd.read_csv(
            sps_design_file, delimiter=r"\s+", usecols=[1, 2, 3]
        )
        if sps_design_df.empty:
            write_message("error", f"unable to read '{sps_design_file}'")
            exit()
    except Exception as e:
        write_message("error", f"'{sps_design_file}': {e}")
        exit()

    sps_design_df.columns = ["line", "point", "design"]
    sps_design_df[["line", "point", "design"]] = sps_design_df[
        ["line", "point", "design"]
    ].astype(int)

    # doing a union between recorded VPs in SPS and the designed VPs
    write_message("crosscheck", None)
    sps_df = pd.merge(sps_df, sps_design_df, on=["line", "point"], how="outer").fillna(
        0
    )
    sps_df[["line", "point", "count"]] = sps_df[["line", "point", "count"]].astype(int)
    sps_df[["design"]] = sps_df[["design"]].astype(bool)

    # write result as csv file
    write_message("csv_out", f"'{sps_extended_file}'")
    sps_df.to_csv(sps_extended_file, index=False)

    write_message("done", None)


def main(sps_design_file, block_name):
    sps_design_file = Path(sps_design_file)
    check_design_sps(sps_design_file, block_name)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        write_message("error", "Give the design SPS source file and block name")
        exit()

    main(sys.argv[1], sys.argv[2])
