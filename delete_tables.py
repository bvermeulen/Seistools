import seis_database

vp_db = seis_database.VpDb()
vp_db.delete_table_vp()
vp_db.delete_table_vp_files()
vp_db.delete_table_vaps()
vp_db.delete_table_vaps_files()
