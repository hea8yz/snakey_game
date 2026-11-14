import colorsys


from snakey_content import BG, FOOD_BY_ID, GRADIENTS, THEME_BY_ID


_BLEND_CACHE = {}
def blend(c1, c2, t):
    key = (c1, c2, round(t, 3))
    hit = _BLEND_CACHE.get(key)
    if hit is not None:
        return hit
    try:
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    except (ValueError, TypeError, IndexError):
        return c1
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    res = f"#{r:02x}{g:02x}{b:02x}"
    if len(_BLEND_CACHE) > 8192:
        _BLEND_CACHE.clear()
    _BLEND_CACHE[key] = res
    return res
_HSV_CACHE = {}
def hsv_hex(h, s, v):
    key = (round(h % 1.0, 3), round(s, 3), round(v, 3))
    hit = _HSV_CACHE.get(key)
    if hit is not None:
        return hit
    r, g, b = colorsys.hsv_to_rgb(*key)
    res = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
    if len(_HSV_CACHE) > 4096:
        _HSV_CACHE.clear()
    _HSV_CACHE[key] = res
    return res
def round_pts(x1, y1, x2, y2, radius):
    return (
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
    )
def round_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    return canvas.create_polygon(round_pts(x1, y1, x2, y2, radius),
                                 smooth=True, **kwargs)
def gradient_bands(c, x1, y1, x2, y2, c1, c2, steps=22, tags=""):
    bh = (y2 - y1) / steps
    for i in range(steps):
        col = blend(c1, c2, i / max(1, steps - 1))
        c.create_rectangle(x1, y1 + i * bh - 1, x2, y1 + (i + 1) * bh + 1,
                           fill=col, outline="", tags=tags)
def seg_color(sel, i, need, tick):
    if sel == "rainbow":
        # квантование тика: цвет обновляется каждые 2 тика вместо каждого —
        # вдвое меньше itemconfig на длинной змейке, для глаза неотличимо
        tick -= tick % 2
        return hsv_hex((i * 14 + tick * 8) / 360, 0.85, 0.95)
    g = GRADIENTS.get(sel)
    if g:
        return blend(g[0], g[1], i / max(1, need - 1))
    if i == 0:
        return blend(sel, "#ffffff", 0.25)
    return blend(sel, BG, min(0.55, 0.06 * i))
def info_text(kind, item, save):
    lines = []
    if kind == "color":
        if item["id"] == "rainbow":
            lines.append("Переливающийся скин змейки")
        elif item["id"] in GRADIENTS:
            lines.append("Градиентный скин змейки")
        else:
            lines.append("Цвет змейки")
    elif kind == "theme":
        t = THEME_BY_ID[item["id"]]
        lines.append("Фон игрового поля")
        lines.append(f"Множитель монет и опыта: ×{t['bonus']:g}")
    elif kind == "food":
        f = FOOD_BY_ID[item["id"]]
        lines.append(f"Еда: +{f['value']} очков")
        lines.append(f"Шанс появления: {f['chance']:g}")
        st = save.get("stats")
        if isinstance(st, dict):
            fc = st.get("food_counts") or {}
            if fc.get(f["id"]):
                lines.append(f"Съедено: {fc[f['id']]}")
    else:
        lines.append("Аксессуар для головы змейки")
    if item.get("price"):
        lines.append(f"Цена: {item['price']} монет")
    if item.get("level", 1) > 1:
        lines.append(f"Открывается на {item['level']} уровне")
    return "\n".join(lines)