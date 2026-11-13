import tkinter as tk


from snakey_content import (


    ACCENT,
    ACCENT_DARK,
    BG,
    BLUE,
    BORDER,
    COLORS,
    DIFFICULTIES,
    DIM,
    GRADIENTS,
    LOCKED_BG,
    PANEL,
    TEXT,
    THEMES,
    THEME_BY_ID,
    WARN,
    WINDOW_SIZES,
    WINDOW_SIZE_LABELS,
    WINDOW_SIZE_ORDER,
)
from snakey_drawing import draw_acc
from snakey_save import level_from_exp
from snakey_shop import ShopCard
from snakey_utils import blend, hsv_hex, round_rect, seg_color
from snakey_widgets import GradientBG, RoundButton, Screen

class SettingsScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.mid = blend(BG, "#0f1a26", 0.55)
        self.bot = blend(BG, "#0f1a26", 0.85)
        self.bg = GradientBG(self, BG, "#0f1a26", accent=BLUE)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Label(self, text="НАСТРОЙКИ", bg=BG, fg=ACCENT,
                 font=(app.font_title, 20, "bold")).pack(pady=(14, 2))
        self.preview = tk.Canvas(self, width=260, height=62, bg=BG,
                                 highlightthickness=0)
        self.preview.pack(pady=(2, 0))
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bg=BG, fg=DIM,
                 font=(app.font_ui, 10)).pack()

        body = tk.Frame(self, bg=self.mid)
        body.pack(fill="both", expand=True, padx=16)
        self.scroller = tk.Canvas(body, width=780, height=400, bg=self.mid,
                                  highlightthickness=0)
        bar = tk.Scrollbar(body, orient="vertical", command=self.scroller.yview)
        self.scroller.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.scroller.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.scroller, bg=self.mid)
        self._win = self.scroller.create_window((0, 0), window=self.inner,
                                                anchor="nw", width=770)
        self.inner.bind("<Configure>",
                        lambda e: self.scroller.configure(
                            scrollregion=self.scroller.bbox("all")))
        self.scroller.bind("<Configure>", self._on_resize)

        self._section("Цвет змейки")
        self.grid_frame = tk.Frame(self.inner, bg=self.mid)
        self.grid_frame.pack(padx=20)

        self._section("Сложность")
        self.diff_frame = tk.Frame(self.inner, bg=self.mid)
        self.diff_frame.pack()
        self.diff_info_var = tk.StringVar()
        tk.Label(self.inner, textvariable=self.diff_info_var, bg=self.mid, fg=WARN,
                 font=(app.font_ui, 10)).pack(pady=(4, 0))

        self._section("Размер экрана")
        self.size_frame = tk.Frame(self.inner, bg=self.mid)
        self.size_frame.pack()

        self._section("Производительность")
        self.low_btn = RoundButton(
            self.inner, "", self._toggle_low, width=380, height=42,
            app_bg=self.mid, font=(app.font_ui, 10, "bold"))
        self.low_btn.pack(pady=(2, 4))
        self.sound_btn = RoundButton(
            self.inner, "", self._toggle_sound, width=380, height=42,
            app_bg=self.mid, font=(app.font_ui, 10, "bold"))
        self.sound_btn.pack(pady=(2, 4))
        self.music_btn = RoundButton(
            self.inner, "", self._toggle_music, width=380, height=42,
            app_bg=self.mid, font=(app.font_ui, 10, "bold"))
        self.music_btn.pack(pady=(2, 4))
        tk.Label(self.inner,
                 text="Упрощает фон и графику для слабых устройств,"
                      " не меняя правила игры",
                 bg=self.mid, fg=DIM, font=(app.font_ui, 9)).pack()

        RoundButton(self, "←  Назад", lambda: app.show("MenuScreen"),
                    width=170, height=40, app_bg=self.bot,
                    font=(app.font_ui, 11, "bold")).pack(pady=(6, 10))

    def on_show(self):
        self._rebuild()
        self.bg.set_animated(not self.app.save.get("low_spec"))
        self.scroller.yview_moveto(0)

    def on_hide(self):
        self.bg.set_animated(False)

    def _on_resize(self, event):
        self.scroller.itemconfig(self._win, width=max(400, event.width - 22))

    def _section(self, title):
        cv = tk.Canvas(self.inner, width=340, height=30, bg=self.mid,
                       highlightthickness=0)
        cv.pack(pady=(10, 2))
        round_rect(cv, 1, 1, 338, 29, 14, fill=PANEL, outline=BORDER)
        cv.create_text(170, 15, text=title,
                       font=(self.app.font_ui, 11, "bold"), fill=ACCENT)

    def _paint_low(self):
        on = bool(self.app.save.get("low_spec", False))
        btn = self.low_btn
        btn.text = ("Режим для слабых устройств:  ВКЛ ✓" if on
                    else "Режим для слабых устройств:  ВЫКЛ ✗")
        btn.base_bg = ACCENT_DARK if on else PANEL
        btn.base_fg = "#c9ffd4" if on else TEXT
        btn.hover_bg = blend(btn.base_bg, "#ffffff", 0.12)
        btn.press_bg = blend(btn.base_bg, "#000000", 0.18)
        btn.repaint()

    def _toggle_low(self):
        self.app.save["low_spec"] = not self.app.save.get("low_spec", False)
        self.app.commit()
        self._paint_low()

    def _paint_sound(self):
        on = bool(self.app.save.get("sound", True))
        btn = self.sound_btn
        btn.text = ("Звуковые эффекты:  ВКЛ ✓" if on
                    else "Звуковые эффекты:  ВЫКЛ ✗")
        btn.base_bg = ACCENT_DARK if on else PANEL
        btn.base_fg = "#c9ffd4" if on else TEXT
        btn.hover_bg = blend(btn.base_bg, "#ffffff", 0.12)
        btn.press_bg = blend(btn.base_bg, "#000000", 0.18)
        btn.repaint()

    def _toggle_sound(self):
        self.app.save["sound"] = not self.app.save.get("sound", True)
        self.app.commit()
        self._paint_sound()

    def _paint_music(self):
        on = bool(self.app.save.get("music", True))
        btn = self.music_btn
        btn.text = "Фоновая музыка:  ВКЛ ✓" if on \
            else "Фоновая музыка:  ВЫКЛ ✗"
        btn.base_bg = ACCENT_DARK if on else PANEL
        btn.base_fg = "#c9ffd4" if on else TEXT
        btn.hover_bg = blend(btn.base_bg, "#ffffff", 0.12)
        btn.press_bg = blend(btn.base_bg, "#000000", 0.18)
        btn.repaint()

    def _toggle_music(self):
        on = not self.app.save.get("music", True)
        self.app.save["music"] = on
        self.app.commit()
        self._paint_music()
        snd = getattr(self.app, "sound", None)
        if snd is not None:
            snd.set_music(on)

    def _rebuild(self, status=""):
        self.status_var.set(status)
        self._paint_low()
        self._paint_sound()
        self._paint_music()
        p = self.preview
        p.delete("all")
        sel = self.app.save.get("selected", ACCENT)
        acc = self.app.save.get("accessory", "none")
        for i in range(3):
            x = 104 + i * 40
            color = seg_color(sel, i, 3, 0)
            round_rect(p, x - 15, 26, x + 15, 54, 8, fill=color, outline="")
        ring = (blend(GRADIENTS[sel][1], "#ffffff", 0.3) if sel in GRADIENTS
                else hsv_hex(0.0, 0.85, 0.95) if sel == "rainbow"
                else blend(sel, "#ffffff", 0.5))
        p.create_oval(87, 22, 121, 58, outline=ring, width=2)
        if acc != "none":
            draw_acc(p, 104, 40, acc)
        for w in self.grid_frame.winfo_children():
            w.destroy()
        owned_items = [it for it in COLORS if it["id"] in self.app.save["owned"]]
        for i, item in enumerate(owned_items):
            card = ShopCard(self.grid_frame, self.app, "color", item,
                            self._rebuild, card_bg=self.mid)
            card.grid(row=i // 5, column=i % 5, padx=4, pady=4, sticky="nsew")
        level = level_from_exp(self.app.save.get("exp", 0))
        for w in self.diff_frame.winfo_children():
            w.destroy()
        current = self.app.save.get("speed", "normal")
        if DIFFICULTIES.get(current, DIFFICULTIES["normal"])["level"] > level:
            current = "normal"
        cfg = DIFFICULTIES[current]
        for key, dcfg in DIFFICULTIES.items():
            if dcfg["level"] > level:
                btn = RoundButton(self.diff_frame, f"🔒 ур. {dcfg['level']}",
                                  width=126, height=42, bg=LOCKED_BG, fg=DIM,
                                  app_bg=self.mid,
                                  font=(self.app.font_ui, 10, "bold"))
            else:
                selected = key == current
                btn = RoundButton(
                    self.diff_frame, dcfg["label"],
                    command=(lambda k=key: self._set_speed(k)),
                    width=126, height=42,
                    bg=ACCENT_DARK if selected else PANEL,
                    fg="#c9ffd4" if selected else TEXT, app_bg=self.mid,
                    font=(self.app.font_ui, 10, "bold"))
            btn.pack(side="left", padx=4)
        for w in self.size_frame.winfo_children():
            w.destroy()
        cur_size = self.app.save.get("window_size", "medium")
        if cur_size not in WINDOW_SIZES:
            cur_size = "medium"
        for key in WINDOW_SIZE_ORDER:
            w_, h_ = WINDOW_SIZES[key]
            selected = key == cur_size
            btn = RoundButton(
                self.size_frame, f"{WINDOW_SIZE_LABELS[key]}  {w_}\u00d7{h_}",
                command=(lambda k=key: self._set_size(k)),
                width=150, height=42,
                bg=ACCENT_DARK if selected else PANEL,
                fg="#c9ffd4" if selected else TEXT, app_bg=self.mid,
                font=(self.app.font_ui, 10, "bold"))
            btn.pack(side="left", padx=4)
        theme = THEME_BY_ID.get(self.app.save.get("theme"), THEMES[0])
        total_c = cfg["reward"] * theme.get("bonus", 1.0)
        total_e = cfg["exp_reward"] * theme.get("bonus", 1.0)
        self.diff_info_var.set((cfg["note"] or "классические правила")
                               + f"  ·  монеты ×{total_c:g}  ·  опыт ×{total_e:g}")

    def _set_speed(self, key):
        level = level_from_exp(self.app.save.get("exp", 0))
        if DIFFICULTIES[key]["level"] > level:
            return
        self.app.save["speed"] = key
        self.app.commit()
        self._rebuild()

    def _set_size(self, key):
        self.app.set_window_size(key)
        self._rebuild()