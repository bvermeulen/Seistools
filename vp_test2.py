import datetime
import vp_database

vpdb = vp_database.VpDb()

start = datetime.datetime(2020, 1, 10, 10, 0, 0)
end = datetime.datetime(2020, 1, 10, 10, 30, 0)

vp_data = vpdb.get_vp_data_by_time(start, end)