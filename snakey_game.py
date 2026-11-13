import math
import random
import tkinter as tk


from snakey_assets import sfx
from snakey_content import (


    ACCENT,
    ACCENT_DARK,
    BG,
    BLUE,
    BORDER,
    CELL,
    COLS,
    DIFFICULTIES,
    DIM,
    FOOD_BY_ID,
    FOOD_ITEMS,
    GOLD,
    GRADIENTS,
    KEY_ALIASES,
    LOCKED_BG,
    MG2_SPOTS,
    MG3_ZONE_R,
    MINIGAMES,
    PANEL,
    RED,
    ROWS,
    TEXT,
    THEMES,
    THEME_BY_ID,
    WARN,
)
from snakey_drawing import draw_acc, draw_food
from snakey_save import check_achievements, level_from_exp
from snakey_utils import (
    blend,
    gradient_bands,
    hsv_hex,
    round_pts,
    round_rect,
    seg_color,
)
from snakey_widgets import Screen

class GameScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=14, pady=(10, 4))
        self.score_var = tk.StringVar(value="Счёт: 0")
        self.diff_var = tk.StringVar()
        self.coins_var = tk.StringVar()
        tk.Label(head, textvariable=self.score_var, bg=BG, fg=TEXT,
                 font=(app.font_ui, 13, "bold")).pack(side="left")
        tk.Label(head, textvariable=self.diff_var, bg=BG, fg=DIM,
                 font=(app.font_ui, 11, "bold")).pack(side="left", expand=True)
        tk.Label(head, textvariable=self.coins_var, bg=BG, fg=GOLD,
                 font=(app.font_ui, 12, "bold")).pack(side="right")

        self.canvas = tk.Canvas(self, width=COLS * CELL, height=ROWS * CELL,
                                bg="#0f1418", highlightthickness=1,
                                highlightbackground=BORDER)
        self.canvas.pack(padx=12, pady=4)

        tk.Label(self, text="Стрелки / WASD — движение    P — пауза    R — заново"
                 "    C — воскреситься    Esc — меню",
                 bg=BG, fg=DIM, font=(app.font_ui, 9)).pack(pady=(2, 10))

        self.job = None
        self.game_over = True
        self.mode = "classic"
        self.low = False
        self._foods_dirty = True
        self._seg_active = 0
        self._fx_active = 0
        self.mg = None
        self.mg_diff = "normal"
        self.cfg = DIFFICULTIES["normal"]
        self.theme = THEMES[0]
        self.revive_used = False
        self.eaten_count = 0
        self.delivered = 0
        self.carrying = False
        self.mg_phase = None
        self.target_color = None
        self.base_hue = 0.0
        self.fruit_colors = {}
        self.time_left = 0.0
        self._time_shown = -1
        self.snake = []
        self.direction = (0, 1)
        self.next_direction = (0, 1)
        self.score = 0
        self.tick_count = 0
        self.speed = 150
        self.obstacles = set()
        self.particles = []
        self.popups = []
        self.foods = []
        self._seg_items = []
        self._shadow_items = []
        self._fx_items = []
        self.paused = False

    def on_show(self):
        self._cancel()
        self.new_game()

    def on_hide(self):
        self._cancel()

    def _cancel(self):
        if self.job is not None:
            self.after_cancel(self.job)
            self.job = None

    def new_game(self, mode=None):
        if mode is None:
            mode = getattr(self.app, "next_mode", None) or getattr(self, "mode", "classic")
        if mode != "classic" and mode not in MINIGAMES:
            mode = "classic"
        self.mode = mode
        self.app.next_mode = None
        level = level_from_exp(self.app.save.get("exp", 0))
        self.mg = None
        if mode == "classic":
            cfg = DIFFICULTIES.get(self.app.save.get("speed"), DIFFICULTIES["normal"])
            if cfg["level"] > level:
                cfg = DIFFICULTIES["normal"]
            self.diff_var.set(f"Ур. {level} · {cfg['label']}"
                              + (f" · {cfg['note']}" if cfg["note"] else ""))
        else:
            mg = MINIGAMES[mode]
            self.mg = mode
            diff_key = (getattr(self.app, "next_diff", None)
                        or getattr(self, "mg_diff", "normal"))
            if diff_key not in mg["diffs"]:
                diff_key = "normal"
            dcfg = mg["diffs"][diff_key]
            if dcfg["level"] > level:
                diff_key = "normal"
                dcfg = mg["diffs"]["normal"]
            self.mg_diff = diff_key
            cfg = dict(dcfg)
            cfg["label"] = mg["label"]
            self.diff_var.set(f"{mg['icon']} {mg['label']} · "
                              f"{DIFFICULTIES[diff_key]['label']}"
                              + (f" · {cfg['time']} сек" if cfg["time"] else ""))
        self.app.next_diff = None
        self.cfg = cfg
        self.theme = self._theme()
        self.canvas.config(bg=self.theme["grad"][0] if self.theme.get("grad")
                           else self.theme["grid_a"],
                           highlightbackground="#ff5c5c" if not cfg["wrap"]
                           and self.mg != "mg3" else self.theme["border"])
        self.revive_used = False
        self.eaten_count = 0
        self.delivered = 0
        self.carrying = False
        self.mg_phase = None
        self.target_color = None
        self.base_hue = 0.0
        self.fruit_colors = {}
        t = cfg.get("time", 0)
        self.time_left = float(t) if isinstance(t, (int, float)) else 0.0
        self._time_shown = -1

        mid_y = ROWS // 2
        self.snake = [(mid_y, COLS // 2), (mid_y, COLS // 2 - 1), (mid_y, COLS // 2 - 2)]
        self.direction = (0, 1)
        self.next_direction = self.direction
        self.score = 0
        self.tick_count = 0
        self.speed = cfg["speed"]
        self.score_var.set("Счёт: 0")
        self.coins_var.set(f"◎  {self.app.save['coins']}")
        self.obstacles = set()
        if cfg["obstacles"]:
            self._spawn_obstacles(cfg["obstacles"])
        self.particles = []
        self.popups = []
        self.foods = []
        self._seg_items = []
        self._shadow_items = []
        self._fx_items = []
        self._seg_active = 0
        self._fx_active = 0
        if self.mg == "mg1":
            self._spawn_food("apple")
            self._spawn_food("apple")
            self._spawn_food("apple")
        elif self.mg == "mg2":
            self._mg2_spawn_base()
        elif self.mg == "mg3":
            self._spawn_mg3_apple()
            self._spawn_mg3_apple()
            self._spawn_mg3_apple()
        else:
            self._spawn_food("apple")
            if random.random() < 0.8:
                self._spawn_extra_food()
            if cfg.get("poison") and random.random() < 0.6:
                self._spawn_food("poison")
        self.paused = False
        self.game_over = False
        self.low = bool(self.app.save.get("low_spec", False))
        self._foods_dirty = True
        self._redraw_static()
        self._draw()
        self._schedule()

    def _schedule(self):
        self._cancel()
        # noinspection PyArgumentList
        self.job = self.after(self.speed, self._tick)

    def _theme(self):
        return THEME_BY_ID.get(self.app.save.get("theme"), THEMES[0])

    def _spawn_obstacles(self, count):
        mid_y, mid_c = ROWS // 2, COLS // 2
        tries = 0
        while len(self.obstacles) < count and tries < 800:
            tries += 1
            roll = random.random()
            if roll < 0.5:
                length = random.randint(2, 4)
                if random.random() < 0.5:
                    r = random.randint(2, ROWS - 3)
                    c0 = random.randint(2, COLS - 2 - length)
                    cells = [(r, c0 + i) for i in range(length)]
                else:
                    r0 = random.randint(2, ROWS - 2 - length)
                    c = random.randint(2, COLS - 3)
                    cells = [(r0 + i, c) for i in range(length)]
            elif roll < 0.85:
                arm = random.randint(1, 2)
                r0 = random.randint(2, ROWS - 3 - arm)
                c0 = random.randint(2, COLS - 3 - arm)
                cells = [(r0, c0 + i) for i in range(arm + 1)]
                cells += [(r0 + i, c0) for i in range(1, arm + 1)]
            else:
                cells = [(random.randint(2, ROWS - 3),
                          random.randint(2, COLS - 3))]
            if any(abs(r - mid_y) <= 1 and mid_c - 6 <= c <= mid_c + 7
                   for r, c in cells):
                continue
            if any(cell in self.obstacles for cell in cells):
                continue
            if len(self.obstacles) + len(cells) > count:
                continue
            too_close = False
            for r, c in cells:
                for orow, ocol in self.obstacles:
                    if max(abs(r - orow), abs(c - ocol)) <= 2:
                        too_close = True
                        break
                if too_close:
                    break
            if too_close:
                continue
            self.obstacles.update(cells)

    def _spawn_food(self, kind):
        occupied = set(self.snake) | self.obstacles | {pos for f in self.foods for pos in (f[1],)}
        free = [(r, c) for r in range(ROWS) for c in range(COLS)
                if (r, c) not in occupied]
        if not free:
            return None
        pos = random.choice(free)
        base = FOOD_BY_ID[kind]["size"] if kind in FOOD_BY_ID else 0.9
        self.foods.append((kind, pos, base + random.uniform(-0.12, 0.12)))
        self._foods_dirty = True
        return pos

    def _spawn_extra_food(self):
        owned = [f for f in FOOD_ITEMS[1:]
                 if f["id"] in self.app.save["owned_foods"]
                 and not any(k == f["id"] for k, *_ in self.foods)]
        if not owned:
            return
        pick = random.choices(owned, weights=[f["chance"] for f in owned])[0]
        self._spawn_food(pick["id"])

    def _spawn_mg3_apple(self):
        occupied = set(self.snake) | {pos for f in self.foods for pos in (f[1],)}
        free = [(r, c) for r in range(ROWS // 2) for c in range(COLS)
                if (r, c) not in occupied]
        if free:
            self.foods.append(("apple", random.choice(free), 1.0))
            self._foods_dirty = True

    def _mg2_spawn_base(self):
        self.base_hue = random.random()
        self.target_color = hsv_hex(self.base_hue, 0.8, 0.95)
        self.mg_phase = "base"
        occupied = set(self.snake) | set(MG2_SPOTS)
        free = [(r, c) for r in range(2, ROWS - 2) for c in range(2, COLS - 2)
                if (r, c) not in occupied]
        if free:
            pos = random.choice(free)
            self.foods.append(("mgfruit", pos, 1.0))
            self.fruit_colors[pos] = self.target_color
            self._foods_dirty = True

    def _mg2_spawn_shades(self):
        step = self.cfg.get("shade_step", 0.05)
        spots = [s for s in MG2_SPOTS if s not in self.snake]
        random.shuffle(spots)
        for k, spot in enumerate(spots[:8]):
            color = (self.target_color if k == 0
                     else hsv_hex(self.base_hue + k * step, 0.8, 0.95))
            self.foods.append(("mgfruit", spot, 1.0))
            self.fruit_colors[spot] = color
            self._foods_dirty = True

    def _mg2_pick(self, eaten):
        color = self.fruit_colors.pop(eaten[1], None)
        if self.mg_phase == "base":
            self.mg_phase = "pick"
            self.eaten_count += 1
            self._mg2_spawn_shades()
            px = eaten[1][1] * CELL + CELL / 2
            py = eaten[1][0] * CELL + CELL / 2
            self.popups.append([px, py - 12, "Ищи цвет!", 10, BLUE])
            self._draw()
            self._schedule()
            return
        self.fruit_colors.clear()
        if color == self.target_color:
            self._end_game("ПОБЕДА!", ok=True)
        else:
            self._end_game("НЕВЕРНЫЙ ЦВЕТ!")

    def _mg3_reset(self):
        hr, hc = self.snake[0]
        self.popups.append([hc * CELL + CELL / 2, hr * CELL + CELL / 2 - 12,
                            "В начало!", 10, WARN])
        mid_y = ROWS // 2
        self.snake = [(mid_y, COLS // 2), (mid_y, COLS // 2 - 1),
                      (mid_y, COLS // 2 - 2)]
        self.direction = (0, 1)
        self.next_direction = self.direction
        self.carrying = False
        self._draw()
        self._schedule()

    @staticmethod
    def _draw_shade_fruit(c, cx, cy, color, simple=False):
        if not simple:
            c.create_oval(cx - 14, cy - 14, cx + 14, cy + 14, fill=color,
                          stipple="gray25", outline="", tags="food")
        c.create_oval(cx - 9, cy - 9, cx + 9, cy + 9, fill=color,
                      outline=blend(color, "#000000", 0.35), tags="food")
        c.create_oval(cx - 5, cy - 6, cx - 1, cy - 2,
                      fill=blend(color, "#ffffff", 0.55), outline="", tags="food")
        c.create_oval(cx - 1, cy - 13, cx + 4, cy - 8, fill=ACCENT,
                      outline="", tags="food")

    def on_key(self, event):
        key = event.keysym.lower()
        key = KEY_ALIASES.get(key, KEY_ALIASES.get(event.char.lower(), key))
        if key == "escape":
            self.app.show("MenuScreen")
            return
        if key == "r":
            self.new_game()
            return
        if self.game_over:
            if key in ("c", "v") and self.mode == "classic":
                self._try_revive()
            elif key == "return":
                self.new_game()
            return
        moves = {
            "up": (-1, 0), "w": (-1, 0),
            "down": (1, 0), "s": (1, 0),
            "left": (0, -1), "a": (0, -1),
            "right": (0, 1), "d": (0, 1),
        }
        if key in moves:
            dr, dc = moves[key]
            cur_dr, cur_dc = self.direction
            if (dr, dc) != (-cur_dr, -cur_dc):
                self.next_direction = (dr, dc)
        elif key == "p":
            self.paused = not self.paused
            if self.paused:
                self._cancel()
            else:
                self._schedule()
            self._draw()

    def _tick(self):
        if self.paused or self.game_over:
            return
        self.tick_count += 1
        if self.cfg.get("time"):
            self.time_left -= self.speed / 1000
            shown = max(0, int(math.ceil(self.time_left)))
            if shown != self._time_shown:
                self._time_shown = shown
                self.diff_var.set(f"⏱ {shown} сек")
            if self.time_left <= 0:
                self._end_game("ВРЕМЯ ВЫШЛО!")
                return

        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[2] *= 0.92
            p[3] *= 0.92
            p[4] -= 1
        self.particles = [p for p in self.particles if p[4] > 0]
        for p in self.popups:
            p[1] -= 2.5
            p[3] -= 1
        self.popups = [p for p in self.popups if p[3] > 0]

        self.direction = self.next_direction
        dr, dc = self.direction
        head_r, head_c = self.snake[0]
        new_r, new_c = head_r + dr, head_c + dc

        if self.cfg["wrap"]:
            new_r %= ROWS
            new_c %= COLS
        elif not (0 <= new_r < ROWS and 0 <= new_c < COLS):
            if self.mg == "mg3":
                self._mg3_reset()
                return
            self._end_game("ВЗРЫВ О СТЕНУ!")
            return
        new_head = (new_r, new_c)

        if new_head in self.snake or new_head in self.obstacles:
            self._end_game()
            return

        self.snake.insert(0, new_head)

        eaten = next((f for f in self.foods if f[1] == new_head), None)
        if eaten is not None:
            self.foods.remove(eaten)
            self._foods_dirty = True
            if eaten[0] == "poison":
                px = eaten[1][1] * CELL + CELL / 2
                py = eaten[1][0] * CELL + CELL / 2
                if not self.low:
                    for _ in range(10):
                        ang = random.uniform(0, 2 * math.pi)
                        spd = random.uniform(1.5, 3.5)
                        self.particles.append([px, py, math.cos(ang) * spd,
                                               math.sin(ang) * spd,
                                               random.randint(6, 10), "#7cb342"])
                self._end_game("ОТРАВЛЕНА!")
                return
            if self.mg == "mg2":
                self._mg2_pick(eaten)
                return
            if self.mg == "mg3":
                self.carrying = True
                sfx("eat")
                self._spawn_mg3_apple()
            else:
                info = FOOD_BY_ID[eaten[0]]
                self.eaten_count += 1
                self.score += info["value"]
                sfx("eat")
                self.score_var.set(f"Счёт: {self.score}")
                self.speed = max(self.cfg["min"], self.speed - self.cfg["step"])
                px = eaten[1][1] * CELL + CELL / 2
                py = eaten[1][0] * CELL + CELL / 2
                self.popups.append([px, py - 10, f"+{info['value']}", 9, info["color"]])
                if not self.low:
                    for _ in range(8):
                        ang = random.uniform(0, 2 * math.pi)
                        spd = random.uniform(1.2, 3.2)
                        self.particles.append([px, py, math.cos(ang) * spd,
                                               math.sin(ang) * spd,
                                               random.randint(5, 9), info["color"]])
                    round_rect(self.canvas, px - 16, py - 16, px + 16,
                               py + 16, 8, fill=info["color"],
                               stipple="gray25", outline="", tags="fx")
                if self.mg == "mg1":
                    self._spawn_food("apple")
                elif eaten[0] == "apple":
                    self._spawn_food("apple")
                    if (not any(k not in ("apple", "poison")
                                for k, *_ in self.foods)
                            and random.random() < 0.8):
                        self._spawn_extra_food()
                elif random.random() < info["chance"]:
                    self._spawn_extra_food()
                if (self.cfg.get("poison")
                        and sum(1 for k, *_ in self.foods if k == "poison") < 2
                        and random.random() < 0.3):
                    self._spawn_food("poison")
        if self.mg == "mg3" or eaten is None:
            self.snake.pop()

        if self.mg == "mg3" and self.carrying:
            hx = (new_c + 0.5) * CELL
            hy = (new_r + 0.5) * CELL
            zx = COLS * CELL / 2
            zy = ROWS * CELL
            if (hx - zx) ** 2 + (hy - zy) ** 2 <= MG3_ZONE_R ** 2:
                self.carrying = False
                self.delivered += 1
                sfx("coin")
                self.score = self.delivered
                self.score_var.set(f"Яблоки: {self.delivered}")
                self.popups.append([hx, hy - 14, "+12 ◎", 10, GOLD])
                if not self.low:
                    for _ in range(8):
                        ang = random.uniform(0, 2 * math.pi)
                        spd = random.uniform(1.2, 3.0)
                        self.particles.append([hx, hy, math.cos(ang) * spd,
                                               math.sin(ang) * spd,
                                               random.randint(5, 9), GOLD])

        self._draw()
        self._schedule()

    def _revive_cost(self):
        return min(500, 30 + self.score * 2)

    def _try_revive(self):
        if self.revive_used or not self.game_over or self.mode != "classic":
            return
        cost = self._revive_cost()
        if self.app.save.get("coins", 0) < cost:
            return
        self.app.save["coins"] -= cost
        self.app.commit()
        self.coins_var.set(f"◉  {self.app.save['coins']}")
        sfx("coin")
        self.revive_used = True
        mid_y = ROWS // 2
        self.snake = [(mid_y, COLS // 2), (mid_y, COLS // 2 - 1),
                      (mid_y, COLS // 2 - 2)]
        self.direction = (0, 1)
        self.next_direction = self.direction
        self.game_over = False
        self.paused = False
        self._draw()
        self._schedule()

    def _end_game(self, title="ИГРА ОКОНЧЕНА", ok=False):
        self.game_over = True
        mode = self.mode
        if ok:
            sfx("win")
        else:
            sfx("death" if mode == "classic" else "lose")
        reward = self.cfg["reward"] * self.theme.get("bonus", 1.0)
        exp_mult = self.cfg["exp_reward"] * self.theme.get("bonus", 1.0)
        if mode == "mg2":
            if ok:
                earned = round(10 * reward)
                exp_gain = round(18 * exp_mult)
            else:
                earned = 0
                exp_gain = round(3 * exp_mult)
        elif mode == "mg3":
            earned = round(self.delivered * 12 * reward)
            exp_gain = round(self.delivered * 6 * exp_mult)
        else:
            earned = round(self.score * 0.6 * reward)
            exp_gain = round(self.score * exp_mult)
        old_level = level_from_exp(self.app.save.get("exp", 0))
        self.app.save["exp"] = self.app.save.get("exp", 0) + exp_gain
        new_level = level_from_exp(self.app.save["exp"])
        if new_level > old_level:
            self.app.save["pending_level"] = new_level
        self.app.save["coins"] = self.app.save.get("coins", 0) + earned
        st = self.app.save.get("stats")
        if not isinstance(st, dict):
            st = {}
            self.app.save["stats"] = st
        for k in ("best_score", "coins_earned", "games", "apples",
                  "mg1_best", "mg2_wins", "mg3_best", "mg3_apples"):
            st.setdefault(k, 0)
        st["games"] += 1
        st["coins_earned"] += earned
        if mode == "mg1":
            st["apples"] += self.eaten_count
            st["mg1_best"] = max(st["mg1_best"], self.score)
        elif mode == "mg2":
            if ok:
                st["mg2_wins"] += 1
        elif mode == "mg3":
            st["apples"] += self.delivered
            st["mg3_apples"] += self.delivered
            st["mg3_best"] = max(st["mg3_best"], self.delivered)
        else:
            st["apples"] += self.eaten_count
            st["best_score"] = max(st["best_score"], self.score)
            if self.score > self.app.save["highscore"]:
                self.app.save["highscore"] = self.score
        check_achievements(self.app.save)
        self.app.commit()
        self.coins_var.set(f"◎  {self.app.save['coins']}")
        self._draw()
        c = self.canvas
        cxm = COLS * CELL / 2
        cy = ROWS * CELL / 2
        cost = self._revive_cost()
        is_mg = mode != "classic"
        can_revive = (not is_mg and not self.revive_used
                      and self.app.save.get("coins", 0) >= cost)
        if mode == "mg1":
            score_line = f"Яблоки: {self.score}      Рекорд: {st['mg1_best']}"
            coin_line = f"+{earned} монет"
            if reward != 1.0:
                coin_line += f"  (×{reward:g})"
        elif mode == "mg2":
            score_line = "Цвет найден!" if ok else "Это был другой оттенок…"
            if ok:
                coin_line = f"+{earned} монет"
                if reward != 1.0:
                    coin_line += f"  (×{reward:g})"
            else:
                coin_line = "Без награды"
        elif mode == "mg3":
            score_line = (f"Доставлено: {self.delivered}      "
                          f"Рекорд: {st['mg3_best']}")
            coin_line = f"+{earned} монет  ({self.delivered} × 12 × {reward:g})"
        else:
            score_line = (f"Счёт: {self.score}      "
                          f"Рекорд: {self.app.save['highscore']}")
            coin_line = f"+{earned} монет"
            if reward != 1.0:
                coin_line += f"  (×{reward:g})"
        title_col = ACCENT if ok else RED
        icon = ("🏆" if ok else (MINIGAMES[mode]["icon"] if mode in MINIGAMES
                                 else "💀"))
        big_title = f"{icon} {title}"
        round_rect(c, cxm - 194, cy - 78, cxm + 194, cy + 86, 18,
                   fill="#000000", stipple="gray25", outline="",
                   tags="overlay")
        round_rect(c, cxm - 190, cy - 82, cxm + 190, cy + 82, 18,
                   fill=PANEL, outline=blend(title_col, "#000000", 0.3),
                   tags="overlay")
        gradient_bands(c, cxm - 189, cy - 81, cxm + 189, cy - 76,
                       title_col, PANEL, 3, tags="overlay")
        round_rect(c, cxm - 70, cy - 82, cxm + 70, cy - 75, 4,
                   fill=title_col, outline="", tags="overlay")
        c.create_text(cxm + 2, cy - 50, text=big_title,
                      font=(self.app.font_title, 17, "bold"),
                      fill="#000000", tags="overlay")
        c.create_text(cxm, cy - 52, text=big_title,
                      font=(self.app.font_title, 17, "bold"),
                      fill=title_col, tags="overlay")
        c.create_text(cxm, cy - 22, text=score_line,
                      font=(self.app.font_ui, 12, "bold"), fill=TEXT,
                      tags="overlay")
        round_rect(c, cxm - 150, cy - 9, cxm + 150, cy + 15, 10,
                   fill=LOCKED_BG, outline="", tags="overlay")
        c.create_text(cxm, cy + 3, text=coin_line,
                      font=(self.app.font_ui, 12, "bold"), fill=GOLD,
                      tags="overlay")
        c.create_text(cxm, cy + 30, text=f"+{exp_gain} EXP · уровень {new_level}",
                      font=(self.app.font_ui, 11, "bold"), fill=BLUE,
                      tags="overlay")
        if can_revive:
            round_rect(c, cxm - 168, cy + 42, cxm + 168, cy + 64, 10,
                       fill=blend(ACCENT_DARK, "#000000", 0.2),
                       outline=ACCENT_DARK, tags="overlay")
            c.create_text(cxm, cy + 53,
                          text=f"C — воскреситься ({cost} монет)",
                          font=(self.app.font_ui, 11, "bold"), fill=ACCENT,
                          tags="overlay")
            c.create_text(cxm, cy + 74,
                          text="R — заново      Esc — в меню",
                          font=(self.app.font_ui, 10), fill=DIM, tags="overlay")
        else:
            c.create_text(cxm, cy + 56,
                          text="R — заново      Esc — в меню",
                          font=(self.app.font_ui, 10), fill=DIM, tags="overlay")

    def _draw_decor(self, c):
        style = self.theme.get("decor")
        if not style:
            return
        rng = random.Random(7)
        w, h = COLS * CELL, ROWS * CELL
        if style == "stars":
            for _ in range(18):
                x, y = rng.uniform(4, w - 4), rng.uniform(4, h - 4)
                s = rng.uniform(0.6, 1.6)
                c.create_oval(x - s, y - s, x + s, y + s, fill="#cdd9e5",
                              outline="", stipple="gray50")
        elif style == "snow":
            for _ in range(20):
                x, y = rng.uniform(4, w - 4), rng.uniform(4, h - 4)
                s = rng.uniform(1.2, 2.4)
                c.create_oval(x - s, y - s, x + s, y + s, fill="#ffffff",
                              outline="", stipple="gray50")
        elif style == "flowers":
            for _ in range(10):
                x, y = rng.uniform(6, w - 6), rng.uniform(6, h - 6)
                col = rng.choice(("#ffffff", "#ffe14d", "#ffb3d9"))
                for a in range(4):
                    px = x + math.cos(a * 1.571) * 2.6
                    py = y + math.sin(a * 1.571) * 2.6
                    c.create_oval(px - 1.8, py - 1.8, px + 1.8, py + 1.8,
                                  fill=col, outline="")
                c.create_oval(x - 1.3, y - 1.3, x + 1.3, y + 1.3,
                              fill="#ffe14d", outline="")
        elif style == "bushes":
            for _ in range(10):
                x, y = rng.uniform(6, w - 6), rng.uniform(6, h - 6)
                s = rng.uniform(3, 6)
                c.create_oval(x - s, y - s * 0.7, x + s, y + s * 0.7,
                              fill="#1a2a1e", outline="", stipple="gray50")
        elif style == "stones":
            for _ in range(10):
                x, y = rng.uniform(6, w - 6), rng.uniform(6, h - 6)
                s = rng.uniform(2, 4.5)
                c.create_oval(x - s, y - s * 0.7, x + s, y + s * 0.7,
                              fill="#b08d4a", outline="", stipple="gray25")
        elif style == "glow":
            for _ in range(8):
                x, y = rng.uniform(6, w - 6), rng.uniform(6, h - 6)
                s = rng.uniform(4, 9)
                c.create_oval(x - s, y - s, x + s, y + s,
                              fill=rng.choice(("#7c3aed", "#00e5ff", "#f778ba")),
                              outline="", stipple="gray25")
        elif style == "petals":
            for _ in range(14):
                x, y = rng.uniform(6, w - 6), rng.uniform(6, h - 6)
                s = rng.uniform(1.5, 3)
                c.create_oval(x - s, y - s * 0.55, x + s, y + s * 0.55,
                              fill=rng.choice(("#ffb3d9", "#ffc2e0")),
                              outline="", stipple="gray50")
        elif style == "bubbles":
            for _ in range(10):
                x, y = rng.uniform(6, w - 6), rng.uniform(6, h - 6)
                s = rng.uniform(2, 5)
                c.create_oval(x - s, y - s, x + s, y + s, outline="#8fd4ff",
                              stipple="gray25")
        elif style == "leaves":
            for _ in range(12):
                x, y = rng.uniform(6, w - 6), rng.uniform(6, h - 6)
                s = rng.uniform(2, 4)
                c.create_oval(x - s, y - s * 0.5, x + s, y + s * 0.5,
                              fill=rng.choice(("#d98f2b", "#c2542b", "#e0b23e")),
                              outline="", stipple="gray50")
        elif style == "embers":
            for _ in range(10):
                x, y = rng.uniform(6, w - 6), rng.uniform(6, h - 6)
                s = rng.uniform(1, 2.5)
                c.create_oval(x - s, y - s, x + s, y + s,
                              fill=rng.choice(("#ff6b35", "#ff9f1c", "#d93a2b")),
                              outline="", stipple="gray50")
        elif style == "aurora":
            for i in range(4):
                x = 60 + i * (w - 120) / 3
                c.create_polygon(x - 20, 0, x + 20, 0, x + 70, h, x - 70, h,
                                 fill=("#3fff9e", "#3fd0ff", "#b03fff", "#3fff9e")[i],
                                 stipple="gray12", outline="")

    def _redraw_static(self):
        c = self.canvas
        c.delete("all")
        w, h = COLS * CELL, ROWS * CELL
        if self.low:
            c.create_rectangle(0, 0, w, h, fill=self.theme["grid_a"],
                               outline="")
        elif self.theme.get("grad"):
            gradient_bands(c, 0, 0, w, h, self.theme["grad"][0],
                           self.theme["grad"][1], 16)
            self._draw_decor(c)
        else:
            for r in range(ROWS):
                for col in range(COLS):
                    if (r + col) % 2:
                        c.create_rectangle(col * CELL, r * CELL,
                                           (col + 1) * CELL, (r + 1) * CELL,
                                           fill=self.theme["grid_b"],
                                           outline="")
            self._draw_decor(c)
        for r, col in self.obstacles:
            x1, y1 = col * CELL + 1, r * CELL + 1
            x2, y2 = (col + 1) * CELL - 1, (r + 1) * CELL - 1
            c.create_rectangle(x1, y1, x2, y2, fill="#7a828c", outline="#4a5158")
            c.create_line(x1 + 2, (y1 + y2) / 2, x2 - 2, (y1 + y2) / 2,
                          fill="#5d646d")
        if not self.cfg["wrap"] and self.mg != "mg3":
            for rect in ((0, 0, w, 12), (0, h - 12, w, h),
                         (0, 0, 12, h), (w - 12, 0, w, h)):
                c.create_rectangle(*rect, fill="#000000", stipple="gray25",
                                   outline="")
        if self.mg == "mg3":
            zx = w / 2
            c.create_arc(zx - MG3_ZONE_R, h - MG3_ZONE_R,
                         zx + MG3_ZONE_R, h + MG3_ZONE_R, start=0, extent=180,
                         style="pieslice", fill=GOLD, outline="#b8860b", width=3)
            c.create_arc(zx - MG3_ZONE_R + 9, h - MG3_ZONE_R + 9,
                         zx + MG3_ZONE_R - 9, h + MG3_ZONE_R - 9,
                         start=0, extent=180, style="arc",
                         outline="#fff3c4", width=2)
        self._seg_items = []
        self._shadow_items = []
        self._fx_items = []
        self._seg_active = 0
        self._fx_active = 0

    def _draw_foods(self, phase, simple):
        c = self.canvas
        for fd in self.foods:
            kind, (r, col) = fd[0], fd[1]
            fx = col * CELL + CELL / 2
            fy = r * CELL + CELL / 2
            if kind == "mgfruit":
                self._draw_shade_fruit(c, fx, fy,
                                       self.fruit_colors.get((r, col), RED),
                                       simple)
            else:
                draw_food(c, fx, fy, kind, phase, simple=simple,
                          scale=fd[2] if len(fd) > 2 else 1.0, tags="food")

    def _draw(self):
        c = self.canvas
        c.delete("head", "fx", "overlay")
        phase = self.tick_count * 0.35
        if self.low:
            if self._foods_dirty:
                c.delete("food")
                self._draw_foods(0.0, True)
                self._foods_dirty = False
        else:
            c.delete("food")
            self._draw_foods(phase, False)

        sel = self.app.save.get("selected", ACCENT)
        need = len(self.snake)
        pool = self._seg_items
        shadows = self._shadow_items
        while len(pool) < need:
            sh = c.create_polygon(-60, -60, -48, -60, -48, -48, -60, -48,
                                  smooth=True, fill="#000000", stipple="gray50",
                                  outline="", tags="shadow", state="hidden")
            seg = c.create_polygon(-60, -60, -48, -60, -48, -48, -60, -48,
                                   smooth=True, outline="", tags="seg",
                                   state="hidden")
            shadows.append(sh)
            pool.append(seg)
        if self._seg_active > need:
            for i in range(need, self._seg_active):
                c.itemconfig(shadows[i], state="hidden")
                c.itemconfig(pool[i], state="hidden")
        for i in range(need):
            sh, seg = shadows[i], pool[i]
            r, col = self.snake[i]
            color = seg_color(sel, i, need, self.tick_count)
            pad = 2 if i == 0 else 3
            radius = 7 if i == 0 else 5
            x1, y1 = col * CELL + pad, r * CELL + pad
            x2, y2 = (col + 1) * CELL - pad, (r + 1) * CELL - pad
            if not self.low:
                c.coords(sh, *round_pts(x1 + 4, y1 + 4, x2 + 4, y2 + 4, radius))
                c.itemconfig(sh, state="normal")
            c.coords(seg, *round_pts(x1, y1, x2, y2, radius))
            c.itemconfig(seg, state="normal", fill=color)
        self._seg_active = need

        hr, hc = self.snake[0]
        cx, cy = hc * CELL + CELL / 2, hr * CELL + CELL / 2
        ring = (blend(GRADIENTS[sel][1], "#ffffff", 0.3) if sel in GRADIENTS
                else hsv_hex((self.tick_count * 8) / 360, 0.85, 0.95)
                if sel == "rainbow" else blend(sel, "#ffffff", 0.5))
        c.create_oval(hc * CELL, hr * CELL, (hc + 1) * CELL, (hr + 1) * CELL,
                      outline=ring, width=2, tags="head")
        dx, dy = self.direction[1], self.direction[0]
        if not self.game_over and self.tick_count % 9 < 3:
            c.create_line(cx + dx * 9, cy + dy * 9, cx + dx * 14, cy + dy * 14,
                          fill=RED, width=2, tags="head")
        px, py = -dy, dx
        for sign in (1, -1):
            ex = cx + dx * 5 + px * 5 * sign
            ey = cy + dy * 5 + py * 5 * sign
            c.create_oval(ex - 2.5, ey - 2.5, ex + 2.5, ey + 2.5,
                          fill="#06220c", outline="", tags="head")
        acc = self.app.save.get("accessory", "none")
        if acc != "none":
            draw_acc(c, cx, cy, acc, self.tick_count * 0.35, tags="head")
        if self.mg == "mg3" and self.carrying and not self.game_over:
            c.create_oval(cx - 6, cy - 22, cx + 6, cy - 10, fill=RED,
                          outline="#c93a3a", tags="head")

        fxp = self._fx_items
        nfx = len(self.particles)
        while len(fxp) < nfx:
            fxp.append(c.create_oval(-40, -40, -39, -39, fill="#ffffff",
                                     outline="", tags="particles",
                                     state="hidden"))
        if self._fx_active > nfx:
            for i in range(nfx, self._fx_active):
                c.itemconfig(fxp[i], state="hidden")
        for i, (x, y, vx, vy, life, color) in enumerate(self.particles):
            rad = max(1.0, life * 0.45)
            it = fxp[i]
            c.coords(it, int(x - rad), int(y - rad),
                     int(x + rad), int(y + rad))
            c.itemconfig(it, state="normal", fill=color)
        self._fx_active = nfx
        for x, y, text_, life, color in self.popups:
            c.create_text(x, y, text=text_, font=(self.app.font_ui, 11, "bold"),
                          fill=color, tags="fx")

        if self.paused:
            round_rect(c, COLS * CELL / 2 - 134, ROWS * CELL / 2 - 38,
                       COLS * CELL / 2 + 134, ROWS * CELL / 2 + 38, 12,
                       fill="#000000", stipple="gray25", outline="",
                       tags="overlay")
            round_rect(c, COLS * CELL / 2 - 130, ROWS * CELL / 2 - 34,
                       COLS * CELL / 2 + 130, ROWS * CELL / 2 + 34, 12,
                       fill=PANEL, outline=BORDER, tags="overlay")
            c.create_text(COLS * CELL / 2, ROWS * CELL / 2,
                          text="ПАУЗА  —  P чтобы продолжить",
                          font=(self.app.font_ui, 13, "bold"), fill=TEXT,
                          tags="overlay")