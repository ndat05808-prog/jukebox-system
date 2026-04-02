from validation import (
    get_valid_position,
    get_valid_rating,
    normalise_playlist_name,
    normalise_track_number,
)


def test_normalise_single_digit():
    assert normalise_track_number("3") == "03"


def test_normalise_double_digit():
    assert normalise_track_number("12") == "12"


def test_normalise_with_spaces():
    assert normalise_track_number("  5  ") == "05"


def test_normalise_empty_string():
    assert normalise_track_number("") is None


def test_normalise_non_numeric():
    assert normalise_track_number("abc") is None


def test_valid_rating_5():
    assert get_valid_rating("5") == 5


def test_invalid_rating_0_without_allow_zero():
    assert get_valid_rating("0") is None


def test_valid_rating_0_with_allow_zero():
    assert get_valid_rating("0", allow_zero=True) == 0


def test_invalid_rating_text():
    assert get_valid_rating("abc") is None


def test_valid_position_inside_range():
    assert get_valid_position("2", 3) == 2


def test_invalid_position_outside_range():
    assert get_valid_position("4", 3) is None


def test_playlist_name_is_cleaned():
    assert normalise_playlist_name("  my:/playlist  ") == "myplaylist"