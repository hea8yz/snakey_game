import shutil
import struct
import subprocess
import sys
import threading
import time
import wave
import zlib
import math
from collections import deque
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parent / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
IMAGES_DIR = ASSETS_DIR / "images"
SFX_NAMES = ("click", "eat", "death", "coin", "levelup", "win", "lose")
SAMPLE_RATE = 22050
ASSET_VERSION = "2"
MUSIC_IDS = ("classic", "retro")


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
    for tr, maker in (("classic", _make_music), ("retro", _make_music_retro)):
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
class SoundManager:
    def __init__(self, save=None):
        self.save = save if save is not None else {}
        self._proc = deque()
        self._music_proc = None
        self._music_path = None
        self._music_thread = None
        self._music_watchdog = None
        self._music_on = False
        self._winmm = None
        self._winsound = None
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

    def play(self, name):
        if not self.save.get("sound", True) or not self._backend:
            return
        path = SOUNDS_DIR / f"{name}.wav"
        if not path.exists():
            return
        try:
            if self._backend == "winsound":
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
        self._mci('close snakeymusic')
        code, _ = self._mci(f'open "{path}" type waveaudio alias snakeymusic')
        if code != 0:
            return False
        self._mci("play snakeymusic from 0 repeat")
        code, mode = self._mci("status snakeymusic mode")
        return code == 0 and mode == "playing"

    def _mci_watchdog(self):
        while self._music_on:
            time.sleep(5.0)
            if not self._music_on:
                break
            code, mode = self._mci("status snakeymusic mode")
            if code != 0 or mode not in ("playing", "paused"):
                path = self._music_path
                if path is not None and Path(path).exists():
                    self._mci_start(path)

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

    def _resolve_music_path(self):
        track = self.save.get("music_track", "classic")
        for cand in (track, "classic"):
            p = _music_file(cand)
            if p.exists():
                return p
        legacy = SOUNDS_DIR / "bg_music.wav"
        return legacy if legacy.exists() else None

    def start_music(self):
        if self._music_on or not self.save.get("music", True):
            return
        path = self._resolve_music_path()
        if path is None:
            return
        self._music_path = str(path)
        self._music_on = True
        if sys.platform == "win32":
            ok = self._mci_start(str(path))
            if ok:
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

    def stop_music(self):
        self._music_on = False
        self._music_path = None
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

    def set_music(self, on):
        if on:
            self._music_on = False
            self.start_music()
        else:
            self.stop_music()

    def restart_music(self):
        self.stop_music()
        time.sleep(0.05)
        self.start_music()
SOUND = None
def sfx(name):
    if SOUND is not None:
        SOUND.play(name)


def set_sound(mgr):
    global SOUND
    SOUND = mgr