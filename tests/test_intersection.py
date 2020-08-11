# test_intersection

from source.generate import intersects

def test_intersection_bl_with_tr():
    b1 = (0, 0, 5, 5)
    b2 = (4, 4, 9, 9)

    assert intersects(*b1, b2) == True

def test_intersection_tr_with_bl():
    b1 = (0, 0, 5, 5)
    b2 = (3, -3, 5, 1)

    assert intersects(*b1, b2) == True

if __name__ == "__main__":
    print("Usage: py -m pytest tests\test_intersection.py")
