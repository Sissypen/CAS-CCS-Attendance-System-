import tkinter as tk

PINK = "#ff6b81"
DARK_GRAY = "#2f3542"
LIGHT_BG = "#f1f2f6"
CARD_BG = "#ffffff"
TEXT_DARK = "#2e2e2e"
BLACK = "000000"

def mk_label(parent, text, font=("Segoe UI", 10, "bold"), fg=TEXT_DARK, bg=None):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg if bg is not None else parent["bg"])
