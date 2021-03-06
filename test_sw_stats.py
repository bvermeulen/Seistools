''' tests '''
import numpy as np
import pytest
import swath_stats

gis_calc = swath_stats.GisCalc()

#pylint: disable=line-too-long

def test_add_swath_0():
    azimuth = 0
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 100, test_azimuth=azimuth)
    assert a == (10, 20)
    assert b == (210, 20)
    assert c == (210, 50_020)
    assert d == (10, 50_020)

def test_add_swath_5():
    azimuth = 0
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 105, test_azimuth=azimuth)
    assert a == (1010, 20)
    assert b == (1210, 20)
    assert c == (1210, 50_020)
    assert d == (1010, 50_020)

def test_add_swath_5_30degrees():
    azimuth = 30
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 105, test_azimuth=azimuth)

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
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 105, test_azimuth=azimuth)

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
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 105, test_azimuth=azimuth)

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
    a, b, c, d = gis_calc.get_envelop_swath_cornerpoint((10, 20), 105, test_azimuth=azimuth)

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

def test_aggregate_src_stats():
    gis_calc.aggregate_src_stats(5, 10, 1, 2)
    result = gis_calc.swath_src_stats.loc[0].to_list()
    # params
    SLS_flat = 25
    SPS_flat = 25
    SLS_dune = 400
    SPS_dune = 12.5
    RLS = 200
    RPS = 25

    assert result[0] == 5
    assert result[1] == 10
    assert result[2] == 7
    assert result[3] == 1
    assert result[4] == 2
    assert result[5] == result[1] * 1000 / SLS_flat * 1000 / SPS_flat
    assert result[6] == result[2] * 1000 / SLS_flat * 1000 / SPS_flat
    assert result[7] == result[3] * 1000 / SLS_flat * 1000 / SPS_flat
    assert result[8] == result[4] * 1000 / SLS_dune * 1000 / SPS_dune
    assert result[9] == result[4] * 1000 /RLS * 1000 / SPS_dune
    assert result[10] == result[8]
    assert result[11] == result[6] + result[7] + result[10]
    assert result[12] == result[10] * SPS_dune / 1000
    assert result[13] == result[11] / 10

    ctm = 3600 / (9 + 18) * 22 * (
        result[6] *.85 + result[7] * 0.60 + result[10] * 0.6) / result[11] * 12
    assert result[14] == pytest.approx(ctm)


def test_aggregate_rcv_stats():
    gis_calc.aggregate_rcv_stats(5, 10, 3)
    result = gis_calc.swath_rcv_stats.loc[0].to_list()
    # params
    # RLS = 200
    # RPS = 25
    receiver_density = 1000 / 200 * 1000 / 25

    assert result[0] == 5
    assert result[1] == 10
    assert result[2] == 7
    assert result[3] == 3
    assert result[4] == 10 * receiver_density
    assert result[5] == 7 * receiver_density
    assert result[6] == 3 * receiver_density
    assert result[7] == 10 * receiver_density
    assert result[8] == 3 * receiver_density * 25 / 1000
    assert result[9] == receiver_density

def test_swath_range_ascending_default():
    gis_calc.total_swaths = 2
    result_range = str(gis_calc.swath_range(False))
    assert result_range == 'range(210, 212)'

def test_swath_range_ascending_with_kwarg():
    gis_calc.total_swaths = 2
    result_range = str(gis_calc.swath_range(swath_reverse=False))
    assert result_range == 'range(210, 212)'

def test_swath_range_descending():
    gis_calc.total_swaths = 2
    result_range = str(gis_calc.swath_range(swath_reverse=True))
    assert result_range == 'range(211, 209, -1)'


if __name__ == '__main__':
    test_aggregate_src_stats()
