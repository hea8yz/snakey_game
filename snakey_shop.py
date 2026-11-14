import tkinter
import tkinter as tk


from snakey_assets import sfx
from snakey_content import (

    ACCENT,
    ACCENT_BRIGHT,
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
from snakey_widgets import (GradientBG, GradientButton, Screen,
                            gradient_round_btn, refocus_app)


_OPEN_TIPS = set()
def close_all_tips():
    """Закрывает все открытые тултипы (защита от «невидимых» окон,
    поглощающих клики после пересоздания карточек)."""
    for win in list(_OPEN_TIPS):
        try:
            win.destroy()
        except tk.TclError:
            pass
    _OPEN_TIPS.clear()


_BTN_GREEN = ("#2ea043", "#155d24")
_BTN_GREEN_FG = "#eafff0"
_COLS = 3          # крупных карточек в ряд
_MINI_COLS = 6     # мини-карточек в ряд на вкладке «Показать все»


class ShopCard(tk.Canvas):
    """Карточка товара.

    mini=False — большая карточка (210x196): товар крупно, название,
    овальная кнопка покупки/выбора снизу, кнопка (i) справа сверху.
    mini=True  — маленькая карточка (118x96) для вкладки «Показать все»:
    только товар и кнопка выбрать/выбрано.
    """

    def __init__(self, master, app, kind, item, refresh, card_bg=BG,
                 mini=False):
        w, h = (118, 96) if mini else (210, 196)
        super().__init__(master, width=w, height=h, bg=card_bg,
                         highlightthickness=0, cursor="arrow")
        self.app = app
        self.kind = kind
        self.item = item
        self.refresh = refresh
        self.mini = mini
        self.clickable = False
        self.gridded = True
        self.tip = None
        self.bind("<Button-1>", self._click)
        if not mini:
            self.bind("<Motion>", self._motion)
            self.bind("<Leave>", self._leave)
        self.bind("<Destroy>", lambda e: self._hide_tip())
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
        """Товар в области sw=(x1,y1,x2,y2)."""
        x1, y1, x2, y2 = sw
        if self.kind == "color":
            if iid == "rainbow":
                for k, hue in enumerate((0.0, 0.33, 0.66)):
                    c.create_arc(x1, y1, x2, y2, start=k * 120,
                                 extent=120, style="pieslice",
                                 fill=hsv_hex(hue, 0.85, 0.95), outline="")
            elif iid in GRADIENTS:
                g = GRADIENTS[iid]
                c.create_arc(x1, y1, x2, y2, start=0, extent=180,
                             style="pieslice", fill=g[0], outline="")
                c.create_arc(x1, y1, x2, y2, start=180,
                             extent=180, style="pieslice", fill=g[1],
                             outline="")
            else:
                c.create_oval(x1, y1, x2, y2, fill=iid,
                              outline=blend(iid, "#000000", 0.35))
        elif self.kind == "theme":
            t = THEME_BY_ID[iid]
            if t.get("grad"):
                c.create_arc(x1, y1, x2, y2, start=0, extent=180,
                             style="pieslice", fill=t["grad"][0], outline="")
                c.create_arc(x1, y1, x2, y2, start=180, extent=180,
                             style="pieslice", fill=t["grad"][1], outline="")
            else:
                c.create_arc(x1, y1, x2, y2, start=0, extent=180,
                             style="pieslice", fill=t["grid_a"], outline="")
                c.create_arc(x1, y1, x2, y2, start=180, extent=180,
                             style="pieslice", fill=t["grid_b"], outline="")
            c.create_oval(x1, y1, x2, y2, outline=t["border"])
        elif self.kind == "acc":
            if iid == "none":
                c.create_oval(x1, y1, x2, y2, outline=DIM)
                c.create_line(x1 + 3, y1 + 3, x2 - 3, y2 - 3, fill=DIM)
                c.create_line(x1 + 3, y2 - 3, x2 - 3, y1 + 3, fill=DIM)
            else:
                draw_acc(c, (x1 + x2) // 2, (y1 + y2) // 2, iid)
        else:
            draw_food(c, (x1 + x2) // 2, (y1 + y2) // 2, iid,
                      scale=1.7 if not self.mini else 1.0)

    def _paint(self):
        c = self
        c.delete("all")
        level = level_from_exp(self.app.save.get("exp", 0))
        owned, selected = self._state()
        locked = not owned and self.item.get("level", 1) > level
        iid = self.item["id"]
        if self.mini:
            w, h = 118, 96
            round_rect(c, 1, 1, w - 1, h - 1, 12,
                       fill=blend(PANEL, "#000000", 0.12),
                       outline=ACCENT if selected else BORDER)
            self._swatch(c, (44, 10, 74, 40), iid)
            self._btn(c, 10, 62, 108, 88, owned, selected, locked, level,
                      small=True)
            self.clickable = self._clickable(owned, selected, locked)
            self.config(cursor="hand2" if self.clickable else "arrow")
            return
        # --- большая карточка 210x196 ---
        # скруглённый градиентный квадратик
        gradient_round_btn(c, 2, 2, 207, 186, 16, PANEL,
                           blend(PANEL, "#000000", 0.28), steps=10)
        if selected:
            round_rect(c, 2, 2, 207, 186, 16, fill="",
                       outline=ACCENT_BRIGHT, width=2)
        # мягкая подсветка за товаром — товар выглядит крупнее
        c.create_oval(63, 22, 147, 106, fill=blend(PANEL, "#ffffff", 0.07),
                      outline=blend(PANEL, "#ffffff", 0.14))
        self._swatch(c, (75, 34, 135, 94), iid)
        name = self.item["name"]
        if self.kind == "food":
            name = f"{name} +{self.item['value']}"
        c.create_text(105, 116, text=name,
                      font=(self.app.font_ui, 10, "bold"),
                      fill=DIM if locked else TEXT)
        # кнопка (i) справа сверху
        c.create_oval(186, 8, 202, 24, fill=blend(PANEL, "#ffffff", 0.12),
                      outline=BORDER)
        c.create_text(194, 16, text="i",
                      font=(self.app.font_ui, 8, "bold"), fill=GOLD)
        self._btn(c, 28, 134, 182, 172, owned, selected, locked, level)
        self.clickable = self._clickable(owned, selected, locked)
        self.config(cursor="hand2" if self.clickable else "arrow")

    def _clickable(self, owned, selected, locked):
        if locked:
            return False
        if owned:
            if self.kind == "food":
                return False
            return not selected
        return True

    def _btn(self, c, x1, y1, x2, y2, owned, selected, locked, level,
             small=False):
        """Овальная кнопка снизу карточки."""
        r = (y2 - y1) // 2
        fnt = (self.app.font_ui, 8 if small else 10, "bold")
        cy = (y1 + y2) // 2
        cx = (x1 + x2) // 2
        if locked:
            round_rect(c, x1, y1, x2, y2, r, fill=LOCKED_BG, outline="")
            c.create_text(cx, cy, text=f"\U0001f512 ур. {self.item['level']}",
                          font=fnt, fill=DIM)
            return
        if owned:
            if self.kind == "food":
                round_rect(c, x1, y1, x2, y2, r, fill=BORDER, outline="")
                c.create_text(cx, cy, text="Куплено", font=fnt, fill=TEXT)
            elif selected:
                gradient_round_btn(c, x1, y1, x2, y2, r, ACCENT_DARK,
                                   blend(ACCENT_DARK, "#000000", 0.3),
                                   steps=8)
                c.create_text(cx, cy, text="Выбрано", font=fnt,
                              fill="#c9ffd4")
            else:
                round_rect(c, x1, y1, x2, y2, r, fill=BORDER, outline="")
                c.create_text(cx, cy, text="Выбрать", font=fnt, fill=TEXT)
            return
        # покупка: овальная зелёная кнопка с ценой
        gradient_round_btn(c, x1, y1, x2, y2, r, *_BTN_GREEN, steps=8)
        round_rect(c, x1 + 4, y1 + 2, x2 - 4,
                   y1 + (y2 - y1) * 0.42, max(4, r - 6), fill="#ffffff",
                   stipple="gray25", outline="")
        price = f"{chr(0x25c9)} {self.item['price']} монет"
        c.create_text(cx, cy, text=price, font=fnt, fill=_BTN_GREEN_FG)

    def _motion(self, event):
        if 180 <= event.x <= 210 and event.y <= 26:
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
            # клик по тултипу закрывает его — окно никогда не «съедает» клики
            win.bind("<Button-1>", lambda e: self._hide_tip())
            try:
                win.wm_attributes("-topmost", True)
            except tk.TclError:
                pass
            self.tip = win
            _OPEN_TIPS.add(win)
            win.bind("<Destroy>", lambda e: _OPEN_TIPS.discard(win))
        except tk.TclError:
            self.tip = None

    def _hide_tip(self, *_args):
        tip = self.tip
        self.tip = None
        if tip is not None:
            _OPEN_TIPS.discard(tip)
            try:
                tip.destroy()
            except tk.TclError:
                pass
            # уничтоженный тултип не должен уносить фокус клавиатуры
            refocus_app(self.app)

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
            self.refresh("Выбрано!")
            return
        if s["coins"] < self.item["price"]:
            self.refresh("Не хватает монет!")
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
        self.refresh(f"Куплено: {self.item['name']}!")


class ShopScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.mid = "#173725"
        self.bot = "#122a1c"
        # 1.1: ярче градиентный фон магазина
        self.bg = GradientBG(self, "#1e4a2e", "#15382b", accent=ACCENT_BRIGHT)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=24, pady=(12, 0))
        tk.Label(head, text="МАГАЗИН", bg=BG, fg=ACCENT_BRIGHT,
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

        self.holder = tk.Frame(self.scroller, bg=self.mid)
        self._win = self.scroller.create_window((0, 0), window=self.holder,
                                                anchor="nw", width=770)
        self.holder.bind("<Configure>",
                         lambda e: self.scroller.configure(
                             scrollregion=self.scroller.bbox("all")))
        self.scroller.bind("<Configure>", self._on_resize)
        # основной вид (секции со страницами) и вкладка «Показать все»
        self.inner = tk.Frame(self.holder, bg=self.mid)
        self.all_inner = tk.Frame(self.holder, bg=self.mid)
        self.inner.pack(fill="both", expand=True)
        self._all_kind = None

        self._cards = []          # большие карточки (по одной на товар)
        self._mini_cards = []     # мини-карточки вкладки «Показать все»
        self._kind_cards = {}     # kind -> [карточки по порядку]
        self._page = {}           # kind -> текущая страница
        self._page_lbl = {}       # kind -> (canvas, iid) индикатора
        self._arrows = {}         # kind -> (btn_left, btn_right)
        self._grids = {}          # kind -> frame с карточками
        self._kind_expected = {}
        self._built_cols = None
        self._shop_queue = None
        self._shop_total = 0
        self._pages_done = set()

        self.back_btn = GradientButton(
            self, "←  Назад", lambda: app.show("MenuScreen"),
            width=190, height=44, radius=18, c1=_BTN_GREEN[0], c2=_BTN_GREEN[1],
            fg=_BTN_GREEN_FG, app_bg=self.bot,
            font=(app.font_ui, 12, "bold"), hover_scale=0.04)
        self.back_btn.pack(pady=(6, 10))

    def _on_resize(self, event):
        self.scroller.itemconfig(self._win,
                                 width=max(400, event.width - 22))

    def on_show(self):
        close_all_tips()
        self._rebuild()
        self.scroller.yview_moveto(0)
        self.bg.set_animated(not self.app.save.get("low_spec"))

    def on_hide(self):
        close_all_tips()
        self.bg.set_animated(False)

    # ---------- страницы секций ----------

    def _flip(self, kind, step):
        cards = self._kind_cards.get(kind, [])
        pages = max(1, (len(cards) + _COLS - 1) // _COLS)
        p = self._page.get(kind, 0) + step
        if p < 0 or p >= pages:
            return
        self._page[kind] = p
        sfx("click")
        self._apply_page(kind)

    def _apply_page(self, kind):
        cards = self._kind_cards.get(kind, [])
        n = len(cards)
        if not n:
            return
        pages = max(1, (n + _COLS - 1) // _COLS)
        p = max(0, min(self._page.get(kind, 0), pages - 1))
        self._page[kind] = p
        for i, card in enumerate(cards):
            if i // _COLS == p:
                card.grid()
                card.gridded = True
            else:
                card.gridded = False
                try:
                    card.grid_remove()
                except Exception:
                    pass
        lbl = self._page_lbl.get(kind)
        if lbl is not None:
            cv, iid = lbl
            try:
                cv.itemconfig(iid, text=f"{p + 1} / {pages}")
            except Exception:
                pass
        arrows = self._arrows.get(kind)
        if arrows is not None:
            for btn, on in ((arrows[0], p > 0), (arrows[1], p < pages - 1)):
                col = TEXT if on else DIM
                if btn.base_fg != col:
                    btn.base_fg = col
                    btn.repaint()

    # ---------- вкладка «Показать все …» ----------

    def _show_all(self, kind):
        self._all_kind = kind
        close_all_tips()
        self.inner.pack_forget()
        for w in self.all_inner.winfo_children():
            w.destroy()
        self._mini_cards = []
        titles = {"color": "Все цвета", "theme": "Все фоны",
                  "food": "Вся еда", "acc": "Все аксессуары"}
        head = tk.Canvas(self.all_inner, width=770, height=32, bg=self.mid,
                         highlightthickness=0)
        head.pack(pady=(10, 4))
        gradient_round_btn(head, 2, 2, 767, 29, 15, PANEL,
                           blend(PANEL, ACCENT_DARK, 0.5))
        head.create_text(20, 16, text=titles.get(kind, ""), anchor="w",
                         font=(self.app.font_ui, 11, "bold"),
                         fill=ACCENT_BRIGHT)
        grid = tk.Frame(self.all_inner, bg=self.mid)
        grid.pack(padx=8)
        items = self._items_for(kind)
        refresh = self._refresh_card_factory(kind)
        for i, item in enumerate(items):
            card = ShopCard(grid, self.app, kind, item, refresh,
                            card_bg=self.mid, mini=True)
            card.grid(row=i // _MINI_COLS, column=i % _MINI_COLS,
                      padx=3, pady=3)
            self._mini_cards.append(card)
        GradientButton(self.all_inner, "←  В магазин", self._show_main,
                       width=190, height=42, radius=16,
                       c1=_BTN_GREEN[0], c2=_BTN_GREEN[1], fg=_BTN_GREEN_FG,
                       app_bg=self.mid, font=(self.app.font_ui, 11, "bold"),
                       hover_scale=0.035).pack(pady=(10, 8))

    def _show_main(self):
        self._all_kind = None
        close_all_tips()
        for w in self.all_inner.winfo_children():
            w.destroy()
        self._mini_cards = []
        self.all_inner.pack_forget()
        self.inner.pack(fill="both", expand=True)

    def _items_for(self, kind):
        return {"color": COLORS, "theme": THEMES, "food": FOOD_ITEMS,
                "acc": ACCESSORIES}[kind]

    # ---------- построение ----------

    def _rebuild(self, status=""):
        self.coins_var.set(f"{chr(0x25c9)}  {self.app.save['coins']}")
        self.status_var.set(status)
        if (self._built_cols == _COLS and self._cards
                and len(self._cards) == self._shop_total):
            # карточки уже созданы — только перерисовать состояние
            ok = True
            for card in self._cards:
                try:
                    card._paint()
                except tk.TclError:
                    ok = False
                    break
            for card in self._mini_cards:
                try:
                    card._paint()
                except tk.TclError:
                    pass
            if ok:
                return
        self._built_cols = _COLS
        close_all_tips()
        for w in self.inner.winfo_children():
            w.destroy()
        self._cards = []
        self._kind_cards = {}
        self._page = {}
        self._page_lbl = {}
        self._arrows = {}
        self._grids = {}
        self._pages_done = set()
        self._all_kind = None
        self.all_inner.pack_forget()
        self.inner.pack(fill="both", expand=True)
        sections = [
            ("Цвета змейки", "color", COLORS, "все цвета"),
            ("Фоны  (дороже фон — выше множитель монет)", "theme", THEMES,
             "все фоны"),
            ("Еда  (дороже еда — больше очков)", "food", FOOD_ITEMS,
             "всю еду"),
            ("Аксессуары для головы", "acc", ACCESSORIES,
             "все аксессуары"),
        ]
        # ~110 карточек строим порциями в фоне: вкладка открывается мгновенно
        self._shop_queue = []
        self._cards = []
        all_btn_texts = {
            "color": "Показать все цвета", "theme": "Показать все фоны",
            "food": "Показать всю еду", "acc": "Показать все аксессуары",
        }
        for title, kind, items, _all in sections:
            head = tk.Canvas(self.inner, width=770, height=32, bg=self.mid,
                             highlightthickness=0)
            head.pack(pady=(10, 2))
            gradient_round_btn(head, 2, 2, 767, 29, 15, PANEL,
                               blend(PANEL, ACCENT_DARK, 0.5))
            head.create_text(20, 16, text=title, anchor="w",
                             font=(self.app.font_ui, 11, "bold"),
                             fill=ACCENT_BRIGHT)
            pages = max(1, (len(items) + _COLS - 1) // _COLS)
            lbl = head.create_text(748, 16, text=f"1 / {pages}", anchor="e",
                                   font=(self.app.font_ui, 9, "bold"),
                                   fill=DIM)
            self._page_lbl[kind] = (head, lbl)
            rowf = tk.Frame(self.inner, bg=self.mid)
            rowf.pack()
            left = GradientButton(
                rowf, "◀", (lambda k=kind: self._flip(k, -1)),
                width=46, height=64, radius=14, c1=_BTN_GREEN[0],
                c2=_BTN_GREEN[1], fg=TEXT, app_bg=self.mid,
                font=(self.app.font_ui, 14, "bold"), hover_scale=0.06)
            left.pack(side="left", padx=(0, 4))
            grid = tk.Frame(rowf, bg=self.mid)
            grid.pack(side="left")
            right = GradientButton(
                rowf, "▶", (lambda k=kind: self._flip(k, 1)),
                width=46, height=64, radius=14, c1=_BTN_GREEN[0],
                c2=_BTN_GREEN[1], fg=TEXT, app_bg=self.mid,
                font=(self.app.font_ui, 14, "bold"), hover_scale=0.06)
            right.pack(side="left", padx=(4, 0))
            self._arrows[kind] = (left, right)
            self._grids[kind] = grid
            self._kind_cards[kind] = []
            self._kind_expected[kind] = len(items)
            self._page[kind] = 0
            for i, item in enumerate(items):
                self._shop_queue.append((kind, item, grid, i))
            if len(items) > _COLS:
                GradientButton(self.inner, all_btn_texts[kind],
                               (lambda k=kind: self._show_all(k)),
                               width=240, height=36, radius=14,
                               c1=blend(PANEL, ACCENT_DARK, 0.45),
                               c2=blend(PANEL, ACCENT_DARK, 0.75),
                               fg=ACCENT_BRIGHT, app_bg=self.mid,
                               font=(self.app.font_ui, 10, "bold"),
                               hover_scale=0.035).pack(pady=(4, 0))
        self._shop_total = len(self._shop_queue)
        self._shop_build_batch()

    def _shop_build_batch(self, batch=12):
        queue = self._shop_queue
        if not queue:
            self._shop_queue = None
            return
        for kind, item, grid, i in queue[:batch]:
            card = ShopCard(grid, self.app, kind, item,
                            self._refresh_card_factory(kind),
                            card_bg=self.mid)
            card.grid(row=i // _COLS, column=i % _COLS, padx=3, pady=3,
                      sticky="nsew")
            self._cards.append(card)
            self._kind_cards[kind].append(card)
        del queue[:batch]
        # секции, собранные полностью, сразу показываем нужную страницу
        for kind, cards in self._kind_cards.items():
            if (len(cards) == self._kind_expected.get(kind)
                    and kind not in self._pages_done):
                self._pages_done.add(kind)
                self._apply_page(kind)
        try:
            self.after(1, self._shop_build_batch)
        except Exception:
            self._shop_queue = None

    def _refresh_card_factory(self, kind):
        return lambda status="": self._refresh_card(status, kind)

    def _refresh_card(self, status="", kind=None):
        """Точечное обновление: монеты/статус + перерисовка карточек
        одного раздела без пересоздания виджетов."""
        self.coins_var.set(f"{chr(0x25c9)}  {self.app.save['coins']}")
        self.status_var.set(status)
        for card in self._cards:
            if kind is None or card.kind == kind:
                try:
                    card._paint()
                except tk.TclError:
                    pass
        for card in self._mini_cards:
            if kind is None or card.kind == kind:
                try:
                    card._paint()
                except tk.TclError:
                    pass
