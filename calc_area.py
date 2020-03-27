''' calculate area of shapefile polygon
'''
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt

EPSG_PSD93_UTM40 = 3440
project_base_folder = Path('D:/OneDrive/Work/PDO/Lekhwair 3D/QGIS - mapping/')


def main():

    file_name = (project_base_folder /
                'Lekhwair Block C - Shapefiles/Dozers/Remaining 25 March - block B.shp')
    shapefile_gpd = gpd.read_file(file_name)
    shapefile_gpd.to_crs(f'EPSG:{EPSG_PSD93_UTM40}')

    _, ax = plt.subplots(figsize=(6, 6))
    shapefile_gpd.plot(ax=ax, facecolor='none', edgecolor='red', linewidth=0.5)

    swath_area = sum(shapefile_gpd.geometry.area.to_list())/ 1e6
    print(f'total area is: {swath_area:.2f} km^2')

    plt.show()

if __name__ == '__main__':
    main()
