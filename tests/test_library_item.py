from src.models.library_item import AlbumTrack, LibraryItem


def test_library_item_stores_name_artist_and_default_values():
    item = LibraryItem("Song A", "Artist A")

    assert item.name == "Song A"
    assert item.artist == "Artist A"
    assert item.rating == 0
    assert item.play_count == 0


def test_stars_returns_the_correct_number_of_stars():
    item = LibraryItem("Song B", "Artist B", 4)

    assert item.stars() == "★★★★☆"


def test_stars_returns_five_empty_stars_when_rating_is_zero():
    item = LibraryItem("Song C", "Artist C", 0)

    assert item.stars() == "☆☆☆☆☆"


def test_info_returns_name_artist_and_stars():
    item = LibraryItem("Song D", "Artist D", 3)

    assert item.info() == "Song D - Artist D ★★★☆☆"


def test_increment_play_count_increases_value():
    item = LibraryItem("Song E", "Artist E", 2)
    item.increment_play_count()

    assert item.play_count == 1


def test_album_track_inherits_and_adds_extra_details():
    item = AlbumTrack("Song F", "Artist F", 5, 2, "Album F", 2023)
    details = item.details("06")

    assert "Track number: 06" in details
    assert "Album: Album F" in details
    assert "Year: 2023" in details
