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
        self.frames = {}
        for cls in (MenuScreen, MiniScreen, AchScreen, ShopScreen,
                    SettingsScreen, GameScreen):
            frame = cls(self.container, self)
            self.frames[cls.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.bind("<KeyPress>", self._on_key)
        self.bind_all("<MouseWheel>", self._on_wheel)
        self.bind_all("<Button-4>", self._on_wheel)
        self.bind_all("<Button-5>", self._on_wheel)
        self.show("MenuScreen")
        self.sound.start_music()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def show(self, name):
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

    def _on_key(self, event):
        self.frames[self.current].on_key(event)

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