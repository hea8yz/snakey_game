import math
import tkinter as tk


from snakey_assets import sfx
from snakey_content import ACCENT, BG, BORDER, DIM, PANEL, TEXT
from snakey_utils import blend, round_rect


def refocus_app(app):
    """Возвращает клавиатурный фокус главному окну.

    На Windows уничтоженный Toplevel-попап может унести фокус с собой:
    главное окно перестаёт получать нажатия клавиш ("мёртвое управление").
    Вызывается при закрытии любого попапа.
    """
    if app is None:
        return

    def _f():
        try:
            if app.winfo_exists():
                app.focus_force()
        except Exception:
            pass

    try:
        app.after_idle(_f)
    except Exception:
        _f()


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
def _round_inset(d, r):
    """Насколько срезан край скруглённого прямоугольника на глубине d от края."""
    if d <= 0:
        return r
    if d >= r:
        return 0.0
    return r - math.sqrt(max(0.0, r * r - (r - d) * (r - d)))


def gradient_round_btn(c, x1, y1, x2, y2, radius, c1, c2, tags="",
                       steps=14, key=None):
    """Скруглённый прямоугольник с вертикальным градиентом: рисуется узкими
    горизонтальными полосами, края которых срезаны по дуге угла.
    Возвращает список id полос (для анимации/перекраски)."""
    ids = []
    h = y2 - y1
    r = min(radius, h / 2.0, (x2 - x1) / 2.0)
    bh = h / steps
    for i in range(steps):
        by1 = y1 + i * bh
        by2 = by1 + bh
        ins = max(_round_inset(by1 - y1, r), _round_inset(y2 - by2, r))
        col = blend(c1, c2, (i + 0.5) / steps)
        ids.append(c.create_rectangle(x1 + ins, by1 - 0.5, x2 - ins,
                                      by2 + 0.5, fill=col, outline="",
                                      tags=tags))
    return ids


def repaint_gradient(c, ids, x1, y1, x2, y2, radius, c1, c2, steps=14):
    """Перекрашивает полосы, созданные gradient_round_btn (hover-анимация)."""
    h = y2 - y1
    r = min(radius, h / 2.0, (x2 - x1) / 2.0)
    bh = h / steps
    for i, item in enumerate(ids):
        by1 = y1 + i * bh
        by2 = by1 + bh
        ins = max(_round_inset(by1 - y1, r), _round_inset(y2 - by2, r))
        col = blend(c1, c2, (i + 0.5) / steps)
        c.coords(item, x1 + ins, by1 - 0.5, x2 - ins, by2 + 0.5)
        c.itemconfig(item, fill=col)


def draw_diff_stickers(c, x1, y1, x2, y2, diff_key, base_color, phase,
                       tags="stickers"):
    """Плавающие стикеры за текстом сложности (1.1): деревья (normal),
    восклицательные знаки (medium), черепа (hard), сирена опасности (extreme).
    Цвет — тот же оттенок, но темнее; лёгкое покачивание по phase."""
    col = blend(base_color, "#000000", 0.42)
    dark = blend(col, "#000000", 0.45)
    w, h = x2 - x1, y2 - y1
    cy = (y1 + y2) / 2.0
    spec = {"normal": (3, "tree"), "medium": (3, "bang"),
            "hard": (4, "skull"), "extreme": (4, "siren")}.get(diff_key,
                                                                (3, "tree"))
    n, kind = spec
    out = []
    for k in range(n):
        t = k / max(1, n - 1) if n > 1 else 0.5
        fx = x1 + w * (0.16 + 0.68 * t)
        fy = cy + math.sin(phase * 2.2 + k * 1.9) * h * 0.20
        s = h * 0.26
        if kind == "tree":
            out.append(c.create_polygon(fx, fy - s, fx - s * 0.75,
                                        fy + s * 0.55, fx + s * 0.75,
                                        fy + s * 0.55, fill=col,
                                        outline="", tags=tags))
            out.append(c.create_rectangle(fx - s * 0.12, fy + s * 0.55,
                                          fx + s * 0.12, fy + s * 0.95,
                                          fill=dark, outline="", tags=tags))
        elif kind == "bang":
            out.append(c.create_rectangle(fx - s * 0.16, fy - s,
                                          fx + s * 0.16, fy + s * 0.25,
                                          fill=col, outline="", tags=tags))
            out.append(c.create_oval(fx - s * 0.17, fy + s * 0.45,
                                     fx + s * 0.17, fy + s * 0.8,
                                     fill=col, outline="", tags=tags))
        elif kind == "skull":
            out.append(c.create_oval(fx - s * 0.75, fy - s * 0.8,
                                     fx + s * 0.75, fy + s * 0.55,
                                     fill=col, outline="", tags=tags))
            out.append(c.create_rectangle(fx - s * 0.4, fy + s * 0.2,
                                          fx + s * 0.4, fy + s * 0.75,
                                          fill=col, outline="", tags=tags))
            out.append(c.create_oval(fx - s * 0.45, fy - s * 0.25,
                                     fx - s * 0.1, fy + s * 0.15,
                                     fill=dark, outline="", tags=tags))
            out.append(c.create_oval(fx + s * 0.1, fy - s * 0.25,
                                     fx + s * 0.45, fy + s * 0.15,
                                     fill=dark, outline="", tags=tags))
        else:  # siren
            out.append(c.create_arc(fx - s * 0.7, fy - s * 0.7,
                                    fx + s * 0.7, fy + s * 0.7, start=0,
                                    extent=180, fill=col, outline="",
                                    tags=tags))
            out.append(c.create_rectangle(fx - s * 0.85, fy,
                                          fx + s * 0.85, fy + s * 0.22,
                                          fill=dark, outline="", tags=tags))
            for a in (-1, 1):
                out.append(c.create_line(fx + a * s * 1.05, fy - s * 0.35,
                                         fx + a * s * 1.35, fy - s * 0.7,
                                         fill=col, width=2, tags=tags))
    return out


class GradientButton(tk.Canvas):
    """Кнопка с вертикальной градиентной заливкой (1.1).
    Hover-анимация: плавное увеличение и посветление, у сложности — стикеры.
    Совместима с RoundButton по контракту (.text/.base_fg/.command/repaint)."""

    def __init__(self, master, text, command=None, width=200, height=44,
                 radius=16, c1=ACCENT, c2="#2ea043", fg="#ffffff",
                 app_bg=BG, font=None, hover_scale=0.045, steps=14,
                 sticker_key=None, sticker_color=None):
        super().__init__(master, width=width, height=height, bg=app_bg,
                         highlightthickness=0,
                         cursor="hand2" if command else "arrow")
        self.command = command
        self.radius = radius
        self.text = text
        self.c1 = c1
        self.c2 = c2
        self.base_fg = fg
        self.app_bg = app_bg
        self.font = font or ("Segoe UI", 12, "bold")
        self._width = width
        self._height = height
        self.hover_scale = hover_scale
        self.steps = steps
        self.sticker_key = sticker_key
        self.sticker_color = sticker_color
        self.disabled = command is None
        self._t = 0.0
        self._last_qt = None
        self._anim_job = None
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self._paint()

    def repaint(self):
        self._paint()

    def set_colors(self, c1, c2):
        self.c1, self.c2 = c1, c2
        self._paint()

    def _geom(self):
        t = 0.0 if self.disabled else self._t
        grow = 1.0 + self.hover_scale * t
        w, h = self._width * grow, self._height * grow
        ox = (self._width - w) / 2.0
        oy = (self._height - h) / 2.0
        return ox + 1, oy + 1, ox + w - 1, oy + h - 1, t

    def _paint(self):
        self.delete("all")
        # перф: запоминаем квантованный t — повторные _paint с тем же состоянием
        # (например дублирующие шаги анимации) отрисовываются заново только при смене
        self._last_qt = round(self._t, 2)
        self._ids = []
        x1, y1, x2, y2, t = self._geom()
        r = self.radius
        if self.disabled:
            round_rect(self, x1, y1, x2, y2, r, fill=blend(self.c1, BG, 0.55),
                       outline=BORDER)
        else:
            round_rect(self, x1 + 1, y1 + 4, x2 + 1, y2 + 4, r, fill="#000000",
                       stipple="gray25", outline="")
            c1 = blend(self.c1, "#ffffff", 0.16 * t)
            c2 = blend(self.c2, "#ffffff", 0.16 * t)
            self._ids = gradient_round_btn(self, x1, y1, x2, y2, r, c1, c2,
                                           steps=self.steps)
            round_rect(self, x1 + 3, y1 + 2, x2 - 3,
                       y1 + (y2 - y1) * 0.42, max(4, r - 6),
                       fill="#ffffff", stipple="gray25" if t < 0.5 else "gray50",
                       outline="")
            if self.sticker_key and t > 0.05:
                draw_diff_stickers(self, x1 + 4, y1 + 2, x2 - 4, y2 - 2,
                                   self.sticker_key,
                                   self.sticker_color or self.c1,
                                   self._t * 3.0)
        self.create_text(self._width / 2, self._height / 2 - 1,
                         text=self.text, font=self.font, fill=self.base_fg)

    def _enter(self, _e=None):
        if self.disabled or self._anim_job is not None:
            return
        self._anim_to(1.0)

    def _leave(self, _e=None):
        self._anim_to(0.0)

    def _anim_to(self, target):
        if self._anim_job is not None:
            try:
                self.after_cancel(self._anim_job)
            except Exception:
                pass
            self._anim_job = None

        def step():
            self._anim_job = None
            d = target - self._t
            if abs(d) < 0.08:
                self._t = target
                self._paint()
                return
            self._t += d * 0.45
            # перф: перекраска только когда квантованный t реально сменился
            if round(self._t, 2) != self._last_qt:
                self._paint()
            self._anim_job = self.after(28, step)

        step()

    def _press(self, _e=None):
        if not self.disabled:
            self._t = 0.0
            self._paint()

    def _release(self, event):
        if self.disabled:
            return
        self._t = 1.0
        self._paint()
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
        self._last_cols = []
        bh = 2004 / steps
        for i in range(steps):
            self.bands.append(self.create_rectangle(-4, i * bh - 2, 2004,
                                                    (i + 1) * bh + 2,
                                                    outline="", tags="band"))
        self._paint_bands()

    def _paint_bands(self):
        n = max(1, self.steps - 1)
        # перф: цвет квантуется и сравнивается с последним применённым —
        # itemconfig вызывается только для полос, чей цвет реально сменился
        last = getattr(self, "_last_cols", None)
        if last is None or len(last) != len(self.bands):
            last = self._last_cols = [None] * len(self.bands)
        for i, item in enumerate(self.bands):
            t = i / n
            col = blend(self.g1, self.g2, t)
            wave = round(math.sin(self.phase + t * 4.0) * 0.05, 2)
            if wave > 0:
                col = blend(col, self.accent, wave)
            if col != last[i]:
                self.itemconfig(item, fill=col)
                last[i] = col

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

    def refocus(self):
        refocus_app(self.app)

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
    def _center_window(win, parent=None):
        """Центрирует окно ПОВЕРХ главного окна игры, а не по центру экрана."""
        win.update_idletasks()
        ww = win.winfo_reqwidth()
        wh = win.winfo_reqheight()
        x = y = None
        try:
            top = (parent or win.master).winfo_toplevel()
            pw, ph = top.winfo_width(), top.winfo_height()
            if pw > 1 and ph > 1:
                px, py = top.winfo_rootx(), top.winfo_rooty()
                x = px + max(0, (pw - ww) // 2)
                y = py + max(0, (ph - wh) // 2 - 20)
        except Exception:
            x = y = None
        if x is None:
            # главное окно ещё не отображено — центр экрана
            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = max(0, (sw - ww) // 2)
            y = max(0, (sh - wh) // 2 - 20)
        win.geometry(f"+{x}+{y}")

    def _borderless(self, win, title, width, wbg, on_close=None):
        user_close = on_close or win.destroy

        def close():
            user_close()
            # закрыли попап — моментально возвращаем фокус главному окну
            self.refocus()
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