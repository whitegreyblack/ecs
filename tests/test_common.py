from source.common import squares

def test_squares_inclusive():
    assert len(list(squares())) == 9

def test_squares_exclusive():
    assert len(list(squares(exclude_center=True))) == 8
