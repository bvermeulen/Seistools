from datetime import datetime
from vp_database import VpDb

def main():
    start = datetime(2020, 1, 1)
    end = datetime(2020, 4, 4)
    VpDb().patch_add_distance_column('VP', start, end)

if __name__ == '__main__':
    main()
