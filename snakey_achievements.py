import math
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
from snakey_assets import sfx
from snakey_save import ach_claimable, ach_reward_text, ach_value, \
    claim_ach_reward
from snakey_utils import blend, round_rect
from snakey_widgets import (GradientBG, GradientButton, Screen,
                            gradient_round_btn)

_CARD_W = 754
_CARD_H = 84


class AchCard(tk.Canvas):
    """Карточка достижения (1.1): во всю ширину, скруглённая, градиентная.

    Состояния:
      locked  — не выполнено: тёмная, прогресс-бар;
      claim   — выполнено, награда не забрана: яркая, пульсирует, клик забирает;
      claimed — награда забрана: статичная, спокойные цвета, «ПОЛУЧЕНО ✓».
    """

    def __init__(self, master, app, ach, card_bg=BG, screen=None):
        super().__init__(master, width=_CARD_W, height=_CARD_H, bg=card_bg,
                         highlightthickness=0)
        self.app = app
        self.ach = ach
        self.screen = screen
        self._paint_key = None
        self._phase = 0.0
        self.bind("<Button-1>", self._click)
        self._paint()

    def state(self):
        save = self.app.save
        if ach_claimable(save, self.ach):
            return "claim"
        if self.ach["id"] in save.get("ach_done", []):
            return "claimed"
        return "locked"

    def _paint(self, phase=None):
        c = self
        ach = self.ach
        if phase is not None:
            self._phase = phase
        # перф: карточка перерисовывается только когда состояние или прогресс
        # реально сменились (пульсация claim-карточек идёт через phase и не кэшируется)
        st = self.state()
        val = ach_value(ach, self.app.save)
        goal = ach["goal"]
        if phase is None:
            key = (st, round(min(val, goal) / max(1, goal), 2))
            if key == getattr(self, "_paint_key", None):
                return
            self._paint_key = key
        c.delete("all")
        frac = max(0.0, min(1.0, val / goal))
        W, H = _CARD_W, _CARD_H
        pulse = 0.5 + 0.5 * math.sin(self._phase * 2.4)
        if st == "claim":
            glow = 0.10 + 0.10 * pulse
            gradient_round_btn(c, 2, 2, W - 2, H - 2, 18, "#8957e5",
                               blend("#5b2fb8", "#ffffff", glow), steps=12)
            round_rect(c, 2, 2, W - 2, H - 2, 18, fill="",
                       outline=blend("#c9a8ff", "#ffffff", 0.25 * pulse),
                       width=2)
        elif st == "claimed":
            gradient_round_btn(c, 2, 2, W - 2, H - 2, 18, PANEL,
                               blend(PANEL, "#8957e5", 0.14), steps=12)
            round_rect(c, 2, 2, W - 2, H - 2, 18, fill="",
                       outline=blend(BORDER, "#8957e5", 0.4))
        else:
            gradient_round_btn(c, 2, 2, W - 2, H - 2, 18, PANEL,
                               blend(PANEL, "#000000", 0.22), steps=12)
            round_rect(c, 2, 2, W - 2, H - 2, 18, fill="", outline=BORDER)
        # значок слева
        bx0, by0, bx1, by1 = 14, H // 2 - 28, 70, H // 2 + 28
        if st == "claim":
            c.create_oval(bx0, by0, bx1, by1, fill="#a371f7",
                          outline=blend("#ffffff", "#c9a8ff", 0.5), width=2)
        elif st == "claimed":
            c.create_oval(bx0, by0, bx1, by1, fill="#4b3577",
                          outline="#8957e5")
        else:
            c.create_oval(bx0, by0, bx1, by1, fill="#241a3a", outline="#4b3577")
        c.create_text((bx0 + bx1) // 2, H // 2 - 1,
                      text="✓" if st != "locked" else "★",
                      font=(self.app.font_title, 18, "bold"),
                      fill="#ffffff" if st == "claim" else "#c9a8ff")
        # название и описание
        tx = 84
        c.create_text(tx, 16, text=ach["name"], anchor="w",
                      font=(self.app.font_ui, 12, "bold"),
                      fill="#ffffff" if st == "claim"
                      else "#e2d5ff" if st == "claimed" else TEXT)
        c.create_text(tx, 36, text=ach["desc"], anchor="w",
                      font=(self.app.font_ui, 9), fill=DIM)
        # прогресс (только у невыполненных)
        if st == "locked":
            round_rect(c, tx, 52, tx + 310, 66, 7, fill=LOCKED_BG, outline="")
            if frac > 0:
                round_rect(c, tx, 52, int(tx + max(8, 310 * frac)), 66, 7,
                           fill="#a371f7", outline="")
            c.create_text(tx + 320, 59, text=f"{min(val, goal)}/{goal}",
                          anchor="w", font=(self.app.font_ui, 9, "bold"),
                          fill=DIM)
        # награда справа
        rx = W - 18
        c.create_text(rx, 22, text=f"🎁  {ach_reward_text(ach)}", anchor="e",
                      font=(self.app.font_ui, 10, "bold"), fill=GOLD)
        if st == "claim":
            # кнопка «Забрать» — пульсирует вместе с карточкой
            kx1, ky1, kx2, ky2 = W - 190, 44, W - 18, 72
            gradient_round_btn(c, kx1, ky1, kx2, ky2, 14, "#2ea043",
                               blend("#155d24", "#ffffff", 0.12 * pulse),
                               steps=8)
            c.create_text((kx1 + kx2) // 2, (ky1 + ky2) // 2,
                          text="🎁 Забрать награду",
                          font=(self.app.font_ui, 10, "bold"),
                          fill="#eafff0")
            self.config(cursor="hand2")
        elif st == "claimed":
            c.create_text(rx, 52, text="ПОЛУЧЕНО ✓", anchor="e",
                          font=(self.app.font_ui, 10, "bold"), fill="#7ee787")
            self.config(cursor="arrow")
        else:
            c.create_text(rx, 52, text="—", anchor="e",
                          font=(self.app.font_ui, 10, "bold"), fill=DIM)
            self.config(cursor="arrow")

    def _click(self, _event=None):
        if self.state() != "claim":
            return
        if self.screen is not None:
            self.screen.claim(self)


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
        self._ach_queue = None
        self._anim_job = None
        self._anim_t = 0.0
        GradientButton(self, "←  Назад", lambda: app.show("MenuScreen"),
                       width=190, height=44, radius=18, c1="#8957e5",
                       c2="#5b2fb8", fg="#f4efff", app_bg=self.bot,
                       font=(app.font_ui, 12, "bold"),
                       hover_scale=0.04).pack(pady=(6, 10))

    def on_show(self):
        self._rebuild()
        self.bg.set_animated(not self.app.save.get("low_spec"))
        self.scroller.yview_moveto(0)
        self._start_anim()

    def on_hide(self):
        self.bg.set_animated(False)
        self._stop_anim()

    def _start_anim(self):
        self._stop_anim()
        if self.app.save.get("low_spec"):
            return
        self._anim_job = self.after(140, self._anim_step)

    def _stop_anim(self):
        if self._anim_job is not None:
            try:
                self.after_cancel(self._anim_job)
            except Exception:
                pass
            self._anim_job = None

    def _anim_step(self):
        self._anim_job = None
        self._anim_t += 0.14
        # лёгкая пульсация: перерисовываем только карточки с наградой
        for card in self._cards:
            if card.state() == "claim":
                try:
                    card._paint(self._anim_t)
                except tk.TclError:
                    pass
        self._anim_job = self.after(140, self._anim_step)

    def claim(self, card):
        ach = card.ach
        if claim_ach_reward(self.app.save, ach):
            self.app.commit()
            sfx("coin")
            self._rebuild(f"Награда получена: {ach['name']}!")
        else:
            self._rebuild()

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
        # 120 карточек строим порциями в фоне: вкладка открывается мгновенно
        self._ach_queue = list(ACHIEVEMENTS)
        self._ach_build_batch()

    def _ach_build_batch(self, batch=16):
        queue = self._ach_queue
        if not queue:
            self._ach_queue = None
            return
        for ach in queue[:batch]:
            card = AchCard(self.inner, self.app, ach, card_bg=self.mid,
                           screen=self)
            card.pack(fill="x", pady=3)
            self._cards.append(card)
        del queue[:batch]
        try:
            self.after(1, self._ach_build_batch)
        except Exception:
            self._ach_queue = None
