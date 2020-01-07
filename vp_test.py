from vp_database import VpDb

vp_db = VpDb()

def test_get_vp_data_by_line():
    vp_df = vp_db.get_vp_data_by_line(1028)
    vp = vp_df[vp_df['station'] == 18373]

    assert vp.iloc[0].avg_phase == 1
    assert vp.iloc[0].peak_phase == 7
    assert vp.iloc[0].avg_dist == 22
    assert vp.iloc[0].peak_dist == 69
    assert vp.iloc[0].avg_force == 61
    assert vp.iloc[0].peak_force == 80
    assert vp.iloc[0].avg_stiffness == 19
    assert vp.iloc[0].avg_viscosity == 17

if __name__ == '__main__':
    test_get_vp_data_by_line()
