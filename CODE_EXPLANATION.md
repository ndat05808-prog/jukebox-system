# Giải thích chi tiết source code — JukeBox System

Tài liệu này đi **từng dòng / từng khối code** trong toàn bộ thư mục `src/` và file
`main.py`, giải thích ý nghĩa, logic xử lý, và vai trò của từng đoạn trong bức
tranh tổng thể của ứng dụng JukeBox.

Mục tiêu: đọc xong có thể trả lời được "vì sao viết như vậy?" chứ không chỉ "nó
làm gì".

---

## Mục lục

1. [Kiến trúc tổng thể](#1-kiến-trúc-tổng-thể)
2. [main.py](#2-mainpy)
3. [src/validation.py](#3-srcvalidationpy)
4. [src/library_item.py](#4-srclibrary_itempy)
5. [src/track_library.py](#5-srctrack_librarypy)
6. [src/audio_manager.py](#6-srcaudio_managerpy)
7. [src/cover_manager.py](#7-srccover_managerpy)
8. [src/audio_player.py](#8-srcaudio_playerpy)
9. [src/font_manager.py](#9-srcfont_managerpy)
10. [src/gui_helpers.py](#10-srcgui_helperspy)
11. [src/auth_manager.py](#11-srcauth_managerpy)
12. [src/auth_ui.py](#12-srcauth_uipy)
13. [src/add_remove_tracks.py](#13-srcadd_remove_trackspy)
14. [src/update_tracks.py](#14-srcupdate_trackspy)
15. [src/update_lyrics.py](#15-srcupdate_lyricspy)
16. [src/view_tracks.py](#16-srcview_trackspy)
17. [src/create_track_list.py](#17-srccreate_track_listpy)
18. [src/track_statistics.py](#18-srctrack_statisticspy)
19. [src/track_player.py](#19-srctrack_playerpy)
20. [Các luồng logic tiêu biểu](#20-các-luồng-logic-tiêu-biểu)

---

## 1. Kiến trúc tổng thể

### 1.1 Mô hình phân lớp

```
┌──────────────────────────────────────────────────────┐
│  UI Layer (Tkinter + ttk)                            │
│  ─ auth_ui / track_player (JukeBoxApp + Pages)       │
│  ─ add_remove_tracks / update_tracks / update_lyrics │
│  ─ create_track_list / track_statistics / view_tracks│
├──────────────────────────────────────────────────────┤
│  UI Helpers: font_manager, gui_helpers               │
├──────────────────────────────────────────────────────┤
│  Domain / Business Logic                             │
│  ─ track_library (CRUD + JSON persistence)           │
│  ─ audio_manager, cover_manager (asset resolution)   │
│  ─ auth_manager (users + password hash)              │
│  ─ validation (input sanitisation)                   │
├──────────────────────────────────────────────────────┤
│  Data model: library_item (LibraryItem, AlbumTrack)  │
├──────────────────────────────────────────────────────┤
│  Playback engine: audio_player (pygame.mixer wrapper)│
├──────────────────────────────────────────────────────┤
│  Storage: data/*.json, playlists/*.json, assets/*/   │
└──────────────────────────────────────────────────────┘
```

### 1.2 Nguyên tắc thiết kế

- **Single source of truth**: `track_library.library` là dict toàn cục
  `{key: LibraryItem}`. Các UI chỉ gọi hàm public (`get_item`, `set_rating`, …)
  chứ không tự manipulate dict.
- **Persist-or-rollback**: mọi hàm ghi (`set_rating`, `delete_track`, …) đều
  snapshot giá trị cũ → mutate → `save_library()` → nếu save fail thì
  rollback in-memory. Bảo đảm JSON và in-memory luôn khớp.
- **App-wide broadcast**: khi có CRUD, UI gọi `app_ref.refresh_library()`
  → `_notify_pages_refresh()` → mọi page có `on_library_change()` được gọi.
  Tránh từng page phải "nghe" nhau trực tiếp.
- **Delegation qua `app_ref`**: các tool embedded (AddRemove, UpdateTracks…)
  nhận tham chiếu tới `JukeBoxApp` qua thuộc tính `app_ref` (set sau khi khởi tạo)
  để có thể gọi `refresh_library()`.
- **Lazy init**: `pygame.mixer` chỉ init lần đầu dùng (`_ensure_init`). Nếu
  thiếu audio device chỉ trả `False` — không crash.
- **Theme tập trung**: mọi màu sắc / font đi qua `font_manager`. Các style
  `"Root.TFrame"`, `"Card.TFrame"`, `"Neon.TButton"`, … được khai báo một lần
  và dùng xuyên suốt.

### 1.3 Thư mục dữ liệu

```
data/
  library_data.json     # toàn bộ track (key → record)
  history_data.json     # lịch sử phát
  users.json            # users + hash password + salt
playlists/
  <name>.json           # mỗi playlist 1 file
assets/
  covers/<key>.png|gif|ppm|pgm
  audio/<key>.mp3|wav|ogg|flac|m4a|aac
```

---

## 2. main.py

Điểm vào (entry point) duy nhất. Chạy bằng `python3 main.py`.

```python
from src.auth_ui import launch_auth_app

if __name__ == "__main__":
    launch_auth_app()
```

**Logic**: chỉ import và gọi `launch_auth_app()` — hàm này tạo `AuthApp`, chạy
`mainloop()`; khi đăng nhập OK, `AuthApp` tự mở `JukeBoxApp`. Khi logout,
`JukeBoxApp` gọi lại `launch_auth_app` (truyền qua tham số `on_logout`). Vòng
đời: **login screen → main app → (logout) → login screen → …**.

---

## 3. src/validation.py

Các hàm thuần (pure function) dùng để chuẩn hoá / kiểm tra input. Tách khỏi UI
để test dễ và tái dùng.

### `normalise_track_number(raw)`

```python
def normalise_track_number(raw):
    if raw is None: return None
    text = str(raw).strip()
    if not text.isdigit(): return None
    return f"{int(text):02d}"
```

- `strip()` bỏ whitespace người dùng gõ thừa.
- `isdigit()` đảm bảo chỉ chứa chữ số (nếu có "-" / "." / space → trả None).
- `f"{int(text):02d}"` chuyển `"3"` → `"03"`. Lý do: key trong library là chuỗi
  padding 2 chữ số, so sánh chuỗi phải giống hệt mới tra được.

### `get_valid_rating(text, allow_zero=False)`

```python
def get_valid_rating(text, allow_zero=False):
    try:
        value = int(str(text).strip())
    except (TypeError, ValueError):
        return None
    lower = 0 if allow_zero else 1
    if value < lower or value > 5: return None
    return value
```

- `try/except` vì `int("abc")` raise. Không cho rating lẻ thập phân.
- `allow_zero`: khi tạo track mới thì cho rating 0 (chưa chấm), nhưng khi
  filter / update thì bắt buộc ≥ 1.
- Trả `None` = invalid → UI hiện popup.

### `get_valid_position(text, maximum)`

Parse số vị trí trong playlist (1-based, ≤ maximum). Dùng cho move up/down.

### `normalise_playlist_name(raw)`

```python
name = raw.strip()
for ch in '<>:"/\\|?*':
    name = name.replace(ch, "")
return name[:60] or None
```

- Loại ký tự không hợp lệ trong tên file (Windows khó chịu nhất).
- Cắt 60 ký tự để file name không quá dài.
- Rỗng sau strip → `None`.

### `get_valid_year(text, minimum=1900, maximum=2100)`

Giống rating nhưng range năm. Trả `None` nếu không phải số hoặc ngoài range.

---

## 4. src/library_item.py

Data model đại diện một bài hát. Không biết gì về GUI hay JSON file — chỉ
lo state của bản thân.

### `class LibraryItem`

```python
def __init__(self, name, artist, rating=0, play_count=0,
             cover_path=None, lyrics=None, audio_path=None):
    self.name = (name or "").strip()
    self.artist = (artist or "").strip()
    self.rating = max(0, min(5, int(rating)))
    self.play_count = max(0, int(play_count))
    self.cover_path = cover_path or None
    self.lyrics = (lyrics or "").strip() or None
    self.audio_path = audio_path or None
```

- `(name or "").strip()` — pattern bảo vệ khỏi `None`.
- `max(0, min(5, …))` — clamp rating trong [0,5]; chặn người tạo dữ liệu xấu.
- Lyrics rỗng → `None` (chứ không `""`) để `to_dict` biết là "không có lyrics"
  và không ghi key thừa vào JSON.

#### `set_rating`, `set_play_count`, `increment_play_count`

Tất cả đều qua clamp/cast. `increment` đơn giản là `self.play_count += 1`.
Hàm tách riêng thay vì mutate trực tiếp từ ngoài để sau này dễ thêm logic
(ví dụ trigger event khi play ≥ 10).

#### `stars()` và `info()`

```python
def stars(self):
    filled = "★" * self.rating
    empty  = "☆" * (5 - self.rating)
    return filled + empty
```

Logic đơn giản, rating 3 → `★★★☆☆`. `info()` gộp `name`, `artist`, `stars`
thành 1 dòng ngắn gọn cho list.

#### `details(track_key=None)`

Trả về đoạn text nhiều dòng. Dùng cho view/statistics — hiện rating, plays,
rồi album/year ở subclass `AlbumTrack`.

#### `matches(keyword)`

```python
lowered = (keyword or "").strip().lower()
if not lowered: return True   # không filter → match tất
return lowered in self.name.lower() or lowered in self.artist.lower()
```

Case-insensitive. `AlbumTrack` override để include tên album.

#### `to_dict()` / `from_dict(data)`

Serialize/deserialize:

```python
def to_dict(self):
    data = {"type": "track", "name": self.name, "artist": self.artist,
            "rating": self.rating, "play_count": self.play_count}
    if self.cover_path: data["cover_path"] = self.cover_path
    if self.lyrics:     data["lyrics"] = self.lyrics
    if self.audio_path: data["audio_path"] = self.audio_path
    return data
```

- Field `"type"` để `track_library._make_item` biết khởi tạo class nào.
- Optional field (`cover_path`, …) chỉ ghi nếu có — JSON gọn, diff git sạch.

`from_dict`:

```python
@classmethod
def from_dict(cls, data):
    return cls(
        name=data.get("name", ""),
        artist=data.get("artist", ""),
        rating=data.get("rating", 0),
        play_count=data.get("play_count", 0),
        cover_path=data.get("cover_path"),
        lyrics=data.get("lyrics"),
        audio_path=data.get("audio_path"),
    )
```

Dùng `.get()` với default vì JSON có thể thiếu field (file cũ, version
trước). Không raise trong parser → app không chết nếu 1 record thiếu field.

### `class AlbumTrack(LibraryItem)`

Thêm 2 field `album` và `year`.

```python
def __init__(self, ..., album="", year=None):
    super().__init__(...)
    self.album = (album or "").strip()
    self.year  = year if isinstance(year, int) else None
```

- `isinstance(year, int)` thay vì `int(year)` vì `year` có thể là `None`
  (track không biết năm) — tránh `TypeError`.

`to_dict`: gắn thêm `"type": "album_track"` + album/year. `matches` mở rộng để
khớp cả album. `details` thêm dòng "Album" / "Year".

---

## 5. src/track_library.py

Module giữ state toàn cục `library: dict[str, LibraryItem]` + đọc/ghi 2 file
JSON (`library_data.json`, `history_data.json`).

### Constants và module state

```python
LIBRARY_FILE = DATA_DIR / "library_data.json"
HISTORY_FILE = DATA_DIR / "history_data.json"
library: dict[str, LibraryItem] = {}
```

Module-level dict là "singleton" — cả app dùng chung. Không cần DI.

### `_make_item(data)` — factory

```python
def _make_item(data):
    if not isinstance(data, dict): return None
    type_ = data.get("type", "track")
    try:
        if type_ == "album_track":
            return AlbumTrack.from_dict(data)
        return LibraryItem.from_dict(data)
    except Exception:
        return None
```

- Dispatch bằng field `"type"`. Mặc định fallback `LibraryItem` nếu thiếu.
- `except Exception` để 1 record hỏng không làm fail cả load.

### `reset_library_to_default(save=False)`

Nạp `DEFAULT_LIBRARY` (5 track seed). Dùng cho lần đầu hoặc khi file hỏng.
Nếu `save=True` thì cũng ghi xuống đĩa.

### `load_library()`

```python
def load_library():
    global library
    if not LIBRARY_FILE.exists():
        reset_library_to_default(save=True)
        return
    try:
        raw = json.loads(LIBRARY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        reset_library_to_default(save=True); return
    if not isinstance(raw, dict):
        reset_library_to_default(save=True); return
    new_library: dict[str, LibraryItem] = {}
    for key, data in raw.items():
        item = _make_item(data)
        if item is not None:
            new_library[str(key)] = item
    library = new_library
```

Logic phục hồi:
1. File không tồn tại → dùng default và ghi lại.
2. JSON sai cú pháp hoặc OSError → fallback default.
3. Root không phải dict → fallback.
4. Mỗi record hỏng → skip, không crash cả app.

### `save_library()`

```python
try:
    payload = {key: item.to_dict() for key, item in library.items()}
    LIBRARY_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    return True
except OSError:
    return False
```

- `ensure_ascii=False` để tiếng Việt không bị escape `\uXXXX`.
- `indent=2` giúp diff git dễ đọc.
- Trả `bool` để caller rollback khi fail.

### Rollback-on-save-fail pattern

Ví dụ `set_rating`:

```python
def set_rating(key, rating, auto_save=True):
    if key not in library: return False
    previous = library[key].rating
    library[key].set_rating(rating)
    if auto_save and not save_library():
        library[key].set_rating(previous)   # rollback!
        return False
    return True
```

Rất quan trọng: nếu `save_library` fail (disk full, permission), không được
để memory đã mutate khác với file. Rollback lại đúng giá trị cũ.

### `update_track_info(key, name, artist, rating, album, year)`

Phức tạp nhất trong module. Cho phép đổi metadata **và** chuyển giữa
`LibraryItem` ↔ `AlbumTrack`:

```python
has_album_info = bool(album) or (year is not None)
preserved = {  # giữ các field không nằm trong form
    "cover_path": old.cover_path,
    "lyrics":     old.lyrics,
    "audio_path": old.audio_path,
    "play_count": old.play_count,
}
if has_album_info:
    new_item = AlbumTrack(name, artist, rating, album=album, year=year,
                          **preserved)
else:
    new_item = LibraryItem(name, artist, rating, **preserved)
library[key] = new_item
```

Vì bài có thể từ standalone → album (user bổ sung album sau), hoặc ngược lại
(bỏ album). Tạo mới class khác rồi gán đè — an toàn hơn là mutate class.

### `get_next_key()`

```python
max_num = 0
for key in library:
    if key.isdigit():
        max_num = max(max_num, int(key))
return f"{max_num + 1:02d}"
```

Key mới = max numeric key + 1, padding 2 chữ số. Nếu thư viện rỗng → "01".

### `add_track`, `delete_track`

Cũng dùng pattern rollback. Khi delete:

```python
previous = library.pop(key)   # giữ lại để rollback
if not save_library():
    library[key] = previous
    return False
return True
```

### History

```python
def add_history_entry(track_key, source="playlist", name=None, artist=None,
                      action="play"):
    history = load_history()
    if name is None:    name   = get_name(track_key)
    if artist is None:  artist = get_artist(track_key)
    history.append({
        "timestamp": _now_text(),
        "track_key": track_key,
        "name": name, "artist": artist,
        "source": source, "action": action,
    })
    save_history(history)
```

- Auto-fill name/artist từ library nếu caller không truyền (tiện).
- `source` cho phân biệt play từ đâu: `"library"`, `"playlist"`, `"queue"`,
  `"dashboard"`, `"manage"` (khi update/clear lyrics), …

### `get_statistics()`

Tính tổng hợp cho StatisticsPage:

```python
total_tracks = len(library)
total_plays  = sum(item.play_count for item in library.values())
ratings = [item.rating for item in library.values() if item.rating > 0]
average_rating = sum(ratings) / len(ratings) if ratings else 0.0
most_played = max(library.items(), key=lambda kv: kv[1].play_count,
                  default=(None, None))
highest_rated = max(library.items(), key=lambda kv: kv[1].rating,
                    default=(None, None))
album_tracks    = sum(1 for i in library.values() if isinstance(i, AlbumTrack))
standard_tracks = total_tracks - album_tracks
```

- Dùng generator expression + `sum()` / `max()` — O(n), không build list thừa.
- `max(..., default=...)` an toàn khi library rỗng.

---

## 6. src/audio_manager.py

Resolver cho file audio. App **chỉ đọc** — không copy file vào project.

### Path handling

```python
PROJECT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR  = PROJECT_DIR / "assets"
AUDIO_DIR   = ASSETS_DIR / "audio"
SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac")
```

`parent.parent` vì file này ở `src/`, project root cao 1 cấp.

### `_resolve_stored_path(stored)`

```python
if stored is None: return None
p = Path(stored)
if not p.is_absolute():
    p = PROJECT_DIR / p
if p.is_file():
    return p
return None
```

Logic "relative path trong JSON → absolute path runtime": an toàn khi clone
project sang máy khác (path tuyệt đối của máy cũ sẽ vô nghĩa).

### `_relative_to_project(path)`

Ngược lại: absolute → relative (nếu nằm trong project) để ghi xuống JSON.

### `find_audio_path(track_key)`

```python
item = lib.get_item(track_key)
if item is not None:
    resolved = _resolve_stored_path(item.audio_path)
    if resolved is not None:
        return resolved
# fallback: tự tìm theo key
for ext in SUPPORTED_EXTENSIONS:
    candidate = AUDIO_DIR / f"{track_key}{ext}"
    if candidate.is_file():
        return candidate
return None
```

**2 cấp fallback**:
1. Path trong library (ưu tiên, vì user đã assign).
2. Convention `assets/audio/<key>.<ext>` — cho seed data.

### `assign_audio`, `remove_audio`

Wrapper mỏng gọi `lib.set_audio_path`. `assign_audio` kiểm tra extension hợp
lệ trước khi lưu.

### `backfill_audio_paths()`

```python
for key in lib.all_keys():
    if lib.get_item(key).audio_path: continue    # đã có
    for ext in SUPPORTED_EXTENSIONS:
        candidate = AUDIO_DIR / f"{key}{ext}"
        if candidate.is_file():
            lib.set_audio_path(key, _relative_to_project(candidate))
            break
```

Chạy lúc app khởi động. Nếu có file `assets/audio/03.mp3` nhưng track 03
trong JSON chưa có `audio_path` → tự gán. Tiện khi bạn bỏ file vào thư mục
bằng tay mà không dùng UI.

---

## 7. src/cover_manager.py

Gần như clone của `audio_manager` nhưng cho ảnh bìa.

Điểm khác:

### `load_cover_image(track_key, max_size=220)`

```python
path = _find_cover_path(track_key)
if path is None: return None
image = tk.PhotoImage(file=str(path))
w, h = image.width(), image.height()
scale = max(w // max_size, h // max_size, 1)
if scale > 1:
    image = image.subsample(scale, scale)
return image
```

- `tk.PhotoImage` chỉ hỗ trợ `.png`, `.gif`, `.ppm`, `.pgm` — nên extensions
  giới hạn 4 loại.
- `subsample` là downscale integer — chất lượng ổn mà không cần PIL.
- Tính `scale` bằng division integer để ra số nguyên ≥ 1.
- **Quan trọng**: `PhotoImage` phải được giữ reference (lưu vào attribute
  của widget), nếu không Python GC sẽ free → ảnh mất.

### `_find_cover_path(track_key)`

3 cấp fallback:
1. Path trong library.
2. Convention `assets/covers/<key>.<ext>`.
3. Default cover `assets/covers/default.png`.

---

## 8. src/audio_player.py

Wrapper quanh `pygame.mixer.music` — engine phát nhạc thật.

### State module-level

```python
_initialised = False
_current_path: Path | None = None
_duration_seconds: float = 0.0
_paused: bool = False
```

Dùng module-level state vì `pygame.mixer.music` bản thân đã là singleton —
không thể có nhiều channel music cùng lúc.

### `_ensure_init()`

```python
global _initialised
if pygame is None: return False
if _initialised:   return True
try:
    pygame.mixer.init()
except pygame.error:
    return False
_initialised = True
return True
```

Lazy init: tránh init khi chưa cần (mixer init tốn vài chục ms). Nếu máy
không có audio device (CI, docker) → return False, app không crash.

### `_probe_duration(path)`

```python
try:
    sound = pygame.mixer.Sound(str(path))
except pygame.error:
    return 0.0
try:
    return float(sound.get_length())
except pygame.error:
    return 0.0
```

`pygame.mixer.music` không có cách lấy duration trực tiếp. Trick: load lại
bằng `pygame.mixer.Sound` (in-memory) → `.get_length()` trả giây.

### `load_and_play(path)`

```python
src = Path(path)
if not src.is_file(): return False
pygame.mixer.music.load(str(src))
pygame.mixer.music.play()
_current_path = src
_duration_seconds = _probe_duration(src)
_paused = False
return True
```

Cập nhật tất cả state sau khi play thành công.

### `pause()`, `resume()`, `stop()`

- `pause`: nếu đang play & chưa pause → `music.pause()`, set flag.
- `resume`: nếu đang pause → `music.unpause()`, clear flag.
- `stop`: gọi `music.stop()` + reset state.

### `is_playing()`

```python
return pygame.mixer.music.get_busy() and not _paused
```

`get_busy()` return True cả khi pause — nên phải combine với `_paused` flag.

### `seek(seconds)`

```python
pygame.mixer.music.play(start=seconds)
if _paused:
    pygame.mixer.music.pause()
```

`pygame.mixer.music` không có API seek trực tiếp — trick là `play(start=…)`.
Nếu trước đó user đã pause thì phải pause lại (vì `play` unpause ngầm).

---

## 9. src/font_manager.py

Cấu hình ttk Styles và bảng màu tối (neon / purple theme).

### Bảng màu (constants)

```python
BG          = "#0B0A14"   # màu nền tối
PANEL       = "#12111F"   # sidebar
CARD        = "#1A1830"   # card chính
CARD_ALT    = "#232142"   # card phụ (hover, secondary)
ACCENT      = "#7C5CFF"   # tím neon — brand
ACCENT_GLOW = "#A68BFF"
TEXT        = "#F1ECFF"   # text chính
TEXT_SOFT   = "#BFB7DB"
MUTED       = "#7F7A9C"
BORDER      = "#2C2A45"
SELECT_BG   = "#3C2F6A"
INPUT_BG    = "#0F0D1C"
```

Một chỗ khai báo → mọi module import từ đây. Đổi màu chỉ sửa 1 file.

### `_pick_font_family()`

```python
candidates = ["SF Pro Display", "SF Pro Text", "Segoe UI", "Inter",
              "Helvetica Neue", "Arial"]
available = set(tkfont.families())
for name in candidates:
    if name in available:
        return name
return "TkDefaultFont"
```

Tìm font "đẹp" có sẵn trên hệ thống. macOS có SF Pro, Windows có Segoe UI,
Linux thường có Arial. Fallback `TkDefaultFont` đảm bảo không bao giờ fail.

### `configure()`

Hàm chính — gọi 1 lần lúc start. Tạo `ttk.Style()` rồi set map cho mọi widget:

```python
style = ttk.Style()
style.theme_use("clam")   # theme dễ custom

style.configure("Root.TFrame",  background=BG)
style.configure("Card.TFrame",  background=CARD)
style.configure("Hero.TLabel",  font=_ff(26, "bold"),
                background=BG, foreground=TEXT)
style.configure("Neon.TButton", background=ACCENT, foreground="white",
                font=_ff(12, "bold"), padding=(16, 10))
style.map("Neon.TButton",
          background=[("active", ACCENT_GLOW), ("disabled", CARD_ALT)])
...
```

Quy ước naming:
- `Root.*` — frame nằm trực tiếp trên window (nền tối).
- `Card.*` — khối content có border radius giả lập.
- `Hero.*` — text to / tiêu đề.
- `Neon.*` — CTA primary button (màu tím).
- `Ghost.*` — secondary button (nền trong).
- `Danger.*` — destructive (delete).
- `Muted.*` — text subtitle mờ.

### `ff(size, weight="normal")`

```python
return (FAMILY, size, weight)
```

Public wrapper để code khác lấy tuple font nhanh. `_ff` là alias nội bộ dùng
trong `configure`.

### `apply_theme(window)`, `style_text_widget`, `style_canvas`

Widget thường (không phải ttk) như `tk.Text`, `tk.Canvas`, `Toplevel` không
nghe style → phải set `configure(bg=…, fg=…)` tay. Các helper này gộp lại
cho đỡ lặp.

---

## 10. src/gui_helpers.py

Utilities dùng chung cho mọi page.

### `setup_page_container(parent, title="", geometry="", minsize=None)`

```python
if isinstance(parent, (tk.Tk, tk.Toplevel)):
    if title:    parent.title(title)
    if geometry: parent.geometry(geometry)
    if minsize:  parent.minsize(*minsize)
    fonts.apply_theme(parent)
```

**Dual-use trick**: page UI có thể được gắn vào `Tk` (chạy standalone, ví dụ
`python3 -m src.update_lyrics`) **hoặc** vào `Frame` (embedded trong tab của
`JukeBoxApp`). Hàm này check `isinstance` và chỉ set window-level property
khi parent là Toplevel/Tk. Nếu parent là Frame thì no-op.

### `clear_tree(tree)`

```python
for item in tree.get_children(""):
    tree.delete(item)
```

Pattern chuẩn để reset `ttk.Treeview` trước khi render lại.

### `stars_text(rating)`

```python
r = max(0, min(5, int(rating or 0)))
return "★" * r + "☆" * (5 - r)
```

Duplicate nhẹ với `LibraryItem.stars()` nhưng hàm này nhận int thuần, không
cần instance — tiện cho treeview render từ record dict.

### `bind_two_column_stacking(container, left, right, breakpoint=900)`

```python
def on_resize(event):
    if event.width < breakpoint:
        left.grid_configure(column=0, row=0, columnspan=2)
        right.grid_configure(column=0, row=1, columnspan=2)
    else:
        left.grid_configure(column=0, row=0, columnspan=1)
        right.grid_configure(column=1, row=0, columnspan=1)

container.bind("<Configure>", on_resize)
```

Responsive 2 cột: nhỏ hơn 900px thì stack dọc, ngược lại chia đôi.
`<Configure>` event fire khi widget resize → reflow grid.

### `create_scrollable_column(parent)`

```python
canvas = tk.Canvas(parent, highlightthickness=0, bg=BG)
scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
inner = ttk.Frame(canvas, style="Root.TFrame")
canvas.create_window((0, 0), window=inner, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

def on_inner_config(e):
    canvas.configure(scrollregion=canvas.bbox("all"))
inner.bind("<Configure>", on_inner_config)

def on_mousewheel(event):
    canvas.yview_scroll(int(-event.delta / 120), "units")
canvas.bind_all("<MouseWheel>", on_mousewheel)

return inner
```

Trick tạo column cuộn được:
1. Canvas là viewport.
2. Frame (`inner`) thả vào canvas bằng `create_window`.
3. Scrollbar điều khiển `canvas.yview`.
4. Mỗi khi `inner` resize, set lại `scrollregion`.
5. Bind mousewheel global (`bind_all`) để lăn chuột ở đâu cũng cuộn.

Return `inner` để caller chỉ thêm widget vào đó — không cần biết canvas/scrollbar.

### `create_metric_card(parent, title, value, subtitle="")`

Tạo card statistics (tiêu đề, số to, subtitle mờ). Trả về dict `{card, value_lbl}`
để caller update giá trị sau.

### `draw_bar_chart(canvas, values, labels)`

Vẽ biểu đồ cột cơ bản trên `tk.Canvas`:
1. `canvas.delete("all")` — clear.
2. Tính `max_value` để scale.
3. Loop values: vẽ `create_rectangle` cho cột + `create_text` cho label.
4. Padding trên/dưới để cột không đè sát mép.

Không dùng matplotlib — tránh dependency nặng.

---

## 11. src/auth_manager.py

Users file + hash password.

### `_make_password_hash(password, salt_hex=None)`

```python
if salt_hex is None:
    salt = os.urandom(16)
else:
    salt = bytes.fromhex(salt_hex)
digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt,
                             iterations=120_000)
return salt.hex(), digest.hex()
```

- Random salt 16 bytes (= 128 bit) mỗi user. Ngăn rainbow table.
- PBKDF2 với 120 000 iteration — chậm có chủ đích để brute-force khó.
- Return hex string để lưu JSON (bytes không serialize được).

Khi verify: truyền `salt_hex` từ file xuống, hash password input rồi so sánh:

```python
def _verify_password(password, salt_hex, expected_hash):
    _, digest = _make_password_hash(password, salt_hex)
    return hmac.compare_digest(digest, expected_hash)
```

`hmac.compare_digest` là **constant-time** — ngăn timing attack (so sánh
`==` sẽ fail sớm khi byte đầu khác, leak thông tin).

### `load_users()`

Tương tự `track_library.load_library` — nếu file hỏng, tạo default với
account `admin / admin` để user tối thiểu đăng nhập được.

### `validate_username`, `validate_password`

Các rule business đơn giản:
- Username: chữ/số/underscore, độ dài 3–20.
- Password: tối thiểu 6 ký tự (có thể nâng lên nếu cần).

### `create_user(username, password, display_name="")`

```python
username_norm = _normalise_username(username)
users = load_users()
if username_norm in users:
    return False, "Tên đăng nhập đã tồn tại."
salt_hex, hash_hex = _make_password_hash(password)
users[username_norm] = {
    "username": username,
    "display_name": display_name or username,
    "salt": salt_hex,
    "password_hash": hash_hex,
    "created_at": _now_text(),
}
_save_users(users)
return True, "Tạo tài khoản thành công."
```

Key trong dict là username lowercase → case-insensitive login. Giữ nguyên
username gốc ở field `"username"` để hiển thị.

### `authenticate_user(username, password)`

```python
user = load_users().get(_normalise_username(username))
if user is None:
    return False, "Tài khoản không tồn tại.", None
if not _verify_password(password, user["salt"], user["password_hash"]):
    return False, "Mật khẩu không đúng.", None
return True, "Đăng nhập thành công.", user
```

Trả 3-tuple để caller `sign_in_clicked` biết đổi status + mở app.

---

## 12. src/auth_ui.py

Màn hình đăng nhập — `Tk` window, 2 cột hero + form.

### `class AuthApp`

```python
def __init__(self):
    self.window = tk.Tk()
    fonts.configure()
    gui_helpers.setup_page_container(self.window, title="JukeBox",
                                     geometry="1100x720", minsize=(960, 640))
    self._build_ui()
```

Một cửa sổ duy nhất. Không dùng Toplevel.

### `_build_ui`

Grid 2 cột: trái hero, phải form.

```python
self.window.columnconfigure(0, weight=1, uniform="auth_cols")
self.window.columnconfigure(1, weight=1, uniform="auth_cols")
self.window.rowconfigure(0, weight=1)

self._build_left_panel(left_frame)
self._build_right_panel(right_frame)
```

`uniform="auth_cols"` buộc 2 cột chia đều pixel.

### `_build_right_panel` — Notebook form

```python
self.notebook = ttk.Notebook(panel)
self.sign_in_frame = ttk.Frame(self.notebook, style="Card.TFrame")
self.sign_up_frame = ttk.Frame(self.notebook, style="Card.TFrame")
self.notebook.add(self.sign_in_frame, text="Sign In")
self.notebook.add(self.sign_up_frame, text="Sign Up")
self._build_sign_in_form()
self._build_sign_up_form()
```

2 tab — user chuyển bằng click tab hoặc bằng `_switch_to_sign_up` (link text).

### `_build_labelled_entry(parent, label, show=None)`

Helper tạo 1 cặp `Label + Entry` có style đồng nhất. `show="*"` khi dùng cho
password (hiện dấu ●).

### Toggle show password

```python
def _toggle_sign_in_password(self):
    current = self.sign_in_password.cget("show")
    self.sign_in_password.config(show="" if current else "*")
```

Check hiện tại đang mask hay không → invert. `cget` đọc thuộc tính widget.

### `sign_in_clicked()`

```python
username = self.sign_in_username.get().strip()
password = self.sign_in_password.get()
if not username or not password:
    self.set_status("Vui lòng nhập đủ thông tin.", level="error")
    return
ok, msg, user = auth.authenticate_user(username, password)
if ok:
    self.set_status(msg, level="success")
    self.open_main_app(user)
else:
    self.set_status(msg, level="error")
```

- Validate client-side: rỗng → báo luôn, không cần gọi auth.
- Gọi `authenticate_user` → xử lý success/error.

### `open_main_app(user)`

```python
self.window.destroy()
from src.track_player import JukeBoxApp
app = JukeBoxApp(current_user=user.get("display_name") or user.get("username"),
                 on_logout=launch_auth_app)
app.run()
```

- `destroy()` cửa sổ auth trước.
- Import `JukeBoxApp` **trong hàm** (lazy import) — tránh circular import
  vì `track_player` cũng có thể kéo theo auth_ui.
- `on_logout=launch_auth_app` — khi JukeBoxApp logout thì gọi lại hàm này
  → vòng lặp auth → app → auth.

### `launch_auth_app()`

Entry point:

```python
def launch_auth_app():
    AuthApp().run()
```

Gọi từ `main.py` và từ `JukeBoxApp.logout`.

---

## 13. src/add_remove_tracks.py

Trang Create / Delete track. Mode tham số cho phép dùng lại cho nhiều ngữ cảnh.

### Mode

```python
def __init__(self, window, mode="both"):
    self.mode = mode   # "add" | "remove" | "both"
```

Trong `ManagePage` của JukeBoxApp, tab "Create" tạo instance mode `"add"`,
tab "Delete" tạo instance mode `"remove"`. Cùng class, chỉ show/hide card
khác nhau.

### `_build_add_card`

Form gồm các Entry cho `name`, `artist`, `album`, `year`, Combobox rating,
button cover picker, button audio picker.

Khi user bấm `Add Track`:

```python
def add_track_clicked(self):
    name   = self.name_input.get().strip()
    artist = self.artist_input.get().strip()
    if not name or not artist:
        self._validation_error("Thiếu tên hoặc nghệ sĩ.")
        return
    rating = validation.get_valid_rating(self.rating_var.get(), allow_zero=True)
    if rating is None:
        self._validation_error("Rating không hợp lệ.")
        return
    year = validation.get_valid_year(self.year_input.get()) if self.year_input.get() else None

    key = lib.add_track(name, artist, rating=rating,
                        album=self.album_input.get().strip(), year=year)
    if key is None:
        self._notify_error("Lỗi", "Không thể thêm track.")
        return

    if self._pending_cover_path:
        cover_manager.assign_cover_image(key, self._pending_cover_path)
    if self._pending_audio_path:
        audio_manager.assign_audio(key, self._pending_audio_path)

    lib.add_history_entry(key, source="manage", action="create",
                          name=name, artist=artist)
    self._notify_success("Thêm thành công", f"Track {key}: {name} — {artist}")
    self._reset_add_form()
    if self.app_ref: self.app_ref.refresh_library()
```

Flow: validate → `lib.add_track` → assign cover/audio → history → notify →
broadcast.

### Cover/audio picker

```python
def _choose_cover_clicked(self):
    init_dir = str(cover_manager.COVERS_DIR)
    path = filedialog.askopenfilename(
        title="Chọn ảnh bìa",
        initialdir=init_dir,
        filetypes=[("Images", "*.png *.gif *.ppm *.pgm")])
    if path:
        self._pending_cover_path = Path(path)
        self._render_cover_preview(self._pending_cover_path)
```

`_pending_cover_path` giữ path khi user đã chọn nhưng chưa bấm Add. Clear
nút → set `None`.

### `remove_track_clicked()`

```python
raw = self.delete_input.get()
key = validation.normalise_track_number(raw)
if key is None or lib.get_item(key) is None:
    self._notify_error("Không tìm thấy", "Track không tồn tại.")
    return
confirmed = messagebox.askyesno(
    "Xoá track",
    f"Xoá track {key}: {item.name} — {item.artist}?",
    parent=self.window)
if not confirmed: return
if lib.delete_track(key):
    lib.add_history_entry(key, source="manage", action="delete",
                          name=item.name, artist=item.artist)
    self._notify_success(...)
    if self.app_ref: self.app_ref.refresh_library()
```

Luôn confirm trước khi xoá (destructive action). Ghi history `action="delete"`
để statistics có thể truy vết về sau.

---

## 14. src/update_tracks.py

Form Update metadata — phức tạp hơn vì có 3 trạng thái cho cover/audio:
**giữ nguyên**, **thay bằng file mới**, **xoá**.

### 3-state handling

```python
self._pending_cover_path = None   # file mới được chọn
self._cover_cleared      = False  # user đã bấm Clear
# Nếu cả hai đều False/None → giữ nguyên cover hiện tại
```

Khi update:

```python
if self._pending_cover_path:
    cover_manager.assign_cover_image(key, self._pending_cover_path)
elif self._cover_cleared:
    cover_manager.remove_cover_image(key)
# else: không làm gì
```

Cùng logic cho audio.

### `load_track_clicked()`

```python
key = validation.normalise_track_number(self.track_key_input.get())
if key is None:
    self._validation_error("Số track không hợp lệ.")
    return
item = lib.get_item(key)
if item is None:
    self._notify_error("Không tìm thấy", f"Track {key} không tồn tại.")
    return

self._clear_form_only()
self.selected_key = key
self.name_input.insert(0, item.name)
self.artist_input.insert(0, item.artist)
self.rating_var.set(str(item.rating))
if isinstance(item, AlbumTrack):
    self.album_input.insert(0, item.album)
    if item.year: self.year_input.insert(0, str(item.year))
# Preview cover/audio hiện tại
cover_path = cover_manager.find_cover_path(key)
self._render_cover_preview(cover_path, empty_text="Chưa có cover")
audio_path = audio_manager.find_audio_path(key)
self._render_audio_name(audio_path, empty_text="Chưa có audio")
```

`_clear_form_only()` không reset `selected_key` — chỉ xoá input để đổ dữ
liệu mới. Avoid lỗi user bấm Update mà không select lại key.

### `update_track_clicked()`

```python
if self.selected_key is None:
    self._notify_error("Chưa chọn track", "Load track trước khi cập nhật.")
    return
name   = self.name_input.get().strip()
artist = self.artist_input.get().strip()
rating = validation.get_valid_rating(self.rating_var.get(), allow_zero=True)
year   = validation.get_valid_year(self.year_input.get()) if self.year_input.get().strip() else None
album  = self.album_input.get().strip()

if not name or not artist:
    self._validation_error("Thiếu tên hoặc nghệ sĩ."); return
if rating is None:
    self._validation_error("Rating không hợp lệ."); return

lib.update_track_info(self.selected_key, name, artist, rating,
                      album=album, year=year)

# Apply cover/audio changes
if self._pending_cover_path:
    cover_manager.assign_cover_image(self.selected_key, self._pending_cover_path)
elif self._cover_cleared:
    cover_manager.remove_cover_image(self.selected_key)
if self._pending_audio_path:
    audio_manager.assign_audio(self.selected_key, self._pending_audio_path)
elif self._audio_cleared:
    audio_manager.remove_audio(self.selected_key)

lib.add_history_entry(self.selected_key, source="manage", action="update")
self._notify_success("Cập nhật thành công", ...)
if self.app_ref: self.app_ref.refresh_library()
```

---

## 15. src/update_lyrics.py

Editor lyrics — file nhỏ, logic ít, tập trung vào 2 hành động `save_lyrics`
và `clear_lyrics`.

### Layout

- Bên trái: search bar + Treeview cột (`#`, `title`, `artist`, `lyrics`,
  `rating`) — cột "lyrics" hiện "Yes"/"—" để biết track nào đã có lyrics.
- Bên phải: Label "Track X: …", Text widget editor, nút Save/Clear.

### `_apply_search()`

```python
keyword = self.search_input.get().strip().lower()
clear_tree(self.tree)
for record in reversed(lib.get_track_records()):   # mới nhất trước
    if keyword and not (
        keyword in record["key"].lower()
        or keyword in record["name"].lower()
        or keyword in record["artist"].lower()
        or keyword in (record["album"] or "").lower()):
        continue
    item = lib.get_item(record["key"])
    has_lyrics = "Yes" if item is not None and item.lyrics else "—"
    self.tree.insert("", "end", values=(record["key"], record["name"],
                     record["artist"], has_lyrics, stars_text(record["rating"])))
```

- `reversed` để key lớn nhất (track mới tạo) hiện đầu tiên.
- Keyword match theo 4 field: key, name, artist, album.
- Cột "Has lyrics" check `item.lyrics` truthy.

### `save_lyrics_clicked()`

```python
if self.selected_key is None:
    self._notify_error("Cannot save lyrics", "Load a track before saving lyrics.")
    return
lyrics = self.lyrics_txt.get("1.0", tk.END).strip()
if not lib.set_lyrics(self.selected_key, lyrics if lyrics else None):
    self._notify_error("Save failed", "Lyrics could not be saved.")
    return
lib.add_history_entry(self.selected_key, source="manage", action="update_lyrics")
self.list_tracks_clicked()
self._notify_success("Lyrics saved", ...)
if self.app_ref: self.app_ref.refresh_library()
```

- `get("1.0", END)` đọc toàn bộ Text từ dòng 1 ký tự 0 đến cuối.
- `strip()` + `if lyrics else None`: nếu user xoá hết thì lưu `None` (không
  phải chuỗi rỗng) → `to_dict` bỏ field → JSON gọn.
- Ghi history với `action="update_lyrics"` để thống kê sau này.

### `clear_lyrics_clicked()`

Tương tự save nhưng luôn set `None` và có confirm dialog trước.

---

## 16. src/view_tracks.py

Trang standalone chỉ xem + search. Dùng cho test nhanh hoặc future chạy
độc lập. Trong app chính không dùng trực tiếp — `LibraryPage` của
`track_player.py` thay thế.

### `__init__`

```python
def __init__(self, window):
    self.window = window
    self.selected_key: str | None = None
    setup_page_container(window, title="Track Viewer",
                         geometry="1280x800", minsize=(1080, 700))
    self._build_toolbar()
    self._build_main_panels()
    self.list_tracks_clicked()
```

Pattern standard: setup container → build các phần UI → load data lần đầu.

### `_build_toolbar`

Search entry + Combobox rating + nút "List All".

### `_build_main_panels`

2 cột: tree (trái), Text detail + cover canvas (phải).

### `_select_track_from_tree`

```python
selected = self.tree.selection()
if not selected: return
values = self.tree.item(selected[0], "values")
self.show_track(values[0])
```

`tree.selection()` trả tuple id. Lấy row đầu → `values` là tuple tương ứng
columns → phần tử đầu là key.

### `show_track(key)`

Render detail text (name, artist, album/year/rating/plays) và vẽ cover. Vì
chỉ view, không có nút play.

### `list_tracks_clicked`, `search_tracks_clicked`, `filter_by_score_clicked`

Đều gọi `_populate_tree` với các filter khác nhau. Đơn giản hơn nhiều so
với `LibraryPage` trong app chính.

---

## 17. src/create_track_list.py

**Trang Playlists** — phức tạp vì có player riêng + file I/O.

### State

```python
self.playlist: list[str] = []        # danh sách key theo thứ tự
self.current_index = 0               # track đang phát / sẽ phát
self.is_playing = False
self.is_paused  = False
self.current_playlist_name: str | None = None
self._autoplay = False               # tự chuyển bài khi hết
self._was_playing_last_tick = False  # edge detection
```

### `_play_current_track(source="playlist_single")`

```python
if not self.playlist:
    self._notify_error(...); return
track_key = self.playlist[self.current_index]
if self.app_ref is not None:
    # Đẩy playlist vào queue của app → bottom player bar hiểu
    self.app_ref.set_queue(self.playlist, self.current_index)
    ok = self.app_ref.play_track(track_key, source=source)
else:
    # Fallback: không có app (standalone) — tự phát
    path = audio_manager.find_audio_path(track_key)
    ok = audio_player.load_and_play(path) if path else False

if not ok: return
self.is_playing = True
self.is_paused = False
self._autoplay = True
self._was_playing_last_tick = True
self.refresh_playlist_tree()
```

**Điểm quan trọng**: `set_queue` đẩy playlist vào JukeBoxApp để khi user bấm
⏭/⏮ ở player bar thì app hiểu đang phát playlist nào — từ đó đi theo thứ tự
playlist chứ không phải thứ tự library.

### `_tick_playback()` — vòng tick 200ms

```python
# 1) Sync với queue của app (nếu user bấm ⏭ ở bottom bar)
if (self.app_ref is not None
    and self.app_ref.queue == self.playlist
    and self.app_ref.queue_index is not None
    and self.app_ref.queue_index != self.current_index):
    self.current_index = self.app_ref.queue_index
    self.is_playing = self.app_ref.is_playing
    self.is_paused = False
    self._autoplay = True
    self._was_playing_last_tick = audio_player.is_playing()
    self.refresh_playlist_tree()

# 2) Autoplay: khi hết bài → nhảy bài tiếp
is_now_playing = audio_player.is_playing()
if (self._autoplay and self._was_playing_last_tick
    and not is_now_playing and not audio_player.is_paused()):
    next_index = self.current_index + 1
    if next_index < len(self.playlist):
        self.current_index = next_index
        self._play_current_track(source="playlist_auto")
    else:
        self._autoplay = False
self._was_playing_last_tick = is_now_playing

# 3) Lên lịch tick kế tiếp
try:
    self.window.after(200, self._tick_playback)
except tk.TclError:
    pass   # window đã destroy
```

**Logic edge-detection**:
- `_was_playing_last_tick = True` & `is_now_playing = False` → bài vừa kết thúc.
- Phải check `not audio_player.is_paused()` để không nhầm với pause.

**Sync queue**: cho phép 2 chiều. User bấm ⏭ ở trang playlist (gọi
`skip_track_clicked`) → update `current_index` + `app.set_queue`. User bấm
⏭ ở player bar (gọi `app._player_next`) → app update `queue_index` → tick
ở đây detect và sync `current_index`.

### `save_playlist_clicked()`

```python
name = validation.normalise_playlist_name(self.playlist_name_input.get())
if not name:
    self._validation_error("Tên playlist không hợp lệ."); return
path = self._get_playlist_path_for(name)
payload = {"name": name, "tracks": list(self.playlist),
           "updated_at": _now_text()}
try:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                    encoding="utf-8")
    self.current_playlist_name = name
    self._notify_success(...)
except OSError as e:
    self._notify_error("Không ghi được file", str(e))
```

JSON per-playlist trong `playlists/<name>.json`. Không dùng chung 1 file lớn
→ xoá/rename dễ hơn (thao tác filesystem).

### `load_playlist_clicked()`

```python
name = simpledialog.askstring("Load playlist", ...)
name = validation.normalise_playlist_name(name)
if not name: return
path = self._get_playlist_path_for(name)
if not path.is_file():
    self._notify_error(...); return
data = json.loads(path.read_text(encoding="utf-8"))
self.playlist = [str(k) for k in data.get("tracks", [])]
self._remove_missing_tracks(show_status=True)
self.current_playlist_name = name
self.current_index = 0
self._reset_playback_state()
self.refresh_playlist_tree()
```

`_remove_missing_tracks` quan trọng: sau khi user xoá track ở Manage, playlist
cũ có thể còn key không tồn tại → clean trước khi hiển thị, tránh crash khi
play.

### `_remove_missing_tracks(show_status=False)`

```python
original = len(self.playlist)
self.playlist = [k for k in self.playlist if lib.get_item(k) is not None]
removed = original - len(self.playlist)
if removed and show_status:
    self.status_lbl.configure(text=f"Bỏ {removed} track không còn tồn tại.")
```

---

## 18. src/track_statistics.py

Dashboard thống kê.

### Layout

- Row 1: 4 metric card (Total tracks, Total plays, Avg rating, Album/Standard
  ratio).
- Row 2: Bar chart "Top played tracks".
- Row 3: Treeview "Listening history" + nút Delete history.

### `show_statistics_clicked()`

```python
stats = lib.get_statistics()
self._set_card_value(self.total_card, str(stats["total_tracks"]))
self._set_card_value(self.plays_card, str(stats["total_plays"]))
self._set_card_value(self.rating_card, f"{stats['average_rating']:.1f}")
most_key, most_item = stats["most_played"]
subtitle = (f"{most_item.name} — {most_item.artist}"
            if most_item else "Chưa có dữ liệu")
self._set_card_value(self.top_card, str(most_item.play_count) if most_item else "0")
self.top_card["subtitle_lbl"].configure(text=subtitle)
self._redraw_chart()
```

### `_redraw_chart()`

```python
records = lib.get_track_records()
records.sort(key=lambda r: r["play_count"], reverse=True)
top = records[:5]
values = [r["play_count"] for r in top]
labels = [r["name"][:12] for r in top]   # cắt ngắn label
gui_helpers.draw_bar_chart(self.chart_canvas, values, labels)
```

Top 5 play count. Label cắt 12 ký tự để không đè cột khác.

### `load_history_clicked()`

```python
clear_tree(self.history_tree)
for entry in reversed(lib.load_history()):   # mới nhất trước
    self.history_tree.insert("", "end", values=(
        entry["timestamp"], entry["track_key"], entry["name"],
        entry["artist"], entry["source"], entry["action"],
    ))
```

### `delete_history_clicked()`

```python
if not messagebox.askyesno("Xoá lịch sử", "Xoá toàn bộ lịch sử nghe?"):
    return
lib.clear_history()
self.load_history_clicked()
```

Destructive action → confirm.

---

## 19. src/track_player.py

File lớn nhất (~1500 dòng). Chứa `JukeBoxApp` + 5 Page class.

### 19.1 `class JukeBoxApp`

#### `__init__`

```python
def __init__(self, current_user="Guest", on_logout=None):
    self.current_user = current_user
    self.on_logout = on_logout

    self.window = tk.Tk()
    fonts.configure()
    self.window.title("JukeBox — Neon Edition")
    self._configure_window_size()
    fonts.apply_theme(self.window)

    cover_manager.backfill_cover_paths()
    audio_manager.backfill_audio_paths()
    lib.load_library()   # ensure loaded

    # State
    self.pages: dict[str, object] = {}
    self.page_handlers: dict[str, object] = {}
    self.nav_buttons: dict[str, ttk.Button] = {}
    self.current_page: str | None = None
    self.current_track_key: str | None = None
    self.queue: list[str] = []          # queue cho ⏭/⏮
    self.queue_index: int | None = None
    self._progress_dragging = False
    self._tick_job = None

    # Build UI
    self._build_sidebar()
    self._build_content_area()
    self._build_player_bar()
    self._build_pages()
    self.switch_page("now_playing")

    # Start tick loop
    self._schedule_progress_tick()

    self.window.protocol("WM_DELETE_WINDOW", self._on_close)
```

**Thứ tự quan trọng**:
1. `fonts.configure()` **trước** khi build UI → style đã sẵn.
2. `backfill` trước `load_library` không bắt buộc nhưng tiện (library load
   rồi thì backfill mới biết key nào).
3. `switch_page` sau `_build_pages` để có trang để raise.
4. `protocol(WM_DELETE_WINDOW)` để clean tick/audio khi user click X.

#### `_build_sidebar`

```python
sidebar = ttk.Frame(self.window, style="Panel.TFrame")
sidebar.grid(row=0, column=0, sticky="ns")
sidebar.columnconfigure(0, weight=1)

# Logo
ttk.Label(sidebar, text="♫ JukeBox", style="SidebarLogo.TLabel").grid(...)

# User card
user_card = ttk.Frame(sidebar, style="UserCard.TFrame", padding=14)
ttk.Label(user_card, text=f"Hi, {self.current_user}",
          style="UserName.TLabel").grid(...)

# Nav buttons
for key, label in [("now_playing", "▶  Now Playing"),
                   ("library", "♫  Library"),
                   ("manage", "⚙  Manage"),
                   ("playlists", "📄  Playlists"),
                   ("statistics", "📊  Statistics")]:
    btn = ttk.Button(sidebar, text=label, style="Nav.TButton",
                     command=lambda k=key: self.switch_page(k))
    btn.grid(...)
    self.nav_buttons[key] = btn

# Spacer + Log out / Close
ttk.Button(sidebar, text="Log Out", style="Ghost.TButton",
           command=self.logout).grid(...)
ttk.Button(sidebar, text="Close App", style="Danger.TButton",
           command=self._on_close).grid(...)
```

- `lambda k=key:` — pattern chuẩn để capture biến trong loop (nếu không có
  default, tất cả callback sẽ gọi với key cuối cùng).
- Lưu button vào `nav_buttons` để `switch_page` đổi style (active).

#### `_build_player_bar`

Bar cố định ở bottom:

```
[cover 56x56] [title]          [⏮] [⏯] [⏭]     [████─────] 1:23/3:45     🔉 − ▁▁▁▁▁ + 70%
              [artist]
```

```python
bar = ttk.Frame(self.window, style="Panel.TFrame")
bar.grid(row=1, column=0, columnspan=2, sticky="ew")
bar.columnconfigure(1, weight=1)  # title expand
bar.columnconfigure(3, weight=2)  # progress expand

# Cover canvas
self.player_cover = tk.Canvas(bar, width=56, height=56,
                              highlightthickness=0, bg=CARD)
# Title label
self.player_title_lbl  = ttk.Label(bar, text="—", style="PlayerTitle.TLabel")
self.player_artist_lbl = ttk.Label(bar, text="—", style="PlayerArtist.TLabel")

# Buttons ⏮ ⏯ ⏭
ttk.Button(bar, text="⏮", style="Player.TButton",
           command=self._player_previous).grid(...)
self.play_button = ttk.Button(bar, text="▶", style="Player.TButton",
                              command=self.toggle_play)
ttk.Button(bar, text="⏭", style="Player.TButton",
           command=self._player_next).grid(...)

# Progress
self.progress_var = tk.DoubleVar(value=0.0)
self.progress = ttk.Scale(bar, from_=0, to=1.0, variable=self.progress_var,
                          orient="horizontal")
self.progress.bind("<ButtonPress-1>",   self._on_progress_press)
self.progress.bind("<ButtonRelease-1>", self._on_progress_release)
self.time_lbl = ttk.Label(bar, text="0:00 / 0:00", style="PlayerTime.TLabel")

# Volume (icon + − − slider + + %)
self.volume_icon_lbl = ttk.Label(bar, text="🔉", style="PlayerIcon.TLabel")
ttk.Button(bar, text="−", style="PlayerMini.TButton",
           command=self._volume_down).grid(...)
self.volume_var = tk.DoubleVar(value=0.7)
self.volume_scale = ttk.Scale(bar, from_=0, to=1.0,
                              variable=self.volume_var,
                              command=self._on_volume_change)
ttk.Button(bar, text="+", style="PlayerMini.TButton",
           command=self._volume_up).grid(...)
self.volume_pct_lbl = ttk.Label(bar, text="70%", style="PlayerPct.TLabel")
self.volume_scale.bind("<MouseWheel>", self._on_volume_wheel)
self._on_volume_change(0.7)  # init
```

#### `switch_page(key)`

```python
page = self.pages.get(key)
if page is None: return
page.tkraise()
self.current_page = key

# Style nav buttons
for k, btn in self.nav_buttons.items():
    btn.configure(style="NavActive.TButton" if k == key else "Nav.TButton")

# Gọi on_show nếu page có
handler = self.page_handlers.get(key)
if handler and hasattr(handler, "on_show"):
    handler.on_show()
```

- `tkraise()` đưa frame lên trên cùng (pattern tabbed UI bằng frame).
- `on_show` hook cho page làm gì đó khi mở (refresh data).

#### `play_track(track_key, source="dashboard")`

```python
path = audio_manager.find_audio_path(track_key)
if path is None:
    messagebox.showwarning("Không có file audio",
                           f"Track {track_key} chưa có audio.",
                           parent=self.window)
    return False
if not audio_player.load_and_play(path):
    messagebox.showerror("Không phát được",
                         "Không thể load file audio.", parent=self.window)
    return False

self.current_track_key = track_key
lib.increment_play_count(track_key)
item = lib.get_item(track_key)
lib.add_history_entry(track_key, source=source,
                      name=item.name if item else None,
                      artist=item.artist if item else None)

# Nếu source không phải playlist/queue → clear queue
if not (source.startswith("playlist") or source == "queue"):
    self.clear_queue()

self._refresh_player_bar()
self.play_button.configure(text="⏸")
self._notify_pages_refresh()
return True
```

**Điểm quan trọng**:
- `clear_queue()` khi play từ library/dashboard → bấm ⏭ sau đó sẽ đi theo
  thứ tự library, không đi theo playlist cũ.
- `increment_play_count` + history luôn xảy ra (không phân biệt source).
- `_notify_pages_refresh` để Library, Statistics, NowPlaying update.

#### `_player_next()` (đã update cho queue)

```python
# 1) Queue có phần tử kế tiếp → đi theo queue
if self.queue and self.queue_index is not None:
    next_idx = self.queue_index + 1
    if next_idx < len(self.queue):
        self.queue_index = next_idx
        self.play_track(self.queue[next_idx], source="queue")
        return
    # Hết queue → fallback về library
# 2) Fallback: library order
keys = lib.all_keys()
if not keys: return
if self.current_track_key in keys:
    idx = keys.index(self.current_track_key)
    next_idx = (idx + 1) % len(keys)
else:
    next_idx = 0
self.play_track(keys[next_idx], source="dashboard")
```

`_player_previous` cùng logic nhưng `- 1` và `max(0, …)` / modulo.

#### `toggle_play()`

```python
if audio_player.is_paused():
    audio_player.resume()
    self.play_button.configure(text="⏸")
elif audio_player.is_playing():
    audio_player.pause()
    self.play_button.configure(text="▶")
elif audio_player.is_loaded():
    audio_player.seek(0)
    self.play_button.configure(text="⏸")
else:
    # Chưa có gì load → play bài đầu tiên
    keys = lib.all_keys()
    if keys:
        self.play_track(keys[0], source="dashboard")
```

4 trạng thái.

#### Volume

```python
def _on_volume_change(self, value):
    try:
        fraction = float(value)
    except (TypeError, ValueError):
        return
    fraction = max(0.0, min(1.0, fraction))
    audio_player.set_volume(fraction)
    self._update_volume_visuals(fraction * 100)

def _volume_up(self):
    new_val = min(1.0, self.volume_var.get() + 0.05)
    self.volume_var.set(new_val)
    self._on_volume_change(new_val)

def _on_volume_wheel(self, event):
    delta = 0.05 if event.delta > 0 else -0.05
    new_val = max(0.0, min(1.0, self.volume_var.get() + delta))
    self.volume_var.set(new_val)
    self._on_volume_change(new_val)

def _update_volume_visuals(self, pct):
    pct = int(round(pct))
    if pct == 0:   icon = "🔇"
    elif pct < 35: icon = "🔈"
    elif pct < 70: icon = "🔉"
    else:          icon = "🔊"
    self.volume_icon_lbl.configure(text=icon)
    self.volume_pct_lbl.configure(text=f"{pct}%")
```

#### Progress

```python
def _on_progress_press(self, event):
    self._progress_dragging = True

def _on_progress_release(self, event):
    self._progress_dragging = False
    if not audio_player.is_loaded(): return
    dur = audio_player.get_duration_seconds() or 0
    target = self.progress_var.get() * dur
    audio_player.seek(target)

def _tick_progress(self):
    try:
        if audio_player.is_loaded():
            dur = audio_player.get_duration_seconds() or 0
            pos = audio_player.get_position_seconds()
            if not self._progress_dragging and dur > 0:
                self.progress_var.set(pos / dur)
            self.time_lbl.configure(
                text=f"{self._format_time(pos)} / {self._format_time(dur)}")
            # Reset play button khi hết bài
            if dur > 0 and pos >= dur - 0.2 and not audio_player.is_paused():
                self.play_button.configure(text="▶")
        self._tick_job = self.window.after(300, self._tick_progress)
    except tk.TclError:
        pass   # window destroyed
```

**Tại sao `_progress_dragging`**: không được set `progress_var` trong khi user
đang drag thumb — sẽ fight nhau, thumb giật.

#### `_on_close`

```python
def _on_close(self):
    if self._tick_job is not None:
        try: self.window.after_cancel(self._tick_job)
        except tk.TclError: pass
    try: audio_player.stop()
    except Exception: pass
    try: self.window.destroy()
    except tk.TclError: pass
```

Cancel tick trước, stop audio, destroy window. `try/except` bảo vệ khỏi các
tình huống widget đã destroy một phần.

#### `logout()`

```python
if not messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
    return
try: audio_player.stop()
except Exception: pass
self.window.destroy()
if self.on_logout is not None:
    self.on_logout()   # mở lại AuthApp
```

### 19.2 `class NowPlayingPage`

#### Layout

2 cột scrollable: trái (cover + meta + button "Go to Library"), phải (lyrics
viewer).

#### `on_show()` / `on_library_change()`

```python
def on_show(self):
    self._draw_cover()
    self._draw_meta()

def on_library_change(self):
    if self.frame.winfo_ismapped():
        self._draw_cover()
        self._draw_meta()
```

`winfo_ismapped` check page có đang hiển thị không — tránh vẽ vô ích khi
đang ở page khác.

#### `_draw_meta`

```python
key = self.app.current_track_key
if key is None:
    self.title_lbl.configure(text="Chưa phát bài nào")
    ...
    return
item = lib.get_item(key)
self.title_lbl.configure(text=item.name)
self.artist_lbl.configure(text=item.artist)
self.meta_lbl.configure(text=(
    f"Album: {getattr(item, 'album', '—') or '—'}    "
    f"Year: {getattr(item, 'year', '—') or '—'}    "
    f"Plays: {item.play_count}    "
    f"Rating: {item.stars()}"))
# Lyrics
if item.lyrics:
    self._set_lyrics_text(item.lyrics, placeholder=False)
else:
    self._set_lyrics_text("Chưa có lyrics. Mở trang Manage → Lyrics để thêm.",
                          placeholder=True)
```

`getattr(item, "album", "—")` — `LibraryItem` không có `album`, `AlbumTrack`
có. `getattr` với default vẽ ra "—" khi không có.

### 19.3 `class LibraryPage`

Trang library — tree + detail.

#### Filter logic

```python
def apply_filters(self):
    keyword = self.search_input.get().strip().lower()
    rating_text = self.rating_var.get()
    try: rating_filter = int(rating_text) if rating_text else None
    except ValueError: rating_filter = None

    records = lib.get_track_records()
    filtered = []
    for r in records:
        if rating_filter is not None and r["rating"] != rating_filter: continue
        if keyword and not (
            keyword in r["name"].lower() or keyword in r["artist"].lower()
            or keyword in (r["album"] or "").lower() or keyword in r["key"]):
            continue
        filtered.append(r)
    self.refresh_tree(filtered)
```

#### `_show_detail(key)`

Cover + title + artist + meta + nút Play. Nếu key không có trong library
thì `_show_empty_detail()`.

#### `_on_double_click` vs `_play_selected`

Cả 2 đều gọi `app.play_track`. Double-click tiện hơn. Nút Play là alternative.

### 19.4 `class ManagePage`

Wrapper nhúng 4 tool vào `ttk.Notebook`:

```python
self.notebook = ttk.Notebook(self.frame)
self.add_frame    = ttk.Frame(self.notebook, style="Root.TFrame")
self.update_frame = ttk.Frame(self.notebook, style="Root.TFrame")
self.delete_frame = ttk.Frame(self.notebook, style="Root.TFrame")
self.lyrics_frame = ttk.Frame(self.notebook, style="Root.TFrame")

self.notebook.add(self.add_frame,    text="Create")
self.notebook.add(self.update_frame, text="Update")
self.notebook.add(self.delete_frame, text="Delete")
self.notebook.add(self.lyrics_frame, text="Lyrics")

self.add_tool    = AddRemoveTracks(self.add_frame, mode="add")
self.update_tool = UpdateTracks(self.update_frame)
self.delete_tool = AddRemoveTracks(self.delete_frame, mode="remove")
self.lyrics_tool = UpdateLyrics(self.lyrics_frame)

# Inject app_ref
for tool in (self.add_tool, self.update_tool, self.delete_tool, self.lyrics_tool):
    tool.app_ref = self.app
```

`on_library_change()` forward cho các tool:

```python
def on_library_change(self):
    self.add_tool.refresh_list()
    self.update_tool.list_tracks_clicked()
    self.delete_tool.refresh_list()
    self.lyrics_tool.list_tracks_clicked()
```

### 19.5 `class PlaylistsPage` / `class StatisticsPage`

Wrapper mỏng nhúng `CreateTrackList` / `TrackStatistics`. Chỉ chuyển tiếp
`app_ref` và `on_library_change` / `on_show`.

---

## 20. Các luồng logic tiêu biểu

### 20.1 App start → hiển thị main window

```
main.py
 └─ launch_auth_app()
     └─ AuthApp.__init__()
         ├─ fonts.configure()            # style ttk
         ├─ setup_page_container()       # title, size
         └─ _build_ui()                   # Grid 2 cột + Notebook
     └─ run() → mainloop()
 └─ user nhập username/password → sign_in_clicked()
     ├─ auth.authenticate_user()
     ├─ open_main_app(user)
     │   ├─ self.window.destroy()
     │   └─ JukeBoxApp(current_user, on_logout=launch_auth_app)
     │       ├─ fonts.configure()
     │       ├─ cover_manager.backfill_cover_paths()
     │       ├─ audio_manager.backfill_audio_paths()
     │       ├─ lib.load_library()
     │       ├─ _build_sidebar/_build_content/_build_player_bar
     │       ├─ _build_pages()           # 5 page
     │       ├─ switch_page("now_playing")
     │       └─ _schedule_progress_tick()
     │   └─ app.run()
```

### 20.2 Phát 1 bài từ Library

```
User double-click row trong LibraryPage
 └─ _on_double_click → app.play_track(key, source="dashboard")
     ├─ audio_manager.find_audio_path(key)     # resolve file
     ├─ audio_player.load_and_play(path)        # pygame
     ├─ lib.increment_play_count(key)           # +1 → save JSON
     ├─ lib.add_history_entry(key, source="dashboard")
     ├─ clear_queue()                            # source ≠ playlist/queue
     ├─ _refresh_player_bar()
     └─ _notify_pages_refresh()
         ├─ NowPlayingPage.on_library_change() → vẽ lại cover/meta
         ├─ LibraryPage.on_library_change()    → refresh tree
         └─ StatisticsPage.on_library_change() → update metric
```

### 20.3 Phát Playlist

```
CreateTrackList.play_playlist_clicked()
 ├─ self.current_index = 0
 └─ self._play_current_track(source="playlist_start")
     ├─ self.app_ref.set_queue(self.playlist, 0)   # đẩy queue!
     └─ self.app_ref.play_track(key, source="playlist_start")
         # play_track thấy source bắt đầu bằng "playlist" → KHÔNG clear queue
```

### 20.4 Bấm ⏭ ở bottom player bar (khi đang phát playlist)

```
JukeBoxApp._player_next()
 ├─ if self.queue and self.queue_index is not None:
 │    next_idx = self.queue_index + 1
 │    if next_idx < len(self.queue):
 │        self.queue_index = next_idx
 │        self.play_track(self.queue[next_idx], source="queue")
 │        return
 # Hết queue → fallback library order

# Sau đó CreateTrackList._tick_playback phát hiện:
if app.queue == self.playlist and app.queue_index != self.current_index:
    self.current_index = app.queue_index
    self.refresh_playlist_tree()   # highlight row mới
```

### 20.5 Lưu Playlist

```
save_playlist_clicked()
 ├─ validation.normalise_playlist_name(name)
 ├─ payload = {name, tracks, updated_at}
 ├─ path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
 └─ notify success
```

### 20.6 Update Lyrics

```
UpdateLyrics.save_lyrics_clicked()
 ├─ lyrics = self.lyrics_txt.get("1.0", END).strip()
 ├─ lib.set_lyrics(key, lyrics or None)
 │   ├─ previous = item.lyrics
 │   ├─ item.lyrics = lyrics
 │   └─ if not save_library(): item.lyrics = previous; return False
 ├─ lib.add_history_entry(key, source="manage", action="update_lyrics")
 ├─ self.list_tracks_clicked()   # refresh tree (cột "Has Lyrics" update)
 └─ self.app_ref.refresh_library()
     └─ _notify_pages_refresh() → NowPlayingPage.on_library_change()
```

### 20.7 Xoá track (có queue/playlist đang chạy)

```
AddRemoveTracks.remove_track_clicked()
 ├─ confirm dialog
 ├─ lib.delete_track(key)
 │   ├─ previous = library.pop(key)
 │   └─ if not save_library(): library[key] = previous
 ├─ lib.add_history_entry(..., action="delete")
 └─ app_ref.refresh_library()
     └─ _notify_pages_refresh()

# Lần tới mở PlaylistsPage:
CreateTrackList.list_tracks_clicked()
 └─ _remove_missing_tracks()   # dọn playlist hiện tại
```

### 20.8 Logout → về AuthApp

```
JukeBoxApp.logout()
 ├─ messagebox.askyesno()
 ├─ audio_player.stop()
 ├─ self.window.destroy()
 └─ self.on_logout()   # = launch_auth_app
     └─ AuthApp().run()   # cửa sổ login quay lại
```

### 20.9 Close App

```
_on_close() (từ nút X hoặc nút Close App trong sidebar)
 ├─ window.after_cancel(self._tick_job)   # huỷ tick loop
 ├─ audio_player.stop()                    # stop mixer
 └─ window.destroy()                       # kết thúc mainloop
```

---

## Ghi chú khi mở rộng

- **Thêm page mới**: tạo class có `on_show` / `on_library_change`, thêm nav
  button + entry vào `_build_pages` và `pages` dict.
- **Thêm source play mới**: truyền `source=` vào `play_track`. Nếu source
  đó nên preserve queue, đảm bảo tên bắt đầu bằng `"playlist"` hoặc bằng
  `"queue"` (xem điều kiện trong `play_track`).
- **Thêm field mới cho track**: cập nhật `LibraryItem.__init__` + `to_dict`
  + `from_dict` + UI `UpdateTracks`. Không cần migrate JSON — field mới chỉ
  xuất hiện cho track mới save.
- **Đổi color theme**: chỉ sửa constants trong `font_manager.py`.
- **Kiểm tra format audio không trong SUPPORTED_EXTENSIONS**: thêm vào
  `audio_manager.SUPPORTED_EXTENSIONS` và đảm bảo `pygame.mixer.music` hỗ
  trợ (mp3/ogg/wav đều OK).
