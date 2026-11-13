import math


from snakey_content import ACCENT, BLUE, CELL, DIM, GOLD, POISON, RED


def _fruit_ball(c, cx, cy, r, fill, outline, tags, simple, hi="#ffffff"):
    if not simple:
        c.create_oval(cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5,
                      fill=fill, stipple="gray25", outline="", tags=tags)
    c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=fill,
                  outline=outline, tags=tags)
    c.create_oval(cx - r * 0.55, cy - r * 0.6, cx - r * 0.1, cy - r * 0.15,
                  fill=hi, outline="", tags=tags)
def draw_food(c, cx, cy, kind, phase=0.0, tags="", simple=False, scale=1.0):
    pulse = 0.0 if simple else math.sin(phase) * 1.2
    r = (9 + pulse) * scale
    if kind == "apple":
        _fruit_ball(c, cx, cy, r, RED, "#c93a3a", tags, simple, "#ffb3b3")
        c.create_oval(cx - 1, cy - r - 4, cx + 5, cy - r + 1, fill=ACCENT,
                      outline="", tags=tags)
    elif kind == "cherry":
        c.create_line(cx, cy - 9, cx - 4, cy + 3, fill="#4d7c33", width=2, tags=tags)
        c.create_line(cx, cy - 9, cx + 5, cy + 1, fill="#4d7c33", width=2, tags=tags)
        for dx, dy in ((-4, 5), (5, 3)):
            c.create_oval(cx + dx - 5, cy + dy - 5, cx + dx + 5, cy + dy + 5,
                          fill="#ff4f7d", outline="#c93a5c", tags=tags)
        c.create_oval(cx - 6, cy + 2, cx - 4, cy + 4, fill="#ffc2d4",
                      outline="", tags=tags)
    elif kind == "banana":
        c.create_arc(cx - 11, cy - 9, cx + 11, cy + 11, start=195, extent=135,
                     style="arc", outline="#ffd33d", width=5, tags=tags)
        c.create_line(cx - 9, cy - 6, cx - 11, cy - 9, fill="#8a6d1d",
                      width=3, tags=tags)
    elif kind == "orange":
        _fruit_ball(c, cx, cy, r, "#ff9f1c", "#d97f06", tags, simple, "#ffd9a0")
        for ang in range(0, 360, 45):
            ex = cx + math.cos(math.radians(ang)) * r
            ey = cy + math.sin(math.radians(ang)) * r
            c.create_line(cx + math.cos(math.radians(ang)) * r * 0.3,
                          cy + math.sin(math.radians(ang)) * r * 0.3,
                          ex, ey, fill="#e08608", tags=tags)
        c.create_oval(cx - 1, cy - r - 4, cx + 4, cy - r + 1, fill="#4d7c33",
                      outline="", tags=tags)
    elif kind == "grape":
        c.create_line(cx, cy - 10, cx, cy - 4, fill="#4d7c33", width=2, tags=tags)
        for dx, dy in ((-4, -4), (4, -4), (-4, 2), (4, 2), (0, 7)):
            c.create_oval(cx + dx - 4, cy + dy - 4, cx + dx + 4, cy + dy + 4,
                          fill="#a371f7", outline="#6e40c9", tags=tags)
    elif kind == "melon":
        _fruit_ball(c, cx, cy, r, "#2e9e4f", "#1d6b35", tags, simple, "#a8f0b0")
        for off in (-5, 0, 5):
            c.create_arc(cx - r + 2, cy - r, cx + r + 2 + off, cy + r,
                         start=110, extent=140, style="arc",
                         outline="#7ee08a", width=2, tags=tags)
    elif kind == "golden":
        _fruit_ball(c, cx, cy, r, GOLD, "#b8860b", tags, simple, "#fff3c4")
        c.create_line(cx + r + 1, cy - r - 1, cx + r + 5, cy - r - 5,
                      fill="#fff3c4", width=2, tags=tags)
        c.create_line(cx - r - 1, cy + r + 1, cx - r - 5, cy + r + 5,
                      fill="#fff3c4", width=2, tags=tags)
    elif kind == "star":
        if not simple:
            c.create_oval(cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6,
                          fill="#ffe14d", stipple="gray25", outline="", tags=tags)
        pts = []
        for k in range(10):
            rad = r if k % 2 == 0 else r * 0.45
            a = math.radians(k * 36 - 90 + phase * 20)
            pts.extend((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
        c.create_polygon(pts, fill="#ffe14d", outline="#c9a227", tags=tags)
        c.create_oval(cx - 3, cy - 3, cx + 1, cy + 1, fill="#fff8d6",
                      outline="", tags=tags)
    elif kind == "raspberry":
        c.create_line(cx, cy - 9, cx - 3, cy - 4, fill="#4d7c33", width=2, tags=tags)
        for dx, dy in ((0, -5), (-4, -2), (4, -2), (-2, 2), (2, 2), (0, 6)):
            c.create_oval(cx + dx - 3.5, cy + dy - 3.5, cx + dx + 3.5, cy + dy + 3.5,
                          fill="#e0356b", outline="#a82050", tags=tags)
        c.create_oval(cx - 3, cy - 6, cx - 1, cy - 4, fill="#ff9cbf",
                      outline="", tags=tags)
    elif kind == "kiwi":
        c.create_oval(cx - 9, cy - 9, cx + 9, cy + 9, fill="#8ac24a",
                      outline="#5f8f33", tags=tags)
        c.create_oval(cx - 6, cy - 6, cx + 6, cy + 6, fill="#d8f0a8",
                      outline="", tags=tags)
        c.create_oval(cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5, fill="#f0f8e0",
                      outline="", tags=tags)
        for ang in range(0, 360, 45):
            x1 = cx + math.cos(math.radians(ang)) * 2.5
            y1 = cy + math.sin(math.radians(ang)) * 2.5
            x2 = cx + math.cos(math.radians(ang)) * 5
            y2 = cy + math.sin(math.radians(ang)) * 5
            c.create_line(x1, y1, x2, y2, fill="#3d5c1d", tags=tags)
    elif kind == "mango":
        _fruit_ball(c, cx, cy, r, "#ffb300", "#d98f00", tags, simple, "#ffd866")
        c.create_oval(cx + 3, cy - 10, cx + 8, cy - 6, fill="#4d7c33",
                      outline="", tags=tags)
    elif kind == "dragon":
        c.create_oval(cx - 9, cy - 10, cx + 9, cy + 10, fill="#f04fd1",
                      outline="#b03098", tags=tags)
        for sx, sy in ((-4, -8), (0, -10), (4, -8)):
            c.create_polygon(cx + sx - 2, cy + sy + 2, cx + sx + 2, cy + sy + 2,
                             cx + sx, cy + sy - 3, fill="#7ee08a",
                             outline="", tags=tags)
        c.create_oval(cx - 4, cy - 3, cx + 2, cy + 3, fill="#ffc2ee",
                      outline="", tags=tags)
    elif kind == "diamond":
        c.create_polygon(cx - 9, cy - 3, cx - 4, cy - 9, cx + 4, cy - 9,
                         cx + 9, cy - 3, cx, cy + 10,
                         fill="#7ee8ff", outline="#38b6d6", tags=tags)
        c.create_line(cx - 9, cy - 3, cx + 9, cy - 3, fill="#b8f4ff", tags=tags)
        c.create_line(cx - 4, cy - 9, cx - 2, cy - 3, fill="#b8f4ff", tags=tags)
        c.create_line(cx + 4, cy - 9, cx + 2, cy - 3, fill="#b8f4ff", tags=tags)
        c.create_line(cx - 2, cy - 3, cx, cy + 10, fill="#b8f4ff", tags=tags)
        c.create_line(cx + 2, cy - 3, cx, cy + 10, fill="#b8f4ff", tags=tags)
    elif kind == "lemon":
        _fruit_ball(c, cx, cy, r, "#e8ff47", "#b8c92e", tags, simple, "#fbffd6")
        c.create_polygon(cx - r - 3, cy - 2, cx - r + 2, cy - 5,
                         cx - r + 2, cy + 1, fill="#e8ff47", outline="", tags=tags)
        c.create_polygon(cx + r + 3, cy + 2, cx + r - 2, cy + 5,
                         cx + r - 2, cy - 1, fill="#e8ff47", outline="", tags=tags)
    elif kind == "peach":
        _fruit_ball(c, cx, cy, r, "#ffb38a", "#d98f5c", tags, simple, "#ffd9c0")
        c.create_arc(cx - 2, cy - r, cx + 6, cy + r, start=90, extent=160,
                     style="arc", outline="#d98f5c", tags=tags)
        c.create_oval(cx - 1, cy - r - 4, cx + 6, cy - r + 2, fill="#4d7c33",
                      outline="", tags=tags)
    elif kind == "pear":
        c.create_oval(cx - 4, cy - 12, cx + 4, cy - 2, fill="#c7e85c",
                      outline="#8fae3a", tags=tags)
        c.create_oval(cx - 8, cy - 4, cx + 8, cy + 10, fill="#c7e85c",
                      outline="#8fae3a", tags=tags)
        c.create_oval(cx - 4, cy + 1, cx - 1, cy + 4, fill="#e9f7b8",
                      outline="", tags=tags)
        c.create_line(cx, cy - 12, cx + 2, cy - 15, fill="#4d7c33", width=2, tags=tags)
    elif kind == "plum":
        _fruit_ball(c, cx, cy, r, "#7a5cff", "#4a2f9e", tags, simple, "#b3a0ff")
        c.create_arc(cx - 2, cy - r, cx + 4, cy + r, start=60, extent=120,
                     style="arc", outline="#4a2f9e", tags=tags)
    elif kind == "strawberry":
        c.create_polygon(cx - 8, cy - 4, cx + 8, cy - 4, cx + 4, cy + 8,
                         cx - 4, cy + 8, fill="#ff4f6d", outline="#c22a4a",
                         tags=tags)
        for sx, sy in ((-4, 0), (0, 2), (4, 0), (-2, 5), (2, 5)):
            c.create_oval(cx + sx - 1, cy + sy - 1, cx + sx + 1, cy + sy + 1,
                          fill="#ffd3dc", outline="", tags=tags)
        c.create_polygon(cx - 5, cy - 4, cx + 5, cy - 4, cx, cy - 9,
                         fill="#4d7c33", outline="", tags=tags)
    elif kind == "pineapple":
        c.create_oval(cx - 7, cy - 8, cx + 7, cy + 10, fill="#ffd33d",
                      outline="#c9a227", tags=tags)
        c.create_line(cx - 7, cy - 3, cx + 7, cy + 3, fill="#c9a227", tags=tags)
        c.create_line(cx - 7, cy + 3, cx + 7, cy - 3, fill="#c9a227", tags=tags)
        for dx in (-4, 0, 4):
            c.create_line(cx + dx, cy - 8, cx + dx * 1.6, cy - 14,
                          fill="#4d7c33", width=2, tags=tags)
    elif kind == "coconut":
        _fruit_ball(c, cx, cy, r, "#b08d6a", "#7a5c3a", tags, simple, "#d9c2a8")
        for sx, sy in ((-3, -2), (3, -2), (0, 3)):
            c.create_oval(cx + sx - 1.5, cy + sy - 1.5, cx + sx + 1.5, cy + sy + 1.5,
                          fill="#5c3f22", outline="", tags=tags)
    elif kind == "pomegranate":
        _fruit_ball(c, cx, cy, r, "#d6336c", "#9e1e4a", tags, simple, "#ff9cbf")
        c.create_polygon(cx - 3, cy - r - 1, cx - 1, cy - r - 5, cx + 1, cy - r - 2,
                         cx + 3, cy - r - 5, cx + 4, cy - r - 1,
                         fill="#9e1e4a", outline="", tags=tags)
    elif kind == "passion":
        _fruit_ball(c, cx, cy, r, "#ff8a3d", "#c25f14", tags, simple, "#ffc299")
        c.create_line(cx, cy - r + 2, cx, cy + r - 2, fill="#c25f14", tags=tags)
    elif kind == "lychee":
        _fruit_ball(c, cx, cy, r, "#ffb3c1", "#c97a8f", tags, simple, "#ffe0e8")
        for sx, sy in ((-4, -3), (3, -1), (-1, 4)):
            c.create_oval(cx + sx - 2, cy + sy - 2, cx + sx + 2, cy + sy + 2,
                          outline="#c97a8f", tags=tags)
    elif kind == "papaya":
        c.create_oval(cx - 9, cy - 7, cx + 9, cy + 9, fill="#ff9f5c",
                      outline="#d97a2e", tags=tags)
        c.create_oval(cx - 5, cy - 3, cx + 2, cy + 4, fill="#ffd9a8",
                      outline="", tags=tags)
        c.create_oval(cx + 5, cy - 10, cx + 9, cy - 6, fill="#4d7c33",
                      outline="", tags=tags)
    elif kind == "fig":
        c.create_polygon(cx - 7, cy - 2, cx + 7, cy - 2, cx + 4, cy + 8,
                         cx - 4, cy + 8, fill="#8e5cd9", outline="#5c3a9e",
                         tags=tags)
        c.create_oval(cx - 6, cy - 10, cx + 6, cy + 1, fill="#8e5cd9",
                      outline="#5c3a9e", tags=tags)
        c.create_line(cx, cy - 10, cx, cy - 14, fill="#4d7c33", width=2, tags=tags)
        c.create_oval(cx - 4, cy - 6, cx - 1, cy - 3, fill="#c9a8ff",
                      outline="", tags=tags)
    elif kind == "iceberry":
        _fruit_ball(c, cx, cy, r, "#7ee8ff", "#38b6d6", tags, simple, "#e0faff")
        c.create_line(cx - 3, cy - 12, cx - 3, cy - 6, fill="#e0faff", width=1, tags=tags)
        c.create_line(cx - 6, cy - 9, cx, cy - 9, fill="#e0faff", width=1, tags=tags)
    elif kind == "sunfruit":
        _fruit_ball(c, cx, cy, r, "#ffe14d", "#c9a227", tags, simple, "#fff8d6")
        for a_ in range(8):
            ang = math.radians(a_ * 45 + phase * 15)
            c.create_line(cx + math.cos(ang) * (r + 2), cy + math.sin(ang) * (r + 2),
                          cx + math.cos(ang) * (r + 6), cy + math.sin(ang) * (r + 6),
                          fill="#ffe14d", width=2, tags=tags)
    elif kind == "mythic":
        _fruit_ball(c, cx, cy, r, "#f04fd1", "#a8308f", tags, simple, "#ffb3ec")
        c.create_oval(cx - 13, cy - 5, cx + 13, cy + 5, outline="#ffb3ec", tags=tags)
        c.create_oval(cx + 10, cy - 8, cx + 13, cy - 5, fill="#ffffff",
                      outline="", tags=tags)
    elif kind == "poison":
        _fruit_ball(c, cx, cy, r, POISON, "#2a1240", tags, simple, "#6b4a94")
        for sx, sy in ((-3, -2), (3, 1), (-1, 4)):
            c.create_oval(cx + sx - 2, cy + sy - 2, cx + sx + 2, cy + sy + 2,
                          fill="#7cb342", outline="", tags=tags)
        c.create_oval(cx - 1, cy - r - 4, cx + 5, cy - r + 1, fill="#3d5c2a",
                      outline="", tags=tags)
def draw_acc(c, cx, cy, kind, phase=0.0, tags=""):
    top = cy - CELL / 2 + 2
    if kind == "santa":
        c.create_polygon(cx - 8, top + 6, cx + 8, top + 6, cx + 6, top - 4,
                         cx - 5, top - 3, fill=RED, outline="#a03030", tags=tags)
        c.create_line(cx - 9, top + 6, cx + 9, top + 6, fill="#f0f6fc",
                      width=4, tags=tags)
        c.create_oval(cx + 5, top - 9, cx + 10, top - 4, fill="#f0f6fc",
                      outline="", tags=tags)
    elif kind == "cap":
        c.create_arc(cx - 8, top - 2, cx + 8, top + 10, start=0, extent=180,
                     style="pieslice", fill=BLUE, outline="#2a5db0", tags=tags)
        c.create_line(cx - 10, top + 7, cx + 10, top + 7, fill="#2a5db0",
                      width=3, tags=tags)
    elif kind == "crown":
        c.create_polygon(cx - 8, top + 7, cx - 8, top - 2, cx - 4, top + 2,
                         cx, top - 4, cx + 4, top + 2, cx + 8, top - 2,
                         cx + 8, top + 7, fill=GOLD, outline="#b8860b", tags=tags)
        c.create_oval(cx - 1.5, top + 1, cx + 1.5, top + 4, fill=RED,
                      outline="", tags=tags)
    elif kind == "halo":
        w = 9 + math.sin(phase) * 1.5
        c.create_oval(cx - w, top - 6, cx + w, top - 1, outline=GOLD,
                      width=3, tags=tags)
    elif kind == "horns":
        for sign in (-1, 1):
            c.create_polygon(cx + sign * 5, top + 8, cx + sign * 9, top + 8,
                             cx + sign * 8, top - 3, cx + sign * 5, top + 1,
                             fill="#e8d8c8", outline="#b09a80", tags=tags)
    elif kind == "propeller":
        c.create_line(cx, top + 8, cx, top + 2, fill=DIM, width=2, tags=tags)
        w = abs(math.sin(phase * 2)) * 7 + 2
        c.create_oval(cx - w, top - 2, cx + w, top + 4, fill=BLUE,
                      outline="#2a5db0", tags=tags)
    elif kind == "wizard":
        c.create_polygon(cx - 8, top + 8, cx + 8, top + 8, cx + 1, top - 8,
                         fill="#7a5cff", outline="#4a2f9e", tags=tags)
        c.create_line(cx - 10, top + 8, cx + 10, top + 8, fill="#4a2f9e",
                      width=3, tags=tags)
        c.create_polygon(cx + 1, top - 6, cx + 3, top - 2, cx - 1, top - 2,
                         fill="#ffe14d", outline="", tags=tags)
    elif kind == "bow":
        c.create_polygon(cx - 9, top + 1, cx - 1, top - 3, cx - 1, top + 5,
                         fill="#f778ba", outline="#c2417f", tags=tags)
        c.create_polygon(cx + 9, top + 1, cx + 1, top - 3, cx + 1, top + 5,
                         fill="#f778ba", outline="#c2417f", tags=tags)
        c.create_oval(cx - 2, top, cx + 2, top + 4, fill="#ffd3e8",
                      outline="#c2417f", tags=tags)
    elif kind == "headphones":
        c.create_arc(cx - 10, top - 4, cx + 10, top + 12, start=0, extent=180,
                     style="arc", outline="#cdd9e5", width=3, tags=tags)
        c.create_oval(cx - 12, top + 2, cx - 6, top + 10, fill="#58a6ff",
                      outline="#2a5db0", tags=tags)
        c.create_oval(cx + 6, top + 2, cx + 12, top + 10, fill="#58a6ff",
                      outline="#2a5db0", tags=tags)
    elif kind == "tophat":
        c.create_rectangle(cx - 6, top - 9, cx + 6, top + 3, fill="#22262b",
                           outline="#0d1117", tags=tags)
        c.create_line(cx - 10, top + 3, cx + 10, top + 3, fill="#22262b",
                      width=4, tags=tags)
        c.create_line(cx - 6, top - 1, cx + 6, top - 1, fill="#8957e5",
                      width=2, tags=tags)
    elif kind == "catears":
        for sign in (-1, 1):
            c.create_polygon(cx + sign * 3, top + 4, cx + sign * 9, top + 6,
                             cx + sign * 6, top - 5,
                             fill="#8b949e", outline="#5d646d", tags=tags)
            c.create_polygon(cx + sign * 4.5, top + 2.5, cx + sign * 7,
                             top + 3.5, cx + sign * 6, top - 1,
                             fill="#f778ba", outline="", tags=tags)
    elif kind == "flower":
        for a_ in range(5):
            ang = math.radians(a_ * 72 - 90)
            px = cx + math.cos(ang) * 5
            py = top + 2 + math.sin(ang) * 5
            c.create_oval(px - 3, py - 3, px + 3, py + 3, fill="#f778ba",
                          outline="#c2417f", tags=tags)
        c.create_oval(cx - 2.5, top - 0.5, cx + 2.5, top + 4.5, fill="#ffe14d",
                      outline="", tags=tags)
    elif kind == "leaf":
        c.create_polygon(cx, top - 6, cx + 7, top + 2, cx, top + 8, cx - 7, top + 2,
                         fill="#4d7c33", outline="#2f5c1d", tags=tags)
        c.create_line(cx, top - 4, cx, top + 6, fill="#7ee08a", tags=tags)
    elif kind == "heart":
        c.create_polygon(cx - 7, top + 1, cx - 3, top - 4, cx, top - 1,
                         cx + 3, top - 4, cx + 7, top + 1, cx, top + 8,
                         fill="#ff5c5c", outline="#c93a3a", tags=tags)
    elif kind == "antenna":
        for sign in (-1, 1):
            c.create_line(cx + sign * 3, top + 4, cx + sign * 7, top - 6,
                          fill=DIM, width=2, tags=tags)
            c.create_oval(cx + sign * 7 - 2, top - 8, cx + sign * 7 + 2, top - 4,
                          fill=ACCENT, outline="", tags=tags)
    elif kind == "starhair":
        pts = []
        for k in range(10):
            rad = 7 if k % 2 == 0 else 3
            a_ = math.radians(k * 36 - 90)
            pts.extend((cx + math.cos(a_) * rad, top + 1 + math.sin(a_) * rad))
        c.create_polygon(pts, fill=GOLD, outline="#b8860b", tags=tags)
    elif kind == "beret":
        c.create_arc(cx - 9, top - 2, cx + 9, top + 10, start=0, extent=180,
                     style="pieslice", fill="#d6336c", outline="#9e1e4a", tags=tags)
        c.create_line(cx - 2, top - 4, cx + 3, top - 6, fill="#9e1e4a",
                      width=2, tags=tags)
    elif kind == "bee":
        bob = math.sin(phase * 2) * 2
        c.create_oval(cx - 6, top - 6 + bob, cx + 6, top + 4 + bob,
                      fill="#ffd33d", outline="#8a6d1d", tags=tags)
        c.create_line(cx - 2, top - 6 + bob, cx - 2, top + 4 + bob,
                      fill="#2a2f36", width=2, tags=tags)
        c.create_line(cx + 2, top - 6 + bob, cx + 2, top + 4 + bob,
                      fill="#2a2f36", width=2, tags=tags)
        c.create_oval(cx - 5, top - 9 + bob, cx - 1, top - 5 + bob,
                      fill="#e0f0ff", outline="", tags=tags)
        c.create_oval(cx + 1, top - 9 + bob, cx + 5, top - 5 + bob,
                      fill="#e0f0ff", outline="", tags=tags)
    elif kind == "chef":
        c.create_rectangle(cx - 5, top + 2, cx + 5, top + 9, fill="#f0f6fc",
                           outline="#c9ccd1", tags=tags)
        c.create_oval(cx - 7, top - 6, cx - 1, top + 3, fill="#f0f6fc",
                      outline="#c9ccd1", tags=tags)
        c.create_oval(cx + 1, top - 6, cx + 7, top + 3, fill="#f0f6fc",
                      outline="#c9ccd1", tags=tags)
    elif kind == "party":
        c.create_polygon(cx - 7, top + 8, cx + 7, top + 8, cx, top - 7,
                         fill="#58a6ff", outline="#2a5db0", tags=tags)
        c.create_oval(cx - 2, top - 10, cx + 2, top - 6, fill="#f778ba",
                      outline="", tags=tags)
        c.create_line(cx - 4, top + 3, cx + 4, top + 3, fill="#ffe14d",
                      width=2, tags=tags)
    elif kind == "mushroom":
        c.create_rectangle(cx - 3, top + 1, cx + 3, top + 8, fill="#f0e6d8",
                           outline="#c9bfa8", tags=tags)
        c.create_arc(cx - 8, top - 4, cx + 8, top + 8, start=0, extent=180,
                     style="pieslice", fill="#ff5c5c", outline="#c93a3a", tags=tags)
        c.create_oval(cx - 4, top, cx - 1, top + 3, fill="#f0f6fc",
                      outline="", tags=tags)
        c.create_oval(cx + 2, top - 1, cx + 5, top + 2, fill="#f0f6fc",
                      outline="", tags=tags)
    elif kind == "turban":
        c.create_arc(cx - 8, top - 3, cx + 8, top + 10, start=0, extent=180,
                     style="pieslice", fill="#39d2c0", outline="#1d8a7a", tags=tags)
        c.create_oval(cx - 2, top - 1, cx + 2, top + 3, fill=GOLD,
                      outline="", tags=tags)
    elif kind == "snowflake":
        for a_ in range(3):
            ang = math.radians(a_ * 60 + phase * 0.4)
            c.create_line(cx - math.cos(ang) * 8, top + 1 - math.sin(ang) * 8,
                          cx + math.cos(ang) * 8, top + 1 + math.sin(ang) * 8,
                          fill="#cdeeff", width=2, tags=tags)
        c.create_oval(cx - 2, top - 1, cx + 2, top + 3, fill="#e0faff",
                      outline="", tags=tags)
    elif kind == "whiskers":
        for sign in (-1, 1):
            for dy in (-3, -1, 1):
                c.create_line(cx + sign * 3, top + 2, cx + sign * 10, top + 2 + dy,
                              fill="#f0f6fc", width=1, tags=tags)
        c.create_oval(cx - 2, top + 1, cx + 2, top + 4, fill="#ff9cbf",
                      outline="", tags=tags)
    elif kind == "pirate":
        c.create_polygon(cx - 10, top + 6, cx + 10, top + 6, cx + 2, top - 7,
                         fill="#22262b", outline="#000000", tags=tags)
        c.create_line(cx - 11, top + 6, cx + 11, top + 6, fill="#f0f6fc",
                      width=2, tags=tags)
        c.create_oval(cx - 3, top - 4, cx + 3, top + 2, fill="#f0f6fc",
                      outline="", tags=tags)
    elif kind == "graduate":
        c.create_polygon(cx - 9, top + 2, cx, top - 3, cx + 9, top + 2, cx, top + 6,
                         fill="#22262b", outline="#000000", tags=tags)
        c.create_line(cx + 6, top + 3, cx + 6, top + 9, fill=GOLD, width=1, tags=tags)
        c.create_oval(cx + 5, top + 8, cx + 7, top + 10, fill=GOLD,
                      outline="", tags=tags)
    elif kind == "ice":
        c.create_polygon(cx, top - 8, cx + 5, top - 2, cx + 3, top + 7,
                         cx - 3, top + 7, cx - 5, top - 2, fill="#a8e8ff",
                         outline="#5fb8d6", tags=tags)
        c.create_line(cx - 2, top - 4, cx + 1, top + 2, fill="#e0faff", tags=tags)
    elif kind == "moon":
        c.create_arc(cx - 7, top - 6, cx + 7, top + 8, start=60, extent=240,
                     style="arc", outline=GOLD, width=3, tags=tags)
        c.create_oval(cx + 4, top - 5, cx + 6, top - 3, fill="#fff3c4",
                      outline="", tags=tags)
    elif kind == "viking":
        c.create_arc(cx - 8, top - 2, cx + 8, top + 10, start=0, extent=180,
                     style="pieslice", fill="#7a828c", outline="#4a5158", tags=tags)
        for sign in (-1, 1):
            c.create_polygon(cx + sign * 7, top + 2, cx + sign * 11, top - 6,
                             cx + sign * 8, top - 1, fill="#e8d8c8",
                             outline="#b09a80", tags=tags)
    elif kind == "gem":
        c.create_polygon(cx - 6, top, cx - 3, top - 5, cx + 3, top - 5,
                         cx + 6, top, cx, top + 8, fill="#7ee8ff",
                         outline="#38b6d6", tags=tags)
        c.create_line(cx - 6, top, cx + 6, top, fill="#e0faff", tags=tags)
    elif kind == "bolt":
        col = "#ffe14d" if math.sin(phase * 3) > -0.2 else "#c9a227"
        c.create_polygon(cx - 1, top - 8, cx + 5, top - 8, cx + 1, top - 1,
                         cx + 5, top - 1, cx - 3, top + 9, cx - 1, top + 1,
                         cx - 5, top + 1, fill=col, outline="", tags=tags)
    elif kind == "flame":
        f = math.sin(phase * 3) * 2
        c.create_polygon(cx - 5, top + 8, cx - 4, top + 2, cx, top - 7 - f,
                         cx + 4, top + 2, cx + 5, top + 8, fill="#ff8a3d",
                         outline="#c25f14", tags=tags)
        c.create_polygon(cx - 2, top + 7, cx + 2, top + 7, cx, top + 1,
                         fill="#ffe14d", outline="", tags=tags)
    elif kind == "spark":
        a_ = phase * 0.8
        for k in range(4):
            ang = a_ + k * math.pi / 2
            c.create_line(cx, top + 1, cx + math.cos(ang) * 8,
                          top + 1 + math.sin(ang) * 8, fill="#ffe14d",
                          width=2, tags=tags)
        c.create_oval(cx - 2, top - 1, cx + 2, top + 3, fill="#fff8d6",
                      outline="", tags=tags)
    elif kind == "orb":
        w_ = 6 + math.sin(phase * 2) * 1.5
        c.create_oval(cx - w_, top + 1 - w_, cx + w_, top + 1 + w_,
                      outline="#7ee8ff", width=2, tags=tags)
        c.create_oval(cx - w_ * 0.4, top + 1 - w_ * 0.4, cx + w_ * 0.4,
                      top + 1 + w_ * 0.4, fill="#38b6d6", outline="", tags=tags)
    elif kind == "sat":
        c.create_oval(cx - 4, top - 2, cx + 4, top + 6, fill="#cdd9e5",
                      outline="#8b949e", tags=tags)
        c.create_arc(cx - 10, top - 1, cx + 10, top + 5, start=0, extent=360,
                     style="arc", outline="#58a6ff", tags=tags)
        mx = cx + math.cos(phase) * 10
        my = top + 2 + math.sin(phase) * 3
        c.create_oval(mx - 1.5, my - 1.5, mx + 1.5, my + 1.5, fill="#58a6ff",
                      outline="", tags=tags)
    elif kind == "icecrown":
        c.create_polygon(cx - 8, top + 7, cx - 8, top - 2, cx - 4, top + 2,
                         cx, top - 5, cx + 4, top + 2, cx + 8, top - 2,
                         cx + 8, top + 7, fill="#a8e8ff", outline="#5fb8d6",
                         tags=tags)
        for sx in (-6, 0, 6):
            c.create_polygon(cx + sx - 1.5, top + 7, cx + sx + 1.5, top + 7,
                             cx + sx, top + 11, fill="#d0f0ff", outline="",
                             tags=tags)