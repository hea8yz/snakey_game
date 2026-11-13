import tkinter
import tkinter as tk


from snakey_assets import sfx
from snakey_content import (


    ACCENT,
    ACCENT_DARK,
    ACCESSORIES,
    BG,
    BORDER,
    COLORS,
    DIM,
    FOOD_ITEMS,
    GOLD,
    GRADIENTS,
    LOCKED_BG,
    PANEL,
    TEXT,
    THEMES,
    THEME_BY_ID,
)
from snakey_drawing import draw_acc, draw_food
from snakey_save import check_achievements, level_from_exp
from snakey_utils import blend, hsv_hex, info_text, round_rect
from snakey_widgets import GradientBG, RoundButton, Screen


class ShopCard(tk.Canvas):
    def __init__(self, master, app, kind, item, refresh, card_bg=BG):
        super().__init__(master, width=146, height=66, bg=card_bg,
                         highlightthickness=0, cursor="arrow")
        self.app = app
        self.kind = kind
        self.item = item
        self.refresh = refresh
        self.clickable = False
        self.tip = None
        self.bind("<Button-1>", self._click)
        self.bind("<Motion>", self._motion)
        self.bind("<Leave>", self._leave)
        self._paint()

    def _state(self):
        s = self.app.save
        iid = self.item["id"]
        if self.kind == "color":
            return iid in s["owned"], s["selected"] == iid
        if self.kind == "theme":
            return iid in s["owned_themes"], s["theme"] == iid
        if self.kind == "acc":
            return iid in s.get("owned_acc", ["none"]), s.get("accessory") == iid
        return iid in s["owned_foods"], False

    def _swatch(self, c, sw, iid):
        if self.kind == "color":
            if iid == "rainbow":
                for k, hue in enumerate((0.0, 0.33, 0.66)):
                    c.create_arc(sw[0], sw[1], sw[2], sw[3], start=k * 120,
                                 extent=120, style="pieslice",
                                 fill=hsv_hex(hue, 0.85, 0.95), outline="")
            elif iid in GRADIENTS:
                g = GRADIENTS[iid]
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=0, extent=180,
                             style="pieslice", fill=g[0], outline="")
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=180,
                             extent=180, style="pieslice", fill=g[1],
                             outline="")
            else:
                c.create_oval(sw[0], sw[1], sw[2], sw[3], fill=iid,
                              outline=blend(iid, "#000000", 0.35))
        elif self.kind == "theme":
            t = THEME_BY_ID[iid]
            if t.get("grad"):
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=0, extent=180,
                             style="pieslice", fill=t["grad"][0], outline="")
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=180,
                             extent=180, style="pieslice", fill=t["grad"][1],
                             outline="")
            else:
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=0, extent=180,
                             style="pieslice", fill=t["grid_a"], outline="")
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=180,
                             extent=180, style="pieslice", fill=t["grid_b"],
                             outline="")
            c.create_oval(sw[0], sw[1], sw[2], sw[3], outline=t["border"])
        elif self.kind == "acc":
            if iid == "none":
                c.create_oval(sw[0], sw[1], sw[2], sw[3], outline=DIM)
                c.create_line(sw[0] + 3, sw[1] + 3, sw[2] - 3, sw[3] - 3,
                              fill=DIM)
                c.create_line(sw[0] + 3, sw[3] - 3, sw[2] - 3, sw[1] + 3,
                              fill=DIM)
            else:
                draw_acc(c, 23, 21, iid)
        else:
            draw_food(c, 23, 21, iid)

    def _paint(self):
        c = self
        c.delete("all")
        level = level_from_exp(self.app.save.get("exp", 0))
        owned, selected = self._state()
        locked = not owned and self.item.get("level", 1) > level
        round_rect(c, 1, 1, 145, 65, 13, fill=PANEL,
                   outline=ACCENT if selected else BORDER)
        sw = (12, 10, 34, 32)
        iid = self.item["id"]
        self._swatch(c, sw, iid)
        name = self.item["name"]
        if self.kind == "food":
            name = f"{name} +{self.item['value']}"
        c.create_text(40, 16, text=name, anchor="w",
                      font=(self.app.font_ui, 8, "bold"),
                      fill=DIM if locked else TEXT)
        c.create_oval(128, 4, 142, 18, fill=blend(PANEL, "#ffffff", 0.12),
                      outline=BORDER)
        c.create_text(135, 11, text="i",
                      font=(self.app.font_ui, 8, "bold"), fill=GOLD)
        if locked:
            self.clickable = False
            self.config(cursor="arrow")
            round_rect(c, 10, 38, 136, 58, 9, fill=LOCKED_BG, outline="")
            c.create_text(73, 48, text=f"\U0001f512 \u0443\u0440. {self.item['level']}",
                          font=(self.app.font_ui, 8, "bold"), fill=DIM)
            return
        if owned:
            if self.kind == "food":
                label, bg, clickable = "\u041a\u0443\u043f\u043b\u0435\u043d\u043e", BORDER, False
            elif selected:
                label, bg, clickable = "\u0412\u044b\u0431\u0440\u0430\u043d\u043e", ACCENT_DARK, False
            else:
                label, bg, clickable = "\u0412\u044b\u0431\u0440\u0430\u0442\u044c", BORDER, True
        else:
            label, bg, clickable = f"{self.item['price']} \u043c\u043e\u043d\u0435\u0442", GOLD, True
        round_rect(c, 10, 38, 136, 58, 9, fill=bg, outline="")
        if selected:
            fg = "#c9ffd4"
        elif clickable and not owned:
            fg = "#241a00"
        else:
            fg = TEXT
        c.create_text(73, 48, text=label, font=(self.app.font_ui, 8, "bold"),
                      fill=fg)
        self.clickable = clickable
        self.config(cursor="hand2" if clickable else "arrow")

    def _motion(self, event):
        if 124 <= event.x <= 146 and event.y <= 22:
            if self.tip is None:
                self._show_tip()
            return
        self._hide_tip()

    def _leave(self, _event=None):
        self._hide_tip()

    def _show_tip(self):
        try:
            win = tk.Toplevel(self)
            win.wm_overrideredirect(True)
            info = info_text(self.kind, self.item, self.app.save)
            tk.Label(win, text=info, bg=PANEL, fg=TEXT, wraplength=230,
                     justify="left", font=(self.app.font_ui, 8, "bold"),
                     padx=8, pady=5).pack()
            win.wm_geometry(
                f"+{self.winfo_pointerx() + 14}+{self.winfo_pointery() + 14}")
            self.tip = win
        except tk.TclError:
            self.tip = None

    def _hide_tip(self):
        tip = self.tip
        self.tip = None
        if tip is not None:
            try:
                tip.destroy()
            except tk.TclError:
                pass

    def _click(self, _event=None):
        self._hide_tip()
        if not self.clickable:
            return
        s = self.app.save
        owned, _ = self._state()
        iid = self.item["id"]
        if owned:
            if self.kind == "color":
                s["selected"] = iid
            elif self.kind == "theme":
                s["theme"] = iid
            elif self.kind == "acc":
                s["accessory"] = iid
            self.app.commit()
            sfx("click")
            self.app.commit()
            self.refresh("\u0412\u044b\u0431\u0440\u0430\u043d\u043e!")
            return
        if s["coins"] < self.item["price"]:
            self.refresh("\u041d\u0435 \u0445\u0432\u0430\u0442\u0430\u0435\u0442 \u043c\u043e\u043d\u0435\u0442!")
            return
        s["coins"] -= self.item["price"]
        if self.kind == "color":
            s["owned"].append(iid)
            s["selected"] = iid
        elif self.kind == "theme":
            s["owned_themes"].append(iid)
            s["theme"] = iid
        elif self.kind == "acc":
            s["owned_acc"].append(iid)
            s["accessory"] = iid
        else:
            s["owned_foods"].append(iid)
        check_achievements(s)
        self.app.commit()
        sfx("coin")
        check_achievements(s)
        self.app.commit()
        self.refresh(f"\u041a\u0443\u043f\u043b\u0435\u043d\u043e: {self.item['name']}!")
class ShopScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.mid = blend(BG, "#0f1d13", 0.55)
        self.bot = blend(BG, "#0f1d13", 0.85)
        self.bg = GradientBG(self, BG, "#0f1d13")
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=24, pady=(12, 0))
        tk.Label(head, text="\u041c\u0410\u0413\u0410\u0417\u0418\u041d", bg=BG, fg=ACCENT,
                 font=(app.font_title, 20, "bold")).pack(side="left")
        self.coins_var = tk.StringVar()
        tk.Label(head, textvariable=self.coins_var, bg=BG, fg=GOLD,
                 font=(app.font_ui, 13, "bold")).pack(side="right")

        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bg=BG, fg=DIM,
                 font=(app.font_ui, 10)).pack()

        body = tk.Frame(self, bg=self.mid)
        body.pack(fill="both", expand=True, padx=16)
        self.scroller = tk.Canvas(body, width=780, height=520, bg=self.mid,
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
        self._cols = 5

        RoundButton(self, "\u2190  \u041d\u0430\u0437\u0430\u0434", lambda: app.show("MenuScreen"),
                    width=170, height=40, app_bg=self.bot,
                    font=(app.font_ui, 11, "bold")).pack(pady=(6, 10))

    def _on_resize(self, event):
        self.scroller.itemconfig(self._win,
                                 width=max(400, event.width - 22))
        cols = 5 if event.width >= 790 else 4
        if cols != self._cols:
            self._cols = cols
            self._rebuild()

    def on_show(self):
        self._rebuild()
        self.scroller.yview_moveto(0)
        self.bg.set_animated(not self.app.save.get("low_spec"))

    def on_hide(self):
        self.bg.set_animated(False)

    def _rebuild(self, status=""):
        self.coins_var.set(f"\u25c9  {self.app.save['coins']}")
        self.status_var.set(status)
        for w in self.inner.winfo_children():
            w.destroy()
        sections = [
            ("\u0426\u0432\u0435\u0442\u0430 \u0437\u043c\u0435\u0439\u043a\u0438", "color", COLORS),
            ("\u0424\u043e\u043d\u044b  (\u0434\u043e\u0440\u043e\u0436\u0435 \u0444\u043e\u043d \u2014 \u0432\u044b\u0448\u0435 \u043c\u043d\u043e\u0436\u0438\u0442\u0435\u043b\u044c \u043c\u043e\u043d\u0435\u0442)", "theme", THEMES),
            ("\u0415\u0434\u0430  (\u0434\u043e\u0440\u043e\u0436\u0435 \u0435\u0434\u0430 \u2014 \u0431\u043e\u043b\u044c\u0448\u0435 \u043e\u0447\u043a\u043e\u0432)", "food", FOOD_ITEMS),
            ("\u0410\u043a\u0441\u0435\u0441\u0441\u0443\u0430\u0440\u044b \u0434\u043b\u044f \u0433\u043e\u043b\u043e\u0432\u044b", "acc", ACCESSORIES),
        ]
        for title, kind, items in sections:
            head = tk.Canvas(self.inner, width=770, height=30, bg=self.mid,
                             highlightthickness=0)
            head.pack(pady=(10, 2))
            round_rect(head, 1, 1, 768, 29, 14, fill=PANEL, outline=BORDER)
            head.create_text(20, 15, text=title, anchor="w",
                             font=(self.app.font_ui, 11, "bold"), fill=ACCENT)
            grid = tk.Frame(self.inner, bg=self.mid)
            grid.pack()
            cols = self._cols
            for i, item in enumerate(items):
                card = ShopCard(grid, self.app, kind, item, self._rebuild,
                                card_bg=self.mid)
                card.grid(row=i // cols, column=i % cols, padx=3, pady=3,
                          sticky="nsew")