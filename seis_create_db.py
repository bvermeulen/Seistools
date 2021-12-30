from seis_database import DbUtils


def create_db():
    DbUtils().create_database()

if __name__ == '__main__':
    create_db()
