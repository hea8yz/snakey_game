import math
import tkinter as tk


from snakey_assets import sfx
from snakey_content import (


    ACCENT,
    ACCENT_BRIGHT,
    ACCENT_DARK,
    ACCESSORIES,
    BG,
    BLUE,
    BORDER,
    CHANGELOG,
    DIFFICULTIES,
    DIM,
    FOOD_ITEMS,
    GOLD,
    LOCKED_BG,
    PANEL,
    TEXT,
    THEMES,
    VERSION,
)
from snakey_save import exp_for_level, level_from_exp
from snakey_utils import blend, gradient_bands, round_rect
from snakey_widgets import GradientBG, RoundButton, Screen

class MenuScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.bg = GradientBG(self, BG, "#121c2c")
        self.bg.pack(fill="both", expand=True)
        self.bg.bind("<Configure>", lambda e: self._layout())
        self.anim_t = 0.0
        self.anim_job = None
        self._btn_ids = {}
        self._btn_cmds = {}
        self._title_letters = []
        self._title_snake = []
        self._title_eyes = []
        self._level_shimmer = None
        self._level_span = (0, 0, 0, 1)
        self._levelup_win = None
        self._ach_win = None
        self._changelog_win = None
        # один обработчик на весь canvas: клик всегда срабатывает ровно раз,
        # даже если элементы меню пересоздаются или перекрываются
        self.bg.bind("<Button-1>", self._on_canvas_click, add="+")
        self._layout()

    def _on_canvas_click(self, event):
        try:
            items = self.bg.find_overlapping(event.x - 1, event.y - 1,
                                             event.x + 1, event.y + 1)
        except tk.TclError:
            return
        for iid in reversed(items):
            try:
                tags = self.bg.gettags(iid)
            except tk.TclError:
                continue
            for t in tags:
                if t.startswith("btn_"):
                    key = t[4:]
                    self._hover(key, True)
                    self.bg.after(120, lambda k=key: self._hover(k, False))
                    sfx("click")
                    cmd = self._btn_cmds.get(key)
                    if cmd is not None:
                        cmd()
                    return

    def _geom(self):
        w = self.bg.winfo_width() or 0
        h = self.bg.winfo_height() or 0
        if w < 50:
            w = 900
        if h < 50:
            h = 740
        return w, h

    def _btn(self, key, cx, cy, bw, bh, text, cmd, bg=PANEL, fg=TEXT,
             fsize=12):
        tag = f"btn_{key}"
        x1, y1 = cx - bw / 2.0, cy - bh / 2.0
        x2, y2 = cx + bw / 2.0, cy + bh / 2.0
        r = min(bh / 2.0, 18)
        poly = round_rect(self.bg, x1, y1, x2, y2, r, fill=bg,
                          outline=blend(bg, "#ffffff", 0.28),
                          tags=("menu", tag))
        round_rect(self.bg, x1 + 4, y1 + 3, x2 - 4, y1 + bh * 0.42,
                   max(4, r - 6), fill=blend(bg, "#ffffff", 0.10),
                   outline="", tags=("menu", tag))
        self.bg.create_text(cx, cy + 1, text=text,
                            font=(self.app.font_ui, fsize, "bold"), fill=fg,
                            tags=("menu", tag))
        self._btn_ids[key] = (poly, bg)
        self._btn_cmds[key] = cmd
        self.bg.tag_bind(tag, "<Enter>",
                         lambda e, k=key: self._hover(k, True))
        self.bg.tag_bind(tag, "<Leave>",
                         lambda e, k=key: self._hover(k, False))

    def _hover(self, key, on):
        info = self._btn_ids.get(key)
        if not info:
            return
        try:
            self.bg.itemconfig(info[0],
                               fill=blend(info[1], "#ffffff", 0.16 if on else 0.0))
        except tk.TclError:
            pass

    def _layout(self):
        w, h = self._geom()
        self.bg.delete("menu")
        self._btn_ids = {}
        self._btn_cmds = {}
        self._title_letters = []
        self._title_snake = []
        self._title_eyes = []
        self._level_shimmer = None
        round_rect(self.bg, 10, 6, 74, 30, 12, fill=PANEL, outline=BORDER,
                   tags="menu")
        self.bg.create_text(42, 18, text=f"v{VERSION}",
                            font=(self.app.font_ui, 9, "bold"), fill=GOLD,
                            tags="menu")
        self._btn("log", 152, 18, 116, 24, "update log",
                  self._open_changelog, bg=PANEL, fg=DIM, fsize=8)
        self._draw_title(w, h)
        self._draw_level(w, h)
        self.bg.create_text(w / 2, h * 0.455,
                            text=f"\u25c9  {self.app.save['coins']} \u043c\u043e\u043d\u0435\u0442",
                            font=(self.app.font_ui, 13, "bold"), fill=GOLD,
                            tags="menu")
        y0 = h * 0.52
        self._btn("play", w / 2, y0, 260, 54, "\u0418\u0413\u0420\u0410\u0422\u042c",
                  self._play_classic, bg=ACCENT, fg="#06220c", fsize=15)
        self._btn("mini", w / 2, y0 + 56, 260, 48, "\u041c\u0418\u041d\u0418-\u0418\u0413\u0420\u042b",
                  lambda: self.app.show("MiniScreen"), bg=BLUE, fg="#061224",
                  fsize=13)
        self._btn("ach", w / 2, y0 + 112, 260, 48, "\u0414\u041e\u0421\u0422\u0418\u0416\u0415\u041d\u0418\u042f",
                  lambda: self.app.show("AchScreen"), bg="#8957e5",
                  fg="#f4efff", fsize=13)
        self._btn("shop", w / 2, y0 + 168, 260, 48, "\u041c\u0410\u0413\u0410\u0417\u0418\u041d",
                  lambda: self.app.show("ShopScreen"), fsize=13)
        self._btn("set", w / 2, y0 + 224, 260, 48, "\u041d\u0410\u0421\u0422\u0420\u041e\u0419\u041a\u0418",
                  lambda: self.app.show("SettingsScreen"), fsize=13)
        self.bg.create_text(w / 2, h * 0.94,
                            text=f"\u0420\u0435\u043a\u043e\u0440\u0434: {self.app.save['highscore']}",
                            font=(self.app.font_ui, 11), fill=DIM, tags="menu")
        self.bg.create_text(w / 2, h * 0.975,
                            text="WASD / \u0441\u0442\u0440\u0435\u043b\u043a\u0438 \u00b7 P \u2014 \u043f\u0430\u0443\u0437\u0430 \u00b7 R \u2014 \u0437\u0430\u043d\u043e\u0432\u043e",
                            font=(self.app.font_ui, 9), fill="#3a4149",
                            tags="menu")

    def _play_classic(self):
        self.app.next_mode = "classic"
        self.app.show("GameScreen")

    def on_show(self):
        try:
            self._layout()
        except tk.TclError:
            pass
        if not self.app.save.get("low_spec"):
            self.bg.set_animated(True)
            self._start_anim()
        try:
            if not self._maybe_show_levelup():
                self._maybe_show_achievements()
        except tk.TclError:
            # даже при ошибке отрисовки уведомления не теряем:
            # pending остаётся в сохранении и покажется при следующем on_show
            pass

    def on_hide(self):
        self.bg.set_animated(False)
        if self.anim_job is not None:
            self.after_cancel(self.anim_job)
            self.anim_job = None

    def _draw_title(self, w=None, h=None):
        if w is None:
            w, h = self._geom()
        self.bg.delete("title")
        t = self.anim_t
        cy = h * 0.16
        font = (self.app.font_title, 46, "bold")
        self._title_letters = []
        for i, ch in enumerate("SNAKEY"):
            x = w / 2 - 110 + i * 44
            y = cy + math.sin(t * 0.08 + i * 0.6) * 3
            sh = self.bg.create_text(x + 3, y + 3, text=ch, font=font,
                                     fill="#0e4415", tags=("menu", "title"))
            main = self.bg.create_text(x, y, text=ch, font=font,
                                       fill=ACCENT, tags=("menu", "title"))
            self._title_letters.append((sh, main, i))
        self.bg.create_text(w / 2, cy + 44,
                            text="\u0441\u043e\u0431\u0438\u0440\u0430\u0439 \u0435\u0434\u0443 \u2014 \u0441\u0442\u0430\u043d\u044c \u0441\u0430\u043c\u043e\u0439 \u0434\u043b\u0438\u043d\u043d\u043e\u0439 \u0437\u043c\u0435\u0439\u043a\u043e\u0439",
                            font=(self.app.font_ui, 10), fill=DIM,
                            tags=("menu", "title"))
        self._title_snake = []
        self._title_eyes = []
        for i in range(15):
            x = w / 2 - 132 + i * 18
            y = cy + 76 + math.sin(t * 0.15 + i * 0.5) * 4
            if i == 14:
                head = self.bg.create_oval(x - 9, y - 9, x + 9, y + 9,
                                           fill=ACCENT_BRIGHT, outline="",
                                           tags=("menu", "title"))
                self._title_snake.append((head, i, 9))
                for ex in (x + 3, x + 7):
                    eye = self.bg.create_oval(ex - 2, y - 5, ex + 2, y - 1,
                                              fill="#06220c", outline="",
                                              tags=("menu", "title"))
                    self._title_eyes.append((eye, ex - x, -3.0))
            else:
                body = self.bg.create_oval(x - 7, y - 7, x + 7, y + 7,
                                           fill=blend(ACCENT, BG, 0.04 * i),
                                           outline="", tags=("menu", "title"))
                self._title_snake.append((body, i, 7))

    def _anim_title(self):
        t = self.anim_t
        w, h = self._geom()
        cy = h * 0.16
        for sh, main, i in self._title_letters:
            glow = 0.15 + 0.75 * (0.5 + 0.5 * math.sin(t * 0.12 - i * 0.7))
            x = w / 2 - 110 + i * 44
            y = cy + math.sin(t * 0.08 + i * 0.6) * 3
            self.bg.coords(sh, x + 3, y + 3)
            self.bg.coords(main, x, y)
            self.bg.itemconfig(main, fill=blend(ACCENT, ACCENT_BRIGHT, glow))
        for iid, i, r in self._title_snake:
            x = w / 2 - 132 + i * 18
            y = cy + 76 + math.sin(t * 0.15 + i * 0.5) * 4
            self.bg.coords(iid, x - r, y - r, x + r, y + r)
        hx = w / 2 - 132 + 14 * 18
        hy = cy + 76 + math.sin(t * 0.15 + 14 * 0.5) * 4
        for eye, ox, oy in self._title_eyes:
            self.bg.coords(eye, hx + ox - 2, hy + oy - 2,
                           hx + ox + 2, hy + oy + 2)

    def _draw_level(self, w=None, h=None):
        if w is None:
            w, h = self._geom()
        self.bg.delete("level")
        exp = self.app.save.get("exp", 0)
        level = level_from_exp(exp)
        cur = exp_for_level(level)
        nxt = exp_for_level(level + 1)
        frac = max(0.0, min(1.0, (exp - cur) / (nxt - cur)))
        cx = w / 2
        bx0, by = cx - 170, h * 0.35 - 32
        bx1, by1 = cx + 170, h * 0.35 + 32
        round_rect(self.bg, bx0, by, bx1, by1, 16, fill=PANEL,
                   outline=blend(ACCENT, BG, 0.5), tags=("menu", "level"))
        self.bg.create_oval(bx0 + 10, by + 10, bx0 + 50, by + 50,
                            fill=ACCENT_DARK, outline=ACCENT,
                            tags=("menu", "level"))
        self.bg.create_text(bx0 + 30, by + 31, text=str(level),
                            font=(self.app.font_title, 16, "bold"),
                            fill=ACCENT_BRIGHT, tags=("menu", "level"))
        self.bg.create_text(bx0 + 62, by + 15, text=f"\u0423\u0420\u041e\u0412\u0415\u041d\u042c {level}",
                            anchor="w", font=(self.app.font_ui, 11, "bold"),
                            fill=TEXT, tags=("menu", "level"))
        self.bg.create_text(bx0 + 62, by + 33,
                            text=f"{exp} EXP \u00b7 \u0434\u043e \u0443\u0440. {level + 1}: {nxt - exp}",
                            anchor="w", font=(self.app.font_ui, 8), fill=DIM,
                            tags=("menu", "level"))
        px0, py0, px1, py1 = bx0 + 64, by + 44, bx1 - 12, by + 53
        round_rect(self.bg, px0, py0, px1, py1, 4, fill=LOCKED_BG,
                   outline="", tags=("menu", "level"))
        if frac > 0:
            width = (px1 - px0) * frac
            seg_w = width / 6
            for k in range(6):
                col = blend(GOLD, ACCENT_BRIGHT, k / 5)
                round_rect(self.bg, px0 + k * seg_w, py0,
                           px0 + (k + 1) * seg_w, py1, 3, fill=col,
                           outline="", tags=("menu", "level"))
            if not self.app.save.get("low_spec"):
                span = max(1, (px1 - px0 - 16))
                sx = px0 + (self.anim_t * 4) % span
                self._level_shimmer = self.bg.create_rectangle(
                    sx, py0 + 1, sx + 14, py1 - 1,
                    fill=blend(GOLD, "#ffffff", 0.45),
                    outline="", tags=("menu", "level"))
                self._level_span = (px0, py0 + 1, py1 - 1, span)

    def _maybe_show_levelup(self):
        pending = self.app.save.get("pending_level", 0)
        if not pending:
            return False
        if self._raise_window("_levelup_win"):
            return True
        unlocked = [f"\u0421\u043b\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u00ab{cfg['label']}\u00bb"
                    for cfg in DIFFICULTIES.values() if cfg["level"] == pending]
        for item in THEMES:
            if item.get("level") == pending and item["price"] > 0:
                unlocked.append(f"\u0424\u043e\u043d \u00ab{item['name']}\u00bb")
        for item in FOOD_ITEMS:
            if item.get("level") == pending and item["price"] > 0:
                unlocked.append(f"\u0415\u0434\u0430 \u00ab{item['name']}\u00bb")
        for item in ACCESSORIES:
            if item.get("level") == pending and item["price"] > 0:
                unlocked.append(f"\u0410\u043a\u0441\u0435\u0441\u0441\u0443\u0430\u0440 \u00ab{item['name']}\u00bb")
        win = tk.Toplevel(self)
        self._levelup_win = win
        win.title("\u041d\u043e\u0432\u044b\u0439 \u0443\u0440\u043e\u0432\u0435\u043d\u044c!")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self.app)
        self._borderless(win, "\u2728 \u041d\u043e\u0432\u044b\u0439 \u0443\u0440\u043e\u0432\u0435\u043d\u044c!", 380, BG)
        cv = tk.Canvas(win, width=380, height=210, bg=BG, highlightthickness=0)
        cv.pack()
        cx, cyc = 190, 106
        for k in range(16):
            a = math.radians(k * 22.5)
            col = GOLD if k % 2 else ACCENT
            cv.create_line(cx + math.cos(a) * 70, cyc + math.sin(a) * 70,
                           cx + math.cos(a) * 98, cyc + math.sin(a) * 98,
                           fill=col, width=2)
        cv.create_oval(120, 36, 260, 176, outline=blend(GOLD, BG, 0.4),
                       width=2)
        cv.create_oval(126, 42, 254, 170, fill=ACCENT_DARK, outline=ACCENT,
                       width=3)
        cv.create_oval(138, 54, 242, 158,
                       fill=blend(ACCENT_DARK, "#000000", 0.3), outline="")
        cv.create_text(cx, cyc - 2, text=str(pending),
                       font=(self.app.font_title, 44, "bold"),
                       fill=ACCENT_BRIGHT)
        cv.create_text(cx, 192, text="\u0423\u0420\u041e\u0412\u0415\u041d\u042c \u041f\u041e\u0412\u042b\u0428\u0415\u041d!",
                       font=(self.app.font_title, 16, "bold"), fill=GOLD)
        tk.Label(win, text=f"\u0422\u0435\u043f\u0435\u0440\u044c \u0443 \u0442\u0435\u0431\u044f {self.app.save.get('exp', 0)} EXP",
                 bg=BG, fg=TEXT, font=(self.app.font_ui, 11, "bold")).pack()
        if unlocked:
            tk.Label(win, text="\u041d\u041e\u0412\u041e\u0415 \u0414\u041e\u0421\u0422\u0423\u041f\u041d\u041e:", bg=BG, fg=ACCENT,
                     font=(self.app.font_ui, 10, "bold")).pack(pady=(8, 0))
            for line in unlocked[:6]:
                tk.Label(win, text=f"\u2605  {line}", bg=PANEL, fg=TEXT,
                         font=(self.app.font_ui, 9, "bold")).pack(
                             pady=1, ipadx=10, ipady=2)
        RoundButton(win, "\u041a\u0440\u0443\u0442\u043e!", win.destroy, width=150, height=40,
                    bg=ACCENT, fg="#06220c", app_bg=BG,
                    font=(self.app.font_ui, 12, "bold")).pack(pady=14)
        self._center_window(win)
        # \u043e\u043a\u043d\u043e \u0443\u0441\u043f\u0435\u0448\u043d\u043e \u043f\u043e\u0441\u0442\u0440\u043e\u0435\u043d\u043e \u2014 \u0442\u043e\u043b\u044c\u043a\u043e \u0442\u0435\u043f\u0435\u0440\u044c \u0441\u0431\u0440\u0430\u0441\u044b\u0432\u0430\u0435\u043c pending
        self.app.save["pending_level"] = 0
        self.app.commit()
        sfx("levelup")
        win.lift()
        win.focus_force()
        return True

    def _maybe_show_achievements(self):
        pending = self.app.save.get("pending_ach", [])
        if not pending:
            return False
        if self._raise_window("_ach_win"):
            return True
        win = tk.Toplevel(self)
        self._ach_win = win
        win.title("\u0414\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u0435 \u043f\u043e\u043b\u0443\u0447\u0435\u043d\u043e!")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self.app)
        self._borderless(win, "\u2605 \u0414\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u0435 \u043f\u043e\u043b\u0443\u0447\u0435\u043d\u043e!", 380, BG)
        cv = tk.Canvas(win, width=380, height=170, bg=BG, highlightthickness=0)
        cv.pack()
        cx, cyc = 190, 78
        for k in range(14):
            a = math.radians(k * (360 / 14))
            col = "#8957e5" if k % 2 else "#c9a8ff"
            cv.create_line(cx + math.cos(a) * 52, cyc + math.sin(a) * 52,
                           cx + math.cos(a) * 72, cyc + math.sin(a) * 72,
                           fill=col, width=2)
        cv.create_oval(138, 26, 242, 130, fill="#3a2a5e", outline="#8957e5",
                       width=3)
        cv.create_text(cx, cyc - 2, text="\u2605",
                       font=(self.app.font_title, 40, "bold"), fill="#c9a8ff")
        cv.create_text(cx, 152, text="\u0414\u041e\u0421\u0422\u0418\u0416\u0415\u041d\u0418\u0415 \u041f\u041e\u041b\u0423\u0427\u0415\u041d\u041e!",
                       font=(self.app.font_title, 15, "bold"), fill="#c9a8ff")
        for name in pending[:5]:
            tk.Label(win, text=f"\u2605  {name}", bg=BG, fg=TEXT,
                     font=(self.app.font_ui, 10, "bold")).pack()
        RoundButton(win, "\u041e\u0442\u043b\u0438\u0447\u043d\u043e!", win.destroy, width=150, height=40,
                    bg="#8957e5", fg="#f4efff", app_bg=BG,
                    font=(self.app.font_ui, 12, "bold")).pack(pady=12)
        self._center_window(win)
        # \u043e\u043a\u043d\u043e \u043f\u043e\u0441\u0442\u0440\u043e\u0435\u043d\u043e \u2014 \u0441\u0431\u0440\u0430\u0441\u044b\u0432\u0430\u0435\u043c pending
        self.app.save["pending_ach"] = []
        self.app.commit()
        sfx("win")
        win.lift()
        win.focus_force()
        return True

    def on_wheel(self, event):
        win = self.__dict__.get("_changelog_win")
        canvas = self.__dict__.get("_changelog_canvas")
        if win is not None and canvas is not None:
            try:
                alive = win.winfo_exists()
            except tk.TclError:
                alive = False
            if alive:
                num = getattr(event, "num", 0)
                if num == 4:
                    canvas.yview_scroll(-2, "units")
                elif num == 5:
                    canvas.yview_scroll(2, "units")
                else:
                    canvas.yview_scroll(
                        -2 if getattr(event, "delta", 0) > 0 else 2, "units")
                return
        super().on_wheel(event)

    def _start_anim(self):
        if self.anim_job is None:
            self._animate()

    def _anim_level(self):
        sh = self._level_shimmer
        if not sh:
            return
        px0, py0, py1, span = self._level_span
        sx = px0 + (self.anim_t * 4) % span
        self.bg.coords(sh, sx, py0, sx + 14, py1)

    def _animate(self):
        self.anim_t += 1
        self._anim_title()
        self._anim_level()
        # noinspection PyArgumentList
        self.anim_job = self.after(60, self._animate)

    def _open_changelog(self):
        if self._raise_window("_changelog_win"):
            return
        wbg = "#0b1420"
        win = tk.Toplevel(self)
        self._changelog_win = win
        win.title("Update log \u2014 SNAKEY")
        win.configure(bg=wbg)
        win.resizable(False, False)
        win.transient(self.app)

        def close():
            win.destroy()

        self._borderless(win, "Update log \u2014 SNAKEY", 560, wbg, on_close=close)
        cv = tk.Canvas(win, width=560, height=88, bg=wbg, highlightthickness=0)
        cv.pack()
        gradient_bands(cv, 0, 0, 560, 88, wbg, "#16233a", 12)
        cx, cyc = 280, 40
        for k in range(16):
            a = math.radians(k * 22.5)
            cv.create_line(cx + math.cos(a) * 42, cyc + math.sin(a) * 42,
                           cx + math.cos(a) * 60, cyc + math.sin(a) * 60,
                           fill=blend(GOLD, wbg, 0.4), width=2)
        cv.create_text(cx + 2, cyc + 1, text="UPDATE LOG",
                       font=(self.app.font_title, 20, "bold"), fill="#3a2a05")
        cv.create_text(cx, cyc, text="UPDATE LOG",
                       font=(self.app.font_title, 20, "bold"), fill=GOLD)
        cv.create_text(cx, cyc + 26, text="\u0438\u0441\u0442\u043e\u0440\u0438\u044f \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0439 SNAKEY",
                       font=(self.app.font_ui, 9), fill=DIM)
        body = tk.Frame(win, bg=wbg)
        body.pack(fill="both", expand=True)
        canvas = tk.Canvas(body, width=560, height=540, bg=wbg,
                           highlightthickness=0)
        bar = tk.Scrollbar(body, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self._changelog_canvas = canvas
        inner = tk.Frame(canvas, bg=wbg)
        canvas.create_window((0, 0), window=inner, anchor="nw", width=540)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        for ver, items in CHANGELOG:
            pill = tk.Canvas(inner, width=540, height=30, bg=wbg,
                             highlightthickness=0)
            pill.pack(pady=(10, 0))
            round_rect(pill, 1, 1, 538, 29, 14, fill=PANEL,
                       outline=blend(GOLD, wbg, 0.4))
            pill.create_text(18, 15, text=f"v{ver}", anchor="w",
                             font=(self.app.font_ui, 11, "bold"), fill=GOLD)
            pill.create_text(522, 15, text=f"{len(items)} \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0439", anchor="e",
                             font=(self.app.font_ui, 8), fill=DIM)
            for line in items:
                row = tk.Frame(inner, bg=wbg)
                row.pack(fill="x", padx=30, pady=1)
                tk.Label(row, text="\uff0b", bg=wbg, fg=GOLD,
                         font=(self.app.font_ui, 10, "bold")).pack(
                             side="left", padx=(2, 7))
                tk.Label(row, text=line, bg=wbg, fg=TEXT, wraplength=450,
                         justify="left", font=(self.app.font_ui, 9),
                         anchor="w").pack(side="left")
        RoundButton(win, "\u0417\u0430\u043a\u0440\u044b\u0442\u044c", close, width=150, height=38,
                    app_bg=wbg, font=(self.app.font_ui, 10, "bold")).pack(pady=12)
        win.protocol("WM_DELETE_WINDOW", close)
        self._center_window(win)