import pickle
import pytest

from spans import floatrange, intrange


def test_empty():
    range = intrange.empty()

    assert not range
    assert range.lower is None
    assert range.upper is None


def test_non_empty():
    assert intrange()


def test_default_bounds():
    inf_range = intrange()
    assert not inf_range.lower_inc
    assert not inf_range.upper_inc

    bounded_range = intrange(1, 10)
    assert bounded_range.lower_inc
    assert not bounded_range.upper_inc

    rebound_range = intrange().replace(lower=1, upper=10)
    assert rebound_range.lower_inc
    assert not rebound_range.upper_inc


def test_unbounded():
    range = intrange()

    assert range.lower is None
    assert range.upper is None

    assert range.lower_inf
    assert range.upper_inf


def test_immutable():
    range = intrange()

    with pytest.raises(AttributeError):
        range.lower = 1

    with pytest.raises(AttributeError):
        range.upper = 10

    with pytest.raises(AttributeError):
        range.lower_inc = True

    with pytest.raises(AttributeError):
        range.upper_inc = True


def test_last():
    assert intrange().last is None
    assert intrange.empty().last is None
    assert intrange(1).last is None

    assert intrange(upper=10).last == 9
    assert intrange(1, 10).last == 9


def test_offset():
    low_range = intrange(0, 5)
    high_range = intrange(5, 10)

    assert low_range != high_range
    assert low_range.offset(5) == high_range
    assert low_range == high_range.offset(-5)

    with pytest.raises(TypeError):
        low_range.offset(5.0)


def test_offset_unbounded():
    range = intrange()
    assert range == range.offset(10)

    assert intrange(1).offset(9) == intrange(10)
    assert intrange(upper=1).offset(9) == intrange(upper=10)


def test_equality():
    assert intrange(1, 5) == intrange(1, 5)
    assert intrange.empty() == intrange.empty()
    assert intrange(1, 5) != intrange(1, 5, upper_inc=True)
    assert not intrange() == None


def test_less_than():
    assert intrange(1, 5) < intrange(2, 5)
    assert intrange(1, 4) < intrange(1, 5)
    assert not intrange(1, 5) < intrange(1, 5)
    assert intrange(1, 5) < intrange(1, 5, upper_inc=True)
    assert not intrange(1, 5, lower_inc=False) < intrange(1, 5)

    assert intrange(1, 5) <= intrange(1, 5)
    assert intrange(1, 4) <= intrange(1, 5)
    assert not intrange(2, 5) <= intrange(1, 5)

    # Hack used to work around version differences between Python 2 and 3
    # Python 2 has its own idea of how objects compare to each other.
    # Python 3 raises type error when an operation is not implemented
    assert intrange().__lt__(floatrange()) is NotImplemented
    assert intrange().__le__(floatrange()) is NotImplemented


def test_greater_than():
    assert intrange(2, 5) > intrange(1, 5)
    assert intrange(1, 5) > intrange(1, 4)
    assert not intrange(1, 5) > intrange(1, 5)
    assert intrange(1, 5, upper_inc=True) > intrange(1, 5)
    assert intrange(1, 5, lower_inc=False) > intrange(1, 5)

    assert intrange(1, 5) >= intrange(1, 5)
    assert intrange(1, 5) >= intrange(1, 4)
    assert not intrange(1, 5) >= intrange(2, 5)

    # Hack used to work around version differences between Python 2 and 3.
    # Python 2 has its own idea of how objects compare to each other.
    # Python 3 raises type error when an operation is not implemented
    assert intrange().__gt__(floatrange()) is NotImplemented
    assert intrange().__ge__(floatrange()) is NotImplemented


def test_left_of():
    assert intrange(1, 5).left_of(intrange(5, 10))
    assert intrange(1, 5).left_of(intrange(10, 15))
    assert not intrange(1, 5, upper_inc=True).left_of(intrange(5, 10))
    assert not intrange(5, 10).left_of(intrange(1, 5))
    assert not intrange.empty().left_of(intrange.empty())


def test_right_of():
    assert intrange(5, 10).right_of(intrange(1, 5))
    assert intrange(5, 10).right_of(intrange(1, 5))
    assert not intrange(5, 10).right_of(intrange(1, 5, upper_inc=True))
    assert not intrange(1, 5).right_of(intrange(5, 10))

    assert not intrange.empty().right_of(intrange.empty())


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(1, 5)),
    (intrange(1, 5), intrange(1, 10)),
    (intrange(5, 10), intrange(5, 10)),
    (intrange(1, 10), intrange(upper=5)),
    (intrange(1, 5), 0),
])
def test_startsafter(a, b):
    assert a.startsafter(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(5, 10)),
    (intrange(1, 5), intrange(1, 5, lower_inc=False)),
    (intrange(1, 10), intrange(5)),
])
def test_not_startsafter(a, b):
    assert not a.startsafter(b)


def test_startsafter_type_check():
    with pytest.raises(TypeError):
        intrange(1, 5).startsafter(1.0)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(1, 5)),
    (intrange(5, 10), intrange(1, 10)),
    (intrange(1, 10), intrange(5)),
    (intrange(1, 5), 5),
])
def test_endsbefore(a, b):
    assert a.endsbefore(b)


@pytest.mark.parametrize("a, b", [
    (intrange(5, 10), intrange(1, 5)),
    (intrange(1, 5, upper_inc=True), intrange(1, 5)),
    (intrange(1, 10), intrange(upper=5)),
])
def test_not_endsbefore(a, b):
    assert not a.endsbefore(b)


def test_endsbefore_type_check():
    with pytest.raises(TypeError):
        intrange(1, 5).startsafter(1.0)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(1, 5)),
    (intrange(1, 5), intrange(1, 10)),
    (intrange(1, 5), 1),
])
def test_startswith(a, b):
    assert a.startswith(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(5, 10)),
    (intrange(5, 10), intrange(1, 5)),
    (intrange(1, 5), intrange(1, 5, lower_inc=False)),
    (intrange(1, 5), 0),
])
def test_not_startswith(a, b):
    assert not a.startswith(b)


def test_startswith_type_check():
    with pytest.raises(TypeError):
        intrange(1, 5).startswith(5.0)


@pytest.mark.parametrize("a, b", [
    (intrange(5, 10), intrange(5, 10)),
    (intrange(1, 10), intrange(5, 10)),
    (intrange(1, 5, upper_inc=True), 5)
])
def test_startswith(a, b):
    assert a.endswith(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(5, 10)),
    (intrange(5, 10), intrange(1, 5)),
    (intrange(1, 5, upper_inc=True), intrange(1, 5)),
    (intrange(1, 5), 5),
])
def test_not_endswith(a, b):
    assert not a.endswith(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(1, 5)),
    (intrange(1, 10), intrange(1, 5)),
    (intrange(1, 10), intrange(5, 10)),
    (intrange(1, 5), 1),
    (intrange(1, 5), 3),
])
def test_contains(a, b):
    assert a.contains(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5, lower_inc=False), intrange(1, 5)),
    (intrange(1, 5), intrange(1, 5, upper_inc=True)),
    (intrange(1, 5, lower_inc=False), 1),
    (intrange(1, 5), 5),
])
def test_not_contains(a, b):
    assert not a.contains(b)


def test_contains_type_check():
    with pytest.raises(TypeError):
        intrange(1, 5).contains(None)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(1, 5)),
    (intrange(1, 5), intrange(1, 10)),
    (intrange(5, 10), intrange(1, 10)),
])
def test_within(a, b):
    assert a.within(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(1, 5, lower_inc=False)),
    (intrange(1, 5, upper_inc=True), intrange(1, 5)),
])
def test_not_within(a, b):
    assert not a.within(b)


@pytest.mark.parametrize("value", [
    True,
    None,
    1,
])
def test_within_type_check(value):
    with pytest.raises(TypeError):
        intrange(1, 5).within(value)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5, upper_inc=True), intrange(5, 10)),
    (intrange(1, 5), intrange(3, 8)),
    (intrange(3, 8), intrange(1, 5)),
    (intrange(1, 10), intrange(5)),
])
def test_overlap(a, b):
    assert a.overlap(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(5, 10)),
    (intrange(1, 5), intrange(5, 10, lower_inc=False)),
])
def test_not_overlap(a, b):
    assert not a.overlap(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(5, 10)),
])
def test_adjacent(a, b):
    assert a.adjacent(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5, upper_inc=True), intrange(5, 10)),
    (intrange(1, 5), intrange(5, 10, lower_inc=False)),
    (intrange(1, 5), intrange(3, 8)),
    (intrange(3, 8), intrange(1, 5)),
    (intrange.empty(), intrange(0, 5)),
])
def test_not_adjacent(a, b):
    assert not a.adjacent(b)


@pytest.mark.parametrize("value", [
    None,
    1,
    floatrange(5.0, 10.0),
])
def test_adjacent_type_check(value):
    with pytest.raises(TypeError):
        intrange(1, 5).adjacent(value)


@pytest.mark.parametrize("a, b, union", [
    (intrange(1, 5), intrange(5, 10), intrange(1, 10)),
    (intrange(1, 5), intrange(3, 10), intrange(1, 10)),
    (intrange(5, 10), intrange(1, 5), intrange(1, 10)),
    (intrange(3, 10), intrange(1, 5), intrange(1, 10)),
    (intrange.empty(), intrange(1, 5), intrange(1, 5)),
    (intrange(1, 5), intrange.empty(), intrange(1, 5)),
])
def test_union(a, b, union):
    assert a.union(b) == union


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(5, 10, lower_inc=False)),
    (intrange(5, 10, lower_inc=False), intrange(1, 5)),
    (intrange(10, 15), intrange(1, 5)),
    (intrange(1, 5), intrange(10, 15)),
])
def test_broken_union(a, b):
    with pytest.raises(ValueError):
        a.union(b)


@pytest.mark.parametrize("a, b, difference", [
    (intrange(1, 5), intrange.empty(), intrange(1, 5)),
    (intrange(1, 5), intrange(5, 10), intrange(1, 5)),
    (intrange(1, 5), intrange(3, 8), intrange(1, 3)),
    (intrange(3, 8), intrange(1, 5), intrange(5, 8)),
    (intrange(3, 8), intrange(1, 5, upper_inc=True), intrange(5, 8, lower_inc=False)),
    (intrange(1, 5), intrange(1, 3), intrange(3, 5)),
    (intrange(1, 5), intrange(3, 5), intrange(1, 3)),
    (intrange(1, 5), intrange(1, 10), intrange.empty()),
])
def test_difference(a, b, difference):
    assert a.difference(b) == difference


def test_broken_difference():
    with pytest.raises(ValueError):
        intrange(1, 15).difference(intrange(5, 10))


@pytest.mark.parametrize("a, b, intersection", [
    (intrange(1, 5), intrange(1, 5), intrange(1, 5)),
    (intrange(1, 15), intrange(5, 10), intrange(5, 10)),
    (intrange(1, 5), intrange(3, 8), intrange(3, 5)),
    (intrange(3, 8), intrange(1, 5), intrange(3, 5)),
    (intrange(3, 8, lower_inc=False), intrange(1, 5), intrange(3, 5, lower_inc=False)),
    (intrange(1, 10), intrange(5), intrange(5, 10)),
    (intrange(1, 10), intrange(upper=5), intrange(1, 5)),
])
def test_intersection(a, b, intersection):
    assert a.intersection(b) == intersection


def test_pickling():
    span = intrange(1, 10)
    assert span == pickle.loads(pickle.dumps(span))