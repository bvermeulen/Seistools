import time
from dataclasses import asdict
from pathlib import Path
import pandas as pd


class OutputMixin:
    @staticmethod
    def print_status(swath_nr, areas):
        ''' print a status line '''
        print(
            f'swath: {swath_nr}, '
            f'area: {areas["area"]:.2f}, '
            f'rough: {areas["area_rough"]:.2f}, '
            f'facilities: {areas["area_facilities"]:.2f}, '
            f'dune: {areas["area_dunes"]:.2f}, '
            f'sabkha: {areas["area_sabkha"]:.2f}\r', end=''
        )

    @staticmethod
    def print_totals(gis, total_src_area, total_src_sabkha_area, total_src_dune_area,
                     total_rcv_area, total_rcv_dune_area):
        # check if totals match the sum of the swathss
        area_src_block = sum(gis.source_block_gpd.geometry.area.to_list()) / 1e6
        print(f'\n\narea source block: {area_src_block}')
        print(f'area source block: {total_src_area}\n')

        try:
            area_sabkha = sum(gis.sabkha_gpd.geometry.area.to_list()) / 1e6
            print(f'area sabkha: {area_sabkha}')
            print(f'area source sabkha: {total_src_sabkha_area}\n')
        except AttributeError:
            pass

        try:
            area_dunes = sum(gis.dunes_gpd.geometry.area.to_list()) / 1e6
            print(f'area dunes: {area_dunes}')
            print(f'area source dunes: {total_src_dune_area}\n')
        except AttributeError:
            pass

        area_rcv_block = sum(gis.receiver_block_gpd.geometry.area.to_list()) / 1e6
        print(f'area receiver block: {area_rcv_block}')
        print(f'area receiver block: {total_rcv_area}\n')

        if area_dunes > 0:
            print(f'area dunes: {area_dunes}')
            print(f'area dunes: {total_rcv_dune_area}')

    @staticmethod
    def print_prod(sw1, sw2, sw_p1, sw_p2, sw_adv1, sw_adv2, print_status=False) -> None:
        if print_status:
            print(
                f'prod: {sw1:4} - {sw2:4}: {sw_p1:4}: {sw_p2:4}; '
                f'advance: {sw_adv1:4} - {sw_adv2:4}'
            )

    def stats_to_excel(self, cfg):
        while True:
            try:
                _ = open(cfg.excel_file, 'w+')
                break

            except IOError:
                print(f'Unable to write the excel file, please close {cfg.excel_file} ...')
                time.sleep(5)

        writer = pd.ExcelWriter(cfg.excel_file, engine='xlsxwriter')  #pylint: disable=abstract-class-instantiated
        workbook = writer.book

        # write setup to excel
        ws_setup = workbook.add_worksheet('Setup')
        ws_setup.write_row('A1', ['Item', 'Value'])
        ws_setup.write_column('A2', list(asdict(cfg).keys()))
        ws_setup.write_column(
            'B2',
            [str(v) if isinstance(v, dict|tuple|Path) else v
                for v in asdict(cfg).values()]
        )

        # sum the columns and write dataframes to excel
        self.swath_src_stats.loc['Totals'] = self.swath_src_stats.sum()
        self.swath_src_stats.to_excel(writer, sheet_name='Source', index=False)
        self.swath_rcv_stats.loc['Totals'] = self.swath_rcv_stats.sum()
        self.swath_rcv_stats.to_excel(writer, sheet_name='Receiver', index=False)
        self.prod_stats.loc['Totals'] = self.prod_stats.sum()
        self.prod_stats.to_excel(writer, sheet_name='Prod', index=False)

        ws_charts = workbook.add_worksheet('Charts')
        total_swaths = len(self.swath_src_stats) - 1
        total_production_days = len(self.prod_stats) - 1
        name_font_title = {'name': 'Arial', 'size': 10}

        # Chart 1: VP by type
        # format ['sheet', first_row, first_column, last_row, last_column]
        chart1 = workbook.add_chart({'type': 'line'})
        col_range = [12, 13, 14, 15, 16, 17, 19] if self.src_infill else [7, 8, 9, 10, 11, 12, 14]
        for col in col_range:
            chart1.add_series({
                'name': ['Source', 0, col],
                'categories': ['Source', 1, 0, total_swaths, 0],
                'values': ['Source', 1, col, total_swaths, col],
            })
        chart1.set_title({'name': cfg.title_chart + ' - VP by type',
                          'name_font': name_font_title,})
        chart1.set_x_axis({'name': 'swath'})
        chart1.set_y_axis({'name': 'vp'})
        chart1.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('B2', chart1)

        # Chart 2: CTM by swath
        chart2 = workbook.add_chart({'type': 'line'})
        col_range = [29] if self.src_infill else [19]
        for col in col_range:
            chart2.add_series({
                'name': ['Source', 0, col],
                'categories': ['Source', 1, 0, total_swaths, 0],
                'values': ['Source', 1, col, total_swaths, col],
            })
        chart2.set_title({'name': cfg.title_chart + ' - CTM by swath',
                          'name_font': name_font_title,})
        chart2.set_x_axis({'name': 'swath'})
        chart2.set_y_axis({'name': 'vp'})
        chart2.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('B18', chart2)

        # Chart 3: Source density by swath
        chart3 = workbook.add_chart({'type': 'line'})
        col_range = [28] if self.src_infill else [18]
        for col in col_range:
            chart3.add_series({
                'name': ['Source', 0, col],
                'categories': ['Source', 1, 0, total_swaths, 0],
                'values': ['Source', 1, col, total_swaths, col],
            })
        chart3.set_title({'name': cfg.title_chart + ' - Source density by swath',
                          'name_font': name_font_title,})
        chart3.set_x_axis({'name': 'swath'})
        chart3.set_y_axis({'name': 'vp'})
        chart3.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('B34', chart3)

        # Chart 4: dozer km per day
        chart4 = workbook.add_chart({'type': 'line'})
        for col in [10]:
            chart4.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 1, total_production_days, 1],
                'values': ['Prod', 1, col, total_production_days, col],
            })
        chart4.set_title({'name': cfg.title_chart + ' - Dozer km',
                          'name_font': name_font_title,})
        # chart4.set_x_axis({'name': 'Day'})
        chart4.set_y_axis({'name': 'km'})
        chart4.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('J2', chart4)

        # # Chart 5: dozer cumulative km
        chart5 = workbook.add_chart({'type': 'line'})
        for col in [11]:
            chart5.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 1, total_production_days, 1],
                'values': ['Prod', 1, col, total_production_days, col],
            })
        chart5.set_title({'name': cfg.title_chart + ' - Cumul. dozer km',
                          'name_font': name_font_title,})
        chart5.set_y_axis({'name': 'km'})
        chart5.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('J18', chart5)

        # Chart 6: Nodes requirement
        chart6 = workbook.add_chart({'type': 'line'})
        for col in [20, 21, 22, 23, 24, 25]:
            chart6.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 1, total_production_days, 1],
                'values': ['Prod', 1, col, total_production_days, col],
            })
        chart6.set_title({'name': cfg.title_chart + ' - Nodes',
                          'name_font': name_font_title,})
        chart6.set_y_axis({'name': 'Nodes'})
        chart6.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('J34', chart6)

        # Chart 7: Production
        chart7 = workbook.add_chart({'type': 'line'})
        for col in [9]:
            chart7.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 1, total_production_days, 1],
                'values': ['Prod', 1, col, total_production_days, col],
            })
        chart7.set_title({'name': cfg.title_chart + ' - Production',
                          'name_font': name_font_title,})
        chart7.set_y_axis({'name': 'vp'})
        chart7.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('R2', chart7)

        # Chart 8: Layout
        chart8 = workbook.add_chart({'type': 'line'})
        for col in [12, 13, 14, 15]:
            chart8.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 1, total_production_days, 1],
                'values': ['Prod', 1, col, total_production_days, col],
            })
        chart8.set_title({'name': cfg.title_chart + ' - Layout',
                          'name_font': name_font_title,})
        chart8.set_y_axis({'name': 'Nodes'})
        chart8.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('R18', chart8)

        # Chart 9: Pickup
        chart9 = workbook.add_chart({'type': 'line'})
        for col in [16, 17, 18, 19]:
            chart9.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 1, total_production_days, 1],
                'values': ['Prod', 1, col, total_production_days, col],
            })
        chart9.set_title({'name': cfg.title_chart + ' - Pickup',
                          'name_font': name_font_title,})
        chart9.set_y_axis({'name': 'Nodes'})
        chart9.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('R34', chart9)

        # ... and save it all to excel
        ws_setup.activate()
        writer.save()