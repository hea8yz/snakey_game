import tkinter as tk


from snakey_content import (

    ACCENT_DARK,
    BG,
    BLUE,
    DIFFICULTIES,
    DIM,
    GOLD,
    LOCKED_BG,
    MG_DIFF_ORDER,
    MINIGAMES,
    PANEL,
    TEXT,
)
from snakey_save import level_from_exp
from snakey_utils import blend, round_rect
from snakey_widgets import GradientBG, RoundButton, Screen

GAME_ORDER = ("mg1", "mg2", "mg3", "mg4", "mg5", "mg6", "mg7", "mg8",
              "mg9", "mg10")
CARD_W = 700
CARD_H = 150


class MiniScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.mid = blend(BG, "#0c1a30", 0.55)
        self.bot = blend(BG, "#0c1a30", 0.85)
        self.bg = GradientBG(self, BG, "#0c1a30", accent=BLUE)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Label(self, text="МИНИ-ИГРЫ", bg=BG, fg=BLUE,
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
        RoundButton(self, "←  Назад", lambda: app.show("MenuScreen"),
                    width=170, height=40, app_bg=self.bot,
                    font=(app.font_ui, 11, "bold")).pack(pady=(6, 8))

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
                            "\u041a\u043e\u043b\u0435\u0441\u043e \u043c\u044b\u0448\u0438 \u2014 \u043f\u0440\u043e\u043a\u0440\u0443\u0442\u043a\u0430 \u00b7 \u0441\u043b\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u0432\u043b\u0438\u044f\u0435\u0442 "
                            "\u043d\u0430 \u0441\u043a\u043e\u0440\u043e\u0441\u0442\u044c \u0438 \u043d\u0430\u0433\u0440\u0430\u0434\u044b")
        level = level_from_exp(self.app.save.get("exp", 0))
        if self._card_widgets and self._built_level == level:
            # \u043a\u0430\u0440\u0442\u043e\u0447\u043a\u0438 \u0443\u0436\u0435 \u0441\u043e\u0437\u0434\u0430\u043d\u044b \u2014 \u0442\u043e\u043b\u044c\u043a\u043e \u043e\u0431\u043d\u043e\u0432\u0438\u0442\u044c \u0441\u0442\u0430\u0442\u044b \u0438 \u043a\u043d\u043e\u043f\u043a\u0438 \u0441\u043b\u043e\u0436\u043d\u043e\u0441\u0442\u0435\u0439:
            # \u0432\u043a\u043b\u0430\u0434\u043a\u0430 \u043e\u0442\u043a\u0440\u044b\u0432\u0430\u0435\u0442\u0441\u044f \u043c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u043e, \u0431\u0435\u0437 \u043f\u0435\u0440\u0435\u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f \u0432\u0438\u0434\u0436\u0435\u0442\u043e\u0432
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
        round_rect(card, 1, 1, CARD_W - 1, CARD_H - 1, 16, fill=PANEL,
                   outline=BLUE)
        round_rect(card, 9, 12, 14, CARD_H - 12, 3, fill=BLUE, outline="")
        card.create_text(26, 26, text=f"{mg['icon']}  {mg['label']}",
                         anchor="w", font=(self.app.font_title, 14, "bold"),
                         fill=BLUE)
        card.create_text(26, 52, text=mg.get("desc", ""), anchor="nw",
                         width=520, justify="left",
                         font=(self.app.font_ui, 9), fill=DIM)
        st = self._stats()
        stat = mg.get("stat")
        stat_line = (mg.get("stat_label", "{}").format(st.get(stat, 0))
                     if stat else "")
        card._stat_id = card.create_text(26, 92, text=stat_line, anchor="w",
                                         font=(self.app.font_ui, 11, "bold"),
                                         fill=GOLD)
        level, current = self._current_diff(mg_key)
        row = tk.Frame(card, bg=PANEL)
        card._row_win = card.create_window(26, 124, window=row, anchor="w")
        card._row = row
        card._diff_state = (level, current)
        self._build_diff_buttons(card, mg_key, row, level, current)
        play = RoundButton(card, "\u0418\u0413\u0420\u0410\u0422\u042c", lambda: self._play(mg_key),
                           width=120, height=44, bg=BLUE, fg="#061224",
                           app_bg=PANEL, font=(self.app.font_ui, 12, "bold"))
        card.create_window(622, 96, window=play)

    def _build_diff_buttons(self, card, mg_key, row, level, current):
        mg = MINIGAMES[mg_key]
        for key in MG_DIFF_ORDER:
            dcfg = mg["diffs"][key]
            if dcfg["level"] > level:
                btn = RoundButton(row, f"\U0001f512 \u0443\u0440. {dcfg['level']}", width=118,
                                  height=32, bg=LOCKED_BG, fg=DIM,
                                  app_bg=PANEL,
                                  font=(self.app.font_ui, 9, "bold"))
            else:
                selected = key == current
                btn = RoundButton(
                    row, f"{DIFFICULTIES[key]['label']} \u00b7 \u00d7{dcfg['reward']:g}",
                    command=(lambda k=key, m=mg_key: self._set_diff(m, k)),
                    width=118, height=32,
                    bg=ACCENT_DARK if selected else "#1c2f4a",
                    fg="#c9ffd4" if selected else TEXT, app_bg=PANEL,
                    font=(self.app.font_ui, 9, "bold"))
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
        # \u0442\u043e\u0447\u0435\u0447\u043d\u043e\u0435 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435 \u043e\u0434\u043d\u043e\u0439 \u043a\u0430\u0440\u0442\u043e\u0447\u043a\u0438 \u2014 \u0441\u043f\u0438\u0441\u043e\u043a \u043d\u0435 \u043f\u0435\u0440\u0435\u0441\u043e\u0437\u0434\u0430\u0451\u0442\u0441\u044f,
        # \u043f\u0440\u043e\u043a\u0440\u0443\u0442\u043a\u0430 \u043d\u0435 \u0441\u0431\u0440\u0430\u0441\u044b\u0432\u0430\u0435\u0442\u0441\u044f
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
