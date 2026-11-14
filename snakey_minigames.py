import random
import tkinter as tk

from snakey_assets import sfx
from snakey_content import (
    CELL,
    COLS,
    FOOD_BY_ID,
    GOLD,
    ROWS,
    WARN,
)
from snakey_utils import blend, round_pts, seg_color


class MinigameMixin:
    def _mg_setup(self):
        getattr(self, "_%s_setup" % self.mg, self._mg_default_setup)()

    def _mg_default_setup(self):
        self._spawn_food("apple")
        self._spawn_food("apple")

    def _mg_after_tick(self):
        return getattr(self, "_%s_after" % self.mg)()

    def _mg_eat_hook(self, eaten, info):
        if self.mg == "mg4" and self.eaten_count >= self.cfg["target"]:
            self._end_game("ЦЕЛЬ СОБРАНА!", ok=True)
            return
        if self.mg == "mg7" and self._mg7_blackout():
            self.score += 1
            self.score_var.set(f"Счёт: {self.score}")
            px = eaten[1][1] * CELL + CELL / 2
            py = eaten[1][0] * CELL + CELL / 2
            self.popups.append([px, py - 24, "В ТЕМНОТЕ ×2", 9, "#7fd4ff"])

    def _mg_draw_extras(self):
        if self.mg == "mg4":
            self._mg4_draw()
        elif self.mg == "mg5":
            self._mg5_draw()
        elif self.mg == "mg6":
            self._mg6_timer_draw()
        elif self.mg == "mg8":
            self._mg8_draw()
        elif self.mg == "mg9":
            # seg_color резолвит ЛЮБОЙ выбранный цвет (hex, rainbow, градиентные id
            # вроде "grad_sunset") в реальный hex — сырой id падал в canvas fill
            base = seg_color(self.app.save.get("selected", "#3fb950"),
                             0, 1, self.tick_count)
            self._draw_pool_snakes([(self.mg9_b,
                                      blend(base, "#00e5ff", 0.35), False)])
        elif self.mg == "mg10":
            self._mg10_draw()

    def _draw_pool_snakes(self, snakes):
        c = self.canvas
        pool = self._mgsnake_items
        need = sum(len(cells) for cells, _col, _hl in snakes)
        while len(pool) < need:
            pool.append(c.create_polygon(-60, -60, -48, -60, -48, -48,
                                         -60, -48, smooth=True, outline="",
                                         tags="mgsnake", state="hidden"))
        if self._mgsnake_active > need:
            for i in range(need, self._mgsnake_active):
                c.itemconfig(pool[i], state="hidden")
        idx = 0
        for cells, color, _hl in snakes:
            for j, (r, col) in enumerate(cells):
                it = pool[idx]
                idx += 1
                pad = 2 if j == 0 else 3
                x1, y1 = col * CELL + pad, r * CELL + pad
                x2, y2 = (col + 1) * CELL - pad, (r + 1) * CELL - pad
                c.coords(it, *round_pts(x1, y1, x2, y2,
                                        7 if j == 0 else 5))
                c.itemconfig(it, state="normal", fill=color)
        self._mgsnake_active = need

    def _mg_indicator(self, text, color, anchor_x):
        c = self.canvas
        x = 8 if anchor_x < 0 else COLS * CELL - 8
        c.create_text(x, 16, text=text, anchor="e" if anchor_x > 0 else "w",
                      font=(self.app.font_ui, 11, "bold"), fill="#000000",
                      tags="mgfx")
        c.create_text(x, 14, text=text, anchor="e" if anchor_x > 0 else "w",
                      font=(self.app.font_ui, 11, "bold"), fill=color,
                      tags="mgfx")

    def _mg4_setup(self):
        for _ in range(3):
            self._spawn_food("apple")
        pr, pc = ROWS // 2, 2
        self.predator = [(pr, pc), (pr, pc - 1), (pr, pc - 2)]
        self.pred_dir = (0, 1)
        self.pred_ms = float(self.cfg["pred_ms"])
        self.pred_t = 0.0

    def _mg4_after(self):
        self.pred_t += self.speed
        if self.pred_t < self.pred_ms:
            return True
        self.pred_t = 0.0
        self.pred_ms = max(110.0, self.pred_ms - 1.5)
        self._mg4_pred_step()
        if self.snake[0] in self.predator:
            self._end_game("ХИЩНИК ДОГНАЛ!")
            return False
        return True

    def _mg4_pred_step(self):
        hr, hc = self.snake[0]
        pr, pc = self.predator[0]
        dr = (hr - pr + ROWS // 2) % ROWS - ROWS // 2
        dc = (hc - pc + COLS // 2) % COLS - COLS // 2
        options = []
        if abs(dr) >= abs(dc):
            if dr:
                options.append((1 if dr > 0 else -1, 0))
            if dc:
                options.append((0, 1 if dc > 0 else -1))
        else:
            if dc:
                options.append((0, 1 if dc > 0 else -1))
            if dr:
                options.append((1 if dr > 0 else -1, 0))
        options += [(1, 0), (-1, 0), (0, 1), (0, -1)]
        body = set(self.predator)
        for d in options:
            nr, nc = (pr + d[0]) % ROWS, (pc + d[1]) % COLS
            if (nr, nc) not in body:
                self.pred_dir = d
                break
        d = self.pred_dir
        self.predator.insert(0, ((pr + d[0]) % ROWS, (pc + d[1]) % COLS))
        if len(self.predator) > 4:
            self.predator.pop()

    def _mg4_draw(self):
        self._draw_pool_snakes([(self.predator, "#c62828", False)])
        self._mg_indicator(
            f"🍎 {self.eaten_count}/{self.cfg['target']}", GOLD, -1)

    def _mg5_setup(self):
        self._spawn_food("apple")
        # золотая еда сбрасывает разгон — теперь она большая редкость (15%)
        if random.random() < 0.15:
            self._spawn_food("golden")
        self.mg5_t = 0.0

    def _mg5_after(self):
        self.mg5_t += self.speed / 1000
        if self.mg5_t >= 5:
            self.mg5_t -= 5
            if self.speed > self.cfg["floor"]:
                self.speed = max(self.cfg["floor"],
                                 self.speed - self.cfg["accel"])
                self.popups.append([COLS * CELL / 2, 30, "⚡ РАЗГОН!",
                                    12, GOLD])
        return True

    def _mg5_draw(self):
        ratio = self.cfg["speed"] / max(1, self.speed)
        self._mg_indicator(f"⚡ ×{ratio:.1f}", GOLD if ratio < 1.5 else WARN, 1)

    def _mg6_setup(self):
        self.mg6_d = 0
        self.mg6_corridor = {}
        self.mg6_col = 3
        self.snake = [(ROWS // 2, 3), (ROWS // 2 - 1, 3), (ROWS // 2 - 2, 3)]
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self._dir_queue.clear()
        self._mg6_timer_items = []
        self._mg6_timer_val = None

    def _mg6_seg(self, d):
        seg = self.mg6_corridor.get(d)
        if seg is not None:
            return seg
        if d < 10:
            seg = (ROWS // 2, 5)
        else:
            pc, _phw = self._mg6_seg(d - 1)
            hw = max(self.cfg["min_hw"], 5 - (d - 10) // 40)
            center = pc + random.randint(-self.cfg["wander"],
                                         self.cfg["wander"])
            center = max(hw + 1, min(ROWS - hw - 2, center))
            seg = (center, hw)
        self.mg6_corridor[d] = seg
        return seg

    def _mg6_tick(self):
        self.mg6_d += 1
        dr, _dc = self.direction
        if (dr, _dc) != (0, 0):
            hr, hc = self.snake[0]
            new_head = (hr + dr, self.mg6_col)
            if new_head in self.snake[2:]:
                self._end_game()
                return
            self.snake.insert(0, new_head)
            self.snake.pop()
        center, hw = self._mg6_seg(self.mg6_d + self.mg6_col)
        if not center - hw <= self.snake[0][0] <= center + hw:
            self._end_game("ВЫЛЕТЕЛ ИЗ ТОННЕЛЯ!")
            return
        # очки = секунды выживания (монеты начисляются за время в _end_game)
        secs = self.mg6_d * self.speed / 1000.0
        self.score = secs
        self.score_var.set(f"Время: {secs:.1f} с")
        self._draw()
        self._schedule()

    def _mg6_timer_draw(self):
        """Большой золотой таймер под сложностью (в зоне ползунка).
        Пул из двух text-items, обновляется только при смене значения."""
        c = getattr(self, "slider", None)
        if c is None:
            return
        secs = getattr(self, "score", 0.0) or 0.0
        if self._mg6_timer_val is not None \
                and abs(secs - self._mg6_timer_val) < 0.1 \
                and self._mg6_timer_items:
            return
        self._mg6_timer_val = secs
        w = c.winfo_width() or 576
        cy = 100
        txt = f"{secs:.1f} с"
        if not self._mg6_timer_items:
            try:
                self._mg6_timer_items = [
                    c.create_text(w / 2 + 2, cy + 2, text=txt,
                                  font=(self.app.font_title, 22, "bold"),
                                  fill="#3a2a05"),
                    c.create_text(w / 2, cy, text=txt,
                                  font=(self.app.font_title, 22, "bold"),
                                  fill=GOLD),
                ]
            except tk.TclError:
                self._mg6_timer_items = []
                return
        for it in self._mg6_timer_items:
            try:
                c.coords(it, w / 2 + (2 if it == self._mg6_timer_items[0] else 0),
                         cy + (2 if it == self._mg6_timer_items[0] else 0))
                c.itemconfig(it, text=txt)
            except tk.TclError:
                self._mg6_timer_items = []
                return

    def _mg6_draw(self):
        c = self.canvas
        pool = self._tunnel_items
        while len(pool) < 2 * COLS:
            pool.append(c.create_rectangle(-40, -40, -39, -39,
                                           fill="#39424c", outline="",
                                           tags="tunnel", state="hidden"))
        for i in range(COLS):
            center, hw = self._mg6_seg(self.mg6_d + i)
            top = (center - hw) * CELL
            bot = (center + hw + 1) * CELL
            it = pool[2 * i]
            c.coords(it, i * CELL, 0, (i + 1) * CELL, top)
            c.itemconfig(it, state="normal")
            it = pool[2 * i + 1]
            c.coords(it, i * CELL, bot, (i + 1) * CELL, ROWS * CELL)
            c.itemconfig(it, state="normal")

    def _mg7_setup(self):
        self._spawn_food("apple")
        self._spawn_food("apple")
        self.mg7_t = 0.0

    def _mg7_blackout(self):
        return self.mg7_t % 12.0 >= 10.0

    def _mg7_after(self):
        self.mg7_t += self.speed / 1000
        return True

    def _mg7_darkness(self):
        c = self.canvas
        if not self._dark_items:
            for _ in range(4):
                self._dark_items.append(
                    c.create_rectangle(-40, -40, -39, -39, fill="#04060c",
                                       outline="", tags="dark"))
            self._dark_items.append(
                c.create_oval(-40, -40, -39, -39, outline="#7fd4ff",
                              width=2, tags="dark"))
        r = self.cfg["radius"] * CELL * (0.3 if self._mg7_blackout() else 1.0)
        hr, hc = self.snake[0]
        cx, cy = hc * CELL + CELL / 2, hr * CELL + CELL / 2
        w, h = COLS * CELL, ROWS * CELL
        for it, coords in zip(
                self._dark_items,
                ((0, 0, w, cy - r), (0, cy + r, w, h),
                 (0, cy - r, cx - r, cy + r), (cx + r, cy - r, w, cy + r))):
            c.coords(it, *coords)
        c.coords(self._dark_items[4], cx - r, cy - r, cx + r, cy + r)
        # еда пересоздаётся при каждом respawn и попадает ПОВЕРХ тьмы —
        # поднимаем тьму, чтобы фрукты вне фонарика были скрыты
        c.tag_raise("dark")

    def _mg8_setup(self):
        for _ in range(4):
            self._spawn_food("apple")
        ar, ac = ROWS // 2, COLS - 6
        self.ai_snake = [(ar, ac), (ar, ac + 1), (ar, ac + 2), (ar, ac + 3)]
        self.ai_ate = 0
        self.mg8_build = False
        self.mg8_walls = set()
        self._mg8_wall_dirty = True
        # стройка мышью: клик по полю ставит блок (только в режиме стройки)
        try:
            self.canvas.bind("<Button-1>", self._mg8_canvas_click, add="+")
        except Exception:
            pass

    def _mg8_canvas_click(self, event):
        if self.mg != "mg8" or not getattr(self, "mg8_build", False):
            return
        if self.game_over:
            return
        col = int(event.x // CELL)
        row = int(event.y // CELL)
        if not (0 <= row < ROWS and 0 <= col < COLS):
            return
        hr, hc = self.snake[0]
        self._mg8_place(row - hr, col - hc)

    def _mg8_after(self):
        if self.tick_count % self.cfg["ai_every"]:
            return True
        return self._mg8_ai_step()

    def _mg8_bfs_step(self, start, targets, blocked):
        """Кратчайший путь BFS от start к ближайшей из targets.
        Возвращает первый шаг пути или None."""
        if start in targets:
            return None
        seen = {start}
        queue = [(start, None)]
        qi = 0
        while qi < len(queue):
            (r, c), first = queue[qi]
            qi += 1
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if not (0 <= nr < ROWS and 0 <= nc < COLS):
                    continue
                cell = (nr, nc)
                if cell in seen or cell in blocked:
                    continue
                step = first if first is not None else (dr, dc)
                if cell in targets:
                    return step
                seen.add(cell)
                queue.append((cell, step))
        return None

    def _mg8_ai_step(self):
        head = self.ai_snake[0]
        occupied = (set(self.ai_snake) | self.mg8_walls | set(self.snake))
        options = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(options)
        step = None
        target = min(self.foods,
                     key=lambda f: abs(f[1][0] - head[0]) + abs(f[1][1] - head[1]),
                     default=None)
        if target is not None and random.random() < 0.85:
            # умный ИИ: идёт по кратчайшему BFS-пути к еде
            step = self._mg8_bfs_step(head, {target[1]},
                                      occupied - {target[1]})
        if step is None:
            for d in options:
                nr, nc = head[0] + d[0], head[1] + d[1]
                if 0 <= nr < ROWS and 0 <= nc < COLS and (nr, nc) not in occupied:
                    step = d
                    break
        if step is None:
            self._end_game("ЗМЕЙКА ЗАПЕРАТА!", ok=True)
            return False
        nr, nc = head[0] + step[0], head[1] + step[1]
        self.ai_snake.insert(0, (nr, nc))
        self.ai_snake.pop()
        eaten = next((f for f in self.foods if f[1] == (nr, nc)), None)
        if eaten is not None:
            self.foods.remove(eaten)
            self._foods_dirty = True
            self.ai_ate += 1
            self._spawn_food("apple")
            if self.ai_ate >= self.cfg["ai_target"]:
                self._end_game("ЗМЕЙКА СЪЕЛА ВСЮ ЕДУ!")
                return False
        if not self._mg8_food_reachable():
            self._end_game("ЗМЕЙКА ЗАПЕРАТА!", ok=True)
            return False
        return True

    def _mg8_food_reachable(self):
        if not self.foods:
            return False
        food_pos = {f[1] for f in self.foods}
        start = self.ai_snake[0]
        seen = {start}
        stack = [start]
        while stack:
            r, c = stack.pop()
            if (r, c) in food_pos:
                return True
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if (0 <= nr < ROWS and 0 <= nc < COLS
                        and (nr, nc) not in self.mg8_walls
                        and (nr, nc) not in seen):
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return False

    def _mg8_place(self, dr, dc):
        if not self.mg8_build or self.game_over:
            return
        cost = self.cfg["build_cost"]
        if self.score < cost:
            hr, hc = self.snake[0]
            self.popups.append([hc * CELL + CELL / 2, hr * CELL - 6,
                                "Мало очков", 9, WARN])
            return
        hr, hc = self.snake[0]
        cell = (hr + dr, hc + dc)
        if not (0 <= cell[0] < ROWS and 0 <= cell[1] < COLS):
            return
        if cell == (hr + self.direction[0], hc + self.direction[1]):
            # нельзя прямо перед головой: выйдешь из стройки — врежешься
            self.popups.append([hc * CELL + CELL / 2, hr * CELL - 6,
                                "Не перед головой!", 9, WARN])
            return
        busy = (set(self.snake) | set(self.ai_snake) | self.mg8_walls
                | {f[1] for f in self.foods})
        if cell in busy:
            return
        self.score -= cost
        self.score_var.set(f"Счёт: {self.score}")
        self.mg8_walls.add(cell)
        self._mg8_wall_dirty = True
        sfx("click")
        if not self._mg8_food_reachable():
            self._end_game("ЗМЕЙКА ЗАПЕРАТА!", ok=True)

    def _mg8_draw(self):
        if self._mg8_wall_dirty:
            c = self.canvas
            c.delete("mgwall")
            for r, col in self.mg8_walls:
                c.create_rectangle(col * CELL + 1, r * CELL + 1,
                                   (col + 1) * CELL - 1, (r + 1) * CELL - 1,
                                   fill="#ffb74d", outline="#e65100",
                                   tags="mgwall")
            self._mg8_wall_dirty = False
        self._draw_pool_snakes([(self.ai_snake, "#a1887f", False)])
        self._mg_indicator(
            f"🍽 {self.ai_ate}/{self.cfg['ai_target']}  🧱 {self.cfg['build_cost']}",
            WARN, 1)
        if self.mg8_build:
            c = self.canvas
            c.create_text(COLS * CELL / 2, ROWS * CELL - 14,
                          text="🧱 СТРОЙКА (змейка ждёт): стрелки или клик — блок · B — выход",
                          font=(self.app.font_ui, 10, "bold"), fill="#ffb74d",
                          tags="mgfx")

    def _mg9_setup(self):
        self._spawn_food("apple")
        self._spawn_food("apple")
        mid_y = ROWS // 2
        brow = mid_y - 4
        self.mg9_b = [(brow, COLS // 2), (brow, COLS // 2 + 1),
                      (brow, COLS // 2 + 2)]
        self.mg9_bdir = (0, -1)

    def _mg9_after(self):
        if self.snake[0] in self.mg9_b:
            self._end_game("СТОЛКНОВЕНИЕ!")
            return False
        dr, dc = self.direction
        bdr, bdc = dr, -dc
        self.mg9_bdir = (bdr, bdc)
        hr, hc = self.mg9_b[0]
        nr, nc = hr + bdr, hc + bdc
        if self.cfg["wrap"]:
            nr %= ROWS
            nc %= COLS
        elif not (0 <= nr < ROWS and 0 <= nc < COLS):
            self._end_game("ЗЕРКАЛЬНАЯ ВРЕЗАЛАСЬ!")
            return False
        if (nr, nc) in self.mg9_b or (nr, nc) in self.snake:
            self._end_game("ЗЕРКАЛЬНАЯ ВРЕЗАЛАСЬ!")
            return False
        self.mg9_b.insert(0, (nr, nc))
        eaten = next((f for f in self.foods if f[1] == (nr, nc)), None)
        if eaten is not None:
            self.foods.remove(eaten)
            self._foods_dirty = True
            info = FOOD_BY_ID[eaten[0]]
            self.score += info["value"]
            sfx("eat")
            self.score_var.set(f"Счёт: {self.score}")
            self._spawn_food("apple")
        else:
            self.mg9_b.pop()
        return True

    def _mg10_setup(self):
        for _ in range(3):
            self._spawn_food("apple")
        mid = ROWS // 2
        self.mg_snakes = [
            [(mid, 4), (mid, 3), (mid, 2)],
            [(4, COLS // 2), (4, COLS // 2 + 1), (4, COLS // 2 + 2)],
            [(ROWS - 5, COLS // 2), (ROWS - 5, COLS // 2 - 1),
             (ROWS - 5, COLS // 2 - 2)],
        ]
        self.mg_dirs = [(0, 1), (0, -1), (0, 1)]
        self.mg_active = 0
        self.mg10_t = 0.0
        self.snake = self.mg_snakes[0]
        self.direction = self.mg_dirs[0]
        self.next_direction = self.direction

    def _mg10_occupied(self, exclude):
        cells = set()
        for i, snk in enumerate(self.mg_snakes):
            if i != exclude:
                cells.update(snk)
        return cells

    def _mg10_after(self):
        self.mg10_t += self.speed / 1000
        if self.mg10_t >= 5:
            self.mg10_t -= 5
            self.mg_active = (self.mg_active + 1) % 3
            self.snake = self.mg_snakes[self.mg_active]
            self.direction = self.mg_dirs[self.mg_active]
            self.next_direction = self.direction
            self._dir_queue.clear()
            self.popups.append([COLS * CELL / 2, 30,
                                f"ХОД ЗМЕЙКИ {self.mg_active + 1}", 12, GOLD])
        for i in range(3):
            if i == self.mg_active:
                continue
            if not self._mg10_move_inactive(i):
                return False
        if self.snake[0] in self._mg10_occupied(self.mg_active):
            self._end_game("СТОЛКНОВЕНИЕ!")
            return False
        return True

    def _mg10_move_inactive(self, i):
        """Неактивная змейка гуляет по всей карте и мешает игроку,
        но НИКОГДА не вызывает конец игры и не сталкивается с другими."""
        snk = self.mg_snakes[i]
        dr, dc = self.mg_dirs[i]
        hr, hc = snk[0]
        occupied = self._mg10_occupied(i) | set(snk[:-1])

        def free(d):
            nr, nc = hr + d[0], hc + d[1]
            return (0 <= nr < ROWS and 0 <= nc < COLS
                    and (nr, nc) not in occupied)

        # изредка поворачиваем случайно — гуляют по всей карте
        if random.random() < 0.10:
            perp = [(dc, dr), (-dc, -dr), (-dr, -dc)]
            random.shuffle(perp)
            for d in perp:
                if free(d):
                    dr, dc = d
                    break
        if not free((dr, dc)):
            perp = [(dc, dr), (-dc, -dr), (-dr, -dc)]
            random.shuffle(perp)
            nd = next((d for d in perp if free(d)), None)
            if nd is None:
                # тупик — просто пропускаем ход (хвост уйдёт, место освободится)
                return True
            dr, dc = nd
        self.mg_dirs[i] = (dr, dc)
        snk.insert(0, (hr + dr, hc + dc))
        snk.pop()
        return True

    def _mg10_draw(self):
        # seg_color резолвит градиентные id ("grad_sunset" и т.п.) в hex
        sel = seg_color(self.app.save.get("selected", "#3fb950"),
                        0, 1, self.tick_count)
        snakes = []
        for i, snk in enumerate(self.mg_snakes):
            if i == self.mg_active:
                continue
            snakes.append((snk, blend(sel, "#000000", 0.45), False))
        if snakes:
            self._draw_pool_snakes(snakes)
        self._mg_indicator(f"🔁 {self.mg_active + 1}/3", GOLD, -1)
