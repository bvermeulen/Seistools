from seis_database import VpDb

def create_db():
    VpDb().create_database()

if __name__ == '__main__':
    create_db()
