# Giai thich chi tiet tung dong code — JukeBox System

Tai lieu nay giai thich **tung dong code** trong moi file cua du an JukeBox,
bao gom: chuc nang, y nghia, va ly do tai sao viet nhu vay.

---

## Muc luc

1. [main.py — Diem khoi chay](#1-mainpy--diem-khoi-chay)
2. [src/library_item.py — Data Models](#2-srclibrary_itempy--data-models)
3. [src/track_library.py — Core Logic](#3-srctrack_librarypy--core-logic)
4. [src/validation.py — Kiem tra Input](#4-srcvalidationpy--kiem-tra-input)
5. [src/font_manager.py — Font va Theme](#5-srcfont_managerpy--font-va-theme)
6. [src/track_player.py — Menu Chinh](#6-srctrack_playerpy--menu-chinh)
7. [src/view_tracks.py — Duyet va Tim kiem](#7-srcview_trackspy--duyet-va-tim-kiem)
8. [src/add_remove_tracks.py — Them / Xoa Track](#8-srcadd_remove_trackspy--them--xoa-track)
9. [src/update_tracks.py — Chinh sua Track](#9-srcupdate_trackspy--chinh-sua-track)
10. [src/create_track_list.py — Playlist Builder](#10-srccreate_track_listpy--playlist-builder)
11. [src/track_statistics.py — Thong ke](#11-srctrack_statisticspy--thong-ke)
12. [tests/test_library_item.py — Test Data Models](#12-teststest_library_itempy--test-data-models)
13. [tests/test_track_library.py — Test Core Logic](#13-teststest_track_librarypy--test-core-logic)
14. [tests/test_validation.py — Test Validation](#14-teststest_validationpy--test-validation)

---

## 1. main.py — Diem khoi chay

```python
from src.track_player import main
```
- Import ham `main` tu module `track_player` trong package `src`.
- Vi `src/` la mot Python package (co `__init__.py`), ta dung cu phap `src.track_player`.

```python
if __name__ == "__main__":
    main()
```
- `__name__ == "__main__"`: Dieu kien nay chi dung khi chay truc tiep file (`python3 main.py`).
- Neu file nay bi import boi file khac, dieu kien nay se sai va `main()` se khong tu dong chay.
- Goi `main()` de khoi dong ung dung JukeBox.

**Tai sao can file nay?**
Khi dung relative imports (`from .module import ...`) trong package `src/`,
Python khong cho phep chay truc tiep `python3 src/track_player.py`.
File `main.py` o goc project giup giai quyet van de nay.

---

## 2. src/library_item.py — Data Models

File nay dinh nghia 2 class: `LibraryItem` (bai hat co ban) va `AlbumTrack` (bai hat co them album).

### Imports

```python
"""Classes that represent tracks stored in the jukebox library."""
```
- Docstring mo ta file — giai thich muc dich cua module.

```python
from __future__ import annotations
```
- Cho phep dung cu phap kieu moi nhu `str | None` ngay ca tren Python 3.9.
- Neu khong co dong nay, `str | None` chi hoat dong tu Python 3.10 tro len.

### Class LibraryItem

```python
class LibraryItem:
```
- Dinh nghia class `LibraryItem` — dai dien cho 1 bai hat trong thu vien nhac.

```python
    """Represents a single track in the music library.

    The class stores the basic data needed by the coursework:
    track name, artist, rating, and play count.
    """
```
- Docstring cua class — mo ta ngan gon class lam gi.

#### Constructor `__init__`

```python
    def __init__(self, name: str, artist: str, rating: int = 0, play_count: int = 0):
```
- Ham khoi tao, chay khi tao doi tuong moi: `LibraryItem("Song", "Artist")`.
- `name: str` — type hint, cho biet `name` can la chuoi.
- `rating: int = 0` — tham so mac dinh, neu khong truyen thi rating = 0.

```python
        self.name = name.strip()
        self.artist = artist.strip()
```
- Luu ten va nghe si vao thuoc tinh cua doi tuong.
- `.strip()` xoa khoang trang thua o dau va cuoi chuoi ("  Song  " → "Song").

```python
        self.rating = 0
        self.play_count = 0
```
- Gan gia tri mac dinh truoc. Se duoc cap nhat boi `set_rating()` va `set_play_count()` phia duoi.

```python
        self.set_rating(rating)
        self.set_play_count(play_count)
```
- Dung setter de kiem tra va gioi han gia tri (rating 0-5, play_count >= 0).
- Khong gan truc tiep `self.rating = rating` de tranh gia tri khong hop le.

#### Method `set_rating`

```python
    def set_rating(self, rating: int) -> None:
```
- Ham dat rating cho bai hat. `-> None` cho biet ham nay khong tra ve gia tri.

```python
        rating = int(rating)
```
- Ep kieu ve so nguyen (phong truong hop truyen vao chuoi "3").

```python
        if rating < 0:
            rating = 0
        if rating > 5:
            rating = 5
```
- Gioi han rating trong khoang 0 den 5.
- Neu nguoi dung truyen -1 → thanh 0. Truyen 10 → thanh 5.
- Goi la "clamping" — dam bao doi tuong luon o trang thai hop le.

```python
        self.rating = rating
```
- Gan gia tri da kiem tra vao thuoc tinh.

#### Method `set_play_count`

```python
    def set_play_count(self, play_count: int) -> None:
        play_count = int(play_count)
        if play_count < 0:
            play_count = 0
        self.play_count = play_count
```
- Tuong tu `set_rating` nhung cho luot nghe.
- Dam bao luot nghe khong bao gio am.

#### Method `increment_play_count`

```python
    def increment_play_count(self) -> None:
        self.play_count += 1
```
- Tang luot nghe len 1. Goi moi khi nguoi dung "play" bai hat.

#### Method `stars`

```python
    def stars(self) -> str:
        return "*" * self.rating
```
- Tra ve chuoi sao tuong ung voi rating.
- `"*" * 3` → `"***"`. `"*" * 0` → `""` (chuoi rong).

#### Method `info`

```python
    def info(self) -> str:
        star_text = self.stars()
        base = f"{self.name} - {self.artist}"
        if star_text == "":
            return base
        return f"{base} {star_text}"
```
- Tra ve 1 dong tom tat: "Song - Artist ***".
- Neu rating = 0 (khong co sao), chi tra ve "Song - Artist" (khong co khoang trang thua).
- Dung trong danh sach hien thi toan bo thu vien.

#### Method `details`

```python
    def details(self, track_key: str | None = None) -> str:
        heading = f"Track number: {track_key}\n" if track_key is not None else ""
        return (
            f"{heading}"
            f"Name: {self.name}\n"
            f"Artist: {self.artist}\n"
            f"Rating: {self.rating} ({self.stars()})\n"
            f"Plays: {self.play_count}"
        )
```
- Tra ve chuoi nhieu dong, hien thi chi tiet day du cua bai hat.
- `track_key` la tuy chon — neu co thi hien thi "Track number: 01" o dau.
- Dung f-string de ghep chuoi. `\n` la xuong dong.

#### Method `matches`

```python
    def matches(self, keyword: str) -> bool:
        keyword = keyword.lower().strip()
        if keyword == "":
            return True
        return keyword in self.name.lower() or keyword in self.artist.lower()
```
- Kiem tra xem tu khoa co xuat hien trong ten hoac nghe si khong.
- `.lower()` de tim kiem khong phan biet hoa/thuong ("Beatles" khop voi "beatles").
- Tu khoa rong → tra ve True (khop voi moi bai hat).
- Toan tu `in` kiem tra chuoi con: `"sun" in "Here Comes the Sun"` → True.

#### Method `to_dict`

```python
    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "name": self.name,
            "artist": self.artist,
            "rating": self.rating,
            "play_count": self.play_count,
        }
```
- Chuyen doi tuong thanh dictionary de luu vao JSON.
- `self.__class__.__name__` tra ve ten class ("LibraryItem" hoac "AlbumTrack").
- Luu truong "type" de khi doc lai biet tao dung loai doi tuong.

#### Class method `from_dict`

```python
    @classmethod
    def from_dict(cls, data: dict) -> "LibraryItem":
        return cls(
            data.get("name", "Unknown Track"),
            data.get("artist", "Unknown Artist"),
            data.get("rating", 0),
            data.get("play_count", 0),
        )
```
- `@classmethod` — goi truc tiep tren class: `LibraryItem.from_dict(data)`.
- `cls` la chinh class do (LibraryItem hoac AlbumTrack neu ke thua).
- `data.get("name", "Unknown Track")` — lay gia tri "name" tu dict, neu khong co thi dung gia tri mac dinh.
- Tao doi tuong moi tu du lieu JSON da doc.

### Class AlbumTrack (ke thua LibraryItem)

```python
class AlbumTrack(LibraryItem):
```
- `AlbumTrack` ke thua tu `LibraryItem` — co moi thu cua LibraryItem, them `album` va `year`.
- Day la **inheritance** (ke thua) trong OOP.

#### Constructor

```python
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
```
- `super().__init__(...)` goi constructor cua class cha (LibraryItem) de khoi tao name, artist, rating, play_count.
- Sau do them 2 thuoc tinh rieng: `album` va `year`.
- `year: int | None` — nam co the la so nguyen hoac None (khong biet).

#### Override `details`

```python
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
```
- Goi `super().details()` de lay noi dung co ban tu LibraryItem.
- Them dong "Album:" va "Year:" neu co.
- Day la **polymorphism** (da hinh) — cung method `details()` nhung ket qua khac nhau tuy loai doi tuong.

#### Override `matches`

```python
    def matches(self, keyword: str) -> bool:
        keyword = keyword.lower().strip()
        if super().matches(keyword):
            return True
        return keyword != "" and keyword in self.album.lower()
```
- Tim kiem trong name va artist (qua class cha), them tim trong album.
- Nguoi dung co the tim "abbey road" va se tim thay bai hat trong album do.

#### Override `to_dict`

```python
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"album": self.album, "year": self.year})
        return data
```
- Lay dict tu class cha, them "album" va "year" vao.
- `data.update(...)` them cap key-value moi vao dict da co.

#### Override `from_dict`

```python
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
```
- Tuong tu LibraryItem nhung them doc "album" va "year" tu dict.

---

## 3. src/track_library.py — Core Logic

File nay quan ly toan bo thu vien nhac: them, xoa, tim, luu, doc.

### Imports va Constants

```python
"""Functions that manage the track library and persistent storage."""
```
- Docstring cua module.

```python
from __future__ import annotations
```
- Cho phep dung `str | None`, `dict[str, LibraryItem]` tren Python 3.9.

```python
import json
from pathlib import Path
```
- `json` — thu vien chuyen doi giua Python dict va JSON string.
- `Path` — thu vien xu ly duong dan file (hien dai hon `os.path`).

```python
from .library_item import AlbumTrack, LibraryItem
```
- Relative import — dau cham `.` nghia la "cung package `src/`".
- Import 2 class de tao va xu ly doi tuong track.

```python
PROJECT_DIR = Path(__file__).resolve().parent.parent
```
- `__file__` — duong dan cua file hien tai (`src/track_library.py`).
- `.resolve()` — chuyen thanh duong dan tuyet doi.
- `.parent` — thu muc cha. `.parent.parent` — len 2 cap (tu `src/` len goc project).

```python
DATA_FILE = PROJECT_DIR / "data" / "library_data.json"
```
- Duong dan den file du lieu JSON.
- Toan tu `/` cua Path noi duong dan lai voi nhau.

### Default Library

```python
DEFAULT_LIBRARY = {
    "01": {
        "type": "LibraryItem",
        "name": "What a Wonderful World",
        "artist": "Louis Armstrong",
        "rating": 5,
        "play_count": 0,
    },
    # ... (cac track khac tuong tu)
}
```
- Du lieu mac dinh — 5 bai hat co san khi chua co file JSON nao.
- Key la so thu tu ("01", "02", ...), value la thong tin bai hat.
- "type" cho biet tao `LibraryItem` hay `AlbumTrack`.

### Bien global va ham khoi tao

```python
library: dict[str, LibraryItem] = {}
```
- Bien toan cuc chua toan bo thu vien nhac trong bo nho (RAM).
- Key la string ("01"), value la doi tuong LibraryItem hoac AlbumTrack.

```python
def _make_item(data: dict) -> LibraryItem:
    item_type = data.get("type", "LibraryItem")
    if item_type == "AlbumTrack":
        return AlbumTrack.from_dict(data)
    return LibraryItem.from_dict(data)
```
- Ham noi bo (dau `_` la quy uoc "private").
- Doc truong "type" de quyet dinh tao loai doi tuong nao.
- Day la **Factory Pattern** — tao doi tuong dua tren du lieu.

```python
def reset_library_to_default(save: bool = False) -> None:
    global library
    library = {key: _make_item(info) for key, info in DEFAULT_LIBRARY.items()}
    if save:
        save_library()
```
- `global library` — bao Python rang bien `library` la bien toan cuc, khong phai bien cuc bo.
- Dict comprehension: lap qua DEFAULT_LIBRARY va tao doi tuong cho moi track.
- `save=True` se ghi ra file JSON ngay.

```python
reset_library_to_default(save=False)
```
- Chay ngay khi module duoc import — thu vien luon co du lieu san.

### Load va Save

```python
def load_library() -> None:
    global library
    if not DATA_FILE.exists():
        reset_library_to_default(save=True)
        return
```
- Neu file JSON chua ton tai → dung du lieu mac dinh va tao file moi.

```python
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        reset_library_to_default(save=True)
        return
```
- Doc file JSON. Neu file bi loi (JSON hong hoac khong doc duoc) → dung du lieu mac dinh.
- `try/except` bat loi de app khong bi crash.

```python
    library = {key: _make_item(info) for key, info in data.items()}
```
- Chuyen moi entry trong JSON thanh doi tuong LibraryItem hoac AlbumTrack.

```python
def save_library() -> None:
    data = {key: item.to_dict() for key, item in library.items()}
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
```
- `item.to_dict()` chuyen doi tuong thanh dict.
- `json.dumps(data, indent=2)` chuyen dict thanh chuoi JSON dep (thut le 2 khoang trang).
- `ensure_ascii=False` cho phep luu ky tu Unicode (vd: tieng Viet).
- `write_text(...)` ghi chuoi ra file.

### Cac ham truy xuat

```python
def all_keys() -> list[str]:
    return sorted(library.keys(), key=int)
```
- Tra ve danh sach key da sap xep theo so ("01", "02", ...).
- `key=int` de sap xep theo gia tri so (khong phai alphabetical).

```python
def list_all() -> str:
    output_lines = []
    for key in all_keys():
        output_lines.append(f"{key} {library[key].info()}")
    return "\n".join(output_lines) + ("\n" if output_lines else "")
```
- Tao chuoi liet ke tat ca track: "01 Song - Artist ***\n02 Song - Artist **\n...".
- Them "\n" cuoi cung neu co it nhat 1 track.

```python
def get_item(key: str) -> LibraryItem | None:
    return library.get(key)
```
- `.get(key)` tra ve doi tuong neu key ton tai, None neu khong.
- An toan hon `library[key]` (se bao loi KeyError neu khong co).

```python
def get_name(key: str) -> str | None:
    item = get_item(key)
    if item is None:
        return None
    return item.name
```
- Lay ten bai hat theo key. Tra ve None neu key khong ton tai.
- `get_artist`, `get_rating`, `get_play_count` hoat dong tuong tu.

```python
def get_rating(key: str) -> int:
    item = get_item(key)
    if item is None:
        return -1
    return item.rating
```
- Tra ve -1 thay vi None khi khong tim thay (vi rating la int, khong phai str).

### Cac ham cap nhat

```python
def set_rating(key: str, rating: int, auto_save: bool = True) -> bool:
    item = get_item(key)
    if item is None:
        return False
    item.set_rating(rating)
    if auto_save:
        save_library()
    return True
```
- Dat rating moi cho track.
- `auto_save=True` — mac dinh tu dong luu file. Dat False khi cap nhat nhieu track lien tiep (de tiet kiem I/O).
- Tra ve `True` neu thanh cong, `False` neu key khong ton tai.

```python
def update_track_info(
    key: str,
    name: str,
    artist: str,
    rating: int,
    album: str = "",
    year: int | None = None,
    auto_save: bool = True,
) -> bool:
```
- Cap nhat toan bo thong tin track.

```python
    item = get_item(key)
    if item is None:
        return False
```
- Kiem tra track co ton tai khong.

```python
    name = name.strip()
    artist = artist.strip()
    album = album.strip()
```
- Lam sach input — xoa khoang trang thua.

```python
    if name == "" or artist == "":
        return False
```
- Ten va nghe si bat buoc phai co.

```python
    play_count = item.play_count
```
- Giu lai luot nghe cu (vi ta thay doi doi tuong, khong muon mat luot nghe).

```python
    if album != "" or year is not None:
        library[key] = AlbumTrack(name, artist, rating, play_count, album, year)
    else:
        library[key] = LibraryItem(name, artist, rating, play_count)
```
- Neu co album hoac year → tao AlbumTrack. Nguoc lai → tao LibraryItem.
- Thay the doi tuong cu bang doi tuong moi trong dict.

### Cac ham them/xoa

```python
def get_next_key() -> str:
    if not library:
        return "01"
    max_key = max(int(key) for key in library)
    return str(max_key + 1).zfill(2)
```
- Tim key lon nhat hien tai, cong 1.
- `.zfill(2)` them so 0 phia truoc neu can ("6" → "06").
- Thu vien rong → bat dau tu "01".

```python
def add_track(name: str, artist: str, rating: int = 0) -> str:
    key = get_next_key()
    library[key] = LibraryItem(name, artist, rating)
    save_library()
    return key
```
- Tao track moi, them vao thu vien, luu file, tra ve key moi.

```python
def delete_track(key: str) -> bool:
    if key not in library:
        return False
    del library[key]
    save_library()
    return True
```
- `del library[key]` xoa entry khoi dict.
- Luu file ngay sau khi xoa.

### Tim kiem

```python
def search_tracks(keyword: str) -> str:
    keyword = keyword.strip().lower()
    if keyword == "":
        return list_all()
```
- Keyword rong → hien thi tat ca.

```python
    output_lines = []
    for key in all_keys():
        item = library[key]
        if item.matches(keyword):
            output_lines.append(f"{key} {item.info()}")
    return "\n".join(output_lines) + ("\n" if output_lines else "")
```
- Lap qua tung track, kiem tra `matches()`, ghep ket qua thanh chuoi.

### Thong ke

```python
def get_statistics() -> dict:
    tracks = []
    for key in all_keys():
        item = library[key]
        tracks.append(
            {
                "key": key,
                "name": item.name,
                "artist": item.artist,
                "rating": item.rating,
                "play_count": item.play_count,
                "type": item.__class__.__name__,
            }
        )
```
- Tao danh sach dict — moi dict chua thong tin 1 track.
- `item.__class__.__name__` tra ve "LibraryItem" hoac "AlbumTrack".

```python
    total_tracks = len(tracks)
    total_plays = sum(track["play_count"] for track in tracks)
```
- `len()` dem so luong track. `sum()` tinh tong luot nghe.

```python
    average_rating = 0.0 if total_tracks == 0 else sum(track["rating"] for track in tracks) / total_tracks
```
- Tinh rating trung binh. Tranh chia cho 0 khi thu vien rong.

```python
    most_played = max(tracks, key=lambda track: track["play_count"], default=None)
    highest_rated = max(tracks, key=lambda track: track["rating"], default=None)
```
- `max()` tim track co gia tri lon nhat.
- `key=lambda track: track["play_count"]` — chi dinh so sanh theo truong nao.
- `default=None` — tra ve None neu danh sach rong (tranh loi).

```python
    return {
        "tracks": tracks,
        "total_tracks": total_tracks,
        "total_plays": total_plays,
        "average_rating": average_rating,
        "most_played": most_played,
        "highest_rated": highest_rated,
    }
```
- Tra ve dict chua toan bo thong ke. GUI se doc dict nay de hien thi.

```python
load_library()
```
- Dong cuoi cung — chay ngay khi module duoc import.
- Doc file JSON de cap nhat thu vien. Neu file khong co, dung du lieu mac dinh.

---

## 4. src/validation.py — Kiem tra Input

File nay chua cac ham kiem tra va chuan hoa du lieu nguoi dung nhap.

```python
"""Validation helper functions used by the GUI classes."""
```

```python
from __future__ import annotations
```

### normalise_track_number

```python
def normalise_track_number(track_number: str) -> str | None:
    track_number = track_number.strip()
```
- Xoa khoang trang: "  5  " → "5".

```python
    if track_number == "":
        return None
```
- Chuoi rong → khong hop le.

```python
    if not track_number.isdigit():
        return None
```
- `.isdigit()` kiem tra moi ky tu deu la so. "abc" → False → None.

```python
    return track_number.zfill(2)
```
- Them so 0 phia truoc: "3" → "03", "12" → "12" (da 2 chu so thi giu nguyen).

### get_valid_rating

```python
def get_valid_rating(rating_text: str, allow_zero: bool = False) -> int | None:
    rating_text = rating_text.strip()
    if rating_text == "":
        return 0 if allow_zero else None
```
- Chuoi rong: neu cho phep 0 → tra ve 0, neu khong → None.
- `allow_zero=True` dung khi them track (rating 0 chap nhan). `False` khi cap nhat (phai co rating).

```python
    if not rating_text.isdigit():
        return None
    rating = int(rating_text)
    minimum = 0 if allow_zero else 1
    if minimum <= rating <= 5:
        return rating
    return None
```
- Kiem tra rating nam trong khoang hop le.
- `minimum <= rating <= 5` — Python cho phep so sanh chuoi nhu nay (chained comparison).

### get_valid_position

```python
def get_valid_position(position_text: str, maximum: int) -> int | None:
    position_text = position_text.strip()
    if not position_text.isdigit():
        return None
    position = int(position_text)
    if 1 <= position <= maximum:
        return position
    return None
```
- Kiem tra vi tri trong playlist (tu 1 den `maximum`).
- Dung cho Move Up, Move Down, Remove Track trong playlist.

### normalise_playlist_name

```python
def normalise_playlist_name(name: str) -> str | None:
    name = name.strip()
    if name == "":
        return None
```
- Ten rong → khong hop le.

```python
    cleaned = "".join(character for character in name if character.isalnum() or character in "_- ")
```
- Chi giu lai: chu cai, so, dau gach duoi, gach ngang, khoang trang.
- Loai bo ky tu dac biet nhu `:`, `/`, `\` (co the lam hong ten file).
- Generator expression lap qua tung ky tu va loc.

```python
    cleaned = " ".join(cleaned.split())
```
- `.split()` tach theo khoang trang (nhieu khoang trang lien tiep tinh la 1).
- `" ".join(...)` ghep lai voi dung 1 khoang trang.
- "  my   playlist  " → "my playlist".

```python
    if cleaned == "":
        return None
    return cleaned
```
- Sau khi lam sach, neu con rong → khong hop le.

---

## 5. src/font_manager.py — Font va Theme

```python
"""Shared font and ttk theme configuration for the JukeBox GUIs."""
```

```python
import tkinter.font as tkfont
from tkinter import ttk
```
- `tkfont` — module quan ly font trong tkinter.
- `ttk` — themed widgets (nut bam, nhan dep hon tkinter thong thuong).

### Ham `configure`

```python
def configure() -> None:
    family = "Helvetica"
```
- Chon font Helvetica cho toan app.

```python
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=11, family=family)
```
- `nametofont("TkDefaultFont")` lay doi tuong font mac dinh cua tkinter.
- Thay doi kich thuoc va font family. Tat ca widget se tu dong cap nhat.

```python
    text_font = tkfont.nametofont("TkTextFont")
    text_font.configure(size=11, family=family)
```
- Font cho cac Text widget (ScrolledText).

```python
    fixed_font = tkfont.nametofont("TkFixedFont")
    fixed_font.configure(size=10, family=family)
```
- Font co dinh (monospace) — dung cho code hoac dang bang.

```python
    heading_font = tkfont.nametofont("TkHeadingFont")
    heading_font.configure(size=11, family=family, weight="bold")
```
- Font cho tieu de — in dam.

### Ham `apply_theme`

```python
def apply_theme(root) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
```
- Ap dung theme "clam" — giao dien hien dai hon theme mac dinh.
- `try/except` phong truong hop theme khong co san tren may.

```python
    style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
```
- Tao style "Title.TLabel" — nhan tieu de, font 14px in dam.

```python
    style.configure("Section.TLabelframe.Label", font=("Helvetica", 11, "bold"))
```
- Style cho tieu de cua LabelFrame (khung nhom widgets).

```python
    style.configure("Status.TLabel", font=("Helvetica", 10))
```
- Style cho dong trang thai phia duoi cua so.

```python
    style.configure("TButton", padding=(8, 5))
    style.configure("TEntry", padding=(4, 3))
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
```
- Tuy chinh padding cho nut bam, o nhap, va tieu de bang.

---

## 6. src/track_player.py — Menu Chinh

```python
import tkinter as tk
from tkinter import ttk
```
- `tk` — thu vien GUI tkinter. `ttk` — themed widgets.

```python
from . import font_manager as fonts
from .add_remove_tracks import AddRemoveTracks
from .create_track_list import CreateTrackList
from .track_statistics import TrackStatistics
from .update_tracks import UpdateTracks
from .view_tracks import TrackViewer
```
- Import tat ca module GUI. Moi module chua 1 class cho 1 cua so chuc nang.

### Ham `main`

```python
def main():
    window = tk.Tk()
```
- Tao cua so chinh (root window). Chi co 1 `Tk()` trong toan app.

```python
    window.geometry("700x260")
```
- Dat kich thuoc cua so: rong 700px, cao 260px.

```python
    window.title("JukeBox")
```
- Tieu de hien tren thanh title bar.

```python
    window.resizable(False, False)
```
- Khong cho phep thay doi kich thuoc (ca chieu ngang lan doc).

```python
    fonts.configure()
    fonts.apply_theme(window)
```
- Thiet lap font va theme cho toan app.

#### Cac ham callback

```python
    def view_tracks_clicked():
        status_lbl.configure(text="Opening View Tracks window.")
        TrackViewer(tk.Toplevel(window))
```
- Ham duoc goi khi bam nut "View Tracks".
- `tk.Toplevel(window)` tao cua so con moi (khong dong cua so chinh).
- `TrackViewer(...)` khoi tao giao dien duyet track trong cua so con.
- Cac ham `create_track_list_clicked`, `update_tracks_clicked`, ... hoat dong tuong tu.

#### Tao cac widget

```python
    header_lbl = ttk.Label(window, text="...", style="Title.TLabel")
    header_lbl.grid(row=0, column=0, columnspan=3, padx=12, pady=(18, 12))
```
- Tao nhan tieu de, dung style "Title.TLabel" (font 14px bold).
- `.grid()` dat widget vao luoi: hang 0, cot 0, trai dai 3 cot.
- `padx=12` — khoang cach ngang 12px. `pady=(18, 12)` — tren 18px, duoi 12px.

```python
    view_tracks_btn = ttk.Button(window, text="View Tracks", command=view_tracks_clicked)
    view_tracks_btn.grid(row=1, column=0, padx=12, pady=10, sticky="ew")
```
- Tao nut bam. `command=view_tracks_clicked` — goi ham khi bam.
- `sticky="ew"` — keo gian nut theo chieu ngang (east-west) de cac nut cung kich thuoc.

```python
    close_btn = ttk.Button(window, text="Close", command=window.destroy)
```
- Nut dong — `window.destroy` ket thuc toan bo app.

```python
    status_lbl = ttk.Label(window, text="Ready.", style="Status.TLabel")
    status_lbl.grid(row=3, column=0, columnspan=3, padx=12, pady=(8, 12), sticky="w")
```
- Dong trang thai phia duoi. `sticky="w"` — can trai (west).

```python
    for column in range(3):
        window.columnconfigure(column, weight=1)
```
- Cho phep 3 cot gian deu khi thay doi kich thuoc (du da tat resizable o tren).

```python
    window.mainloop()
```
- Bat dau vong lap su kien cua tkinter — chua so mo, lang nghe click, ghi phim, ...
- Dong nay CHAY MAI cho den khi cua so bi dong.

---

## 7. src/view_tracks.py — Duyet va Tim kiem

### Ham `set_text`

```python
def set_text(text_area, content):
    text_area.configure(state="normal")
    text_area.delete("1.0", tk.END)
    text_area.insert("1.0", content)
    text_area.configure(state="disabled")
```
- Widget ScrolledText duoc khoa ("disabled") de nguoi dung khong go vao.
- De cap nhat noi dung: mo khoa → xoa het → chen moi → khoa lai.
- `"1.0"` la vi tri dong 1, ky tu 0 (cach tkinter danh so).
- `tk.END` la cuoi van ban.

### Class TrackViewer

#### Constructor `__init__`

```python
    def __init__(self, window):
        self.window = window
        window.geometry("1040x560")
        window.title("View Tracks")
        fonts.apply_theme(window)
```
- Luu reference den cua so. Dat kich thuoc va tieu de.

```python
        window.columnconfigure(0, weight=1)
        window.columnconfigure(1, weight=1)
```
- 2 cot gian deu — cot trai (danh sach) va cot phai (chi tiet).

```python
        control_frame = ttk.LabelFrame(window, text="Controls", style="Section.TLabelframe")
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=6)
```
- LabelFrame — khung co tieu de "Controls", nhom cac widget dieu khien.

```python
        self.input_txt = ttk.Entry(control_frame, width=8)
```
- O nhap so track. `width=8` — rong 8 ky tu.
- `self.` de truy cap o phuong thuc khac (doc gia tri khi bam nut).

```python
        self.list_txt = tkst.ScrolledText(library_frame, width=56, height=18, wrap="none")
```
- Vung van ban co thanh cuon. `wrap="none"` — khong tu dong xuong dong.

```python
        self.list_tracks_clicked()
        set_text(self.track_txt, "Choose a track number and click 'View Track Details'.")
```
- Khi mo cua so: hien thi danh sach track va huong dan su dung.

#### Method `view_track_clicked`

```python
    def view_track_clicked(self):
        track_key = normalise_track_number(self.input_txt.get())
```
- `.get()` lay noi dung nguoi dung da go.
- `normalise_track_number` chuan hoa: "3" → "03", "abc" → None.

```python
        if track_key is None:
            set_text(self.track_txt, "Please enter digits only for the track number.")
            self.status_lbl.configure(text="Track number must contain digits only.")
            return
```
- Input khong hop le → bao loi va dung lai (`return`).

```python
        track_details = lib.get_details(track_key)
        if track_details is None:
            set_text(self.track_txt, f"Track {track_key} was not found.")
            self.status_lbl.configure(text="That track number does not exist.")
            return
```
- Track khong ton tai → bao loi.

```python
        set_text(self.track_txt, track_details)
        self.status_lbl.configure(text=f"Showing details for track {track_key}.")
```
- Thanh cong → hien thi chi tiet track va cap nhat dong trang thai.

#### Method `search_tracks_clicked`

```python
    def search_tracks_clicked(self):
        keyword = self.search_txt.get().strip()
        results = lib.search_tracks(keyword)
```
- Lay tu khoa va goi ham tim kiem.

```python
        if results == "":
            set_text(self.list_txt, "No matching tracks were found.")
        else:
            set_text(self.list_txt, results)
```
- Khong co ket qua → hien thong bao. Co ket qua → hien danh sach.

---

## 8. src/add_remove_tracks.py — Them / Xoa Track

### Class AddRemoveTracks

#### Constructor

- Tao 3 khung: "Add New Track" (form nhap), "Delete Track" (nhap so track), "Current Library" (danh sach).
- Cau truc tuong tu TrackViewer — dung grid layout, LabelFrame, Entry, Button.

#### Method `add_track_clicked`

```python
    def add_track_clicked(self):
        name = self.name_input.get().strip()
        artist = self.artist_input.get().strip()
        rating_text = self.rating_input.get().strip()
```
- Doc 3 o nhap: ten, nghe si, rating.

```python
        if name == "" or artist == "":
            self.status_lbl.configure(text="Name and artist cannot be empty.")
            return
```
- Ten va nghe si bat buoc.

```python
        rating = get_valid_rating(rating_text, allow_zero=True)
        if rating is None:
            self.status_lbl.configure(text="Rating must be a whole number from 0 to 5.")
            return
```
- Kiem tra rating hop le (0-5). `allow_zero=True` vi track moi co the chua co rating.

```python
        key = lib.add_track(name, artist, rating)
        self.refresh_list()
        self.status_lbl.configure(text=f"Added track {key}: '{name}' by {artist}.")
```
- Them track → lam moi danh sach → hien thong bao thanh cong.

```python
        self.name_input.delete(0, tk.END)
        self.artist_input.delete(0, tk.END)
        self.rating_input.delete(0, tk.END)
```
- Xoa noi dung 3 o nhap sau khi them thanh cong (san sang cho lan nhap tiep).

#### Method `remove_track_clicked`

```python
        track_key = normalise_track_number(self.remove_input.get())
        if track_key is None:
            ...
            return

        track_name = lib.get_name(track_key)
        if track_name is None:
            ...
            return

        lib.delete_track(track_key)
        self.refresh_list()
```
- Chuan hoa so track → kiem tra ton tai → xoa → lam moi danh sach.

---

## 9. src/update_tracks.py — Chinh sua Track

### Class UpdateTracks

#### Method `_clear_edit_fields`

```python
    def _clear_edit_fields(self):
        self.name_input.delete(0, tk.END)
        self.artist_input.delete(0, tk.END)
        self.rating_input.delete(0, tk.END)
        self.album_input.delete(0, tk.END)
        self.year_input.delete(0, tk.END)
```
- Ham noi bo — xoa tat ca 5 o nhap. Goi truoc khi load track moi.

#### Method `_parse_optional_year`

```python
    def _parse_optional_year(self):
        year_text = self.year_input.get().strip()
        if year_text == "":
            return None, None
```
- Neu o nam rong → `(None, None)` — khong co nam, khong co loi.

```python
        if not year_text.isdigit():
            return None, "Year must be a whole number or left blank."
        return int(year_text), None
```
- Khong phai so → tra ve thong bao loi.
- Hop le → tra ve `(so_nam, None)`.
- Ham tra ve 2 gia tri (tuple) — gia tri va loi. Day la pattern "value, error" thuong gap trong Python.

#### Method `load_track_clicked`

```python
        item = lib.get_item(track_key)
        ...
        self._clear_edit_fields()
        self.name_input.insert(0, item.name)
        self.artist_input.insert(0, item.artist)
        self.rating_input.insert(0, str(item.rating))
```
- Xoa o nhap → dien thong tin track hien tai vao.
- `str(item.rating)` vi Entry chi chap nhan chuoi.

```python
        if isinstance(item, AlbumTrack):
            self.album_input.insert(0, item.album)
            if item.year is not None:
                self.year_input.insert(0, str(item.year))
```
- `isinstance()` kiem tra doi tuong co phai AlbumTrack khong.
- Chi dien album va year neu track la AlbumTrack.

#### Method `update_track_clicked`

```python
        year, year_error = self._parse_optional_year()
        if year_error is not None:
            ...
            return
```
- Giai nen tuple: `year` la gia tri, `year_error` la thong bao loi.

```python
        success = lib.update_track_info(
            track_key, name, artist, rating,
            album=album, year=year,
        )
```
- Goi ham cap nhat trong track_library.
- `album=album` — truyen theo ten tham so (keyword argument) de ro rang.

---

## 10. src/create_track_list.py — Playlist Builder

### Constants

```python
PROJECT_DIR = Path(__file__).resolve().parent.parent
PLAYLIST_DIR = PROJECT_DIR / "playlists"
PLAYLIST_DIR.mkdir(exist_ok=True)
```
- `PLAYLIST_DIR` la thu muc luu playlist.
- `.mkdir(exist_ok=True)` tao thu muc neu chua co, khong bao loi neu da co.

### Class CreateTrackList

#### `self.playlist = []`
- Danh sach cac key track trong playlist hien tai (luu trong RAM).
- Vi du: `["01", "03", "02"]` — 3 bai hat theo thu tu.

#### Method `refresh_playlist_text`

```python
    def refresh_playlist_text(self):
        if len(self.playlist) == 0:
            set_text(self.playlist_txt, "")
            return
        output_lines = []
        for number, track_key in enumerate(self.playlist, start=1):
            track_name = lib.get_name(track_key)
            output_lines.append(f"{number}. {track_key} {track_name}")
        set_text(self.playlist_txt, "\n".join(output_lines))
```
- `enumerate(self.playlist, start=1)` — lap qua danh sach va dem tu 1.
- Hien thi: "1. 01 What a Wonderful World\n2. 03 Count on Me\n...".

#### Method `add_track_clicked`

```python
        self.playlist.append(track_key)
```
- Them key vao cuoi danh sach playlist.

#### Method `remove_track_clicked`

```python
        position = get_valid_position(self.remove_input.get(), len(self.playlist))
```
- `len(self.playlist)` la so track hien co — gioi han vi tri hop le.

```python
        removed_key = self.playlist.pop(position - 1)
```
- `.pop(index)` xoa va tra ve phan tu tai vi tri do.
- `position - 1` vi nguoi dung nhap tu 1, nhung list danh so tu 0.

#### Method `move_up_clicked`

```python
        index = position - 1
        self.playlist[index - 1], self.playlist[index] = self.playlist[index], self.playlist[index - 1]
```
- Hoan doi 2 phan tu ke nhau. Day la cu phap swap cua Python.
- Vi du: vi tri 3 chuyen len vi tri 2 → doi cho phan tu tai index 1 va 2.

#### Method `play_playlist_clicked`

```python
        for track_key in self.playlist:
            lib.increment_play_count(track_key, auto_save=False)
        lib.save_library()
```
- Tang luot nghe cho TUNG track trong playlist.
- `auto_save=False` — khong luu file sau moi track (tiet kiem I/O).
- `save_library()` cuoi cung — luu 1 lan duy nhat sau khi cap nhat tat ca.

#### Method `_get_playlist_path`

```python
    def _get_playlist_path(self):
        playlist_name = normalise_playlist_name(self.playlist_name_input.get())
        if playlist_name is None:
            return None
        return PLAYLIST_DIR / f"{playlist_name}.txt"
```
- Chuyen ten playlist thanh duong dan file: "my_playlist" → "playlists/my_playlist.txt".

#### Method `save_playlist_clicked`

```python
        path.write_text("\n".join(self.playlist), encoding="utf-8")
```
- Ghi danh sach key ra file, moi key 1 dong: "01\n03\n02".

#### Method `load_playlist_clicked`

```python
        loaded_playlist = []
        for track_key in path.read_text(encoding="utf-8").splitlines():
            if lib.get_name(track_key) is not None:
                loaded_playlist.append(track_key)
```
- Doc file → tach tung dong → kiem tra track con ton tai → them vao playlist.
- Bo qua key khong con ton tai trong thu vien (phong track da bi xoa).

#### Method `rename_playlist_clicked`

```python
        new_name_text = simpledialog.askstring(
            "Rename Playlist",
            "Enter the new playlist name:",
            parent=self.window,
        )
```
- Mo hop thoai nhap ten moi. Tra ve None neu nguoi dung bam Cancel.

```python
        old_path.rename(new_path)
```
- Doi ten file. Day la thao tac cua `pathlib.Path`.

#### Method `list_playlists_clicked`

```python
        playlist_files = sorted(path.name for path in PLAYLIST_DIR.glob("*.txt"))
```
- `.glob("*.txt")` tim tat ca file .txt trong thu muc playlists.
- `path.name` lay ten file (khong co duong dan).
- `sorted()` sap xep theo alphabet.

#### Method `delete_playlist_clicked`

```python
        path.unlink()
```
- `.unlink()` xoa file. Tuong tu `os.remove()` nhung dung cho Path object.

---

## 11. src/track_statistics.py — Thong ke

### Class TrackStatistics

#### Constructor

```python
        self.stats_txt = tkst.ScrolledText(window, width=82, height=30, wrap="word")
```
- `wrap="word"` — tu dong xuong dong tai ranh gioi tu (khong cat giua tu).

#### Method `refresh`

```python
    def refresh(self):
        stats = lib.get_statistics()
        output = self.generate_statistics_text(stats)
        set_text(self.stats_txt, output)
```
- Lay du lieu thong ke → tao chuoi hien thi → cap nhat vung van ban.

#### Method `generate_statistics_text`

```python
        output.append("=" * 56)
        output.append("J U K E B O X   S T A T I S T I C S")
        output.append("=" * 56)
```
- Tao tieu de dep voi duong ke.

```python
        output.append(f"Average rating: {stats['average_rating']:.1f} / 5")
```
- `:.1f` dinh dang so thap phan 1 chu so (3.666... → "3.7").

```python
        for track in sorted(stats["tracks"], key=lambda item: (-item["play_count"], item["key"])):
```
- Sap xep theo luot nghe giam dan (`-item["play_count"]`).
- Neu bang nhau, sap xep theo key tang dan.

```python
            bar = "#" * track["play_count"]
            output.append(f"{track['key']} {track['name'][:24]:24} | {bar} ({track['play_count']})")
```
- Tao bieu do ngang bang ky tu `#`.
- `track['name'][:24]` cat ten con 24 ky tu.
- `:24` can trai 24 ky tu (them khoang trang neu ngan hon) — de cac dong thang cot.

```python
        for track in stats["tracks"]:
            output.append(f"- {track['key']} {track['name']} -> {track['type']}")
```
- Liet ke loai cua moi track (LibraryItem hay AlbumTrack).

---

## 12. tests/test_library_item.py — Test Data Models

```python
from src.library_item import AlbumTrack, LibraryItem
```
- Import tu package `src` (khong dung relative import vi tests/ la package rieng).

### Cac ham test

```python
def test_library_item_stores_name_artist_and_default_values():
    item = LibraryItem("Song A", "Artist A")
    assert item.name == "Song A"
    assert item.artist == "Artist A"
    assert item.rating == 0
    assert item.play_count == 0
```
- Tao 1 LibraryItem va kiem tra cac gia tri mac dinh.
- `assert` — neu dieu kien sai, test FAIL.
- Khong truyen rating va play_count → phai la 0.

```python
def test_stars_returns_the_correct_number_of_stars():
    item = LibraryItem("Song B", "Artist B", 4)
    assert item.stars() == "****"
```
- Rating 4 → phai tra ve 4 dau sao.

```python
def test_stars_returns_an_empty_string_when_rating_is_zero():
    item = LibraryItem("Song C", "Artist C", 0)
    assert item.stars() == ""
```
- Rating 0 → chuoi rong (khong co sao).

```python
def test_info_returns_name_artist_and_stars():
    item = LibraryItem("Song D", "Artist D", 3)
    assert item.info() == "Song D - Artist D ***"
```
- Kiem tra dinh dang chuoi tom tat.

```python
def test_increment_play_count_increases_value():
    item = LibraryItem("Song E", "Artist E", 2)
    item.increment_play_count()
    assert item.play_count == 1
```
- Ban dau play_count = 0. Goi increment 1 lan → phai la 1.

```python
def test_album_track_inherits_and_adds_extra_details():
    item = AlbumTrack("Song F", "Artist F", 5, 2, "Album F", 2023)
    details = item.details("06")
    assert "Track number: 06" in details
    assert "Album: Album F" in details
    assert "Year: 2023" in details
```
- AlbumTrack phai co ca thong tin co ban (Track number) va thong tin album.
- `in` kiem tra chuoi con nam trong chuoi lon.

---

## 13. tests/test_track_library.py — Test Core Logic

### Setup va Teardown

```python
def setup_module(module):
    module.original_data_file = lib.DATA_FILE
    lib.DATA_FILE = Path("test_library_data.json")
    lib.reset_library_to_default(save=False)
```
- `setup_module` chay 1 lan truoc tat ca test trong file.
- Luu duong dan file goc, doi sang file test (tranh ghi de du lieu that).
- Reset thu vien ve mac dinh.

```python
def teardown_module(module):
    if lib.DATA_FILE.exists():
        lib.DATA_FILE.unlink()
    lib.DATA_FILE = module.original_data_file
    lib.reset_library_to_default(save=False)
```
- `teardown_module` chay 1 lan SAU tat ca test.
- Xoa file test JSON, tra lai duong dan file goc.
- Don dep — dam bao test khong de lai rac.

```python
def setup_function(function):
    lib.reset_library_to_default(save=False)
```
- Chay TRUOC MOI ham test — reset thu vien ve mac dinh.
- Dam bao moi test doc lap, khong bi anh huong boi test truoc do.

### Cac ham test

```python
def test_list_all_returns_all_tracks():
    output = lib.list_all()
    assert "What a Wonderful World" in output
    assert "Here Comes the Sun" in output
    assert "Count on Me" in output
```
- Thu vien mac dinh co 5 track — kiem tra 3 trong so do co mat.

```python
def test_get_name_non_existing_track():
    assert lib.get_name("99") is None
```
- Track 99 khong ton tai → phai tra ve None.

```python
def test_set_rating_changes_rating():
    assert lib.set_rating("03", 4, auto_save=False) is True
    assert lib.get_rating("03") == 4
```
- Dat rating 4 cho track 03 → kiem tra da thay doi.
- `auto_save=False` de khong ghi file (test chi kiem tra logic).

```python
def test_search_tracks_by_album_for_subclass():
    results = lib.search_tracks("abbey road")
    assert "Here Comes the Sun" in results
```
- Tim theo ten album — AlbumTrack phai khop vi override `matches()`.

```python
def test_save_and_load_library_preserve_changes():
    lib.set_rating("01", 4, auto_save=False)
    lib.increment_play_count("01", auto_save=False)
    lib.save_library()
    lib.reset_library_to_default(save=False)
    lib.load_library()
    assert lib.get_rating("01") == 4
    assert lib.get_play_count("01") == 1
```
- Test quan trong nhat — kiem tra du lieu con nguyen sau khi luu va doc lai.
- Thay doi → luu → reset bo nho → doc lai tu file → kiem tra gia tri.

---

## 14. tests/test_validation.py — Test Validation

```python
from src.validation import (
    get_valid_position,
    get_valid_rating,
    normalise_playlist_name,
    normalise_track_number,
)
```
- Import tat ca 4 ham validation de test.

### Test normalise_track_number

```python
def test_normalise_single_digit():
    assert normalise_track_number("3") == "03"
```
- 1 chu so → them 0 phia truoc.

```python
def test_normalise_double_digit():
    assert normalise_track_number("12") == "12"
```
- 2 chu so → giu nguyen.

```python
def test_normalise_with_spaces():
    assert normalise_track_number("  5  ") == "05"
```
- Khoang trang bi xoa truoc khi xu ly.

```python
def test_normalise_empty_string():
    assert normalise_track_number("") is None
```
- Chuoi rong → None (khong hop le).

```python
def test_normalise_non_numeric():
    assert normalise_track_number("abc") is None
```
- Khong phai so → None.

### Test get_valid_rating

```python
def test_valid_rating_5():
    assert get_valid_rating("5") == 5
```
- Rating 5 hop le.

```python
def test_invalid_rating_0_without_allow_zero():
    assert get_valid_rating("0") is None
```
- Mac dinh khong cho phep rating 0 (khi cap nhat track).

```python
def test_valid_rating_0_with_allow_zero():
    assert get_valid_rating("0", allow_zero=True) == 0
```
- Khi them track moi, cho phep rating 0.

```python
def test_invalid_rating_text():
    assert get_valid_rating("abc") is None
```
- Chu cai → None.

### Test get_valid_position

```python
def test_valid_position_inside_range():
    assert get_valid_position("2", 3) == 2
```
- Vi tri 2 trong playlist co 3 track → hop le.

```python
def test_invalid_position_outside_range():
    assert get_valid_position("4", 3) is None
```
- Vi tri 4 nhung chi co 3 track → None.

### Test normalise_playlist_name

```python
def test_playlist_name_is_cleaned():
    assert normalise_playlist_name("  my:/playlist  ") == "myplaylist"
```
- Khoang trang bi xoa, ky tu dac biet `:` va `/` bi loai bo.
