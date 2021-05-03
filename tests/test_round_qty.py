from round_qty import round_qty

def test_round_qty():
    assert round_qty(0.12345) == 0.123
    assert round_qty(1.23456) == 1.235
    assert round_qty(5.6782) == 5.678
    assert round_qty(15.678) == 15
    assert round_qty(155.678) == 150
    assert round_qty(1567.891) == 1500
    assert round_qty(15678.912) == 15000

