import tkinter as tk
from tkinter import ttk

from . import font_manager as fonts


def setup_page_container(parent, title: str = "", geometry: str = "", minsize: tuple | None = None):
    if isinstance(parent, (tk.Tk, tk.Toplevel)):
        if title:
            parent.title(title)
        if geometry:
            parent.geometry(geometry)
        if minsize:
            parent.minsize(*minsize)
        fonts.apply_theme(parent)


def set_text(text_area, content: str):
    text_area.configure(state="normal")
    text_area.delete("1.0", tk.END)
    text_area.insert("1.0", content)
    text_area.configure(state="disabled")


def configure_scrolled_text(widget):
    fonts.style_text_widget(widget)
    try:
        widget.configure(selectbackground=fonts.SELECT_BG, selectforeground=fonts.TEXT)
    except tk.TclError:
        pass


def stars_text(rating: int | None) -> str:
    rating = rating or 0
    return "★" * rating + "☆" * (5 - rating)


def clear_tree(tree: ttk.Treeview):
    for item_id in tree.get_children():
        tree.delete(item_id)


def bind_two_column_stacking(
    container,
    left,
    right,
    *,
    breakpoint: int = 900,
    left_weight: int = 2,
    right_weight: int = 1,
    side_row: int = 2,
    stacked_right_row: int | None = None,
    side_padx_left: tuple = (18, 10),
    side_padx_right: tuple = (10, 18),
    stacked_padx: tuple = (18, 18),
    pady: int = 10,
):
    """Toggle a two-column layout between side-by-side and stacked based on container width.

    `left` and `right` are the two frames currently gridded at (side_row, 0) / (side_row, 1).
    When the container is narrower than `breakpoint`, `right` is moved below `left`
    (spanning both columns). Safe to call on ttk widgets managed by grid.
    """
    if stacked_right_row is None:
        stacked_right_row = side_row + 1

    state = {"stacked": None}
    uniform_token = f"__stack_{id(container)}"

    def on_resize(event=None):
        if event is not None and event.widget is not container:
            return
        width = container.winfo_width()
        if width <= 1:
            return
        stacked = width < breakpoint
        if stacked == state["stacked"]:
            return
        if stacked:
            container.columnconfigure(0, weight=1, uniform="")
            container.columnconfigure(1, weight=0, uniform="")
            left.grid_configure(
                row=side_row, column=0, columnspan=2,
                padx=stacked_padx, pady=pady, sticky="nsew",
            )
            right.grid_configure(
                row=stacked_right_row, column=0, columnspan=2,
                padx=stacked_padx, pady=(0, pady), sticky="nsew",
            )
            container.rowconfigure(side_row, weight=1)
            container.rowconfigure(stacked_right_row, weight=1)
        else:
            container.columnconfigure(0, weight=left_weight, uniform=uniform_token)
            container.columnconfigure(1, weight=right_weight, uniform=uniform_token)
            left.grid_configure(
                row=side_row, column=0, columnspan=1,
                padx=side_padx_left, pady=pady, sticky="nsew",
            )
            right.grid_configure(
                row=side_row, column=1, columnspan=1,
                padx=side_padx_right, pady=pady, sticky="nsew",
            )
            container.rowconfigure(side_row, weight=1)
            container.rowconfigure(stacked_right_row, weight=0)
        state["stacked"] = stacked

    container.bind("<Configure>", on_resize)
    return on_resize


def create_scrollable_column(parent):
    """Wrap a vertically scrollable inner frame inside ``parent``.

    Returns the inner frame; caller should add content there. The ``parent`` is
    reconfigured to host a Canvas + Scrollbar, so pass a dedicated container.
    """
    for child in parent.winfo_children():
        child.destroy()

    parent.columnconfigure(0, weight=1)
    parent.columnconfigure(1, weight=0)
    parent.rowconfigure(0, weight=1)

    canvas = tk.Canvas(parent, borderwidth=0, highlightthickness=0, bg=fonts.BG)
    scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scroll.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    scroll.grid(row=0, column=1, sticky="ns")

    inner = ttk.Frame(canvas, style="Root.TFrame")
    window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_inner_configure(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event=None):
        canvas.itemconfigure(window_id, width=event.width if event else canvas.winfo_width())

    def _on_mousewheel(event):
        bbox = canvas.bbox("all")
        if bbox is None:
            return
        content_h = bbox[3] - bbox[1]
        if content_h <= canvas.winfo_height():
            return
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = int(-1 * (event.delta / 120)) if event.delta else 0
        if delta:
            canvas.yview_scroll(delta, "units")

    def _bind_wheel(_event=None):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

    def _unbind_wheel(_event=None):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    inner.bind("<Configure>", _on_inner_configure)
    canvas.bind("<Configure>", _on_canvas_configure)
    canvas.bind("<Enter>", _bind_wheel)
    canvas.bind("<Leave>", _unbind_wheel)
    inner.bind("<Enter>", _bind_wheel)
    inner.bind("<Leave>", _unbind_wheel)

    return inner


def create_metric_card(parent, title: str, value: str, subtitle: str = ""):
    card = ttk.Frame(parent, style="Card.TFrame", padding=16)
    ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
    ttk.Label(card, text=value, style="Metric.TLabel").pack(anchor="w", pady=(8, 2))
    ttk.Label(card, text=subtitle, style="CardMuted.TLabel").pack(anchor="w")
    return card


def draw_bar_chart(canvas: tk.Canvas, values: list[int], labels: list[str]):
    canvas.delete("all")
    width = max(canvas.winfo_width(), 360)
    height = max(canvas.winfo_height(), 180)
    left = 26
    right = width - 12
    top = 16
    bottom = height - 28
    chart_width = max(1, right - left)
    chart_height = max(1, bottom - top)

    canvas.create_line(left, bottom, right, bottom, fill=fonts.BORDER)
    canvas.create_line(left, top, left, bottom, fill=fonts.BORDER)

    if not values:
        canvas.create_text(width / 2, height / 2, text="No data yet", fill=fonts.MUTED, font=("Segoe UI", 11))
        return

    max_value = max(values)
    bar_count = len(values)
    gap = 12
    bar_width = max(10, (chart_width - gap * (bar_count + 1)) / max(1, bar_count))

    for index, value in enumerate(values):
        x1 = left + gap + index * (bar_width + gap)
        x2 = x1 + bar_width
        bar_height = 0 if max_value == 0 else (value / max_value) * (chart_height - 12)
        y1 = bottom - bar_height
        canvas.create_rectangle(x1, y1, x2, bottom, fill=fonts.ACCENT, outline="")
        canvas.create_text((x1 + x2) / 2, y1 - 8, text=str(value), fill=fonts.TEXT, font=("Segoe UI", 9))
        canvas.create_text((x1 + x2) / 2, bottom + 12, text=labels[index], fill=fonts.MUTED, font=("Segoe UI", 9))