"""Classes that represent tracks stored in the jukebox library."""

from __future__ import annotations


class LibraryItem:
    def __init__(self, name: str, artist: str, rating: int = 0, play_count: int = 0):
        self.name = name.strip()
        self.artist = artist.strip()
        self.rating = 0
        self.play_count = 0
        self.set_rating(rating)
        self.set_play_count(play_count)

    def set_rating(self, rating: int) -> None:
        rating = int(rating)
        if rating < 0:
            rating = 0
        if rating > 5:
            rating = 5
        self.rating = rating

    def set_play_count(self, play_count: int) -> None:
        play_count = int(play_count)
        if play_count < 0:
            play_count = 0
        self.play_count = play_count

    def increment_play_count(self) -> None:
        self.play_count += 1

    def stars(self) -> str:
        return "★" * self.rating + "☆" * (5 - self.rating)

    def info(self) -> str:
        return f"{self.name} - {self.artist} {self.stars()}"

    def details(self, track_key: str | None = None) -> str:
        heading = f"Track number: {track_key}\n" if track_key is not None else ""
        return (
            f"{heading}"
            f"Name: {self.name}\n"
            f"Artist: {self.artist}\n"
            f"Rating: {self.rating} ({self.stars()})\n"
            f"Plays: {self.play_count}"
        )

    def matches(self, keyword: str) -> bool:
        keyword = keyword.lower().strip()
        if keyword == "":
            return True
        return keyword in self.name.lower() or keyword in self.artist.lower()

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "name": self.name,
            "artist": self.artist,
            "rating": self.rating,
            "play_count": self.play_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryItem":
        return cls(
            data.get("name", "Unknown Track"),
            data.get("artist", "Unknown Artist"),
            data.get("rating", 0),
            data.get("play_count", 0),
        )


class AlbumTrack(LibraryItem):
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