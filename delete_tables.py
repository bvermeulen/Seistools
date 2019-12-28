import update_vaps

vp_db = update_vaps.VpDb()
vp_db.delete_table_vaps()
vp_db.delete_table_vaps_files()
vp_db.delete_table_vp()
vp_db.delete_table_vp_files()
