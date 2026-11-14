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
                            "Колесо мыши — прокрутка · сложность влияет "
                            "на скорость и награды")
        for w in self.card_holder.winfo_children():
            w.destroy()
        self._card_widgets = {}
        for mg_key in GAME_ORDER:
            self._card(mg_key)
        if reset_scroll:
            self.scroller.yview_moveto(0)

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
        card.create_text(26, 92, text=stat_line, anchor="w",
                         font=(self.app.font_ui, 11, "bold"), fill=GOLD)
        level = level_from_exp(self.app.save.get("exp", 0))
        current = self.app.save.get(f"{mg_key}_diff", "normal")
        if current not in mg["diffs"]:
            current = "normal"
        if mg["diffs"][current]["level"] > level:
            current = "normal"
        row = tk.Frame(card, bg=PANEL)
        card.create_window(26, 124, window=row, anchor="w")
        for key in MG_DIFF_ORDER:
            dcfg = mg["diffs"][key]
            if dcfg["level"] > level:
                btn = RoundButton(row, f"🔒 ур. {dcfg['level']}", width=118,
                                  height=32, bg=LOCKED_BG, fg=DIM,
                                  app_bg=PANEL,
                                  font=(self.app.font_ui, 9, "bold"))
            else:
                selected = key == current
                btn = RoundButton(
                    row, f"{DIFFICULTIES[key]['label']} · ×{dcfg['reward']:g}",
                    command=(lambda k=key, m=mg_key: self._set_diff(m, k)),
                    width=118, height=32,
                    bg=ACCENT_DARK if selected else "#1c2f4a",
                    fg="#c9ffd4" if selected else TEXT, app_bg=PANEL,
                    font=(self.app.font_ui, 9, "bold"))
            btn.pack(side="left", padx=3)
        play = RoundButton(card, "ИГРАТЬ", lambda: self._play(mg_key),
                           width=120, height=44, bg=BLUE, fg="#061224",
                           app_bg=PANEL, font=(self.app.font_ui, 12, "bold"))
        card.create_window(622, 96, window=play)

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
        old_card = self._card_widgets.get(mg_key)
        if old_card is not None:
            try:
                old_card.destroy()
            except tk.TclError:
                pass
        self._card(mg_key)

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
