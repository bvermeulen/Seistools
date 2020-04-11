import seis_database

rcv_db = seis_database.RcvDb()

rcv_db.delete_table_records()
rcv_db.delete_table_files()
