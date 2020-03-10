'''
boundary to shape conversion
'''
import geopandas as gpd
from shapely.geometry import Polygon
from boundary_data import boundary_data


def boundary_to_gpd(boundary):
    ''' conversion of boundary vertices to
        a geopandas dataframe
        arguments:
            boundary: dict with structure defined in boundary_data.py
        returns:
            geopandas dataframe with vertex as geomeetry and crs as
                defined in boundary dict
    '''
    boundary_gpd = gpd.GeoDataFrame(
        geometry=gpd.GeoSeries(Polygon(boundary.get('vertices'))))
    boundary_gpd.crs = f'epsg:{boundary.get("crs")}'
    return boundary_gpd


def boundaries_to_shapefiles():
    folder_name = './boundaries/'

    for boundary in boundary_data:
        file_name = folder_name + boundary.get('name') + '.shp'
        boundary_to_gpd(boundary).to_file(file_name)


if __name__ == '__main__':
    boundaries_to_shapefiles()
