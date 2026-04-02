"""Classes that represent tracks stored in the jukebox library."""

from __future__ import annotations


class LibraryItem:
    """Represents a single track in the music library.

    The class stores the basic data needed by the coursework:
    track name, artist, rating, and play count.
    """

    def __init__(self, name: str, artist: str, rating: int = 0, play_count: int = 0):
        self.name = name.strip()
        self.artist = artist.strip()
        self.rating = 0
        self.play_count = 0
        self.set_rating(rating)
        self.set_play_count(play_count)

    def set_rating(self, rating: int) -> None:
        """Store a rating between 0 and 5 inclusive.

        A value outside the range is clipped to the nearest valid value so the
        object always stays in a valid state.
        """
        rating = int(rating)
        if rating < 0:
            rating = 0
        if rating > 5:
            rating = 5
        self.rating = rating

    def set_play_count(self, play_count: int) -> None:
        """Store a play count that cannot drop below zero."""
        play_count = int(play_count)
        if play_count < 0:
            play_count = 0
        self.play_count = play_count

    def increment_play_count(self) -> None:
        """Increase the number of times the track has been played by one."""
        self.play_count += 1

    def stars(self) -> str:
        """Return the current rating as a row of stars."""
        return "*" * self.rating

    def info(self) -> str:
        """Return one short line used when listing tracks in the library."""
        star_text = self.stars()
        base = f"{self.name} - {self.artist}"
        if star_text == "":
            return base
        return f"{base} {star_text}"

    def details(self, track_key: str | None = None) -> str:
        """Return a multi-line description used by the GUI detail view."""
        heading = f"Track number: {track_key}\n" if track_key is not None else ""
        return (
            f"{heading}"
            f"Name: {self.name}\n"
            f"Artist: {self.artist}\n"
            f"Rating: {self.rating} ({self.stars()})\n"
            f"Plays: {self.play_count}"
        )

    def matches(self, keyword: str) -> bool:
        """Return True when the keyword appears in searchable fields."""
        keyword = keyword.lower().strip()
        if keyword == "":
            return True
        return keyword in self.name.lower() or keyword in self.artist.lower()

    def to_dict(self) -> dict:
        """Convert the object to a plain dictionary for JSON storage."""
        return {
            "type": self.__class__.__name__,
            "name": self.name,
            "artist": self.artist,
            "rating": self.rating,
            "play_count": self.play_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryItem":
        """Create a LibraryItem from JSON data."""
        return cls(
            data.get("name", "Unknown Track"),
            data.get("artist", "Unknown Artist"),
            data.get("rating", 0),
            data.get("play_count", 0),
        )


class AlbumTrack(LibraryItem):
    """A specialised track that also stores album information.

    This subclass demonstrates inheritance and polymorphism for the coursework.
    The GUI calls details() on the base class interface, but AlbumTrack can
    extend the returned information with album-specific fields.
    """

    def __init__(
        self,
        name: str,
        artist: str,
        rating: int = 0,
        play_count: int = 0,
        album: str = "",
        year: int | None = None,
    ):
        super().__init__(name, artist, rating, play_count)
        self.album = album.strip()
        self.year = year

    def details(self, track_key: str | None = None) -> str:
        text = super().details(track_key)
        extra_lines = []
        if self.album:
            extra_lines.append(f"Album: {self.album}")
        if self.year is not None:
            extra_lines.append(f"Year: {self.year}")
        if extra_lines:
            text += "\n" + "\n".join(extra_lines)
        return text

    def matches(self, keyword: str) -> bool:
        keyword = keyword.lower().strip()
        if super().matches(keyword):
            return True
        return keyword != "" and keyword in self.album.lower()

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"album": self.album, "year": self.year})
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "AlbumTrack":
        return cls(
            data.get("name", "Unknown Track"),
            data.get("artist", "Unknown Artist"),
            data.get("rating", 0),
            data.get("play_count", 0),
            data.get("album", ""),
            data.get("year"),
        )