''' test convert_tools
'''
from .convert_tools import ConvertTools
import pytest

ctools = ConvertTools()
degree_symbol = '\u00B0'

def test_dec_degree_to_dms_invalid():
    lat, lon = -181, 100
    v1, v2 = ctools.convert_dec_degree_to_dms(lon, lat)
    assert v1 == '-'
    assert v2 == '-'

    lat, lon = 181, -100
    v1, v2 = ctools.convert_dec_degree_to_dms(lon, lat)
    assert v1 == '-'
    assert v2 == '-'

    lat, lon = 100, -181
    v1, v2 = ctools.convert_dec_degree_to_dms(lon, lat)
    assert v1 == '-'
    assert v2 == '-'

    lat, lon = -100, 181
    v1, v2 = ctools.convert_dec_degree_to_dms(lon, lat)
    assert v1 == '-'
    assert v2 == '-'

def test_dec_degree_to_dms_sign():
    lat, lon = 10.1, 122.5
    v1, v2 = ctools.convert_dec_degree_to_dms(lon, lat)
    assert v1 == f'122{degree_symbol} 30\' 0.000" E'
    assert v2 == f' 10{degree_symbol} 06\' 0.000" N'

    lat, lon = 10.1, -122.5
    v1, v2 = ctools.convert_dec_degree_to_dms(lon, lat)
    assert v1 == f'122{degree_symbol} 30\' 0.000" W'
    assert v2 == f' 10{degree_symbol} 06\' 0.000" N'

    lat, lon = -1.1, 122.5
    v1, v2 = ctools.convert_dec_degree_to_dms(lon, lat)
    assert v1 == f'122{degree_symbol} 30\' 0.000" E'
    assert v2 == f'  1{degree_symbol} 06\' 0.000" S'

    lat, lon = -1.1, -15.5
    v1, v2 = ctools.convert_dec_degree_to_dms(lon, lat)
    assert v1 == f' 15{degree_symbol} 30\' 0.000" W'
    assert v2 == f'  1{degree_symbol} 06\' 0.000" S'

def test_dec_degree_to_dms_value():
    lat, lon = 21.868937, 56.606085
    v1, v2 = ctools.convert_dec_degree_to_dms(lon, lat)
    assert v1 == f' 56{degree_symbol} 36\' 21.906" E'
    assert v2 == f' 21{degree_symbol} 52\' 8.173" N'

    lat, lon = 18.102086, 55.909611
    v1, v2 = ctools.convert_dec_degree_to_dms(lon, lat)
    assert v1 == f' 55{degree_symbol} 54\' 34.600" E'
    assert v2 == f' 18{degree_symbol} 06\' 7.510" N'

def test_dms_to_dec_degree_invalid():
    lon, lat = '181 10 10 E', '10 10 10 N'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 == -1
    assert val2 == -1

    lon, lat = '10 10 10 E', '181 10 10 N'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 == -1
    assert val2 == -1

    lon, lat = '10 65 10 E', '10 10 10 N'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 == -1
    assert val2 == -1

    lon, lat = '10 10 10 E', '10 65 10 N'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 == -1
    assert val2 == -1

    lon, lat = '10 10 65 E', '10 10 10 N'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 == -1
    assert val2 == -1

    lon, lat = '10 10 10 E', '10 10 65 N'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 == -1
    assert val2 == -1

def test_dms_to_dec_degree_format():
    lon, lat = f'10{degree_symbol}  10\'  10"  E', f'10{degree_symbol}10\'10"N'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 != -1
    assert val2 != -1

    lon, lat = f'10 10 10 e', f'10 10 10 n'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 != -1
    assert val2 != -1

def test_dms_to_dec_degree_sign():
    lon, lat = '10 10 10 e', '10 10 10 n'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 > 0
    assert val2 > 0

    lon, lat = '10 10 10 w', '10 10 10 n'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 < 0
    assert val2 > 0

    lon, lat = '10 10 10 e', '10 10 10 s'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 > 0
    assert val2 < 0

    lon, lat = '10 10 10 w', '10 10 10 s'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 < 0
    assert val2 < 0

def test_dms_to_dec_degree_value():
    lon, lat = '56 36 21.906 e', '21 52 8.173n'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 == pytest.approx(56.606085)
    assert val2 == pytest.approx(21.868937)

    lon, lat = '55 54 34.601e', '18 06 7.509 n'
    val1, val2 = ctools.convert_dms_to_dec_degree(lon, lat)
    assert val1 == pytest.approx(55.909611)
    assert val2 == pytest.approx(18.102086)

def test_utm40n_to_wgs():
    easting, northing = 384629.55, 2001821.11
    val1, val2 = ctools.utm40n_to_wgs84(easting, northing)
    assert val1 == pytest.approx(55.909611)
    assert val2 == pytest.approx(18.102086)

    easting, northing = 459302.27, 2418372.34
    val1, val2 = ctools.utm40n_to_wgs84(easting, northing)
    assert val1 == pytest.approx(56.606085)
    assert val2 == pytest.approx(21.868937)

def test_psd93_to_wgs():
    easting, northing = 384339.0, 2001588.0
    val1, val2 = ctools.psd93_to_wgs84(easting, northing)
    assert val1 == pytest.approx(55.909611)
    assert val2 == pytest.approx(18.102086)

    easting, northing = 459012.0, 2418130.0
    val1, val2 = ctools.psd93_to_wgs84(easting, northing)
    assert val1 == pytest.approx(56.606085)
    assert val2 == pytest.approx(21.868937)

def test_wgs84_to_utm40n():
    lon, lat = 55.909611, 18.102086
    val1, val2 = ctools.wgs84_to_utm40n(lon, lat)
    assert val1 == pytest.approx(384629.55)
    assert val2 == pytest.approx(2001821.11)

    lon, lat = 56.606085, 21.868937,
    val1, val2 = ctools.wgs84_to_utm40n(lon, lat)
    assert val1 == pytest.approx(459302.27)
    assert val2 == pytest.approx(2418372.34)

def test_wgs84_to_psd93():
    lon, lat = 55.909611, 18.102086
    val1, val2 = ctools.wgs84_to_psd93(lon, lat)
    assert val1 == pytest.approx(384339.0)
    assert val2 == pytest.approx(2001588.0)

    lon, lat = 56.606085, 21.868937,
    val1, val2 = ctools.wgs84_to_psd93(lon, lat)
    assert val1 == pytest.approx(459012.0)
    assert val2 == pytest.approx(2418130.0)

def test_utm40n_to_psd93():
    easting, northing = 459302.27, 2418372.34
    val1, val2 = ctools.utm40n_to_psd93(easting, northing)
    assert val1 == pytest.approx(459012)
    assert val2 == pytest.approx(2418130)

    easting, northing = 384629.55, 2001821.11
    val1, val2 = ctools.utm40n_to_psd93(easting, northing)
    assert val1 == pytest.approx(384339.0)
    assert val2 == pytest.approx(2001588.0)

def test_psd93_to_utm40n():
    easting, northing = 459012.0, 2418130.0
    val1, val2 = ctools.psd93_to_utm40n(easting, northing)
    assert val1 == pytest.approx(459302.27)
    assert val2 == pytest.approx(2418372.34)

    easting, northing = 384339.0, 2001588.0
    val1, val2 = ctools.psd93_to_utm40n(easting, northing)
    assert val1 == pytest.approx(384629.55)
    assert val2 == pytest.approx(2001821.11)
