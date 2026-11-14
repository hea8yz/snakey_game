import tkinter as tk
import tkinter.font as tkfont


from snakey_achievements import AchScreen
from snakey_assets import IMAGES_DIR, SoundManager, ensure_assets, set_sound
from snakey_content import BG, WINDOW_SIZES
from snakey_game import GameScreen
from snakey_menu import MenuScreen
from snakey_minis import MiniScreen
from snakey_save import load_save, save_save
from snakey_settings import SettingsScreen
from snakey_shop import ShopScreen
from snakey_widgets import refocus_app

import snakey_achievements as _achievements
import snakey_assets as _assets
import snakey_content as _content
import snakey_drawing as _drawing
import snakey_game as _game
import snakey_menu as _menu
import snakey_minigames as _minigames
import snakey_minis as _minis
import snakey_save as _save
import snakey_settings as _settings
import snakey_shop as _shop
import snakey_utils as _utils
import snakey_widgets as _widgets

for _m in (_content, _save, _utils, _drawing, _assets, _widgets, _shop,
           _settings, _minigames, _minis, _achievements, _menu, _game):
    globals().update({n: v for n, v in vars(_m).items()
                      if not n.startswith("_")})



# ---------------- Автообновление ----------------
import os as _os
import sys as _sys
import threading as _threading
import urllib.request as _urllib_request

REPO_RAW = "https://raw.githubusercontent.com/hea8yz/snakey_game/main/"


def _local_version():
    # в exe-сборке VERSION лежит рядом с exe; при запуске из исходников — рядом с кодом
    bases = []
    if getattr(_sys, "frozen", False):
        bases.append(_os.path.dirname(_os.path.abspath(_sys.executable)))
    bases.append(_os.path.dirname(_os.path.abspath(__file__)))
    for base in bases:
        try:
            with open(_os.path.join(base, "VERSION"), encoding="utf-8") as f:
                v = f.read().strip()
                if v:
                    return v
        except Exception:
            pass
    return "1.0"


def _version_tuple(v):
    try:
        return tuple(int(x) for x in v.replace("v", "").split("."))
    except Exception:
        return (0,)


def _fetch_text(url, timeout=3):
    with _urllib_request.urlopen(url, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def _show_update_prompt(app, new_version):
    """Всплывающее окно «пора обновиться» с кнопками «Позже» и «Обновить».

    «Обновить» просто закрывает игру — файлы сами по себе не меняются.
    Обновляет папку игры отдельный скрипт update.bat (скачивает из репозитория
    только изменённые файлы и добавляет новые)."""
    try:
        win = tk.Toplevel(app)
        win.title("SNAKEY — обновление")
        win.configure(bg="#101820")
        win.resizable(False, False)
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass
        fam = getattr(app, "font_ui", "Helvetica")
        tk.Label(win, text="✨  Доступна новая версия " + new_version + "!",
                 bg="#101820", fg="#3fff9e",
                 font=(fam, 13, "bold")).pack(padx=30, pady=(20, 4))
        tk.Label(win, text="У тебя версия " + _local_version()
                           + " — пора обновить игру!",
                 bg="#101820", fg="#cdd9e5",
                 font=(fam, 10)).pack(padx=30, pady=(0, 10))
        tk.Label(win, text="«Обновить» закроет игру — файлы сами не изменятся.\n"
                           "Затем запусти update.bat из папки игры: он скачает\n"
                           "новые файлы из репозитория и добавит их в папку.",
                 bg="#101820", fg="#8b949e", justify="center",
                 font=(fam, 9)).pack(padx=30, pady=(0, 14))
        btns = tk.Frame(win, bg="#101820")
        btns.pack(pady=(0, 18))

        def later():
            win.destroy()
            refocus_app(app)

        def do_update():
            # игра просто закрывается; обновление файлов делает update.bat
            try:
                app.sound.stop_music()
            except Exception:
                pass
            app.destroy()

        tk.Button(btns, text="Позже", command=later,
                  bg="#30363d", fg="#cdd9e5", activebackground="#3d444d",
                  activeforeground="#ffffff", relief="flat",
                  font=(fam, 10, "bold"), padx=16, pady=4,
                  cursor="hand2").pack(side="left", padx=6)
        tk.Button(btns, text="⬇  Обновить", command=do_update,
                  bg="#1f6feb", fg="#ffffff", activebackground="#388bfd",
                  activeforeground="#ffffff", relief="flat",
                  font=(fam, 10, "bold"), padx=16, pady=4,
                  cursor="hand2").pack(side="left", padx=6)

        # центрируем поверх основного окна (как все попапы игры)
        win.update_idletasks()
        w = max(win.winfo_reqwidth(), 380)
        h = win.winfo_reqheight()
        try:
            px, py = app.winfo_rootx(), app.winfo_rooty()
            pw, ph = app.winfo_width(), app.winfo_height()
            if pw > 1 and ph > 1:
                x = px + max(0, (pw - w) // 2)
                y = py + max(0, (ph - h) // 2)
            else:
                raise ValueError
        except Exception:
            x = (app.winfo_screenwidth() - w) // 2
            y = (app.winfo_screenheight() - h) // 2
        win.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
        win.lift()
        win.focus_force()
    except Exception:
        pass


def start_autoupdate(app):
    """Фоновая проверка новой версии на GitHub (не блокирует GUI)."""
    try:
        if not app.save.get("autoupdate", True):
            return
    except Exception:
        return
    local = _local_version()

    def worker():
        try:
            remote = _fetch_text(REPO_RAW + "VERSION", timeout=3).strip()
            if not remote or _version_tuple(remote) <= _version_tuple(local):
                return
        except Exception:
            return
        try:
            app.after(0, lambda: _show_update_prompt(app, remote))
        except Exception:
            pass

    _threading.Thread(target=worker, name="snakey-autoupdate",
                      daemon=True).start()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SNAKEY")
        self.configure(bg=BG)
        self.resizable(False, False)
        families = set(tkfont.families())

        def pick(options, fallback):
            return next((f for f in options if f in families), fallback)

        self.font_title = pick(("Segoe UI Black", "Arial Rounded MT Bold",
                                "Arial Black", "Impact"), "Helvetica")
        self.font_ui = pick(("Segoe UI", "Helvetica Neue", "DejaVu Sans"),
                            "Helvetica")

        self.save = load_save()
        self.sound = SoundManager(self.save)
        set_sound(self.sound)
        self._set_icon()
        self.next_mode = None
        self.next_diff = None
        self.current = "MenuScreen"
        self.win_size = self.save.get("window_size", "medium")
        if self.win_size not in WINDOW_SIZES:
            self.win_size = "medium"
        self._apply_size()

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.frame_classes = {cls.__name__: cls for cls in
                              (MenuScreen, MiniScreen, AchScreen, ShopScreen,
                               SettingsScreen, GameScreen)}
        self.frames = {}
        # быстрый запуск: при старте строим только меню, остальные экраны
        # достраиваются в фоне сразу после открытия окна
        self._make_frame("MenuScreen")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.bind("<KeyPress>", self._on_key)
        # клик по главному окну всегда возвращает клавиатурный фокус —
        # страховка от "мёртвого" управления
        self.bind("<Button-1>", self._restore_focus, add="+")
        self.after(400, self._focus_watch)
        self.bind_all("<MouseWheel>", self._on_wheel)
        self.bind_all("<Button-4>", self._on_wheel)
        self.bind_all("<Button-5>", self._on_wheel)
        self.show("MenuScreen")
        self.after_idle(self._prebuild_rest)
        self.sound.start_music()
        start_autoupdate(self)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _make_frame(self, name):
        frame = self.frames.get(name)
        if frame is not None:
            return frame
        cls = self.frame_classes.get(name)
        if cls is None:
            return None
        frame = cls(self.container, self)
        self.frames[name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        # новый grid-виджет отображается ПОВЕРХ предыдущих в той же ячейке —
        # опускаем его вниз, чтобы он не закрыл текущий экран
        frame.lower()
        try:
            self.frames[self.current].tkraise()
        except Exception:
            pass
        return frame

    def _prebuild_rest(self, i=0):
        # достраиваем остальные экраны по одному с паузой — окно не фризит
        order = ("MiniScreen", "SettingsScreen", "ShopScreen", "AchScreen",
                 "GameScreen")
        if i >= len(order):
            # страховка: текущий экран всегда поверх всех
            try:
                self.frames[self.current].tkraise()
            except Exception:
                pass
            return
        try:
            self._make_frame(order[i])
            self.after(40, lambda: self._prebuild_rest(i + 1))
        except Exception:
            pass

    def show(self, name):
        self._make_frame(name)
        self.current = name
        for name_, frame in self.frames.items():
            if name_ != name:
                frame.on_hide()
        self.frames[name].on_show()
        self.frames[name].tkraise()

    def _apply_size(self):
        w, h = WINDOW_SIZES[self.win_size]
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{max(0, (sw - w) // 2)}"
                      f"+{max(0, (sh - h) // 2 - 20)}")

    def set_window_size(self, key):
        if key not in WINDOW_SIZES:
            return
        self.win_size = key
        self.save["window_size"] = key
        self.commit()
        self._apply_size()

    def _restore_focus(self, _event=None):
        try:
            self.focus_set()
        except Exception:
            pass

    def _focus_watch(self):
        # если попап унёс фокус и уничтожился, а курсор внутри игры —
        # моментально возвращаем управление без перезапуска
        try:
            if self.winfo_exists() and self.focus_displayof() is None:
                inside = self.winfo_containing(self.winfo_pointerx(),
                                               self.winfo_pointery())
                if inside is not None:
                    self.focus_force()
        except Exception:
            pass
        try:
            self.after(400, self._focus_watch)
        except Exception:
            pass

    def _on_key(self, event):
        frame = self.frames.get(self.current)
        if frame is not None:
            frame.on_key(event)

    def _on_wheel(self, event):
        frame = self.frames.get(self.current)
        if frame is not None:
            frame.on_wheel(event)

    def commit(self):
        save_save(self.save)

    def _set_icon(self):
        self._icon_img = None
        try:
            p = IMAGES_DIR / "icon.png"
            if p.exists() and hasattr(tk, "PhotoImage"):
                self._icon_img = tk.PhotoImage(file=str(p))
                self.iconphoto(True, self._icon_img)
        except Exception:
            self._icon_img = None

    def _on_close(self):
        try:
            self.sound.stop_music()
        except Exception:
            pass
        self.destroy()
if __name__ == "__main__":
    ensure_assets()
    App().mainloop()