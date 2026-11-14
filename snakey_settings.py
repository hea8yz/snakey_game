import tkinter as tk


from snakey_content import (


    ACCENT,
    ACCENT_DARK,
    BG,
    BLUE,
    BORDER,
    DIFFICULTIES,
    DIM,
    GRADIENTS,
    LOCKED_BG,
    MUSIC_BY_ID,
    MUSIC_TRACKS,
    RED,
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
from snakey_utils import blend, gradient_bands, hsv_hex, round_rect, seg_color
from snakey_widgets import GradientBG, RoundButton, Screen

class VolumeSlider(tk.Canvas):
    """Компактный слайдер громкости в стиле игры (0..100)."""
    def __init__(self, master, bg, on_change, width=200, height=30):
        super().__init__(master, width=width, height=height, bg=bg,
                         highlightthickness=0)
        self.on_change = on_change
        # ВАЖНО: нельзя использовать имена _w/_h — это внутренние поля tkinter
        # (Tcl-путь виджета). Перезапись _w ломала виджет: настройки не открывались.
        self._sw = width
        self._sh = height
        self.value = 100
        self.bind("<Button-1>", self._on_drag)
        self.bind("<B1-Motion>", self._on_drag)
        self._draw()

    def set_value(self, v):
        self.value = max(0, min(100, int(v)))
        self._draw()

    def _on_drag(self, event):
        pad = 8
        usable = self._sw - pad * 2 - 34  # справа место под подпись "N%"
        frac = (event.x - pad) / max(1, usable)
        v = int(round(max(0.0, min(1.0, frac)) * 100))
        if v != self.value:
            self.set_value(v)
            self.on_change(v)

    def _draw(self):
        self.delete("all")
        pad, h = 8, self._sh
        mid = h / 2
        x2 = pad + (self._sw - pad * 2 - 34) * self.value / 100.0
        round_rect(self, pad, mid - 4, self._sw - pad - 34, mid + 4, 4,
                   fill=PANEL, outline=BORDER)
        if self.value > 0:
            round_rect(self, pad, mid - 4, max(pad + 8, x2), mid + 4, 4,
                       fill=ACCENT, outline="")
        self.create_oval(x2 - 7, mid - 7, x2 + 7, mid + 7,
                         fill="#eafff0", outline=ACCENT)
        self.create_text(self._sw - pad, mid, anchor="e",
                         text=f"{self.value}%", fill=TEXT,
                         font=("Helvetica", 9, "bold"))

class SettingsScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.mid = blend(BG, "#0f1a26", 0.55)
        self.bot = blend(BG, "#0f1a26", 0.85)
        self.bg = GradientBG(self, BG, "#0f1a26", accent=BLUE)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Label(self, text="НАСТРОЙКИ", bg=BG, fg=ACCENT,
                 font=(app.font_title, 20, "bold")).pack(pady=(14, 2))
        self.preview = tk.Canvas(self, width=320, height=132, bg=BG,
                                 highlightthickness=0)
        self.preview.pack(pady=(4, 0))
        tk.Label(self, text="Скин, фон и аксессуары выбираются в магазине",
                 bg=BG, fg=DIM, font=(app.font_ui, 9)).pack()
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
        self.au_btn = RoundButton(
            self.inner, "", self._toggle_au, width=380, height=42,
            app_bg=self.mid, font=(app.font_ui, 10, "bold"))
        self.au_btn.pack(pady=(2, 4))

        self._section("Громкость")
        self._music_vol_job = None
        self._sound_vol_job = None
        mrow = tk.Frame(self.inner, bg=self.mid)
        mrow.pack(pady=(2, 0))
        tk.Label(mrow, text="Музыка", bg=self.mid, fg=TEXT,
                 font=(app.font_ui, 10), width=9,
                 anchor="w").pack(side="left")
        self.music_vol = VolumeSlider(mrow, self.mid, self._on_music_vol)
        self.music_vol.pack(side="left")
        srow = tk.Frame(self.inner, bg=self.mid)
        srow.pack(pady=(2, 2))
        tk.Label(srow, text="Звуки", bg=self.mid, fg=TEXT,
                 font=(app.font_ui, 10), width=9,
                 anchor="w").pack(side="left")
        self.sound_vol = VolumeSlider(srow, self.mid, self._on_sound_vol)
        self.sound_vol.pack(side="left")
        self.mute_btn = RoundButton(
            self.inner, "", self._toggle_mute, width=380, height=42,
            app_bg=self.mid, font=(app.font_ui, 10, "bold"))
        self.mute_btn.pack(pady=(2, 4))

        self._section("Фоновая музыка")
        self.track_frame = tk.Frame(self.inner, bg=self.mid)
        self.track_frame.pack()
        self.track_prev_btn = RoundButton(
            self.track_frame, "◀", self._track_prev, width=56, height=42,
            app_bg=self.mid, font=(self.app.font_ui, 12, "bold"))
        self.track_prev_btn.pack(side="left", padx=(0, 6))
        self.track_btn = RoundButton(
            self.track_frame, "", self._track_next, width=280, height=42,
            app_bg=self.mid, font=(self.app.font_ui, 10, "bold"))
        self.track_btn.pack(side="left")
        self.track_next_btn = RoundButton(
            self.track_frame, "▶", self._track_next, width=56, height=42,
            app_bg=self.mid, font=(self.app.font_ui, 12, "bold"))
        self.track_next_btn.pack(side="left", padx=(6, 0))
        tk.Label(self.inner,
                 text="Новый трек можно получить за достижения",
                 bg=self.mid, fg=DIM, font=(app.font_ui, 9)).pack()
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

    def _paint_preview(self):
        """Экранчик предпросмотра: змейка выбранным цветом с аксессуаром
        на фоне выбранной темы."""
        p = self.preview
        p.delete("all")
        W, H = 320, 132
        theme = THEME_BY_ID.get(self.app.save.get("theme"), THEMES[0])
        sel = self.app.save.get("selected", ACCENT)
        acc = self.app.save.get("accessory", "none")
        # фон выбранной темы: градиент или шахматная клетка
        if theme.get("grad"):
            gradient_bands(p, 5, 5, W - 5, H - 5,
                           theme["grad"][0], theme["grad"][1], 12)
        else:
            p.create_rectangle(5, 5, W - 5, H - 5, fill=theme["grid_a"],
                               outline="")
            cs = 16
            for r in range((H - 10) // cs + 1):
                for c in range((W - 10) // cs + 1):
                    if (r + c) % 2:
                        p.create_rectangle(5 + c * cs, 5 + r * cs,
                                           5 + (c + 1) * cs, 5 + (r + 1) * cs,
                                           fill=theme["grid_b"], outline="")
        # лёгкий намёк на декор темы
        dec_col = {"stars": "#ffffff", "snow": "#ffffff", "flowers": "#f778ba",
                   "petals": "#f778ba", "embers": "#ff9f1c", "bubbles": "#bfe6ff",
                   "leaves": "#7ee08a", "glow": "#a06bff", "stones": "#8b949e",
                   "bushes": "#5d8f3e"}.get(theme.get("decor"))
        if dec_col:
            for x, y, s in ((40, 28, 2), (272, 36, 1.5), (250, 98, 1.8),
                            (66, 102, 1.4), (150, 22, 1.2)):
                p.create_oval(x - s, y - s, x + s, y + s, fill=dec_col,
                              outline="")
        # рамка в цвете границы темы
        round_rect(p, 3, 3, W - 3, H - 3, 16, fill="",
                   outline=theme["border"], width=2)
        # змейка выбранным цветом (хвост слева, голова справа)
        cy = H // 2 + 8
        n = 5
        head_x = 200
        for i in range(n):
            x = head_x - i * 26
            round_rect(p, x - 12, cy - 12, x + 12, cy + 12, 7,
                       fill=seg_color(sel, i, n, 0), outline="")
        ring = (blend(GRADIENTS[sel][1], "#ffffff", 0.3) if sel in GRADIENTS
                else hsv_hex(0.0, 0.85, 0.95) if sel == "rainbow"
                else blend(sel, "#ffffff", 0.5))
        p.create_oval(head_x - 14, cy - 14, head_x + 14, cy + 14,
                      outline=ring, width=2)
        p.create_oval(head_x + 2, cy - 7, head_x + 7, cy - 2,
                      fill="#06220c", outline="")
        p.create_oval(head_x + 2, cy + 2, head_x + 7, cy + 7,
                      fill="#06220c", outline="")
        p.create_line(head_x + 14, cy, head_x + 20, cy, fill=RED, width=2)
        if acc != "none":
            draw_acc(p, head_x, cy, acc)
        # название темы в углу экранчика
        p.create_text(16, H - 14, text=theme["name"], anchor="w",
                      font=(self.app.font_ui, 9, "bold"),
                      fill=theme["border"])

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

    def _paint_volumes(self):
        self.music_vol.set_value(int(self.app.save.get("music_volume", 70)))
        self.sound_vol.set_value(int(self.app.save.get("sound_volume", 80)))
        on = bool(self.app.save.get("mute", False))
        btn = self.mute_btn
        btn.text = ("Беззвучный режим:  ВКЛ ✓" if on
                    else "Беззвучный режим:  ВЫКЛ ✗")
        btn.base_bg = ACCENT_DARK if on else PANEL
        btn.base_fg = "#c9ffd4" if on else TEXT
        btn.hover_bg = blend(btn.base_bg, "#ffffff", 0.12)
        btn.press_bg = blend(btn.base_bg, "#000000", 0.18)
        btn.repaint()

    def _on_music_vol(self, v):
        self.app.save["music_volume"] = v
        self.music_vol.set_value(v)
        if self._music_vol_job is not None:
            try:
                self.app.after_cancel(self._music_vol_job)
            except Exception:
                pass
        self._music_vol_job = self.app.after(350, self._apply_music_vol)

    def _apply_music_vol(self):
        self._music_vol_job = None
        self.app.commit()
        snd = getattr(self.app, "sound", None)
        if snd is not None:
            snd.apply_music_volume()

    def _on_sound_vol(self, v):
        self.app.save["sound_volume"] = v
        self.sound_vol.set_value(v)
        if self._sound_vol_job is not None:
            try:
                self.app.after_cancel(self._sound_vol_job)
            except Exception:
                pass
        self._sound_vol_job = self.app.after(350, self._apply_sound_vol)

    def _apply_sound_vol(self):
        self._sound_vol_job = None
        self.app.commit()

    def _toggle_mute(self):
        on = not self.app.save.get("mute", False)
        self.app.save["mute"] = on
        self.app.commit()
        self._paint_volumes()
        snd = getattr(self.app, "sound", None)
        if snd is not None:
            snd.set_mute(on)

    def _paint_au(self):
        on = bool(self.app.save.get("autoupdate", True))
        btn = self.au_btn
        btn.text = "Автообновление:  ВКЛ ✓" if on else "Автообновление:  ВЫКЛ ✗"
        btn.base_bg = ACCENT_DARK if on else PANEL
        btn.base_fg = "#c9ffd4" if on else TEXT
        btn.hover_bg = blend(btn.base_bg, "#ffffff", 0.12)
        btn.press_bg = blend(btn.base_bg, "#000000", 0.18)
        btn.repaint()

    def _toggle_au(self):
        self.app.save["autoupdate"] = not self.app.save.get("autoupdate", True)
        self.app.commit()
        self._paint_au()

    def _owned_tracks(self):
        owned = set(self.app.save.get("owned_music", ["classic"]))
        return [tr for tr in MUSIC_TRACKS if tr["id"] in owned]

    def _paint_tracks(self):
        owned = self._owned_tracks()
        cur = self.app.save.get("music_track", "classic")
        ids = [tr["id"] for tr in owned]
        if cur not in ids:
            cur = ids[0]
            self.app.save["music_track"] = cur
        key = (cur, tuple(ids))
        if getattr(self, "_tracks_key", None) == key:
            return  # ничего не изменилось — кнопки не пересоздаём
        self._tracks_key = key
        idx = ids.index(cur) + 1
        name = MUSIC_BY_ID[cur]["name"]
        self.track_btn.text = f"♫ {name}   ·   {idx} из {len(owned)}"
        self.track_btn.base_fg = "#c9ffd4" if len(owned) > 1 else TEXT
        self.track_btn.repaint()
        multi = len(owned) > 1
        for b in (self.track_prev_btn, self.track_next_btn):
            b.base_fg = TEXT if multi else DIM
            b.repaint()

    def _track_step(self, step):
        owned = self._owned_tracks()
        if len(owned) < 2:
            return
        ids = [tr["id"] for tr in owned]
        cur = self.app.save.get("music_track", "classic")
        if cur not in ids:
            cur = ids[0]
        self._set_track(ids[(ids.index(cur) + step) % len(ids)])

    def _track_prev(self):
        self._track_step(-1)

    def _track_next(self):
        self._track_step(1)

    def _set_track(self, key):
        if key not in set(self.app.save.get("owned_music", ["classic"])):
            return
        changed = self.app.save.get("music_track") != key
        self.app.save["music_track"] = key
        self.app.commit()
        self._rebuild()
        snd = getattr(self.app, "sound", None)
        if changed and snd is not None and self.app.save.get("music", True):
            snd.restart_music()

    def _rebuild(self, status=""):
        self.status_var.set(status)
        self._paint_low()
        self._paint_sound()
        self._paint_music()
        self._paint_au()
        self._paint_volumes()
        self._paint_tracks()
        self._paint_preview()
        level = level_from_exp(self.app.save.get("exp", 0))
        current = self.app.save.get("speed", "normal")
        if DIFFICULTIES.get(current, DIFFICULTIES["normal"])["level"] > level:
            current = "normal"
        cfg = DIFFICULTIES[current]
        if getattr(self, "_diff_key", None) != (current, level):
            self._diff_key = (current, level)
            for w in self.diff_frame.winfo_children():
                w.destroy()
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
        cur_size = self.app.save.get("window_size", "medium")
        if cur_size not in WINDOW_SIZES:
            cur_size = "medium"
        if getattr(self, "_size_key", None) != cur_size:
            self._size_key = cur_size
            for w in self.size_frame.winfo_children():
                w.destroy()
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