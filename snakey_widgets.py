import math
import tkinter as tk


from snakey_assets import sfx
from snakey_content import ACCENT, BG, BORDER, DIM, PANEL, TEXT
from snakey_utils import blend, round_rect


class RoundButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=200, height=44,
                 radius=16, bg=PANEL, fg=TEXT, app_bg=BG, font=None,
                 outline=None):
        super().__init__(master, width=width, height=height, bg=app_bg,
                         highlightthickness=0,
                         cursor="hand2" if command else "arrow")
        self.command = command
        self.radius = radius
        self.text = text
        self.base_bg = bg
        self.base_fg = fg
        self.app_bg = app_bg
        self.outline = outline
        self.font = font or ("Segoe UI", 12, "bold")
        self._width = width
        self._height = height
        self.disabled = command is None
        self.hover_bg = blend(bg, "#ffffff", 0.12)
        self.press_bg = blend(bg, "#000000", 0.18)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)
        self.bind("<Enter>", lambda e: None if self.disabled
                  else self._paint(self.hover_bg))
        self.bind("<Leave>", lambda e: self._paint(self.base_bg))
        self._paint(self.base_bg)

    def repaint(self):
        self._paint(self.base_bg)

    def _paint(self, bg=None):
        if bg is None:
            bg = self.base_bg
        self.delete("all")
        w, h, r = self._width, self._height, self.radius
        if self.disabled:
            round_rect(self, 1, 1, w - 1, h - 1, r, fill=bg,
                       outline=self.outline or BORDER)
        else:
            round_rect(self, 2, 5, w - 2, h + 1, r, fill="#000000",
                       stipple="gray25", outline="")
            round_rect(self, 1, 1, w - 1, h - 1, r, fill=bg,
                       outline=self.outline or blend(bg, "#000000", 0.3))
            round_rect(self, 4, 3, w - 4, h * 0.42, max(4, r - 6),
                       fill=blend(bg, "#ffffff", 0.10), outline="")
        self.create_text(w / 2, h / 2 - 1, text=self.text, font=self.font,
                         fill=self.base_fg)

    def _press(self, _event=None):
        if not self.disabled:
            self._paint(self.press_bg)

    def _release(self, event):
        if self.disabled:
            return
        self._paint(self.base_bg)
        if 0 <= event.x <= self._width and 0 <= event.y <= self._height \
                and self.command:
            sfx("click")
            self.command()
class GradientBG(tk.Canvas):
    def __init__(self, master, c1, c2, accent=ACCENT, steps=20):
        super().__init__(master, width=100, height=100, bg=c1,
                         highlightthickness=0)
        self.g1, self.g2, self.accent = c1, c2, accent
        self.steps = steps
        self.phase = 0.0
        self.job = None
        self.bands = []
        bh = 2004 / steps
        for i in range(steps):
            self.bands.append(self.create_rectangle(-4, i * bh - 2, 2004,
                                                    (i + 1) * bh + 2,
                                                    outline="", tags="band"))
        self._paint_bands()

    def _paint_bands(self):
        n = max(1, self.steps - 1)
        for i, item in enumerate(self.bands):
            t = i / n
            col = blend(self.g1, self.g2, t)
            wave = math.sin(self.phase + t * 4.0) * 0.05
            if wave > 0:
                col = blend(col, self.accent, wave)
            self.itemconfig(item, fill=col)

    def set_animated(self, on):
        if on and self.job is None:
            self._tick()
        elif not on and self.job is not None:
            self.after_cancel(self.job)
            self.job = None

    def _tick(self):
        self.phase += 0.045
        self._paint_bands()
        # noinspection PyArgumentList
        self.job = self.after(90, self._tick)
class Screen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=BG)
        self.app = app

    def on_show(self):
        pass

    def on_hide(self):
        pass

    def on_key(self, event):
        pass

    def on_wheel(self, event):
        scroller = getattr(self, "scroller", None)
        if not hasattr(scroller, "yview_scroll"):
            return
        num = getattr(event, "num", 0)
        if num == 4:
            scroller.yview_scroll(-2, "units")
        elif num == 5:
            scroller.yview_scroll(2, "units")
        else:
            scroller.yview_scroll(-2 if getattr(event, "delta", 0) > 0 else 2,
                                  "units")

    def _raise_window(self, attr):
        win = self.__dict__.get(attr)
        if win is None:
            return False
        try:
            alive = win.winfo_exists()
        except tk.TclError:
            alive = False
        if alive:
            win.deiconify()
            win.lift()
            win.focus_force()
            return True
        return False

    @staticmethod
    def _center_window(win):
        win.update_idletasks()
        ww = win.winfo_reqwidth()
        wh = win.winfo_reqheight()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = max(0, (sw - ww) // 2)
        y = max(0, (sh - wh) // 2 - 20)
        win.geometry(f"+{x}+{y}")

    def _borderless(self, win, title, width, wbg, on_close=None):
        close = on_close or win.destroy
        win.title(title)
        try:
            win.overrideredirect(True)
            if not win.overrideredirect():
                return None
        except Exception:
            return None
        bar = tk.Canvas(win, width=width, height=42, bg=wbg,
                        highlightthickness=0)
        bar.pack(fill="x")
        round_rect(bar, 1, 1, width - 2, 41, 12, fill=PANEL, outline=BORDER)
        bar.create_oval(14, 13, 28, 27, fill=ACCENT, outline="")
        bar.create_text(38, 21, text=title, anchor="w",
                        font=(self.app.font_ui, 11, "bold"), fill=TEXT)
        bar.create_oval(width - 34, 10, width - 12, 32,
                        fill=blend(PANEL, "#ffffff", 0.08), outline=BORDER)
        bar.create_text(width - 23, 21, text="\u2715",
                        font=(self.app.font_ui, 10, "bold"), fill=DIM)
        state = {"off": None}

        def press(event):
            if event.x >= width - 36:
                close()
                return
            state["off"] = (event.x, event.y)
            win.focus_force()

        def drag(event):
            off = state["off"]
            if off is not None:
                win.geometry(f"+{event.x_root - off[0]}"
                             f"+{event.y_root - off[1]}")

        bar.bind("<Button-1>", press)
        bar.bind("<B1-Motion>", drag)
        bar.bind("<ButtonRelease-1>",
                 lambda e: state.__setitem__("off", None))
        try:
            win.bind("<Escape>", lambda e: close())
        except Exception:
            pass
        return bar