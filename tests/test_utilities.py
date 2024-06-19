from earthkit.time.utilities import merge_sorted


def test_merge_sorted():
    assert list(merge_sorted([])) == []
    assert list(merge_sorted([range(5)])) == list(range(5))
    assert list(merge_sorted([range(3), range(4, 7)])) == [0, 1, 2, 4, 5, 6]
    assert list(merge_sorted((range(n, 10, 2) for n in range(2)))) == list(range(10))
    assert list(merge_sorted((range(n, 10, 3) for n in range(3)))) == list(range(10))
    assert list(merge_sorted((range(n, 10, 4) for n in range(4)))) == list(range(10))
