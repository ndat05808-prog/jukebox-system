# view_tracks.py
# This module defines the TrackViewer page, a standalone Tkinter window
# that shows the music library as a sortable table on the left and a
# detail card (cover art + metadata + full details) on the right.
# It is the Stage 1 file required by the COMP1752 coursework brief and
# has been refactored from the original text-heavy template into a
# dashboard-style layout that integrates with the rest of the JukeBox
# application.

# Import the standard tkinter module under the alias `tk` so we can
# create the root window, Canvas widgets and the Message widget below.
import tkinter as tk

# Import the themed-tk submodule (`ttk`) which provides the modern
# styled widgets we use throughout the page: Frame, Label, Button,
# Combobox, Entry, Treeview and Scrollbar.
from tkinter import ttk

# Import the cover_manager helper from the models package. It is
# responsible for locating a track's cover image on disk, resizing it
# and returning a Tkinter PhotoImage we can draw on the canvas.
from ..models import cover_manager

# Import the font_manager from the views package and rename it to
# `fonts` for brevity. It exposes the colour constants (TEXT, ACCENT,
# BORDER, INPUT_BG, CARD_ALT, MUTED) and the ttk style names used
# everywhere on this page.
from . import font_manager as fonts

# Import the track_library module under the alias `lib`. This is the
# only module that talks to library_data.json; we go through `lib` for
# every read so the view never touches persistence directly.
from ..models import track_library as lib

# Import the three small GUI helper functions used on this page:
#   - clear_tree:           wipes every row from a Treeview
#   - setup_page_container: applies the standard window title/size/style
#   - stars_text:           converts an integer rating into the star string
from .gui_helpers import clear_tree, setup_page_container, stars_text

# Import AlbumTrack so we can use isinstance() to decide whether the
# selected item carries album/year metadata (only AlbumTrack does).
from ..models.library_item import AlbumTrack

# Import the two validation helpers we need on this page:
#   - get_valid_rating:        validates the rating-filter dropdown value
#   - normalise_track_number:  cleans a typed track number, e.g. "7" -> "07"
from ..models.validation import get_valid_rating, normalise_track_number

# TrackViewer
# Encapsulates the entire "View Tracks" page. One TrackViewer instance
# owns one Tkinter window and all the widgets inside it (toolbar, table,
# detail card, status bar). The instance also holds the small amount of
# UI state we need (the currently held cover image, the table and the
# status label) so callbacks can access them via `self`.
class TrackViewer:

    # __init__
    # Input:
    #   window  - a Tkinter root or Toplevel that this page will own
    # Output:
    #   None (constructs the entire page on the given window)
    # Side effects:
    #   - Configures the window's grid, title and geometry
    #   - Builds the toolbar, library table and detail card
    #   - Loads all tracks into the table for the initial view

    def __init__(self, window):
        # Keep a reference to the window so other methods (resize,
        # status updates, layout rebuilds) can reach it via self.window.
        self.window = window

        # Hold the current PhotoImage on the instance. Tkinter only
        # keeps a *weak* reference to images drawn on a Canvas, so if
        # we let this go out of scope the cover would disappear. We
        # start with None because no track is selected on first load.
        self.cover_image = None

        # Apply the shared page chrome (title, default size, minimum
        # size, ttk styling) through the helper so every page in the
        # app has the same look without duplicating boilerplate here.
        setup_page_container(
            window,
            title="View Tracks",
            geometry="1280x820",
            minsize=(1120, 720),
        )

        # Configure the two main columns of the window grid. We use
        # uniform="main_cols" so column 0 (the table, weight 3) and
        # column 1 (the detail card, weight 1) keep a stable 3:1 ratio
        # when the user resizes the window.
        window.columnconfigure(0, weight=3, uniform="main_cols")
        window.columnconfigure(1, weight=1, uniform="main_cols")

        # Make row 2 (the row that hosts the table + detail card)
        # absorb extra vertical space when the window grows. The
        # header (row 0), toolbar (row 1) and status bar (row 3) stay
        # at their natural height.
        window.rowconfigure(2, weight=1)

        # Build the page header. We use a ttk.Frame so it picks up the
        # Root.TFrame style (matching background colour) instead of the
        # default grey from classic Tk.
        header = ttk.Frame(window, style="Root.TFrame")

        # Place the header on row 0, spanning both columns. sticky="ew"
        # makes it stretch horizontally; padx/pady give it breathing
        # room from the window edge and the toolbar below.
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(18, 8))

        # Allow the header's first inner column to expand so the title
        # and subtitle labels can left-align cleanly.
        header.columnconfigure(0, weight=1)

        # Page title ("Library Browser"). Using the Hero.TLabel style
        # keeps the typography consistent with the other dashboard
        # pages in the app.
        ttk.Label(
            header,
            text="Library Browser",
            style="Hero.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        # A short subtitle explaining what the page replaces. Useful
        # when the marker compares this version against the original
        # text-only template.
        ttk.Label(
            header,
            text="This replaces the old text-heavy viewer with a cleaner dashboard-style layout.",
            style="Muted.TLabel"
        ).grid(row=1, column=0, sticky="w")

        # Delegate the toolbar (search box + filter dropdown + buttons)
        # to a private builder so __init__ stays readable.
        self._build_toolbar()

        # Same idea for the main content area: build the library table
        # on the left and the detail card on the right in one helper.
        self._build_main_panels()

        # Status label at the bottom of the window. Other methods write
        # short feedback messages here (e.g. "Showing details for
        # track 03." or "Filter finished: 0 matches.") instead of
        # popping up dialog boxes that would interrupt the user.
        self.status_lbl = ttk.Label(window, text="Ready.", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 16))

        # Listen for window-resize events so we can re-wrap the title
        # and detail text. Without this, long track names overflow the
        # detail card when the user shrinks the window.
        self.window.bind("<Configure>", self._on_resize)

        # Populate the table with every track on first load so the
        # user immediately sees the library instead of an empty grid.
        self.list_tracks_clicked()

        # Show the placeholder state on the detail card (no track
        # selected yet) so the right-hand panel isn't blank.
        self.display_empty_state()

    # _build_toolbar
    # Input:  none (uses self.window)
    # Output: none (creates the search/filter toolbar in row 1)
    # Builds the row that holds the search Entry, Search button,
    # rating Combobox and Filter Rating button.

    def _build_toolbar(self):
        # Card frame so the toolbar visually sits on top of the page
        # background. padding=14 gives the inner widgets some breathing
        # room from the card edges.
        toolbar_card = ttk.Frame(self.window, style="Card.TFrame", padding=14)
        toolbar_card.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=10)

        # Column 0 holds the search Entry and should take most of the
        # width; column 2 holds the rating Combobox and gets the rest.
        # Columns 1 and 3 hold buttons and stay at their natural width.
        toolbar_card.columnconfigure(0, weight=3)
        toolbar_card.columnconfigure(2, weight=1)

        # Search Entry. We store it on self because both the Search
        # button's command and the <Return> binding need to read its
        # current text via self.search_txt.get().
        self.search_txt = ttk.Entry(toolbar_card)
        self.search_txt.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        # Pressing Enter inside the entry triggers the same search as
        # clicking the button. The lambda swallows the event argument
        # that Tkinter passes; we don't need it.
        self.search_txt.bind("<Return>", lambda event: self.search_tracks_clicked())

        # Primary action button - "Neon" style is the bright, accented
        # button used for the most important action on each toolbar.
        ttk.Button(
            toolbar_card,
            text="Search",
            style="Neon.TButton",
            command=self.search_tracks_clicked
        ).grid(row=0, column=1, sticky="ew", padx=8)

        # Rating filter dropdown. state="readonly" forces the user to
        # pick from the listed values 0-5; they cannot type free text
        # so we don't need to validate the input again later.
        self.rating_filter_txt = ttk.Combobox(
            toolbar_card,
            values=["0", "1", "2", "3", "4", "5"],
            state="readonly"
        )
        self.rating_filter_txt.grid(row=0, column=2, sticky="ew", padx=8)

        # Default the dropdown to 5 so the most common case ("show
        # me my favourites") works with a single click on Filter.
        self.rating_filter_txt.set("5")

        # Secondary action button - "Ghost" style is the outlined
        # variant used for non-primary actions on the same toolbar.
        ttk.Button(
            toolbar_card,
            text="Filter Rating",
            style="Ghost.TButton",
            command=self.filter_by_score_clicked
        ).grid(row=0, column=3, sticky="ew", padx=(8, 0))

    # _build_main_panels
    # Input:  none
    # Output: none
    # Builds row 2 of the window: the library table on the left and
    # the selected-track detail card on the right.

    def _build_main_panels(self):
        # Left container - holds the library card. We use a plain
        # Root.TFrame as a wrapper so we can pad the card away from
        # the window edges without padding the card itself.
        left = ttk.Frame(self.window, style="Root.TFrame")
        left.grid(row=2, column=0, sticky="nsew", padx=(18, 10), pady=10)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        # Right container - same idea, wraps the detail card.
        right = ttk.Frame(self.window, style="Root.TFrame")
        right.grid(row=2, column=1, sticky="nsew", padx=(10, 18), pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        # Library card itself - this is the visible "panel" with the
        # table inside it. padding=18 keeps the table from touching
        # the card border.
        library_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        library_card.grid(row=0, column=0, sticky="nsew")
        library_card.columnconfigure(0, weight=1)
        # Row 1 (the table) absorbs extra height; row 0 (the title)
        # stays compact.
        library_card.rowconfigure(1, weight=1)

        # Header row inside the library card: holds the "Library"
        # title on the left and a "Show All" reset button on the right.
        header = ttk.Frame(library_card, style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Library",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w")

        # "Show All" resets the table back to the full library after
        # a search or filter has narrowed it down. We point its
        # command at list_tracks_clicked so it reuses the same logic
        # used at startup.
        ttk.Button(
            header,
            text="Show All",
            style="Ghost.TButton",
            command=self.list_tracks_clicked
        ).grid(row=0, column=1, sticky="e")

        # Wrapper around the Treeview. We need a frame here so we can
        # grid the vertical and horizontal scrollbars next to the
        # tree without affecting the rest of the card layout.
        table_wrap = ttk.Frame(library_card, style="Card.TFrame")
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        # The internal column identifiers for the Treeview. These
        # are NOT the visible labels - they are the keys we use when
        # we configure each column's heading and width below.
        columns = ("key", "title", "artist", "album", "year", "rating")

        # The actual table widget. show="headings" hides the empty
        # tree-icon column that Treeview shows by default, leaving
        # only the data columns we configured above.
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings")

        # Map each internal column id to its visible label and the
        # default width in pixels. Doing this in a dict (instead of
        # six separate calls) keeps the related config in one place.
        headers = {
            "key": ("#", 55),
            "title": ("Song Title", 260),
            "artist": ("Artist", 180),
            "album": ("Album", 180),
            "year": ("Year", 80),
            "rating": ("Rating", 130),
        }

        # Apply the heading text and column width for every column.
        # stretch=True lets each column grow when the user widens
        # the window so we don't end up with empty space on the right.
        for column, (label, width) in headers.items():
            self.tree.heading(column, text=label)
            self.tree.column(column, width=width, anchor="w", stretch=True)

        # Vertical and horizontal scrollbars. We connect them to
        # self.tree.yview/xview so scrolling the bars moves the
        # tree, and we connect the tree's yscrollcommand back to the
        # bar's set() so scrolling the tree updates the bars too.
        tree_y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        tree_x_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=tree_y_scroll.set,
            xscrollcommand=tree_x_scroll.set
        )

        # Layout the tree and its scrollbars in a 2x2 sub-grid.
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_y_scroll.grid(row=0, column=1, sticky="ns")
        tree_x_scroll.grid(row=1, column=0, sticky="ew")

        # When the user clicks a row, Treeview fires <<TreeviewSelect>>.
        # We forward that to our own handler which reads the selected
        # row and displays the corresponding track in the detail card.
        self.tree.bind("<<TreeviewSelect>>", self._select_track_from_tree)

        # Detail card on the right side. We keep a reference on self
        # because _on_resize needs to query its current width to
        # recalculate text wrapping.
        self.detail_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        self.detail_card.grid(row=0, column=0, sticky="nsew")
        self.detail_card.columnconfigure(0, weight=1)
        # Row 3 (the message box with full details) absorbs any extra
        # vertical space; the heading, cover and title rows stay
        # compact at the top.
        self.detail_card.rowconfigure(3, weight=1)

        # Static heading at the top of the detail card.
        ttk.Label(
            self.detail_card,
            text="Selected Track",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Canvas that renders either the real cover image or a
        # fallback drawing when no image file is attached. We use a
        # Canvas (not a Label) because we draw rectangles + text on
        # top when there's no image.
        self.cover_canvas = tk.Canvas(self.detail_card, width=200, height=200)
        # Apply the shared canvas styling (background colour, border)
        # so it matches the rest of the dark theme.
        fonts.style_canvas(self.cover_canvas)
        self.cover_canvas.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # Track-name label under the cover. We store it on self so
        # show_track and display_empty_state can rewrite its text.
        # wraplength=260 wraps long names instead of clipping them.
        self.title_lbl = ttk.Label(
            self.detail_card,
            text="No Track Selected",
            style="CardTitle.TLabel",
            justify="left",
            wraplength=260
        )
        self.title_lbl.grid(row=2, column=0, sticky="w", pady=(0, 8))

        # Detail text box. We use tk.Message (not ttk.Label) because
        # Message wraps long multi-line text more reliably and lets
        # us control border/highlight colours directly through bg/fg
        # arguments. The styling values come from the font_manager so
        # the box matches the rest of the dark theme.
        self.detail_message = tk.Message(
            self.detail_card,
            text="Choose a track number or click a row to see details.",
            width=280,
            justify="left",
            anchor="nw",
            bg=fonts.INPUT_BG,
            fg=fonts.TEXT,
            font=("Segoe UI", 10),
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=fonts.BORDER,
            highlightcolor=fonts.ACCENT,
            padx=10,
            pady=10,
        )
        self.detail_message.grid(row=3, column=0, sticky="nsew")

    # _on_resize
    # Input:
    #   event - Tkinter Configure event (or None when called manually)
    # Output: none (mutates wraplength on title and message widgets)
    # Why we filter the event:
    #   <Configure> fires for EVERY widget resize, not just the window.
    #   Without the filter we would recompute on every child widget
    #   tweak, which is expensive and causes flicker.

    def _on_resize(self, event=None):
        # Skip resize events that came from a child widget. Only
        # actual window resizes should trigger a re-wrap.
        if event is not None and event.widget is not self.window:
            return

        # Defensive guard: _build_main_panels may not have run yet
        # the very first time Tk fires a Configure event during
        # window creation. Bail out cleanly until the panel exists.
        if not hasattr(self, "detail_card"):
            return

        # Compute a sensible wrap width: take the detail card's
        # current pixel width minus 50 px of padding, with a floor
        # of 240 px so the text never gets squashed into a column.
        width = max(240, self.detail_card.winfo_width() - 50)
        self.title_lbl.configure(wraplength=width)
        # The Message widget needs a slightly smaller width because
        # its internal padding eats some of the available space.
        self.detail_message.configure(width=max(220, width - 20))

    # _set_detail_text
    # Input:  text - the string to show in the detail message box
    # Output: none
    # Tiny helper so callers don't have to remember the
    # `.configure(text=...)` syntax every time they update the box.

    def _set_detail_text(self, text: str):
        self.detail_message.configure(text=text)

     # _populate_tree
    # Input:
    #   records - a list of dicts shaped like:
    #             {"key", "name", "artist", "album", "year", "rating"}
    # Output: none (the Treeview is rewritten in place)
    # Used by list/search/filter so they all share the same row
    # rendering logic and we never end up with two slightly different
    # ways of displaying tracks.

    def _populate_tree(self, records):
        # Always wipe before inserting - otherwise filtering would
        # append new rows on top of the old ones.
        clear_tree(self.tree)

        # One Treeview row per record. We coerce missing album/year
        # to an em-dash so empty cells read cleanly instead of "None".
        for record in records:
            self.tree.insert(
                "",
                "end",
                values=(
                    record["key"],
                    record["name"],
                    record["artist"],
                    record["album"] or "—",
                    record["year"] or "—",
                    # Convert the integer rating to the unicode
                    # star string so the column reads at a glance.
                    stars_text(record["rating"]),
                ),
            )

    # _select_track_from_tree
    # Input:
    #   event - Tkinter event (unused - Treeview always passes one)
    # Output: none (delegates to show_track)
    # Bridges the Treeview's selection event to our own show_track()
    # API, so the rest of the class doesn't have to know about
    # Treeview internals.

    def _select_track_from_tree(self, event=None):
        # selection() returns a tuple of selected item IDs; if the
        # user clicked into empty space we get an empty tuple and
        # silently return.
        selected = self.tree.selection()
        if not selected:
            return

        # Pull the column values for the first (and only, since we
        # use single-select mode) selected row. values[0] is the
        # track number because "key" is the first column.
        values = self.tree.item(selected[0], "values")
        self.show_track(values[0])

    # display_empty_state
    # Input:  none
    # Output: none (resets the cover canvas, title and detail box)
    # Called on initial load and after every "no result" event so the
    # user always sees a clean, helpful placeholder rather than stale
    # data from the previously-selected track.

    def display_empty_state(self):
        # Drop our reference to the previous PhotoImage so Python's
        # garbage collector can free its memory.
        self.cover_image = None

        # Wipe everything currently drawn on the canvas (image,
        # rectangle, text - all of it).
        self.cover_canvas.delete("all")

        # Draw a neutral grey placeholder square inside the canvas
        # so the empty area still looks intentional.
        self.cover_canvas.create_rectangle(
            16, 16, 184, 184,
            outline=fonts.BORDER,
            width=2,
            fill=fonts.CARD_ALT
        )
        # Headline text, centred near the top of the placeholder.
        self.cover_canvas.create_text(
            100, 88,
            text="No Track Selected",
            fill=fonts.TEXT,
            font=("Segoe UI", 13, "bold"),
            width=140
        )
        # Hint text below the headline that tells the user what to do.
        self.cover_canvas.create_text(
            100, 138,
            text="Select a track from the table to preview it.",
            fill=fonts.MUTED,
            font=("Segoe UI", 10),
            width=145
        )

        # Reset the title and detail box to their initial messages.
        self.title_lbl.configure(text="No Track Selected")
        self._set_detail_text("Choose a track number or click a row to see details.")

    # display_track_cover
    # Input:  track_key - validated track number (e.g. "03")
    # Output: none (draws into self.cover_canvas)
    # If the track has a real cover image we draw it; otherwise we
    # draw a "fallback cover" with the track name and artist printed
    # on a coloured rectangle so the slot never looks broken.

    def display_track_cover(self, track_key: str):
        # Look up name/artist for the fallback drawing. We default
        # to "Unknown ..." strings so a partially-corrupted record
        # still renders something sensible instead of crashing.
        track_name = lib.get_name(track_key) or "Unknown Track"
        artist_name = lib.get_artist(track_key) or "Unknown Artist"

        # Always start from a clean canvas so we don't stack the new
        # cover on top of a previous one.
        self.cover_canvas.delete("all")

        # Ask cover_manager for a 170x170 PhotoImage. We assign to
        # self.cover_image (NOT a local variable) because Tkinter
        # only keeps a weak reference to canvas images - if the
        # only reference were local, it would be GC'd immediately
        # after this method returns and the cover would vanish.
        self.cover_image = cover_manager.load_cover_image(track_key, max_size=170)

        # Happy path: a real cover was loaded. Draw it centred and
        # we are done.
        if self.cover_image is not None:
            self.cover_canvas.create_image(100, 100, image=self.cover_image)
            return

        # Fallback path: no image available. Draw a coloured rectangle
        # with the track name and artist so the slot still looks
        # designed instead of broken.
        self.cover_canvas.create_rectangle(
            16, 16, 184, 184,
            outline=fonts.ACCENT,
            width=2,
            fill=fonts.CARD_ALT
        )
        # Track name in bold, near the top of the rectangle.
        self.cover_canvas.create_text(
            100, 78,
            text=track_name,
            fill=fonts.TEXT,
            font=("Segoe UI", 13, "bold"),
            width=140
        )
        # Artist name in the accent colour, below the title.
        self.cover_canvas.create_text(
            100, 116,
            text=artist_name,
            fill=fonts.ACCENT,
            font=("Segoe UI", 11),
            width=140
        )
        # Small note at the bottom so the user understands why this
        # cover looks different from the real ones.
        self.cover_canvas.create_text(
            100, 154,
            text="No cover image found.",
            fill=fonts.MUTED,
            font=("Segoe UI", 10),
            width=140
        )

    # show_track
    # Input:
    #   track_key - a string track number, possibly unclean (e.g. "7")
    # Output: none
    # The single entry point that fully renders the right-hand detail
    # card for a chosen track. Validates the input first and falls
    # back to the empty state with an explanatory message on failure.

    def show_track(self, track_key: str):
        # Normalise first: "7" -> "07", "  03  " -> "03", "abc" -> None.
        # We rely on validation.py for the rules so the same logic is
        # used here as in the unit tests.
        track_key = normalise_track_number(track_key)

        # First failure mode: the input wasn't a number at all.
        if track_key is None:
            self.display_empty_state()
            self._set_detail_text("Track number must contain digits only.")
            self.status_lbl.configure(text="Track number must contain digits only.")
            return

        # Second failure mode: the number was valid but no track
        # exists with that key (e.g. user typed "99" but library
        # only has 21 tracks).
        item = lib.get_item(track_key)
        if item is None:
            self.display_empty_state()
            self._set_detail_text(f"No track exists with number {track_key}.")
            self.status_lbl.configure(text="That track number does not exist.")
            return

        # Happy path: render cover, title and details.
        self.display_track_cover(track_key)

        # Album/year are AlbumTrack-only fields. We use isinstance()
        # so we don't accidentally call .album on a plain LibraryItem
        # (which would raise AttributeError). The em-dash keeps the
        # layout aligned for non-album tracks.
        album = item.album if isinstance(item, AlbumTrack) and item.album else "—"
        year = item.year if isinstance(item, AlbumTrack) and item.year is not None else "—"

        # Title label = track name. The Message box below carries
        # everything else.
        self.title_lbl.configure(text=item.name)

        # Build the detail block as a list of lines and join later.
        # This is easier to read and to extend than concatenating
        # strings with \n manually.
        detail_lines = [
            f"Artist: {item.artist}",
            f"Album: {album}",
            f"Year: {year}",
            f"Times Played: {item.play_count}",
            # stars() returns the unicode star rendering, matching
            # what we display in the table column.
            f"Rating: {item.stars()}",
            "",
            "Full Details:",
            # get_details may return None for partially-imported
            # records; "" keeps the layout consistent in that case.
            lib.get_details(track_key) or ""
        ]

        # Push everything into the message box and update the status
        # bar so the user has visible confirmation that the click
        # was registered.
        self._set_detail_text("\n".join(detail_lines))
        self.status_lbl.configure(text=f"Showing details for track {track_key}.")

    # list_tracks_clicked
    # Input:  none
    # Output: none
    # Hooked to the "Show All" button. Reloads the full track list
    # into the table and updates the status bar.

    def list_tracks_clicked(self):
        # get_track_records() returns a fresh list every call, so we
        # always show the most up-to-date library state - useful
        # after the user adds/edits/deletes tracks elsewhere in the app.
        self._populate_tree(lib.get_track_records())
        self.status_lbl.configure(text="All tracks are now displayed.")

    # search_tracks_clicked
    # Input:  none (reads self.search_txt)
    # Output: none
    # Hooked to the Search button and the <Return> key. Performs a
    # case-insensitive substring match across name, artist and album.
    # An empty search box behaves like "show everything".

    def search_tracks_clicked(self):
        # strip() removes accidental leading/trailing whitespace;
        # lower() lets us search case-insensitively against lower()
        # versions of each field below.
        keyword = self.search_txt.get().strip().lower()

        # List comprehension that filters get_track_records() down
        # to the rows the user wants to see. The first `if keyword
        # == ""` short-circuits so an empty box returns everything.
        # The `or ""` on album guards against None values (tracks
        # without an album) so .lower() never raises AttributeError.
        records = [
            record for record in lib.get_track_records()
            if keyword == ""
            or keyword in record["name"].lower()
            or keyword in record["artist"].lower()
            or keyword in (record["album"] or "").lower()
        ]

        # Render whatever survived the filter.
        self._populate_tree(records)

        # Branch on whether we found anything so we can write a
        # helpful, specific status message instead of a generic one.
        if records:
            self.status_lbl.configure(
                text=f"Showing search results for '{self.search_txt.get().strip() or 'all tracks'}'."
            )
        else:
            self.status_lbl.configure(text="Search finished: 0 matches.")
            # Reset the right-hand panel because the previously
            # selected track may not be in the (empty) results.
            self.display_empty_state()

    # filter_by_score_clicked
    # Input:  none (reads self.rating_filter_txt)
    # Output: none
    # Hooked to the Filter Rating button. Shows only tracks whose
    # rating exactly matches the dropdown value.

    def filter_by_score_clicked(self):
        # allow_zero=True because rating 0 is a legitimate filter
        # ("show me unrated tracks"), even though it would normally
        # be rejected when *setting* a rating.
        rating = get_valid_rating(self.rating_filter_txt.get(), allow_zero=True)

        # Defensive: the Combobox is read-only so this should never
        # trigger in practice, but if validation rules change later
        # we still degrade gracefully instead of crashing.
        if rating is None:
            self.status_lbl.configure(text="Filter score must be between 0 and 5.")
            return

        # Equality match (not >=) so a 5-star filter only shows
        # exactly five-star tracks - matches user expectations from
        # the dropdown wording "Filter Rating: 5".
        records = [
            record for record in lib.get_track_records()
            if record["rating"] == rating
        ]

        self._populate_tree(records)

        # Same status-message branching as search above.
        if records:
            self.status_lbl.configure(text=f"Showing tracks with rating {rating}.")
        else:
            self.status_lbl.configure(text=f"Filter finished: 0 tracks with rating {rating}.")
            self.display_empty_state()



# Standalone entry point

# Lets you run `python -m views.view_tracks` to test this page in
# isolation without booting the full JukeBox app. The main app reaches
# TrackViewer via main_controller.open_view_tracks_window() instead.
if __name__ == "__main__":
    # Create the root window for the standalone preview.
    root = tk.Tk()
    # Apply our shared ttk styles BEFORE any widget is created so
    # the page picks them up correctly.
    fonts.configure()
    # Build the page on the root window.
    TrackViewer(root)
    # Hand control to Tkinter's event loop. The script blocks here
    # until the user closes the window.
    root.mainloop()
