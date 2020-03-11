''' tests '''
import numpy as np
import pytest
import sw_stats

gis_calc = sw_stats.GisCalc()

def test_add_swath_0():
    azimuth = 0
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 1, test_azimuth=azimuth)
    assert a == (10, 20)
    assert b == (210, 20)
    assert c == (210, 50_020)
    assert d == (10, 50_020)

def test_add_swath_5():
    azimuth = 0
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 6, test_azimuth=azimuth)
    assert a == (1010, 20)
    assert b == (1210, 20)
    assert c == (1210, 50_020)
    assert d == (1010, 50_020)

def test_add_swath_5_30degrees():
    azimuth = 30
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 6, test_azimuth=azimuth)

    azimuth = np.pi * azimuth / 180
    width_dx = 200 * np.cos(azimuth)
    width_dy = -200 * np.sin(azimuth)
    length_dx = 50_000 * np.sin(azimuth)
    length_dy = 50_000 * np.cos(azimuth)

    assert a[0] == pytest.approx(10 + 5*width_dx)
    assert a[1] == pytest.approx(20 + 5*width_dy)
    assert b[0] == pytest.approx(10 + 6*width_dx)
    assert b[1] == pytest.approx(20 + 6*width_dy)
    assert c[0] == pytest.approx(10 + 6*width_dx + length_dx)
    assert c[1] == pytest.approx(20 + 6*width_dy + length_dy)
    assert d[0] == pytest.approx(10 + 5*width_dx + length_dx)
    assert d[1] == pytest.approx(20 + 5*width_dy + length_dy)


def test_add_swath_5_120degrees():
    azimuth = 120
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 6, test_azimuth=azimuth)

    azimuth = np.pi * azimuth / 180
    width_dx = 200 * np.cos(azimuth)
    width_dy = -200 * np.sin(azimuth)
    length_dx = 50_000 * np.sin(azimuth)
    length_dy = 50_000 * np.cos(azimuth)

    assert a[0] == pytest.approx(10 + 5*width_dx)
    assert a[1] == pytest.approx(20 + 5*width_dy)
    assert b[0] == pytest.approx(10 + 6*width_dx)
    assert b[1] == pytest.approx(20 + 6*width_dy)
    assert c[0] == pytest.approx(10 + 6*width_dx + length_dx)
    assert c[1] == pytest.approx(20 + 6*width_dy + length_dy)
    assert d[0] == pytest.approx(10 + 5*width_dx + length_dx)
    assert d[1] == pytest.approx(20 + 5*width_dy + length_dy)

def test_add_swath_5_210degrees():
    azimuth = 210
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 6, test_azimuth=azimuth)

    azimuth = np.pi * azimuth / 180
    width_dx = 200 * np.cos(azimuth)
    width_dy = -200 * np.sin(azimuth)
    length_dx = 50_000 * np.sin(azimuth)
    length_dy = 50_000 * np.cos(azimuth)

    assert a[0] == pytest.approx(10 + 5*width_dx)
    assert a[1] == pytest.approx(20 + 5*width_dy)
    assert b[0] == pytest.approx(10 + 6*width_dx)
    assert b[1] == pytest.approx(20 + 6*width_dy)
    assert c[0] == pytest.approx(10 + 6*width_dx + length_dx)
    assert c[1] == pytest.approx(20 + 6*width_dy + length_dy)
    assert d[0] == pytest.approx(10 + 5*width_dx + length_dx)
    assert d[1] == pytest.approx(20 + 5*width_dy + length_dy)

def test_add_swath_5_300degrees():
    azimuth = 300
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 6, test_azimuth=azimuth)

    azimuth = np.pi * azimuth / 180
    width_dx = 200 * np.cos(azimuth)
    width_dy = -200 * np.sin(azimuth)
    length_dx = 50_000 * np.sin(azimuth)
    length_dy = 50_000 * np.cos(azimuth)

    assert a[0] == pytest.approx(10 + 5*width_dx)
    assert a[1] == pytest.approx(20 + 5*width_dy)
    assert b[0] == pytest.approx(10 + 6*width_dx)
    assert b[1] == pytest.approx(20 + 6*width_dy)
    assert c[0] == pytest.approx(10 + 6*width_dx + length_dx)
    assert c[1] == pytest.approx(20 + 6*width_dy + length_dy)
    assert d[0] == pytest.approx(10 + 5*width_dx + length_dx)
    assert d[1] == pytest.approx(20 + 5*width_dy + length_dy)

def test_collate_stats():
    gis_calc.collate_stats(5, 10, 3)
    result = gis_calc.swath_stats.loc[0].to_list()
    # params
    # SLS_flat = 25
    # SPS_flat = 25
    # SLS_dune = 400
    # SPS_dune = 12.5
    # RLS = 200
    # RPS = 25
    assert result[0] == 5
    assert result[1] == 10
    assert result[2] == 7
    assert result[3] == 3
    assert result[4] == 16_000
    assert result[5] == 11_200
    assert result[6] == 600
    assert result[7] == 1200
    assert result[8] == 1800
    assert result[9] == 13_000
    assert result[10] == 22.5


if __name__ == '__main__':
    test_collate_stats()
