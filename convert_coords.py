'''
Convert coordinates
'''
import pandas as pd
import numpy as np
from shapely.geometry import Point
from pyproj import Proj

coords_file = '200123 - tracked_vibe_vps.csv'
coords_out_file = '200123 - tracked_vibe_vps_converted.csv'

EPSG_PSD93 = ('+proj=utm +zone=40 +ellps=clrk80 +towgs84=-180.624,-225.516,173.919,-0.81,-1.898,8.336,16.71006 +units=m +no_defs')

coords_df = pd.read_csv(coords_file, sep=',')
longs = coords_df['Long'].to_list()
lats = coords_df['Lat'].to_list()

utm_40n_psd93 = Proj(EPSG_PSD93)
eastings, northings = utm_40n_psd93(longs, lats)
points = [Point(easting, northing) for easting, northing in zip(eastings, northings)]
coords_df['Easting'] = eastings
coords_df['Northing'] = northings

print(points)
spacings = []
spacings.append(0)
for i in range(len(points)-1):
    spacings.append(np.sqrt((points[i+1].x - points[i].x)**2 +
                            (points[i+1].y - points[i].y)**2))

print(spacings)
coords_df['spacing'] = spacings
print(coords_df['spacing'].stdev())
coords_df.to_csv(coords_out_file)
