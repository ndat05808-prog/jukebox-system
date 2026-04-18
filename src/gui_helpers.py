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