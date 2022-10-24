''' app to count terrain types by swath '''
import pandas as pd
from pathlib import Path
from seis_settings import SwathDefinition as sd
from seis_database import DbUtils

table_name = 'planned_vps_block_c'
vps_df = DbUtils.db_table_to_df(table_name).loc[:, ['Line', 'Point', 'Type']]
point_increment = int(sd.line_spacing / sd.point_spacing / 2)
vps_per_swath = int(sd.line_spacing / sd.point_spacing)


def output_to_excel(file_name, result_df):
    result_df = pd.DataFrame(result_df)
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')  #pylint: disable=abstract-class-instantiated
    result_df.loc['Totals'] = result_df.sum()
    result_df.to_excel(writer, sheet_name='swath_stats', index=False)
    writer.save()
    return f'{file_name} written to disk'


def calc_swath_stats(file_name):
    swath_stats = {
        'swath': [], 'from': [], 'to': [], 'flat': [],
        'rough': [], 'facility': [], 'dune': [], 'sabkha': [], 'total': []
    }
    for swath in range(sd.first_swath, sd.last_swath + 1):
        first_line = (
            sd.first_line + (swath - sd.first_swath) * point_increment * vps_per_swath
        )
        last_line = first_line + (vps_per_swath - 1) * point_increment
        swath_vp_df = vps_df[vps_df['Line'].between(first_line, last_line, inclusive=True)]
        c_flat = swath_vp_df[swath_vp_df['Type'] == 'flat'].shape[0]
        c_rough = swath_vp_df[swath_vp_df['Type'] == 'rough'].shape[0]
        c_facility = swath_vp_df[swath_vp_df['Type'] == 'facility'].shape[0]
        c_dune = swath_vp_df[swath_vp_df['Type'] == 'dune'].shape[0]
        c_sabkha = swath_vp_df[swath_vp_df['Type'] == 'sabkha'].shape[0]
        c_total = sum([c_flat, c_rough, c_facility, c_dune, c_sabkha])

        swath_stats['swath'].append(swath)
        swath_stats['from'].append(first_line)
        swath_stats['to'].append(last_line)
        swath_stats['flat'].append(c_flat)
        swath_stats['rough'].append(c_rough)
        swath_stats['facility'].append(c_facility)
        swath_stats['dune'].append(c_dune)
        swath_stats['sabkha'].append(c_sabkha)
        swath_stats['total'].append(c_total)

        print(f'swath: {swath}, line_1: {first_line}, line_2: {last_line}, total: {c_total}')

    print(output_to_excel(file_name, pd.DataFrame(swath_stats)))


if __name__ == '__main__':
    file_name = Path('vp_count_terrain.xlsx')
    calc_swath_stats(file_name)
