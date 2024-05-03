import pytest

from loafer.utils import calculate_backoff_multiplier


@pytest.mark.parametrize(
    ("number_of_tries", "backoff_factor", "expected"),
    [
        (0, 1.5, 1),
        (1, 1.5, 1.5),
        (2, 1.5, 2.25),
        (3, 1.5, 3.375),
        (4, 1.5, 5.0625),
        (5, 1.5, 7.59375),
    ],
)
def test_calculate_backoff_multiplier(number_of_tries, backoff_factor, expected):
    assert calculate_backoff_multiplier(number_of_tries, backoff_factor) == expected
