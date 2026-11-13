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
        self.card_holder = tk.Frame(self, bg=self.mid)
        self.card_holder.pack(pady=6, expand=True)
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

    def _rebuild(self, status=""):
        self.status_var.set(status)
        for w in self.card_holder.winfo_children():
            w.destroy()
        self._card_mg1()
        self._card_mg2()
        self._card_mg3()

    def _card_base(self, height):
        card = tk.Canvas(self.card_holder, width=700, height=height,
                         bg=self.mid, highlightthickness=0)
        card.pack(pady=4)
        round_rect(card, 1, 1, 698, height - 1, 16, fill=PANEL, outline=BLUE)
        round_rect(card, 9, 12, 14, height - 12, 3, fill=BLUE, outline="")
        return card

    def _play_btn(self, card, mg_key, x, y):
        btn = RoundButton(card, "ИГРАТЬ", lambda: self._play(mg_key),
                          width=130, height=42, bg=BLUE, fg="#061224",
                          app_bg=PANEL, font=(self.app.font_ui, 12, "bold"))
        card.create_window(x, y, window=btn)

    def _card_mg1(self):
        card = self._card_base(176)
        card.create_text(26, 30, text="🍎  СБОР ЯБЛОК", anchor="w",
                         font=(self.app.font_title, 15, "bold"), fill=BLUE)
        card.create_text(26, 58, text="Собери как можно больше яблок за отведённое время!",
                         anchor="w", font=(self.app.font_ui, 10, "bold"), fill=TEXT)
        card.create_text(26, 77, text="Препятствия и скорость зависят от сложности · границы проходимы",
                         anchor="w", font=(self.app.font_ui, 9), fill=DIM)
        mg1_best = self._stats().get("mg1_best", 0)
        card.create_text(26, 97, text=f"Рекорд: {mg1_best} яблок",
                         anchor="w", font=(self.app.font_ui, 11, "bold"), fill=GOLD)
        level = level_from_exp(self.app.save.get("exp", 0))
        current = self.app.save.get("mg1_diff", "normal")
        if current not in MINIGAMES["mg1"]["diffs"]:
            current = "normal"
        if MINIGAMES["mg1"]["diffs"][current]["level"] > level:
            current = "normal"
        row = tk.Frame(card, bg=PANEL)
        card.create_window(26, 140, window=row, anchor="w")
        for key in MG_DIFF_ORDER:
            dcfg = MINIGAMES["mg1"]["diffs"][key]
            if dcfg["level"] > level:
                btn = RoundButton(row, f"🔒 ур. {dcfg['level']}", width=118,
                                  height=32, bg=LOCKED_BG, fg=DIM, app_bg=PANEL,
                                  font=(self.app.font_ui, 9, "bold"))
            else:
                selected = key == current
                btn = RoundButton(
                    row, f"{DIFFICULTIES[key]['label']} · {dcfg['time']}с",
                    command=(lambda k=key: self._set_mg_diff(k)),
                    width=118, height=32,
                    bg=ACCENT_DARK if selected else "#1c2f4a",
                    fg="#c9ffd4" if selected else TEXT, app_bg=PANEL,
                    font=(self.app.font_ui, 9, "bold"))
            btn.pack(side="left", padx=3)
        self._play_btn(card, "mg1", 622, 96)

    def _card_mg2(self):
        card = self._card_base(122)
        card.create_text(26, 28, text="🧠  ПОПРОБУЙ ЗАПОМНИТЬ!", anchor="w",
                         font=(self.app.font_title, 15, "bold"), fill=BLUE)
        card.create_text(26, 54, text="Запомни цвет фрукта и найди его среди 8 оттенков!",
                         anchor="w", font=(self.app.font_ui, 10, "bold"), fill=TEXT)
        card.create_text(26, 73, text="Победа: 10 монет × множитель · неверный цвет — поражение",
                         anchor="w", font=(self.app.font_ui, 9), fill=DIM)
        wins = self._stats().get("mg2_wins", 0)
        card.create_text(26, 94, text=f"Побед: {wins}",
                         anchor="w", font=(self.app.font_ui, 11, "bold"), fill=GOLD)
        self._play_btn(card, "mg2", 622, 66)

    def _card_mg3(self):
        card = self._card_base(122)
        card.create_text(26, 28, text="🧺  ЯБЛОЧНЫЙ СБОР", anchor="w",
                         font=(self.app.font_title, 15, "bold"), fill=BLUE)
        card.create_text(26, 54, text="Приноси яблоки в зону сбора — размер змейки не меняется!",
                         anchor="w", font=(self.app.font_ui, 10, "bold"), fill=TEXT)
        card.create_text(26, 73, text="+12 монет за каждое яблоко × множитель · 60 секунд · граница — в начало",
                         anchor="w", font=(self.app.font_ui, 9), fill=DIM)
        mg3_best = self._stats().get("mg3_best", 0)
        card.create_text(26, 94, text=f"Рекорд: {mg3_best} яблок",
                         anchor="w", font=(self.app.font_ui, 11, "bold"), fill=GOLD)
        self._play_btn(card, "mg3", 622, 66)

    def _set_mg_diff(self, key):
        level = level_from_exp(self.app.save.get("exp", 0))
        if MINIGAMES["mg1"]["diffs"][key]["level"] > level:
            return
        self.app.save["mg1_diff"] = key
        self.app.commit()
        self._rebuild()

    def _play(self, mg_key):
        self.app.next_mode = mg_key
        if mg_key == "mg1":
            diff = self.app.save.get("mg1_diff", "normal")
            self.app.next_diff = (diff if diff in MINIGAMES["mg1"]["diffs"]
                                  else "normal")
        else:
            self.app.next_diff = "normal"
        self.app.show("GameScreen")