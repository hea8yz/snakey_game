import tkinter as tk


from snakey_content import (


    ACHIEVEMENTS,
    BG,
    BORDER,
    DIM,
    GOLD,
    LOCKED_BG,
    PANEL,
    TEXT,
)
from snakey_save import ach_reward_text, ach_value
from snakey_utils import blend, round_rect
from snakey_widgets import GradientBG, RoundButton, Screen

class AchCard(tk.Canvas):
    def __init__(self, master, app, ach, card_bg=BG):
        super().__init__(master, width=750, height=56, bg=card_bg,
                         highlightthickness=0)
        self.app = app
        self.ach = ach
        self._paint()

    def _paint(self):
        c = self
        ach = self.ach
        c.delete("all")
        done = ach["id"] in self.app.save.get("ach_done", [])
        val = ach_value(ach, self.app.save)
        goal = ach["goal"]
        frac = max(0.0, min(1.0, val / goal))
        round_rect(c, 1, 1, 749, 55, 13, fill=PANEL,
                   outline="#8957e5" if done else BORDER)
        c.create_oval(10, 10, 46, 46, fill="#8957e5" if done else "#3a2a5e",
                      outline="#a371f7")
        c.create_text(28, 28, text="✓" if done else "★",
                      font=(self.app.font_title, 14, "bold"),
                      fill="#ffffff" if done else "#c9a8ff")
        c.create_text(56, 16, text=ach["name"], anchor="w",
                      font=(self.app.font_ui, 10, "bold"),
                      fill="#e2d5ff" if done else TEXT)
        c.create_text(56, 32, text=ach["desc"], anchor="w",
                      font=(self.app.font_ui, 8), fill=DIM)
        round_rect(c, 56, 42, 356, 50, 4, fill=LOCKED_BG, outline="")
        if frac > 0:
            round_rect(c, 56, 42, int(56 + max(6, 300 * frac)), 50, 4,
                       fill="#a371f7", outline="")
        c.create_text(366, 46, text=f"{min(val, goal)}/{goal}", anchor="w",
                      font=(self.app.font_ui, 8, "bold"), fill=DIM)
        c.create_text(738, 20, text=f"🎁  {ach_reward_text(ach)}", anchor="e",
                      font=(self.app.font_ui, 9, "bold"), fill=GOLD)
        if done:
            c.create_text(738, 38, text="ПОЛУЧЕНО ✓", anchor="e",
                          font=(self.app.font_ui, 9, "bold"), fill="#7ee787")
class AchScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.mid = blend(BG, "#160f28", 0.55)
        self.bot = blend(BG, "#160f28", 0.85)
        self.bg = GradientBG(self, BG, "#160f28", accent="#8957e5")
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=24, pady=(12, 0))
        tk.Label(head, text="ДОСТИЖЕНИЯ", bg=BG, fg="#c9a8ff",
                 font=(app.font_title, 20, "bold")).pack(side="left")
        self.count_var = tk.StringVar()
        tk.Label(head, textvariable=self.count_var, bg=BG, fg="#a371f7",
                 font=(app.font_ui, 13, "bold")).pack(side="right")
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bg=BG, fg=DIM,
                 font=(app.font_ui, 10)).pack()
        self.prog = tk.Canvas(self, width=420, height=14, bg=BG,
                              highlightthickness=0)
        self.prog.pack(pady=(2, 0))
        body = tk.Frame(self, bg=self.mid)
        body.pack(fill="both", expand=True, padx=24)
        self.scroller = tk.Canvas(body, width=770, height=520, bg=self.mid,
                                  highlightthickness=0)
        bar = tk.Scrollbar(body, orient="vertical", command=self.scroller.yview)
        self.scroller.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.scroller.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.scroller, bg=self.mid)
        self._win = self.scroller.create_window((0, 0), window=self.inner,
                                                anchor="nw", width=754)
        self.inner.bind("<Configure>",
                        lambda e: self.scroller.configure(
                            scrollregion=self.scroller.bbox("all")))
        self.scroller.bind("<Configure>", self._on_resize)
        self._cards = []
        self._built = False
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

    def _rebuild(self, status=""):
        self.status_var.set(status)
        done = self.app.save.get("ach_done", [])
        self.count_var.set(f"{len(done)} / {len(ACHIEVEMENTS)}")
        frac = len(done) / max(1, len(ACHIEVEMENTS))
        p = self.prog
        p.delete("all")
        round_rect(p, 1, 1, 418, 13, 6, fill=LOCKED_BG, outline=BORDER)
        if frac > 0:
            width = max(14, round(418 * frac))
            seg_w = width / 5
            for k in range(5):
                col = blend("#8957e5", "#c9a8ff", k / 4)
                round_rect(p, 1 + k * seg_w, 1, 1 + (k + 1) * seg_w, 13, 5,
                           fill=col, outline="")
        if self._built and self._cards:
            # карточки уже созданы — только обновить их состояние
            alive = []
            for card in self._cards:
                try:
                    card._paint()
                    alive.append(card)
                except tk.TclError:
                    pass
            self._cards = alive
            if len(self._cards) == len(ACHIEVEMENTS):
                return
        self._built = True
        for w in self.inner.winfo_children():
            w.destroy()
        self._cards = []
        for ach in ACHIEVEMENTS:
            card = AchCard(self.inner, self.app, ach, card_bg=self.mid)
            card.pack(fill="x", pady=3)
            self._cards.append(card)