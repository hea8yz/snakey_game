import json
from pathlib import Path


from snakey_content import ACCESSORIES, COLORS, FOOD_ITEMS, MUSIC_TRACKS, THEMES
from snakey_content import ACHIEVEMENTS


SAVE_FILE = Path.home() / ".snakey_save.json"
DEFAULT_OWNED = {"owned": {"#3fb950"}, "owned_themes": {"night"},
                 "owned_foods": {"apple"}, "owned_acc": {"none"}}
def ach_value(ach, save):
    stat = ach["stat"]
    if stat == "level":
        return level_from_exp(save.get("exp", 0))
    if stat == "skins":
        return sum(sum(1 for iid in (save.get(key) or []) if iid not in defs)
                   for key, defs in DEFAULT_OWNED.items())
    st = save.get("stats")
    if isinstance(st, dict):
        return st.get(stat, 0)
    return 0
def ach_reward_text(ach):
    r = ach["reward"]
    if "coins" in r:
        return f"{r['coins']} монет"
    kind, iid = r["item"]
    table = {"color": COLORS, "theme": THEMES,
             "food": FOOD_ITEMS, "acc": ACCESSORIES,
             "music": MUSIC_TRACKS}
    kindname = {"color": "цвет", "theme": "фон",
                "food": "еда", "acc": "аксессуар",
                "music": "музыка"}[kind]
    name = next(it["name"] for it in table[kind] if it["id"] == iid)
    return f"{kindname} «{name}»"
def grant_ach_reward(save, ach):
    r = ach["reward"]
    if "coins" in r:
        save["coins"] = save.get("coins", 0) + r["coins"]
    else:
        kind, iid = r["item"]
        key = {"color": "owned", "theme": "owned_themes",
               "food": "owned_foods", "acc": "owned_acc",
               "music": "owned_music"}[kind]
        lst = save.setdefault(key, [])
        if iid not in lst:
            lst.append(iid)
def check_achievements(save):
    done = save.setdefault("ach_done", [])
    pending = save.setdefault("pending_ach", [])
    newly = []
    for ach in ACHIEVEMENTS:
        if ach["id"] in done:
            continue
        if ach_value(ach, save) >= ach["goal"]:
            done.append(ach["id"])
            grant_ach_reward(save, ach)
            newly.append(ach["name"])
    pending.extend(newly)
    return newly
DEFAULT_SAVE = {
    "highscore": 0,
    "coins": 0,
    "exp": 0,
    "pending_level": 0,
    "owned": ["#3fb950"],
    "selected": "#3fb950",
    "owned_themes": ["night"],
    "theme": "night",
    "owned_foods": ["apple"],
    "owned_acc": ["none"],
    "accessory": "none",
    "speed": "normal",
    "mg1_diff": "normal",
    "low_spec": False,
    "window_size": "medium",
    "sound": True,
    "music": True,
    "music_track": "classic",
    "music_volume": 70,
    "sound_volume": 80,
    "mute": False,
    "owned_music": ["classic"],
    "autoupdate": True,
    "stats": {},
    "ach_done": [],
    "pending_ach": [],
}
def load_save():
    data = json.loads(json.dumps(DEFAULT_SAVE))
    try:
        loaded = json.loads(SAVE_FILE.read_text())
        if isinstance(loaded, dict):
            data.update(loaded)
    except (OSError, ValueError):
        pass
    return data
def save_save(data):
    try:
        SAVE_FILE.write_text(json.dumps(data))
    except OSError:
        pass
def exp_for_level(level):
    x = max(0, level - 1)
    return 10 * x * x + 2 * x * x * x
def level_from_exp(exp):
    e = max(0, exp)
    lo, hi = 1, 2
    while exp_for_level(hi) <= e:
        hi *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if exp_for_level(mid) <= e:
            lo = mid
        else:
            hi = mid
    return lo