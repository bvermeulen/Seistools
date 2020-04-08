from datetime import datetime
import warnings
import seis_utils
from seis_database import VpDb

warnings.filterwarnings("ignore", category=RuntimeWarning)

def main():
    start = datetime(2020, 4, 7)
    end = datetime(2020, 4, 7)
    start = vp_utils.get_production_date()
    end = start

    VpDb().patch_add_distance_column('VP', start, end)
    VpDb().patch_add_distance_column('VAPS', start, end)

if __name__ == '__main__':
    main()
