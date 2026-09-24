from app.analytics.partition import partition_value


def test_partition_typical_bullish_body():
    value = partition_value(open_=100, high=110, low=100, close=110)
    assert value == 100.0


def test_partition_doji():
    value = partition_value(open_=100, high=110, low=90, close=100)
    assert value == 0.0


def test_partition_high_equals_low():
    value = partition_value(open_=50, high=50, low=50, close=50)
    assert value == 0.0


def test_partition_missing():
    assert partition_value(open_=None, high=1, low=0, close=1) is None
