import tkinter as tk


from snakey_content import (

    BG,
    BLUE,
    DIFFICULTIES,
    DIFF_SLIDER,
    DIM,
    GOLD,
    LOCKED_BG,
    MG_DIFF_ORDER,
    MINIGAMES,
    PANEL,
)
from snakey_save import level_from_exp
from snakey_utils import blend, round_rect
from snakey_widgets import (GradientBG, GradientButton, RoundButton, Screen,
                            gradient_round_btn)

GAME_ORDER = ("mg1", "mg2", "mg3", "mg4", "mg5", "mg6", "mg7", "mg8",
              "mg9", "mg10")
CARD_W = 754
CARD_H = 170
_PLAY_W = 110


class MiniScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.mid = blend(BG, "#0c1a30", 0.55)
        self.bot = blend(BG, "#0c1a30", 0.85)
        self.bg = GradientBG(self, BG, "#0c1a30", accent=BLUE)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Label(self, text="МИНИ-ИГРЫ", bg=BG, fg="#7cb3ff",
                 font=(app.font_title, 20, "bold")).pack(pady=(12, 2))
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bg=BG, fg=DIM,
                 font=(app.font_ui, 10)).pack()
        shell_row = tk.Frame(self, bg=BG)
        shell_row.pack(pady=6, expand=True, fill="both")
        self.scroller = tk.Canvas(shell_row, bg=BG, highlightthickness=0)
        bar = tk.Scrollbar(shell_row, orient="vertical",
                           command=self.scroller.yview)
        self.scroller.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.scroller.pack(side="left", fill="both", expand=True)
        self.card_holder = tk.Frame(self.scroller, bg=self.mid)
        self.scroller.create_window((0, 0), window=self.card_holder,
                                    anchor="nw", width=CARD_W + 20)
        self.card_holder.bind(
            "<Configure>",
            lambda _e: self.scroller.configure(
                scrollregion=self.scroller.bbox("all")))
        self._card_widgets = {}
        self._built_level = -1
        GradientButton(self, "←  Назад", lambda: app.show("MenuScreen"),
                       width=190, height=44, radius=18, c1="#3b82f6",
                       c2="#1d4ed8", fg="#eaf2ff", app_bg=self.bot,
                       font=(app.font_ui, 12, "bold"),
                       hover_scale=0.04).pack(pady=(6, 8))

    def on_show(self):
        self._rebuild()
        self.bg.set_animated(not self.app.save.get("low_spec"))

    def on_hide(self):
        self.bg.set_animated(False)

    def _stats(self):
        st = self.app.save.get("stats")
        return st if isinstance(st, dict) else {}

    def _rebuild(self, status="", reset_scroll=True):
        self.status_var.set(status or
                            "Колесо мыши — прокрутка · сложность влияет "
                            "на скорость и награды")
        level = level_from_exp(self.app.save.get("exp", 0))
        if self._card_widgets and self._built_level == level:
            # карточки уже созданы — только обновить статы и кнопки сложностей:
            # вкладка открывается мгновенно, без пересоздания виджетов
            for mg_key in GAME_ORDER:
                self._refresh_card_state(mg_key)
            if reset_scroll:
                self.scroller.yview_moveto(0)
            return
        self._built_level = level
        for w in self.card_holder.winfo_children():
            w.destroy()
        self._card_widgets = {}
        for mg_key in GAME_ORDER:
            self._card(mg_key)
        if reset_scroll:
            self.scroller.yview_moveto(0)

    def _current_diff(self, mg_key):
        level = level_from_exp(self.app.save.get("exp", 0))
        current = self.app.save.get(f"{mg_key}_diff", "normal")
        if current not in MINIGAMES[mg_key]["diffs"]:
            current = "normal"
        if MINIGAMES[mg_key]["diffs"][current]["level"] > level:
            current = "normal"
        return level, current

    def _card(self, mg_key):
        mg = MINIGAMES[mg_key]
        card = tk.Canvas(self.card_holder, width=CARD_W, height=CARD_H,
                         bg=self.mid, highlightthickness=0)
        prev = None
        idx = GAME_ORDER.index(mg_key)
        for k in GAME_ORDER[idx + 1:]:
            w = self._card_widgets.get(k)
            if w is not None:
                try:
                    w.winfo_exists()
                except tk.TclError:
                    continue
                prev = w
                break
        if prev is not None:
            card.pack(pady=4, before=prev)
        else:
            card.pack(pady=4)
        self._card_widgets[mg_key] = card
        # скруглённая градиентная карточка во всю ширину
        gradient_round_btn(card, 2, 2, CARD_W - 2, CARD_H - 2, 18, PANEL,
                           blend(PANEL, "#0c1a30", 0.4), steps=12)
        round_rect(card, 2, 2, CARD_W - 2, CARD_H - 2, 18, fill="",
                   outline=blend(BLUE, PANEL, 0.35))
        round_rect(card, 10, 14, 15, CARD_H - 14, 3, fill=BLUE, outline="")
        card.create_text(28, 28, text=f"{mg['icon']}  {mg['label']}",
                         anchor="w", font=(self.app.font_title, 15, "bold"),
                         fill="#7cb3ff")
        card.create_text(28, 56, text=mg.get("desc", ""), anchor="nw",
                         width=500, justify="left",
                         font=(self.app.font_ui, 9), fill=DIM)
        st = self._stats()
        stat = mg.get("stat")
        stat_line = (mg.get("stat_label", "{}").format(st.get(stat, 0))
                     if stat else "")
        card._stat_id = card.create_text(28, 100, text=stat_line, anchor="w",
                                         font=(self.app.font_ui, 11, "bold"),
                                         fill=GOLD)
        level, current = self._current_diff(mg_key)
        row = tk.Frame(card, bg=PANEL)
        card._row_win = card.create_window(28, 140, window=row, anchor="w")
        card._row = row
        card._diff_state = (level, current)
        self._build_diff_buttons(card, mg_key, row, level, current)
        # кнопка ИГРАТЬ высотой во всю карточку
        play = GradientButton(
            card, "ИГРАТЬ", lambda: self._play(mg_key),
            width=_PLAY_W, height=CARD_H - 24, radius=16,
            c1="#3b82f6", c2="#1d4ed8", fg="#eaf2ff", app_bg=self.mid,
            font=(self.app.font_ui, 13, "bold"), hover_scale=0.05)
        card.create_window(CARD_W - _PLAY_W // 2 - 14, CARD_H // 2,
                           window=play)

    def _build_diff_buttons(self, card, mg_key, row, level, current):
        """Сложности как в настройках (1.1): крупные градиентные кнопки
        с плавным hover-увеличением и плавающими стикерами."""
        mg = MINIGAMES[mg_key]
        for key in MG_DIFF_ORDER:
            dcfg = mg["diffs"][key]
            if dcfg["level"] > level:
                btn = RoundButton(row, f"\U0001f512 ур. {dcfg['level']}",
                                  width=128, height=48, bg=LOCKED_BG, fg=DIM,
                                  app_bg=PANEL,
                                  font=(self.app.font_ui, 10, "bold"))
            else:
                col = DIFF_SLIDER[key][0]
                selected = key == current
                lit = "#ffffff" if selected else "#000000"
                amt = 0.22 if selected else 0.0
                btn = GradientButton(
                    row, f"{DIFFICULTIES[key]['label']} · ×{dcfg['reward']:g}",
                    command=(lambda k=key, m=mg_key: self._set_diff(m, k)),
                    width=128, height=48, radius=14,
                    c1=blend(col, lit, amt),
                    c2=blend(DIFF_SLIDER[key][1], lit, amt),
                    fg="#0b2413" if key in ("normal", "medium") else "#fff3e0",
                    app_bg=PANEL, font=(self.app.font_ui, 10, "bold"),
                    hover_scale=0.05, sticker_key=key, sticker_color=col)
            btn.pack(side="left", padx=3)

    def _set_diff(self, mg_key, key):
        if key not in MG_DIFF_ORDER or mg_key not in MINIGAMES:
            return
        level = level_from_exp(self.app.save.get("exp", 0))
        if MINIGAMES[mg_key]["diffs"][key]["level"] > level:
            return
        self.app.save[f"{mg_key}_diff"] = key
        self.app.commit()
        # пересоздаём только одну карточку — прокрутка списка не сбрасывается
        self._refresh_card(mg_key)

    def _refresh_card(self, mg_key):
        # точечное обновление одной карточки — список не пересоздаётся,
        # прокрутка не сбрасывается
        self._refresh_card_state(mg_key)

    def _refresh_card_state(self, mg_key):
        card = self._card_widgets.get(mg_key)
        if card is None:
            return
        try:
            card.winfo_exists()
        except tk.TclError:
            self._card_widgets.pop(mg_key, None)
            return
        mg = MINIGAMES[mg_key]
        st = self._stats()
        stat = mg.get("stat")
        stat_line = (mg.get("stat_label", "{}").format(st.get(stat, 0))
                     if stat else "")
        try:
            card.itemconfig(card._stat_id, text=stat_line)
        except tk.TclError:
            pass
        level, current = self._current_diff(mg_key)
        if getattr(card, "_diff_state", None) != (level, current):
            row = getattr(card, "_row", None)
            if row is not None:
                try:
                    row.destroy()
                except tk.TclError:
                    pass
            row = tk.Frame(card, bg=PANEL)
            card.itemconfig(card._row_win, window=row)
            card._row = row
            card._diff_state = (level, current)
            self._build_diff_buttons(card, mg_key, row, level, current)

    def _set_mg_diff(self, key):
        self._set_diff("mg1", key)

    def _play(self, mg_key):
        if mg_key not in MINIGAMES:
            return
        level = level_from_exp(self.app.save.get("exp", 0))
        diff = self.app.save.get(f"{mg_key}_diff", "normal")
        if diff not in MINIGAMES[mg_key]["diffs"]:
            diff = "normal"
        if MINIGAMES[mg_key]["diffs"][diff]["level"] > level:
            diff = "normal"
        self.app.next_mode = mg_key
        self.app.next_diff = diff
        self.app.show("GameScreen")
