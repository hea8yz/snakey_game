import shutil
import struct
import array
import subprocess
import sys
import threading
import time
import wave
import zlib
import math
from collections import deque
from pathlib import Path


def _base_dir():
    # в собранном exe (PyInstaller) код распакован во временную папку, а ресурсы
    # (assets/, VERSION) лежат рядом с exe — берём их оттуда, чтобы файлы
    # оставались в файловой системе и их можно было менять/модить без пересборки
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


ASSETS_DIR = _base_dir() / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
IMAGES_DIR = ASSETS_DIR / "images"
SFX_NAMES = ("click", "eat", "death", "coin", "levelup", "win", "lose")
SAMPLE_RATE = 22050
ASSET_VERSION = "2"
MUSIC_IDS = ("classic", "retro", "chiptune", "ambient", "funk", "arcade")
VOL_STEPS = 10  # громкость квантуется в 10 шагов (0..10) для кэша wav-вариантов


def _music_file(track):
    return SOUNDS_DIR / f"music_{track}.wav"
def _env(i, n, attack=0.01, release=0.35):
    t = i / max(1, n - 1)
    a = 1.0 if attack <= 0 else min(1.0, t / attack)
    r = 1.0 if release <= 0 else min(1.0, (1.0 - t) / release)
    return a * r
def _sweep(dur, f0, f1, amp, harmonics, decay):
    n = max(1, int(SAMPLE_RATE * dur))
    norm = sum(a for _, a in harmonics) or 1.0
    out = []
    phase = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        f = f0 + (f1 - f0) * (i / n)
        phase += 2.0 * math.pi * f / SAMPLE_RATE
        s = sum(a * math.sin(phase * h) for h, a in harmonics) / norm
        out.append(s * amp * math.exp(-decay * t) * _env(i, n, 0.004, 0.08))
    return out
def _make_sfx(name):
    if name == "click":
        return _sweep(0.06, 1150, 720, 0.32, ((1, 1.0), (2, 0.25)), 20)
    if name == "eat":
        return _sweep(0.13, 320, 980, 0.5, ((1, 1.0), (2, 0.3)), 11)
    if name == "death":
        return _sweep(0.7, 430, 60, 0.5, ((1, 1.0), (2, 0.4), (3, 0.25)), 3.2)
    if name == "coin":
        return (_sweep(0.09, 1046.5, 1046.5, 0.42, ((1, 1.0), (2, 0.2)), 9)
                + _sweep(0.2, 1568.0, 1568.0, 0.42, ((1, 1.0), (2, 0.2)), 7))
    if name == "levelup":
        out = []
        for f in (523.25, 659.25, 783.99, 1046.5):
            out += _sweep(0.14, f, f, 0.4, ((1, 1.0), (2, 0.2)), 6)
        return out
    if name == "win":
        out = []
        for f in (783.99, 1046.5, 1318.5):
            out += _sweep(0.16, f, f, 0.42, ((1, 1.0), (2, 0.2)), 5)
        return out
    if name == "lose":
        out = []
        for f in (329.63, 261.63, 220.0):
            out += _sweep(0.18, f, f * 0.97, 0.42, ((1, 1.0),), 5)
        return out
    return []
def _make_music():
    beat = 0.6
    bar_s = beat * 4
    bars = 4
    total = int(SAMPLE_RATE * bar_s * bars)
    out = [0.0] * total
    chords = ((220.0, 261.63, 329.63), (174.61, 220.0, 261.63),
              (261.63, 329.63, 392.0), (196.0, 246.94, 293.66))
    bass = (110.0, 87.31, 130.81, 98.0)
    melody = (440.0, 523.25, 659.25, 523.25, 440.0, 392.0, 440.0, 523.25,
              659.25, 784.0, 659.25, 523.25, 440.0, 392.0, 329.63, 392.0)
    nbar = int(SAMPLE_RATE * bar_s)
    nbeat = int(SAMPLE_RATE * beat)
    for b in range(bars):
        start = b * nbar
        for j in range(nbar):
            t = j / SAMPLE_RATE
            pad = 0.0
            for f in chords[b]:
                pad += math.sin(2 * math.pi * f * t)
            out[start + j] += pad * 0.08 * _env(j, nbar, 0.18, 0.3)
        for k in range(4):
            s0 = start + k * nbeat
            nd = int(nbeat * 0.9)
            for j in range(nd):
                t = j / SAMPLE_RATE
                out[s0 + j] += (0.16 * math.sin(2 * math.pi * bass[b] * t)
                                * math.exp(-6 * t)
                                * _env(j, nd, 0.004, 0.1))
            f = melody[(b * 4 + k) % len(melody)]
            s0 = start + int((k + 0.5) * nbeat)
            nd = int(nbeat * 0.8)
            if s0 + nd > total:
                continue
            for j in range(nd):
                t = j / SAMPLE_RATE
                out[s0 + j] += (0.12 * math.sin(2 * math.pi * f * t)
                                * math.exp(-7 * t))
    peak = max(abs(s) for s in out) or 1.0
    if peak > 0.95:
        k = 0.95 / peak
        out = [s * k for s in out]
    return out
def _osc_saw(phase):
    return 2.0 * (phase % 1.0) - 1.0
def _osc_square(phase):
    return 1.0 if (phase % 1.0) < 0.5 else -1.0
def _make_music_retro():
    import random as _rnd
    rng = _rnd.Random(808)
    beat = 0.5
    nbeat = int(SAMPLE_RATE * beat)
    bars = 8
    total = nbeat * 4 * bars
    out = [0.0] * total
    roots = (220.00, 174.61, 261.63, 196.00)
    lead = (440.0, 523.25, 659.25, 523.25, 440.0, 392.0, 349.23, 392.0,
            523.25, 659.25, 783.99, 659.25, 523.25, 440.0, 392.0, 329.63)
    bass_pat = (0, 0, 7, 0, 12, 7, 0, 7)
    for b in range(bars):
        root = roots[b % 4]
        base = b * nbeat * 4
        for k in range(8):
            f = root / 2 * (2 ** (bass_pat[k] / 12))
            s0 = base + k * nbeat // 2
            nd = int(nbeat * 0.45)
            ph = 0.0
            for j in range(nd):
                ph += f / SAMPLE_RATE
                t = j / SAMPLE_RATE
                out[s0 + j] += (0.13 * _osc_saw(ph) * math.exp(-5 * t)
                                * _env(j, nd, 0.004, 0.06))
        for k in range(4):
            f = lead[(b * 4 + k) % len(lead)]
            s0 = base + k * nbeat
            nd = int(nbeat * 0.85)
            ph = 0.0
            for j in range(nd):
                ph += f / SAMPLE_RATE
                t = j / SAMPLE_RATE
                v = _osc_square(ph) * 0.55 + math.sin(2 * math.pi * f * t) * 0.45
                out[s0 + j] += (0.085 * v * math.exp(-3.5 * t)
                                * _env(j, nd, 0.01, 0.15))
        for k in range(4):
            s0 = base + k * nbeat
            nd = int(nbeat * 0.5)
            if k % 2 == 0:
                for j in range(nd):
                    t = j / SAMPLE_RATE
                    f = 120 * math.exp(-18 * t) + 40
                    out[s0 + j] += (0.30 * math.sin(2 * math.pi * f * t)
                                    * math.exp(-14 * t))
            else:
                for j in range(nd):
                    out[s0 + j] += (0.11 * (rng.random() * 2 - 1)
                                    * math.exp(-22 * (j / SAMPLE_RATE)))
        for k in range(8):
            s0 = base + k * nbeat // 2
            nd = int(nbeat * 0.22)
            for j in range(nd):
                out[s0 + j] += (0.05 * (rng.random() * 2 - 1)
                                * math.exp(-40 * (j / SAMPLE_RATE)))
    peak = max(abs(s) for s in out) or 1.0
    if peak > 0.95:
        k = 0.95 / peak
        out = [s * k for s in out]
    return out
def _normalize(out):
    peak = max(abs(s) for s in out) or 1.0
    if peak > 0.95:
        k = 0.95 / peak
        out = [s * k for s in out]
    return out
def _make_music_chiptune():
    # быстрый весёлый 8-бит: квадратное арпеджио, пила-бас, шумовые хэты
    import random as _rnd
    rng = _rnd.Random(4242)
    beat = 0.34
    nbeat = int(SAMPLE_RATE * beat)
    bars = 8
    total = nbeat * 4 * bars
    out = [0.0] * total
    roots = (261.63, 196.00, 220.00, 174.61)
    lead = (523.25, 659.25, 783.99, 659.25, 523.25, 587.33, 523.25, 392.0,
            440.0, 523.25, 659.25, 523.25, 783.99, 880.0, 783.99, 659.25)
    arp = (0, 4, 7, 12)
    for b in range(bars):
        root = roots[b % 4]
        base = b * nbeat * 4
        for k in range(16):
            f = root * (2 ** (arp[k % 4] / 12))
            s0 = base + k * nbeat // 4
            nd = int(nbeat * 0.22)
            ph = 0.0
            for j in range(nd):
                ph += f / SAMPLE_RATE
                out[s0 + j] += 0.05 * _osc_square(ph) * _env(j, nd, 0.004, 0.05)
        for k in range(8):
            f = root / 2
            s0 = base + k * nbeat // 2
            nd = int(nbeat * 0.4)
            ph = 0.0
            for j in range(nd):
                ph += f / SAMPLE_RATE
                t = j / SAMPLE_RATE
                out[s0 + j] += (0.12 * _osc_saw(ph) * math.exp(-7 * t)
                                * _env(j, nd, 0.004, 0.05))
        for k in range(4):
            f = lead[(b * 4 + k) % len(lead)]
            s0 = base + k * nbeat
            nd = int(nbeat * 0.9)
            ph = 0.0
            for j in range(nd):
                ph += f / SAMPLE_RATE
                t = j / SAMPLE_RATE
                v = _osc_square(ph) * 0.6 + math.sin(2 * math.pi * f * t) * 0.4
                out[s0 + j] += (0.085 * v * math.exp(-3 * t)
                                * _env(j, nd, 0.008, 0.12))
        for k in range(4):
            s0 = base + k * nbeat
            nd = int(nbeat * 0.4)
            if k % 2 == 0:
                for j in range(nd):
                    t = j / SAMPLE_RATE
                    f = 150 * math.exp(-20 * t) + 45
                    out[s0 + j] += (0.24 * math.sin(2 * math.pi * f * t)
                                    * math.exp(-16 * t))
            else:
                for j in range(nd):
                    out[s0 + j] += (0.06 * (rng.random() * 2 - 1)
                                    * math.exp(-30 * (j / SAMPLE_RATE)))
    return _normalize(out)
def _make_music_ambient():
    # медленный космический эмбиент: мягкие пады с расстройкой и колокольчики
    beat = 1.2
    nbeat = int(SAMPLE_RATE * beat)
    bars = 4
    total = nbeat * 4 * bars
    out = [0.0] * total
    chords = ((220.0, 277.18, 329.63), (174.61, 220.0, 261.63),
              (196.0, 246.94, 293.66), (164.81, 207.65, 246.94))
    bell = (880.0, 1108.73, 1318.51, 987.77, 739.99, 659.25)
    nbar = int(SAMPLE_RATE * beat * 4)
    for b in range(bars):
        start = b * nbar
        for j in range(nbar):
            t = j / SAMPLE_RATE
            pad = 0.0
            for f in chords[b]:
                pad += (math.sin(2 * math.pi * f * t)
                        + 0.6 * math.sin(2 * math.pi * f * 1.003 * t))
            out[start + j] += pad * 0.045 * _env(j, nbar, 0.35, 0.45)
        for k in range(3):
            f = bell[(b * 3 + k) % len(bell)]
            s0 = start + int((k * 1.3 + 0.2) * nbeat)
            nd = int(nbeat * 2.2)
            if s0 + nd > total:
                continue
            for j in range(nd):
                t = j / SAMPLE_RATE
                out[s0 + j] += (0.06 * math.sin(2 * math.pi * f * t)
                                * math.exp(-2.2 * t) * _env(j, nd, 0.002, 0.8))
    return _normalize(out)
def _make_music_funk():
    # фанковый грув: синкопированный пила-бас, аккордовые уколы, сухие барабаны
    import random as _rnd
    rng = _rnd.Random(1971)
    beat = 0.46
    nbeat = int(SAMPLE_RATE * beat)
    bars = 8
    total = nbeat * 4 * bars
    out = [0.0] * total
    roots = (110.0, 110.0, 146.83, 98.0)
    stab = ((220.0, 277.18, 329.63), (233.08, 293.66, 349.23))
    bass_pat = (0, 0, 12, 0, 10, 0, 7, 12)
    for b in range(bars):
        root = roots[b % 4]
        base = b * nbeat * 4
        for k in range(16):
            if k % 4 == 2 and (k // 4) % 2 == 1:
                continue  # пропуски долей — грув
            semis = bass_pat[k % 8] if k % 2 == 0 else 0
            f = root * (2 ** (semis / 12))
            s0 = base + k * nbeat // 4
            nd = int(nbeat * 0.3)
            if s0 + nd > total:
                continue
            ph = 0.0
            for j in range(nd):
                ph += f / SAMPLE_RATE
                t = j / SAMPLE_RATE
                v = _osc_saw(ph) * 0.7 + math.sin(2 * math.pi * f * t) * 0.3
                out[s0 + j] += (0.15 * v * math.exp(-8 * t)
                                * _env(j, nd, 0.003, 0.05))
        for k in range(2):
            ch = stab[(b + k) % 2]
            s0 = base + int((0.5 + k * 2) * nbeat)
            nd = int(nbeat * 0.35)
            for j in range(nd):
                t = j / SAMPLE_RATE
                v = sum(math.sin(2 * math.pi * f * t) for f in ch) / 3
                out[s0 + j] += 0.085 * v * math.exp(-9 * t) * _env(j, nd, 0.003, 0.08)
        for k in range(8):
            s0 = base + k * nbeat // 2
            nd = int(nbeat * 0.3)
            if k % 4 == 0:
                for j in range(nd):
                    t = j / SAMPLE_RATE
                    f = 130 * math.exp(-18 * t) + 42
                    out[s0 + j] += (0.28 * math.sin(2 * math.pi * f * t)
                                    * math.exp(-14 * t))
            elif k % 2 == 1:
                for j in range(nd):
                    out[s0 + j] += (0.09 * (rng.random() * 2 - 1)
                                    * math.exp(-25 * (j / SAMPLE_RATE)))
    return _normalize(out)
def _make_music_arcade():
    # бодрая аркада: ведущая мелодия восьмыми, пила-бас, энергичная бочка
    import random as _rnd
    rng = _rnd.Random(1985)
    beat = 0.4
    nbeat = int(SAMPLE_RATE * beat)
    bars = 8
    total = nbeat * 4 * bars
    out = [0.0] * total
    roots = (220.0, 164.81, 196.0, 174.61)
    lead = (440.0, 523.25, 587.33, 659.25, 587.33, 523.25, 440.0, 392.0,
            349.23, 440.0, 523.25, 440.0, 659.25, 587.33, 523.25, 440.0)
    for b in range(bars):
        root = roots[b % 4]
        base = b * nbeat * 4
        for k in range(4):
            f = root / 2
            s0 = base + k * nbeat
            nd = int(nbeat * 0.55)
            ph = 0.0
            for j in range(nd):
                ph += f / SAMPLE_RATE
                t = j / SAMPLE_RATE
                out[s0 + j] += (0.12 * _osc_saw(ph) * math.exp(-5 * t)
                                * _env(j, nd, 0.004, 0.08))
        for k in range(8):
            f = lead[(b * 8 + k) % len(lead)]
            s0 = base + k * nbeat // 2
            nd = int(nbeat * 0.45)
            ph = 0.0
            for j in range(nd):
                ph += f / SAMPLE_RATE
                t = j / SAMPLE_RATE
                v = math.sin(2 * math.pi * f * t) * 0.5 + _osc_square(ph) * 0.25
                out[s0 + j] += (0.095 * v * math.exp(-4 * t)
                                * _env(j, nd, 0.006, 0.1))
        for k in range(4):
            s0 = base + k * nbeat
            nd = int(nbeat * 0.35)
            if k % 2 == 0:
                for j in range(nd):
                    t = j / SAMPLE_RATE
                    f = 140 * math.exp(-19 * t) + 44
                    out[s0 + j] += (0.26 * math.sin(2 * math.pi * f * t)
                                    * math.exp(-15 * t))
            else:
                for j in range(nd):
                    out[s0 + j] += (0.07 * (rng.random() * 2 - 1)
                                    * math.exp(-28 * (j / SAMPLE_RATE)))
    return _normalize(out)
def _wav_write(path, samples):
    frames = b"".join(
        struct.pack("<h", max(-32768, min(32767, int(s * 32767))))
        for s in samples)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(frames)
def _png_write(path, size, rows):
    def chunk(tag, data):
        blob = tag + data
        return (struct.pack(">I", len(data)) + blob
                + struct.pack(">I", zlib.crc32(blob) & 0xFFFFFFFF))

    raw = b"".join(b"\x00" + row for row in rows)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b""))
def _icon_rows(size=128, ss=3):
    n = size * ss
    half = n / 2.0
    rad = 30 * ss
    grid = {}

    def inside(x, y):
        qx = abs(x + 0.5 - half) - (half - rad)
        qy = abs(y + 0.5 - half) - (half - rad)
        if qx <= 0 or qy <= 0:
            return True
        return qx * qx + qy * qy <= rad * rad

    def stamp(cx, cy, r, col):
        r2 = r * r
        x0 = max(0, int(cx - r) - 1)
        x1 = min(n - 1, int(cx + r) + 1)
        y0 = max(0, int(cy - r) - 1)
        y1 = min(n - 1, int(cy + r) + 1)
        for yy in range(y0, y1 + 1):
            dy2 = (yy + 0.5 - cy) ** 2
            row = grid.setdefault(yy, {})
            for xx in range(x0, x1 + 1):
                dx = xx + 0.5 - cx
                if dx * dx + dy2 <= r2:
                    row[xx] = col

    steps = 110
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (97 - 72 * t) * ss
        y = (64 + 21 * math.sin(t * 4.4 + 0.5)) * ss
        frac = 1.0 - 0.45 * t
        col = (int(31 + (124 - 31) * frac),
               int(122 + (252 - 122) * frac),
               int(61 + (154 - 61) * frac))
        pts.append((x, y, (13.0 - 5.5 * t) * ss, col))
    for x, y, r, col in reversed(pts):
        stamp(x, y, r, col)
    hx, hy = pts[0][0], pts[0][1]
    hr = 16.5 * ss
    stamp(hx, hy, hr, (124, 252, 154))
    dxn, dyn = -72.0, 21 * 4.4 * math.cos(0.5)
    dl = math.hypot(dxn, dyn) or 1.0
    dxn, dyn = dxn / dl, dyn / dl
    pxn, pyn = -dyn, dxn
    for side in (-1, 1):
        ex = hx + dxn * hr * 0.30 + pxn * side * hr * 0.42
        ey = hy + dyn * hr * 0.30 + pyn * side * hr * 0.42
        stamp(ex, ey, 4.6 * ss, (245, 250, 245))
        stamp(ex + dxn * 2.2 * ss, ey + dyn * 2.2 * ss, 2.3 * ss, (16, 32, 22))
    stamp(100 * ss, 27 * ss, 6.2 * ss, (232, 58, 58))
    stamp(98.4 * ss, 25.4 * ss, 1.8 * ss, (255, 190, 190))
    stamp(103.5 * ss, 21.5 * ss, 2.2 * ss, (46, 160, 67))
    bg = (16, 32, 24)
    rows = []
    for oy in range(size):
        row = bytearray()
        for ox in range(size):
            rs = gs = bs = a = 0
            for yy in range(oy * ss, (oy + 1) * ss):
                grow = grid.get(yy)
                for xx in range(ox * ss, (ox + 1) * ss):
                    if not inside(xx, yy):
                        continue
                    a += 1
                    col = grow.get(xx) if grow else None
                    if col is None:
                        col = bg
                    rs += col[0]
                    gs += col[1]
                    bs += col[2]
            if a:
                row += bytes((rs // a, gs // a, bs // a, 255))
            else:
                row += bytes((0, 0, 0, 0))
        rows.append(bytes(row))
    return rows
def _make_icon(path):
    _png_write(path, 128, _icon_rows())
def _music_needs_build():
    try:
        marker = ASSETS_DIR / ".version"
        if not marker.exists() or marker.read_text().strip() != ASSET_VERSION:
            return True
    except OSError:
        return True
    return any(not _music_file(tr).exists() for tr in MUSIC_IDS)
def _build_music():
    for tr, maker in (("classic", _make_music), ("retro", _make_music_retro),
                      ("chiptune", _make_music_chiptune),
                      ("ambient", _make_music_ambient),
                      ("funk", _make_music_funk),
                      ("arcade", _make_music_arcade)):
        p = _music_file(tr)
        if not p.exists():
            _wav_write(p, maker())
    try:
        (ASSETS_DIR / ".version").write_text(ASSET_VERSION)
    except OSError:
        pass
def _safe_build_music():
    try:
        _build_music()
    except Exception:
        pass
def ensure_assets():
    try:
        SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        icon = IMAGES_DIR / "icon.png"
        if not icon.exists():
            _make_icon(icon)
        for name in SFX_NAMES:
            p = SOUNDS_DIR / f"{name}.wav"
            if not p.exists():
                _wav_write(p, _make_sfx(name))
    except OSError:
        pass
    if _music_needs_build():
        threading.Thread(target=_safe_build_music, daemon=True).start()
def _vol_step(save, key, default):
    # шаг громкости 0..10 (0 = тишина: беззвучный режим или громкость 0)
    if save.get("mute", False):
        return 0
    try:
        v = int(save.get(key, default))
    except (TypeError, ValueError):
        v = default
    v = max(0, min(100, v))
    if v <= 0:
        return 0
    # любое nonzero значение остаётся слышимым (шаг 1..10)
    return max(1, (v + 5) // VOL_STEPS)
def _scaled_copy(src, dst, step):
    """Копия wav с громкостью step/10 (кэшируется на диске)."""
    if dst.exists():
        return True
    tmp = dst.with_name(dst.stem + ".tmp")
    try:
        with wave.open(str(src), "rb") as f:
            params = f.getparams()
            frames = f.readframes(f.getnframes())
        k = step / float(VOL_STEPS)
        samples = array.array("h")
        samples.frombytes(frames)
        for i in range(len(samples)):
            s = int(samples[i] * k)
            if s > 32767:
                s = 32767
            elif s < -32768:
                s = -32768
            samples[i] = s
        with wave.open(str(tmp), "wb") as f:
            f.setparams(params)
            f.writeframes(samples.tobytes())
        tmp.replace(dst)
        return True
    except Exception:
        try:
            tmp.unlink()
        except OSError:
            pass
        return False
class SoundManager:
    def __init__(self, save=None):
        self.save = save if save is not None else {}
        self._proc = deque()
        self._sfx_aliases = deque()
        self._sfx_n = 0
        self._music_proc = None
        self._music_thread = None
        self._music_watchdog = None
        self._music_waiter = None
        self._music_on = False
        self._music_want = False
        self._music_step_cur = VOL_STEPS
        self._building = set()
        self._winsound = None
        self._winmm = None
        self._backend = None
        if sys.platform == "win32":
            try:
                import winsound
                self._winsound = winsound
                self._backend = "winsound"
            except Exception:
                self._backend = None
            return
        for cand in ("afplay", "aplay", "paplay"):
            if shutil.which(cand):
                self._backend = cand
                break

    # ---------- громкость ----------
    def _sfx_step(self):
        if not self.save.get("sound", True):
            return 0
        return _vol_step(self.save, "sound_volume", 80)

    def _music_step(self):
        if not self.save.get("music", True):
            return 0
        return _vol_step(self.save, "music_volume", 70)

    def _variant(self, path, step):
        # путь к wav с громкостью step/10; при отсутствии создаётся на месте
        if step >= VOL_STEPS:
            return path
        dst = path.with_name(f"{path.stem}_v{step}.wav")
        if dst.exists():
            return dst
        return path if _scaled_copy(path, dst, step) else None

    # ---------- звуки ----------
    def play(self, name):
        step = self._sfx_step()
        if step <= 0 or not self._backend:
            return
        path = SOUNDS_DIR / f"{name}.wav"
        if not path.exists():
            return
        if step < VOL_STEPS:
            path = self._variant(path, step)
            if path is None:
                return
        try:
            if self._backend == "winsound":
                # winsound.PlaySound ОДНОКАНАЛЬНЫЙ: каждый новый звук обрывает
                # предыдущий — из-за этого звуки «ломались» при быстрых
                # переключениях. Играем через MCI с уникальными alias —
                # до 6 звуков одновременно (полифония).
                if not self._mci_sfx(path):
                    w = self._winsound
                    w.PlaySound(str(path),
                                w.SND_FILENAME | w.SND_ASYNC
                                | w.SND_NODEFAULT)
            else:
                self._prune()
                proc = subprocess.Popen(
                    [self._backend, str(path)], stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
                self._proc.append(proc)
        except Exception:
            pass

    def _prune(self):
        while self._proc and self._proc[0].poll() is not None:
            self._proc.popleft()
        while len(self._proc) > 8:
            old = self._proc.popleft()
            try:
                old.terminate()
            except Exception:
                pass

    # ---------- полифоничные SFX на Windows (MCI, alias на каждый звук) ----------
    def _mci_sfx(self, path):
        """Играет SFX через отдельный MCI-alias. Возвращает False, если MCI
        недоступен (тогда вызывающий код откатывается на winsound)."""
        if self._winmm is None and sys.platform != "win32":
            return False
        self._sfx_n += 1
        alias = f"snakeysfx{self._sfx_n}"
        code, _ = self._mci(f'open "{path}" type waveaudio alias {alias}')
        if code != 0:
            return False
        self._sfx_aliases.append(alias)
        # лимит полифонии: самые старые звуки закрываем (они уже отыграли)
        while len(self._sfx_aliases) > 6:
            old = self._sfx_aliases.popleft()
            self._mci(f"close {old}")
        self._mci(f"play {alias} from 0")
        code, ln = self._mci(f"status {alias} length")
        try:
            ms = max(150, int(ln))
        except (TypeError, ValueError):
            ms = 800
        threading.Thread(target=self._mci_sfx_reap, args=(alias, ms),
                         daemon=True).start()
        return True

    def _mci_sfx_reap(self, alias, ms):
        # уборщик: закрывает alias после окончания звука, освобождая канал
        time.sleep(ms / 1000.0 + 0.15)
        self._mci(f"close {alias}")
        try:
            self._sfx_aliases.remove(alias)
        except ValueError:
            pass

    def _close_all_sfx(self):
        while self._sfx_aliases:
            self._mci(f"close {self._sfx_aliases.popleft()}")

    # ---------- музыка (Windows: MCI, цикл через watchdog) ----------
    def _mci(self, cmd):
        try:
            import ctypes
            if self._winmm is None:
                self._winmm = ctypes.windll.winmm
            buf = ctypes.create_unicode_buffer(128)
            code = self._winmm.mciSendStringW(cmd, buf, 128, 0)
            return code, buf.value
        except Exception:
            return 1, ""

    def _mci_start(self, path):
        # ВАЖНО: у waveaudio НЕТ флага "repeat" — команда с ним падает и
        # музыка вообще не включалась. Цикл обеспечивает _mci_watchdog.
        self._mci('close snakeymusic')
        code, _ = self._mci(f'open "{path}" type waveaudio alias snakeymusic')
        if code != 0:
            return False
        self._mci("play snakeymusic from 0")
        code, mode = self._mci("status snakeymusic mode")
        return code == 0 and mode == "playing"

    def _mci_watchdog(self):
        # держит трек цикличным: как только mode == "stopped" — играем сначала
        while self._music_on:
            time.sleep(0.25)
            if not self._music_on:
                break
            code, mode = self._mci("status snakeymusic mode")
            path = self._music_path
            if code != 0:
                if path is not None and Path(path).exists():
                    self._mci_start(path)
            elif mode == "stopped":
                self._mci("play snakeymusic from 0")
            elif mode not in ("playing", "paused"):
                if path is not None and Path(path).exists():
                    self._mci_start(path)

    # ---------- музыка (Linux/macOS: внешний плеер по кругу) ----------
    def _music_loop(self, path):
        while self._music_on:
            try:
                proc = subprocess.Popen(
                    [self._backend, str(path)], stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
            except OSError:
                return
            self._music_proc = proc
            while self._music_on and proc.poll() is None:
                time.sleep(0.2)
            if self._music_on and proc.poll() is None:
                try:
                    proc.terminate()
                except Exception:
                    pass

    # ---------- управление музыкой ----------
    def _music_play_path(self, step):
        track = self.save.get("music_track", "classic")
        for cand in (track, "classic"):
            base = _music_file(cand)
            if not base.exists():
                continue
            if step >= VOL_STEPS:
                return base
            dst = base.with_name(f"music_{cand}_v{step}.wav")
            if dst.exists():
                return dst
            if cand not in self._building:
                self._building.add(cand)
                threading.Thread(target=self._build_variant_worker,
                                 args=(base, dst, step, cand),
                                 daemon=True).start()
            return None
        return None

    def _build_variant_worker(self, base, dst, step, cand):
        try:
            _scaled_copy(base, dst, step)
        finally:
            self._building.discard(cand)

    def _music_wait_loop(self):
        # музыкальные wav генерируются в фоне при первом запуске —
        # ждём их появления и стартуем автоматически (раньше музыка
        # просто не включалась, если файл ещё не был готов)
        for _ in range(600):
            if not self._music_want:
                self._music_waiter = None
                return
            step = self._music_step()
            if step <= 0:
                self._music_waiter = None
                return
            path = self._music_play_path(step)
            if path is not None:
                self._music_waiter = None
                self._begin_music(path, step)
                return
            time.sleep(0.5)
        self._music_waiter = None

    def _begin_music(self, path, step):
        self._music_path = str(path)
        self._music_step_cur = step
        self._music_on = True
        if self._backend == "winsound":
            if self._mci_start(str(path)):
                self._music_watchdog = threading.Thread(
                    target=self._mci_watchdog, daemon=True)
                self._music_watchdog.start()
            else:
                self._music_on = False
        elif self._backend:
            self._music_thread = threading.Thread(
                target=self._music_loop, args=(str(path),), daemon=True)
            self._music_thread.start()
        else:
            self._music_on = False

    def start_music(self):
        self._music_want = True
        if self._music_on:
            return
        if not self.save.get("music", True) or self.save.get("mute", False):
            return
        step = self._music_step()
        if step <= 0:
            return
        path = self._music_play_path(step)
        if path is None:
            if self._music_waiter is None:
                self._music_waiter = threading.Thread(
                    target=self._music_wait_loop, daemon=True)
                self._music_waiter.start()
            return
        self._begin_music(path, step)

    def _halt_playback(self):
        # остановить воспроизведение, но сохранить желание слушать музыку
        self._music_on = False
        self._close_all_sfx()
        if self._winmm is not None:
            try:
                self._winmm.mciSendStringW("stop snakeymusic", None, 0, 0)
                self._winmm.mciSendStringW("close snakeymusic", None, 0, 0)
            except Exception:
                pass
            self._winmm = None
        proc = self._music_proc
        self._music_proc = None
        if proc is not None:
            try:
                proc.terminate()
            except Exception:
                pass

    def stop_music(self):
        self._music_want = False
        self._halt_playback()
        self._music_path = None

    def set_music(self, on):
        if on:
            self.start_music()
        else:
            self.stop_music()

    def set_mute(self, on):
        if on:
            self.stop_music()
        else:
            self.start_music()

    def restart_music(self):
        self.stop_music()
        self.start_music()

    def apply_music_volume(self):
        # применяется без лишних перезапусков: смена шага громкости
        # требует другой wav-вариант
        if not self._music_want:
            return
        step = self._music_step()
        if step <= 0:
            self._halt_playback()
            return
        if self._music_on and step == self._music_step_cur:
            return
        self._halt_playback()
        self.start_music()

SOUND = None
def sfx(name):
    if SOUND is not None:
        SOUND.play(name)


def set_sound(mgr):
    global SOUND
    SOUND = mgr