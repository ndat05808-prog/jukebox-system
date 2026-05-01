from pathlib import Path

from src.models import track_library as lib


def setup_module(module):
    module.original_data_file = lib.DATA_FILE
    lib.DATA_FILE = Path("test_library_data.json")
    lib.reset_library_to_default(save=False)


def teardown_module(module):
    if lib.DATA_FILE.exists():
        lib.DATA_FILE.unlink()
    lib.DATA_FILE = module.original_data_file
    lib.reset_library_to_default(save=False)


def setup_function(function):
    lib.reset_library_to_default(save=False)


def test_list_all_returns_all_tracks():
    output = lib.list_all()
    assert "What a Wonderful World" in output
    assert "Here Comes the Sun" in output
    assert "Count on Me" in output


def test_get_name_existing_track():
    assert lib.get_name("01") == "What a Wonderful World"


def test_get_name_non_existing_track():
    assert lib.get_name("99") is None


def test_get_artist_existing_track():
    assert lib.get_artist("02") == "The Beatles"


def test_get_rating_existing_track():
    assert lib.get_rating("01") == 5


def test_set_rating_changes_rating():
    assert lib.set_rating("03", 4, auto_save=False) is True
    assert lib.get_rating("03") == 4


def test_increment_play_count_changes_value():
    original = lib.get_play_count("01")
    assert lib.increment_play_count("01", auto_save=False) is True
    assert lib.get_play_count("01") == original + 1


def test_search_tracks_by_artist():
    results = lib.search_tracks("beatles")
    assert "Here Comes the Sun" in results


def test_search_tracks_by_album_for_subclass():
    results = lib.search_tracks("abbey road")
    assert "Here Comes the Sun" in results


def test_add_track_creates_new_key():
    key = lib.add_track("New Song", "New Artist", 4)
    assert key == "06"
    assert lib.get_name("06") == "New Song"


def test_delete_track_removes_item():
    lib.add_track("Temp Song", "Temp Artist", 2)
    assert lib.delete_track("06") is True
    assert lib.get_name("06") is None


def test_get_details_includes_album_when_available():
    details = lib.get_details("02")
    assert "Album: Abbey Road" in details


def test_save_and_load_library_preserve_changes():
    lib.set_rating("01", 4, auto_save=False)
    lib.increment_play_count("01", auto_save=False)
    lib.save_library()
    lib.reset_library_to_default(save=False)
    lib.load_library()
    assert lib.get_rating("01") == 4
    assert lib.get_play_count("01") == 1
