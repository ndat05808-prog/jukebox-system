# JukeBox System

A desktop music library manager built with Python and Tkinter.

## Features

- **View Tracks** — Browse and search tracks by number, name, artist, or album
- **Add / Remove Tracks** — Add new tracks or delete existing ones
- **Update Tracks** — Edit track info (name, artist, rating, album, year)
- **Create Playlists** — Build, reorder, save, and load playlists
- **Statistics** — View total tracks, play counts, average ratings, and top tracks

## Requirements

- Python 3.10+
- Tkinter (included with standard Python installation)
- pytest (for running tests)

## Usage

```bash
python3 main.py
```

## Running Tests

```bash
python3 -m pytest tests/ -v
```

---

## Project Structure — Chi tiet

```
jukebox-system/
├── .gitignore                # Cau hinh Git — bo qua file rac
├── main.py                   # Diem khoi chay duy nhat
├── README.md                 # Tai lieu du an
│
├── data/                     # Du lieu
│   └── library_data.json
│
├── src/                      # Ma nguon chinh
│   ├── __init__.py
│   ├── library_item.py       # Data models
│   ├── track_library.py      # Core logic — quan ly thu vien
│   ├── validation.py         # Kiem tra input nguoi dung
│   ├── font_manager.py       # Cau hinh font va theme
│   ├── track_player.py       # Cua so menu chinh
│   ├── view_tracks.py        # Duyet va tim kiem bai hat
│   ├── add_remove_tracks.py  # Them / xoa bai hat
│   ├── update_tracks.py      # Chinh sua thong tin bai hat
│   ├── create_track_list.py  # Tao va quan ly playlist
│   └── track_statistics.py   # Hien thi thong ke
│
└── tests/                    # Kiem thu
    ├── __init__.py
    ├── test_library_item.py
    ├── test_track_library.py
    └── test_validation.py
```

---

## Giai thich tung folder

### `.gitignore` — Bo loc Git

File nay bao Git **bo qua** nhung file khong can thiet, tranh commit rac vao repository.

| Loai              | Vi du                          | Tai sao bo qua?                                    |
| ----------------- | ------------------------------ | -------------------------------------------------- |
| Bytecode Python   | `__pycache__/`, `*.pyc`        | Tu sinh khi chay, moi may khac nhau                |
| IDE config        | `.idea/`, `*.iml`, `*.xml`     | Cai dat ca nhan, khong lien quan den code           |
| OS files          | `.DS_Store`                    | macOS tu tao, khong co y nghia                      |
| Test artifacts    | `test_library_data.json`       | File tam khi chay test                              |
| Runtime data      | `playlists/`                   | Nguoi dung tu tao khi dung app                      |

### `main.py` — Diem khoi chay duy nhat

```python
from src.track_player import main

if __name__ == "__main__":
    main()
```

Khi dung relative imports (`from .module import ...`) trong package `src/`, khong the chay truc tiep
`python3 src/track_player.py`. File `main.py` nam o goc project de giai quyet van de do.
Chi can chay: `python3 main.py`

### `data/` — Thu muc du lieu

```
data/
└── library_data.json
```

Chua toan bo thu vien nhac duoi dang JSON. Moi track luu: ten, nghe si, rating, luot nghe,
loai (LibraryItem hoac AlbumTrack), va thong tin album/nam (neu co).

**Tai sao tach rieng?** Tach **du lieu** khoi **ma nguon**. Khi code thay doi, data khong bi anh huong
va nguoc lai. De backup, de tim.

### `src/` — Ma nguon chinh

Day la Python package (co file `__init__.py`). Tat ca file source deu nam trong day,
su dung relative imports de tham chieu lan nhau.

---

## Giai thich tung file trong `src/`

### `library_item.py` — Data Models

Dinh nghia 2 class chinh:

- **`LibraryItem`**: Class co ban — chua `name`, `artist`, `rating`, `play_count`.
  Cac method: `stars()` (tra ve sao), `info()` (tom tat), `details()` (chi tiet day du),
  `matches()` (tim kiem), `to_dict()` / `from_dict()` (chuyen doi JSON).

- **`AlbumTrack`** (ke thua `LibraryItem`): Them `album` va `year`.
  Override `details()` va `matches()` de bao gom thong tin album.

**Tai sao can?** Day la **nen tang du lieu** cua ca app. Moi file khac deu dung 2 class nay
de tao, doc, va hien thi thong tin bai hat.

### `track_library.py` — Core Logic

Bo nao cua ung dung — quan ly dict chua tat ca track trong bo nho.

Chuc nang chinh:
- `load_library()` / `save_library()` — Doc/ghi file `data/library_data.json`
- `add_track()` / `delete_track()` — Them/xoa track
- `search_tracks()` — Tim kiem theo tu khoa (ten, nghe si, album)
- `get_name()`, `get_artist()`, `get_rating()`, `get_play_count()` — Truy xuat thong tin
- `set_rating()`, `update_track_info()` — Cap nhat thong tin
- `increment_play_count()` — Tang luot nghe
- `get_statistics()` — Tra ve thong ke toan bo thu vien
- `list_all()` / `all_keys()` — Liet ke toan bo track

**Tai sao can?** Tach logic xu ly du lieu ra khoi giao dien. Cac file GUI chi goi ham tu day,
khong truc tiep doc/ghi JSON. Giup de test va de bao tri.

### `validation.py` — Kiem tra Input

Cac ham loc va chuan hoa du lieu nguoi dung nhap:

- `normalise_track_number(text)` — Chuyen "3" thanh "03", loai bo khoang trang, tra ve None neu khong hop le
- `get_valid_rating(text, allow_zero)` — Kiem tra rating tu 1-5 (hoac 0-5), tra ve None neu sai
- `get_valid_position(text, max_pos)` — Kiem tra vi tri trong playlist (1 den max)
- `normalise_playlist_name(text)` — Lam sach ten playlist (loai ky tu dac biet)

**Tai sao can?** Nguoi dung co the nhap bat ky thu gi. Validation ngan loi truoc khi du lieu
vao he thong. Tach rieng de tai su dung o nhieu file GUI khac nhau.

### `font_manager.py` — Cau hinh Font va Theme

- `configure()` — Thiet lap font mac dinh cho tkinter
- `apply_theme(window)` — Ap dung theme "clam" voi cac style tuy chinh (Title, Status, Section...)

**Tai sao can?** Thay vi copy-paste code font o moi cua so, goi 1 lan la dong bo toan app.

### `track_player.py` — Cua so Menu Chinh

Ham `main()` tao cua so Tk chinh voi 5 nut bam:
1. **View Tracks** → mo `TrackViewer`
2. **Create Track List** → mo `CreateTrackList`
3. **Update Tracks** → mo `UpdateTracks`
4. **Add / Remove Tracks** → mo `AddRemoveTracks`
5. **Statistics** → mo `TrackStatistics`

Moi nut mo mot cua so `Toplevel` moi. Day la diem dieu huong trung tam cua app.

### `view_tracks.py` — Duyet va Tim kiem

Class `TrackViewer` cung cap:
- Liet ke toan bo track trong thu vien
- Tim kiem theo so track cu the
- Tim kiem theo tu khoa (ten, nghe si, album)
- Hien thi chi tiet khi chon track
- Tang luot nghe khi bam "Play"

### `add_remove_tracks.py` — Them / Xoa Track

Class `AddRemoveTracks` cung cap:
- Form nhap: ten, nghe si, rating → them track moi vao thu vien
- Nhap so track → xoa track khoi thu vien
- Hien thi danh sach track hien tai

### `update_tracks.py` — Chinh sua Track

Class `UpdateTracks` cung cap:
- Nhap so track de load thong tin hien tai
- Chinh sua: ten, nghe si, rating, album, nam
- Chuyen doi giua LibraryItem va AlbumTrack khi them/xoa thong tin album

### `create_track_list.py` — Playlist Builder

Class `CreateTrackList` cung cap:
- Them track vao playlist theo so
- Xoa track khoi playlist theo vi tri
- Sap xep lai (Move Up / Move Down)
- Play playlist (tang luot nghe cho tat ca track)
- Luu playlist thanh file `.txt` trong thu muc `playlists/`
- Load playlist tu file
- Doi ten / Xoa playlist da luu

### `track_statistics.py` — Hien thi Thong ke

Class `TrackStatistics` hien thi:
- Tong so track trong thu vien
- Tong luot nghe
- Rating trung binh
- Track duoc nghe nhieu nhat
- Track co rating cao nhat
- Phan loai theo type (LibraryItem vs AlbumTrack)

---

## Giai thich folder `tests/`

```
tests/
├── __init__.py              # Danh dau la Python package
├── test_library_item.py     # Test class LibraryItem va AlbumTrack
├── test_track_library.py    # Test CRUD, search, save/load
└── test_validation.py       # Test cac ham validation
```

### `test_library_item.py`

Test cac class data model:
- Tao LibraryItem va kiem tra name, artist, rating, play_count mac dinh
- Kiem tra `stars()` tra ve dung so sao
- Kiem tra `info()` tra ve chuoi tom tat dung dinh dang
- Kiem tra `increment_play_count()` tang gia tri
- Kiem tra AlbumTrack ke thua dung va co them album/year

### `test_track_library.py`

Test logic quan ly thu vien:
- `list_all()` tra ve tat ca track
- `get_name()`, `get_artist()`, `get_rating()` tra ve dung gia tri
- `set_rating()` thay doi rating
- `increment_play_count()` tang luot nghe
- `search_tracks()` tim dung theo artist va album
- `add_track()` tao key moi
- `delete_track()` xoa track
- `save_library()` / `load_library()` giu nguyen du lieu sau khi luu va doc lai

### `test_validation.py`

Test cac ham kiem tra input:
- `normalise_track_number()`: "3" → "03", "  5 " → "05", "" → None, "abc" → None
- `get_valid_rating()`: 5 → 5, 0 (khong cho phep) → None, 0 (cho phep) → 0, "x" → None
- `get_valid_position()`: trong pham vi → hop le, ngoai pham vi → None
- `normalise_playlist_name()`: lam sach ten, loai ky tu dac biet

**Tai sao tach rieng?** Test khong phai code chay production. Tach ra de:
- Chay rieng: `python3 -m pytest tests/`
- Khong lan voi code chinh
- CI/CD de cau hinh

---

## Tai sao can cau truc nay?

| Nguyen tac                  | Giai thich                                                                 |
| --------------------------- | -------------------------------------------------------------------------- |
| **Separation of Concerns**  | Code (`src/`), test (`tests/`), data (`data/`) tach biet ro rang           |
| **Package structure**       | `src/` la Python package — import ro rang, khong xung dot ten module       |
| **Single entry point**      | `main.py` — ai cung biet chay app tu dau                                  |
| **Clean repository**        | `.gitignore` loai bo rac — repo chi chua code thuc su can thiet            |
| **Scalability**             | Them module moi? Bo vao `src/`. Them test? Bo vao `tests/`. Ro rang       |
| **Testability**             | Logic tach khoi GUI — de viet unit test ma khong can mo giao dien          |
| **Maintainability**         | Moi file co 1 nhiem vu — khi co loi, biet ngay can sua o dau              |
