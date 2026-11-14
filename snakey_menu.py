import math
import tkinter as tk


from snakey_assets import sfx
from snakey_content import (


    ACCENT,
    ACCENT_BRIGHT,
    ACCENT_DARK,
    ACCESSORIES,
    BG,
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
from snakey_widgets import (GradientBG, RoundButton, Screen,
                            gradient_round_btn, repaint_gradient)

# 1.1: градиентные пары цветов кнопок меню — все оттенки согласованы
# (зелёный игровой, синий, фиолетовый, золотой, бирюзовый, графит)
MENU_BTN_COLORS = {
    "play": ("#3fb950", "#1f7a33", "#eafff0"),
    "mini": ("#3b82f6", "#1d4ed8", "#eaf2ff"),
    "ach": ("#8957e5", "#5b2fb8", "#f4efff"),
    "shop": ("#e0a437", "#a8761c", "#241a05"),
    "set": ("#2dd4bf", "#0f766e", "#032b27"),
    "log": ("#2a3340", "#1a222c", "#aab4c0"),
}


class MenuScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        # 1.1: фон меню заметно ярче — сочный зелёно-синий градиент
        self.bg = GradientBG(self, "#1b3a26", "#122c44", accent=ACCENT_BRIGHT)
        self.bg.pack(fill="both", expand=True)
        self.bg.bind("<Configure>", lambda e: self._layout())
        self.anim_t = 0.0
        self.anim_job = None
        self._btn_ids = {}
        self._btn_cmds = {}
        self._btn_grad = {}   # key -> (ids, x1, y1, x2, y2, r, c1, c2)
        self._hover_t = {}    # key -> 0..1 (анимация наведения)
        self._hover_job = {}
        self._title_letters = []
        self._title_snake = []
        self._title_eyes = []
        self._level_shimmer = None
        self._level_span = (0, 0, 0, 1)
        self._level_fill_w = 0.0
        self._badge_ring = None
        self._sparkles = []
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

    def _btn(self, key, cx, cy, bw, bh, text, cmd, colors=None, fsize=12):
        """Градиентная canvas-кнопка с hover-анимацией (1.1)."""
        tag = f"btn_{key}"
        if colors is None:
            colors = MENU_BTN_COLORS.get(key, ("#2a3340", "#1a222c", TEXT))
        c1, c2, fg = colors
        x1, y1 = cx - bw / 2.0, cy - bh / 2.0
        x2, y2 = cx + bw / 2.0, cy + bh / 2.0
        r = min(bh / 2.0, 18)
        round_rect(self.bg, x1 + 1, y1 + 4, x2 + 1, y2 + 4, r, fill="#000000",
                   stipple="gray25", outline="", tags=("menu", tag))
        ids = gradient_round_btn(self.bg, x1, y1, x2, y2, r, c1, c2,
                                 tags=("menu", tag))
        round_rect(self.bg, x1 + 4, y1 + 3, x2 - 4, y1 + bh * 0.40,
                   max(4, r - 6), fill="#ffffff", stipple="gray50",
                   outline="", tags=("menu", tag))
        self.bg.create_text(cx, cy + 1, text=text,
                            font=(self.app.font_ui, fsize, "bold"), fill=fg,
                            tags=("menu", tag))
        self._btn_ids[key] = (ids[0] if ids else None, c1)
        self._btn_grad[key] = (ids, x1, y1, x2, y2, r, c1, c2)
        self._hover_t[key] = 0.0
        self._btn_cmds[key] = cmd
        self.bg.tag_bind(tag, "<Enter>",
                         lambda e, k=key: self._hover(k, True))
        self.bg.tag_bind(tag, "<Leave>",
                         lambda e, k=key: self._hover(k, False))

    def _hover(self, key, on):
        """Плавная анимация наведения: кнопка светлеет и чуть приподнимается."""
        grad = self._btn_grad.get(key)
        if not grad:
            return
        job = self._hover_job.pop(key, None)
        if job is not None:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        target = 1.0 if on else 0.0

        def step():
            cur = self._hover_t.get(key, 0.0)
            d = target - cur
            if abs(d) < 0.1:
                self._hover_t[key] = target
                self._paint_hover(key)
                self._hover_job.pop(key, None)
                return
            self._hover_t[key] = cur + d * 0.45
            self._paint_hover(key)
            self._hover_job[key] = self.after(28, step)

        step()

    def _paint_hover(self, key):
        grad = self._btn_grad.get(key)
        if not grad:
            return
        ids, x1, y1, x2, y2, r, c1, c2 = grad
        t = self._hover_t.get(key, 0.0)
        lift = 2.0 * t
        try:
            repaint_gradient(self.bg, ids, x1, y1 - lift, x2, y2 - lift, r,
                             blend(c1, "#ffffff", 0.18 * t),
                             blend(c2, "#ffffff", 0.18 * t))
        except tk.TclError:
            pass

    def _layout(self):
        w, h = self._geom()
        self.bg.delete("menu")
        self._btn_ids = {}
        self._btn_cmds = {}
        self._btn_grad = {}
        self._hover_t = {}
        self._title_letters = []
        self._title_snake = []
        self._title_eyes = []
        self._level_shimmer = None
        self._badge_ring = None
        self._sparkles = []
        round_rect(self.bg, 10, 6, 74, 30, 12, fill=PANEL, outline=BORDER,
                   tags="menu")
        self.bg.create_text(42, 18, text=f"v{VERSION}",
                            font=(self.app.font_ui, 9, "bold"), fill=GOLD,
                            tags="menu")
        self._btn("log", 152, 18, 116, 24, "update log",
                  self._open_changelog, fsize=8)
        self._draw_title(w, h)
        self._draw_level(w, h)
        self.bg.create_text(w / 2, h * 0.455,
                            text=f"\u25c9  {self.app.save['coins']} монет",
                            font=(self.app.font_ui, 13, "bold"), fill=GOLD,
                            tags="menu")
        y0 = h * 0.52
        self._btn("play", w / 2, y0, 260, 54, "ИГРАТЬ",
                  self._play_classic, fsize=15)
        self._btn("mini", w / 2, y0 + 56, 260, 48, "МИНИ-ИГРЫ",
                  lambda: self.app.show("MiniScreen"), fsize=13)
        self._btn("ach", w / 2, y0 + 112, 260, 48, "ДОСТИЖЕНИЯ",
                  lambda: self.app.show("AchScreen"), fsize=13)
        self._btn("shop", w / 2, y0 + 168, 260, 48, "МАГАЗИН",
                  lambda: self.app.show("ShopScreen"), fsize=13)
        self._btn("set", w / 2, y0 + 224, 260, 48, "НАСТРОЙКИ",
                  lambda: self.app.show("SettingsScreen"), fsize=13)
        self.bg.create_text(w / 2, h * 0.94,
                            text=f"Рекорд: {self.app.save['highscore']}",
                            font=(self.app.font_ui, 11), fill=DIM, tags="menu")
        self.bg.create_text(w / 2, h * 0.975,
                            text="WASD / стрелки · P — пауза · R — заново",
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
                            text="собирай еду — стань самой длинной змейкой",
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
        """Экранчик уровня (1.1): выше, скруглённее, с градиентом, пульсирующим
        бейджем и искрами; shimmer бегает ТОЛЬКО по заполненной части полосы."""
        if w is None:
            w, h = self._geom()
        self.bg.delete("level")
        exp = self.app.save.get("exp", 0)
        level = level_from_exp(exp)
        cur = exp_for_level(level)
        nxt = exp_for_level(level + 1)
        frac = max(0.0, min(1.0, (exp - cur) / max(1, nxt - cur)))
        cx = w / 2
        # панель выше и мягче: 96px высотой, радиус 20
        bx0, by = cx - 180, h * 0.35 - 48
        bx1, by1 = cx + 180, h * 0.35 + 48
        round_rect(self.bg, bx0 + 2, by + 5, bx1 + 2, by1 + 5, 20,
                   fill="#000000", stipple="gray25", outline="",
                   tags=("menu", "level"))
        gradient_round_btn(self.bg, bx0, by, bx1, by1, 20, PANEL,
                           blend(PANEL, ACCENT_DARK, 0.35), steps=12,
                           tags=("menu", "level"))
        round_rect(self.bg, bx0 + 3, by + 2, bx1 - 3, by + 30, 16,
                   fill="#ffffff", stipple="gray75", outline="",
                   tags=("menu", "level"))
        # бейдж уровня: кольцо + градиент, кольцо пульсирует (анимация)
        br = 22
        bcx, bcy = bx0 + 34, (by + by1) / 2
        self._badge_ring = self.bg.create_oval(
            bcx - br - 4, bcy - br - 4, bcx + br + 4, bcy + br + 4,
            outline=ACCENT, width=2, tags=("menu", "level"))
        gradient_round_btn(self.bg, bcx - br, bcy - br, bcx + br, bcy + br,
                           br, ACCENT, ACCENT_DARK, steps=8,
                           tags=("menu", "level"))
        self.bg.create_text(bcx, bcy + 1, text=str(level),
                            font=(self.app.font_title, 17, "bold"),
                            fill="#eafff0", tags=("menu", "level"))
        self.bg.create_text(bx0 + 66, by + 20, text=f"УРОВЕНЬ {level}",
                            anchor="w", font=(self.app.font_ui, 12, "bold"),
                            fill=TEXT, tags=("menu", "level"))
        self.bg.create_text(bx0 + 66, by + 40,
                            text=f"{exp} EXP · до ур. {level + 1}: {nxt - exp}",
                            anchor="w", font=(self.app.font_ui, 9), fill=DIM,
                            tags=("menu", "level"))
        px0, py0, px1, py1 = bx0 + 66, by + 60, bx1 - 14, by + 74
        round_rect(self.bg, px0, py0, px1, py1, 7, fill=LOCKED_BG,
                   outline="", tags=("menu", "level"))
        self._level_fill_w = (px1 - px0) * frac
        if frac > 0:
            width = self._level_fill_w
            seg_w = width / 6
            for k in range(6):
                col = blend(GOLD, ACCENT_BRIGHT, k / 5)
                round_rect(self.bg, px0 + k * seg_w, py0,
                           px0 + (k + 1) * seg_w, py1, 5, fill=col,
                           outline="", tags=("menu", "level"))
            # 1.1: shimmer живёт строго внутри заполненной части
            if not self.app.save.get("low_spec") and width > 20:
                span = max(1, width - 14)
                sx = px0 + (self.anim_t * 3) % span
                self._level_shimmer = self.bg.create_rectangle(
                    sx, py0 + 1, sx + 14, py1 - 1,
                    fill=blend(GOLD, "#ffffff", 0.45),
                    outline="", tags=("menu", "level"))
                self._level_span = (px0, py0 + 1, py1 - 1, span)
        # искры вокруг панельки (при low_spec не создаём)
        if not self.app.save.get("low_spec"):
            for k in range(6):
                a = math.radians(k * 60)
                sx = cx + math.cos(a) * 196
                sy = (by + by1) / 2 + math.sin(a) * 62
                iid = self.bg.create_oval(
                    sx - 2, sy - 2, sx + 2, sy + 2,
                    fill=blend(ACCENT_BRIGHT, "#ffffff", 0.3), outline="",
                    tags=("menu", "level"))
                self._sparkles.append((iid, sx, sy, k))

    def _maybe_show_levelup(self):
        pending = self.app.save.get("pending_level", 0)
        if not pending:
            return False
        if self._raise_window("_levelup_win"):
            return True
        unlocked = [f"Сложность «{cfg['label']}»"
                    for cfg in DIFFICULTIES.values() if cfg["level"] == pending]
        for item in THEMES:
            if item.get("level") == pending and item["price"] > 0:
                unlocked.append(f"Фон «{item['name']}»")
        for item in FOOD_ITEMS:
            if item.get("level") == pending and item["price"] > 0:
                unlocked.append(f"Еда «{item['name']}»")
        for item in ACCESSORIES:
            if item.get("level") == pending and item["price"] > 0:
                unlocked.append(f"Аксессуар «{item['name']}»")
        win = tk.Toplevel(self)
        self._levelup_win = win
        win.title("Новый уровень!")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self.app)
        self._borderless(win, "✨ Новый уровень!", 380, BG)
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
        cv.create_text(cx, 192, text="УРОВЕНЬ ПОВЫШЕН!",
                       font=(self.app.font_title, 16, "bold"), fill=GOLD)
        tk.Label(win, text=f"Теперь у тебя {self.app.save.get('exp', 0)} EXP",
                 bg=BG, fg=TEXT, font=(self.app.font_ui, 11, "bold")).pack()
        if unlocked:
            tk.Label(win, text="НОВОЕ ДОСТУПНО:", bg=BG, fg=ACCENT,
                     font=(self.app.font_ui, 10, "bold")).pack(pady=(8, 0))
            for line in unlocked[:6]:
                tk.Label(win, text=f"★  {line}", bg=PANEL, fg=TEXT,
                         font=(self.app.font_ui, 9, "bold")).pack(
                             pady=1, ipadx=10, ipady=2)
        RoundButton(win, "Круто!",
                    lambda: (win.destroy(), self.refocus()), width=150, height=40,
                    bg=ACCENT, fg="#06220c", app_bg=BG,
                    font=(self.app.font_ui, 12, "bold")).pack(pady=14)
        self._center_window(win)
        # окно успешно построено — только теперь сбрасываем pending
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
        win.title("Достижение получено!")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self.app)
        self._borderless(win, "★ Достижение получено!", 380, BG)
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
        cv.create_text(cx, cyc - 2, text="★",
                       font=(self.app.font_title, 40, "bold"), fill="#c9a8ff")
        cv.create_text(cx, 152, text="ДОСТИЖЕНИЕ ПОЛУЧЕНО!",
                       font=(self.app.font_title, 15, "bold"), fill="#c9a8ff")
        for name in pending[:5]:
            tk.Label(win, text=f"★  {name}", bg=BG, fg=TEXT,
                     font=(self.app.font_ui, 10, "bold")).pack()
        RoundButton(win, "Отлично!",
                    lambda: (win.destroy(), self.refocus()), width=150, height=40,
                    bg="#8957e5", fg="#f4efff", app_bg=BG,
                    font=(self.app.font_ui, 12, "bold")).pack(pady=12)
        self._center_window(win)
        # окно построено — сбрасываем pending
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
        if sh:
            px0, py0, py1, span = self._level_span
            # 1.1: shimmer не выезжает на незаполненную часть полосы
            sx = px0 + (self.anim_t * 3) % max(1, span)
            self.bg.coords(sh, sx, py0, sx + 14, py1)
        t = self.anim_t
        # пульс кольца бейджа уровня
        ring = self._badge_ring
        if ring:
            try:
                x1, y1, x2, y2 = self.bg.coords(ring)
            except (tk.TclError, ValueError):
                return
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            br = 26 + math.sin(t * 0.11) * 2.0
            self.bg.coords(ring, cx - br, cy - br, cx + br, cy + br)
        # искры вокруг панельки уровня (орбита вокруг базовой точки)
        for iid, bx, byy, k in self._sparkles:
            a = math.radians(k * 60 + t * 2)
            sx = bx + math.cos(a) * 4.0
            sy = byy + math.sin(a) * 3.0
            r = 2 + math.sin(t * 0.2 + k) * 1.0
            try:
                self.bg.coords(iid, sx - r, sy - r, sx + r, sy + r)
            except tk.TclError:
                continue

    def _animate(self):
        self.anim_t += 1
        self._anim_title()
        self._anim_level()
        # 1.1: «дыхание» градиентных кнопок — лёгкая волна яркости по очереди
        for i, (key, grad) in enumerate(list(self._btn_grad.items())):
            ids, x1, y1, x2, y2, r, c1, c2 = grad
            glow = 0.05 + 0.05 * math.sin(self.anim_t * 0.09 - i * 0.9)
            try:
                repaint_gradient(self.bg, ids, x1, y1, x2, y2, r,
                                 blend(c1, "#ffffff", glow),
                                 blend(c2, "#ffffff", glow))
            except tk.TclError:
                continue
        # noinspection PyArgumentList
        self.anim_job = self.after(60, self._animate)

    def _open_changelog(self):
        if self._raise_window("_changelog_win"):
            return
        # 1.1: update log в зелёной гамме — основном цвете игры
        wbg = "#0c1a10"
        win = tk.Toplevel(self)
        self._changelog_win = win
        win.title("Update log — SNAKEY")
        win.configure(bg=wbg)
        win.resizable(False, False)
        win.transient(self.app)

        def close():
            # окно не уничтожается, а прячется: повторное открытие мгновенное,
            # фокус не теряется вместе с уничтоженным окном
            try:
                win.withdraw()
            except tk.TclError:
                pass
            self.refocus()

        self._borderless(win, "Update log — SNAKEY", 560, wbg, on_close=close)
        cv = tk.Canvas(win, width=560, height=88, bg=wbg, highlightthickness=0)
        cv.pack()
        gradient_bands(cv, 0, 0, 560, 88, wbg, "#14351e", 12)
        cx, cyc = 280, 40
        for k in range(16):
            a = math.radians(k * 22.5)
            cv.create_line(cx + math.cos(a) * 42, cyc + math.sin(a) * 42,
                           cx + math.cos(a) * 60, cyc + math.sin(a) * 60,
                           fill=blend(ACCENT, wbg, 0.4), width=2)
        cv.create_text(cx + 2, cyc + 1, text="UPDATE LOG",
                       font=(self.app.font_title, 20, "bold"), fill="#0a2d12")
        cv.create_text(cx, cyc, text="UPDATE LOG",
                       font=(self.app.font_title, 20, "bold"), fill=ACCENT_BRIGHT)
        cv.create_text(cx, cyc + 26, text="история изменений SNAKEY",
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
            round_rect(pill, 1, 1, 538, 29, 14, fill="#12251a",
                       outline=blend(ACCENT, wbg, 0.45))
            pill.create_text(18, 15, text=f"v{ver}", anchor="w",
                             font=(self.app.font_ui, 11, "bold"),
                             fill=ACCENT_BRIGHT)
            pill.create_text(522, 15, text=f"{len(items)} обновлений", anchor="e",
                             font=(self.app.font_ui, 8), fill=DIM)
            for line in items:
                row = tk.Frame(inner, bg=wbg)
                row.pack(fill="x", padx=30, pady=1)
                tk.Label(row, text="＋", bg=wbg, fg=ACCENT,
                         font=(self.app.font_ui, 10, "bold")).pack(
                             side="left", padx=(2, 7))
                tk.Label(row, text=line, bg=wbg, fg=TEXT, wraplength=450,
                         justify="left", font=(self.app.font_ui, 9),
                         anchor="w").pack(side="left")
        RoundButton(win, "Закрыть", close, width=150, height=38,
                    bg="#184d28", fg="#eafff0", app_bg=wbg,
                    font=(self.app.font_ui, 10, "bold")).pack(pady=12)
        win.protocol("WM_DELETE_WINDOW", close)
        self._center_window(win)
        # окно появляется ПОВЕРХ главного сразу, а не со второго клика
        win.deiconify()
        win.lift()
        win.focus_force()
