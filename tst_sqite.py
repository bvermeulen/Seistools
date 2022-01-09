import sqlite3

test_db = 'test_db.sqlite'
c = sqlite3.connect(test_db)
c.enable_load_extension(True)

c.execute('SELECT load_extension("mod_spatialite")')
# c.execute('SELECT InitSpatialMetaData(1);')

cur = c.cursor()

# cur.execute('''CREATE TABLE my_line(id INTEGER PRIMARY KEY)''')
# cur.execute('SELECT AddGeometryColumn("my_line","geom" , 4326, "LINESTRING", 2)')
# c.commit()

polygon_wkt = 'POLYGON ((11 50,11 51,12 51,12 50,11 50))'

XA = 11
YA = 52
XB = 12
YB = 49

line_wkt = 'LINESTRING({0} {1}, {2} {3})'.format(XA, YA, XB, YB)

cur.execute("""INSERT INTO my_line VALUES (?,GeomFromText(?, 4326))""", (2, line_wkt))

c.commit()

cursor = c.execute('''
    SELECT astext(st_intersection(geom, GeomFromText(?, 4326))) from my_line
    WHERE st_intersects(geom, GeomFromText(?, 4326))''', (polygon_wkt, polygon_wkt))

for item in cursor:
    print(item)
