import colorsys
import json
import math
import random
import shutil
import struct
import subprocess
import sys
import threading
import time
import wave
import zlib
import tkinter as tk
import tkinter.font as tkfont
from collections import deque
from pathlib import Path

CELL = 24
COLS = 24
ROWS = 18
SAVE_FILE = Path.home() / ".snakey_save.json"
VERSION = "0.8"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
IMAGES_DIR = ASSETS_DIR / "images"

CHANGELOG = [
    ("0.8", [
        "+20 новых цветов для змейки, включая градиентные скины",
        "+15 новых видов еды с личной статистикой и одинаковым размером",
        "+15 новых фонов, включая красивые градиентные",
        "+25 новых аксессуаров, многие — с анимацией",
        "Новое меню: переливающийся градиент, анимации, кнопки не сдвигаются при смене размера экрана",
        "Update log в едином стиле: жирные плюсики у каждого изменения",
        "Настройки, магазин, мини-игры и достижения — единый стиль с градиентным фоном",
        "Полоса уровня: градиентная, выше размером и переливается",
        "Магазин: кнопка (i) у каждого товара — множители, шансы и статистика по наведению",
        "Игра: градиентный фон поля, анимация появления еды, кольца при поедании",
        "Змейка стала красивее: контур сегментов и плавные градиенты",
        "Режим для слабых ПК отключает все новые анимации и упрощает графику по максимуму",
        "Оптимизация: кэши цветов, пулы объектов, минимум перерисовок",
        "Иконка игры — минималистичная зелёная змейка (assets/images/icon.png)",
        "Звуки без авторских прав: фоновая музыка, клики, поедание, смерть, победа, покупка, новый уровень (assets/sounds)",
        "В настройках можно включить/выключить звуки и музыку по отдельности",
        "Всплывающие окна (уровень, достижения, update log) — без рамки ОС: своя шапка, перетаскивание, закрытие ✕ и Esc",
    ]),
    ("0.7", [
        "Исправлен экран настроек: теперь он полностью прокручиваемый — все кнопки доступны",
        "Новый режим для слабых устройств: упрощённая графика (фон, модельки, частицы) без изменения механики — галочка в настройках",
        "Глобальная оптимизация: кэширование цветов, пул частиц, меньше перерисовок — игра летает даже на слабых ПК",
        "Исправлено воскресение (C): теперь работает на любой раскладке клавиатуры",
        "Множество мелких исправлений и ускорение отрисовки по всему коду",
        "Исправлено открытие настроек, если выбран скин «Радуга» — теперь превью показывает настоящую радугу",
        "Новый баланс монет: зарабатывать их сложнее в игре, мини-играх и достижениях",
        "Ускоряющаяся кривая уровней: чем выше уровень, тем больше нужно EXP",
        "Перебалансированы множители монет и опыта, редкие фрукты выпадают реже",
        "Окно стало больше, а в настройках появился выбор размера экрана",
        "Update log и все экраны вмещают весь текст: длинные строки переносятся",
        "Исправлены все замечания PyCharm: типы, статические методы, инициализация атрибутов",
    ]),
    ("0.6", [
        "Три мини-игры с наградами: Сбор яблок, Попробуй запомнить!, Яблочный сбор",
        "Сбор яблок — итоговая версия: 4 сложности, −15 секунд за шаг (90/75/60/45)",
        "Попробуй запомнить!: найди исходный цвет среди 8 оттенков — 15 монет за победу",
        "Яблочный сбор: зона сбора, фикс-размер змейки, +20 монет за яблоко, 60 секунд",
        "Сложности мини-игр открываются по уровню: 1 / 5 / 10 / 20 — как в классике",
        "Монеты за мини-игры умножаются на сложность и бонус фона",
        "33 достижения для новичков и профи: мини-игры, монеты, очки, уровень, скины",
        "Новая статистика: рекорды каждой мини-игры, победы, доставленные яблоки",
        "Обновлены все экраны: смерть, настройки, update log, окна наград",
        "В классике появляется максимум один дополнительный фрукт за раз",
        "Окно игры открывается по центру экрана",
    ]),
    ("0.5", [
        "Новое оформление: скруглённые кнопки и минимализм во всех меню",
        "Система уровней и EXP: +1 EXP за очко, множитель опыта выше монетного",
        "Сложности по уровням: средняя — 5, сложная — 10, экстремальная — 20",
        "Еда и фоны с множителями требуют уровень: выше множитель — выше уровень",
        "Аксессуары для головы: шапка Деда Мороза, корона, нимб, пропеллер и другие",
        "Воскрешение после смерти за монеты (клавиша C) — ровно 1 раз за игру",
        "Красивое окно празднования при повышении уровня",
    ]),
    ("0.4", [
        "Экстремальная сложность: змея разбивается об границы поля!",
        "Экстремальная: ещё выше скорость и непредсказуемые стены",
        "Ядовитые фрукты (тёмные) на экстремальной — не съедай их!",
        "Множитель монет за фон: чем дороже фон, тем выше ставка",
        "Множитель экстремальной сложности повышен до ×2.5",
        "Новый товар: 8 цветов, 3 фона (Пустыня, Неон, Космос), 3 фрукта",
        "Оптимизация: статичное поле рисуется один раз, без микрофризов",
        "Анимированное меню с эффектами и новая отрисовка змейки",
    ]),
    ("0.3", [
        "4 сложности: Обычная, Средняя, Сложная (стены смертельны), Экстремальная (препятствия)",
        "Монеты умножаются по сложности: ×1.0 / ×1.2 / ×1.5 / ×2.0",
        "Фоны: Ночь, Поляна, Лес, Зима",
        "Новая еда: вишня, банан, виноград, золотое яблоко — с разными шансами и очками",
        "6 новых цветов змейки (всего 17)",
        "Улучшенная графика: частицы, тени, свечение еды, всплывающие очки, язычок",
    ]),
    ("0.2", [
        "Главное меню с логотипом SNAKEY",
        "Магазин цветов за монеты",
        "Монеты за очки: +1 за очко и +5 за каждые 10",
        "Настройки цвета и сложности",
    ]),
    ("0.1", [
        "Первый релиз: змейка на tkinter",
        "Счёт, рекорд, ускорение, пауза, рестарт",
    ]),
]

BG = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
ACCENT = "#3fb950"
ACCENT_BRIGHT = "#7ee787"
ACCENT_DARK = "#238636"
TEXT = "#e6edf3"
DIM = "#8b949e"
GOLD = "#e3b341"
RED = "#ff5c5c"
WARN = "#f0883e"
POISON = "#3b1f5e"
BLUE = "#58a6ff"
LOCKED_BG = "#1a2029"

COLORS = [
    {"name": "Классический", "id": "#3fb950", "price": 0},
    {"name": "Стальной", "id": "#8b949e", "price": 20},
    {"name": "Алый", "id": "#ff5c5c", "price": 40},
    {"name": "Лайм", "id": "#a4f24a", "price": 40},
    {"name": "Оранжевый", "id": "#ffa657", "price": 40},
    {"name": "Коралл", "id": "#ff8a5c", "price": 60},
    {"name": "Лазурный", "id": "#58a6ff", "price": 60},
    {"name": "Лавандовый", "id": "#d2a8ff", "price": 60},
    {"name": "Медный", "id": "#c98a5a", "price": 60},
    {"name": "Бирюзовый", "id": "#39d2c0", "price": 80},
    {"name": "Розовый", "id": "#f778ba", "price": 80},
    {"name": "Фуксия", "id": "#e04fd1", "price": 80},
    {"name": "Белый", "id": "#f0f6fc", "price": 100},
    {"name": "Индиго", "id": "#7a5cff", "price": 100},
    {"name": "Золотой", "id": "#e3b341", "price": 120},
    {"name": "Неон", "id": "#00e5ff", "price": 120},
    {"name": "Радуга", "id": "rainbow", "price": 150},
    {"name": "Графит", "id": "#4d5b66", "price": 40},
    {"name": "Персик", "id": "#ffb38a", "price": 60},
    {"name": "Сирень", "id": "#b39cff", "price": 60},
    {"name": "Лимонный", "id": "#e8ff47", "price": 60},
    {"name": "Вишнёвый", "id": "#d6336c", "price": 80},
    {"name": "Глубокий океан", "id": "#0e7490", "price": 80},
    {"name": "Магма", "id": "#ff4f30", "price": 100},
    {"name": "Хром", "id": "#cdd9e5", "price": 100},
    {"name": "Мятный", "id": "#7fe8c3", "price": 60},
    {"name": "Ультрамарин", "id": "#4655ff", "price": 100},
    {"name": "Песочный", "id": "#e8d5a3", "price": 40},
    {"name": "Пурпурный", "id": "#9d3ff2", "price": 100},
    {"name": "Аквамарин", "id": "#5ce8d5", "price": 80},
    {"name": "Фисташковый", "id": "#a8d878", "price": 60},
    {"name": "Лососевый", "id": "#ff8f6b", "price": 60},
    {"name": "Океанический", "id": "#2f9dd0", "price": 80},
    {"name": "Васильковый", "id": "#6b8cff", "price": 80},
    {"name": "Малиновый лёд", "id": "#ff6b9d", "price": 80},
    {"name": "Изумруд", "id": "#2ecc71", "price": 100},
    {"name": "Сапфир", "id": "#2456c9", "price": 100},
    {"name": "Аметист", "id": "#8e5cd9", "price": 100},
    {"name": "Медовый", "id": "#ffb84d", "price": 100},
    {"name": "Тёмная бирюза", "id": "#12857a", "price": 120},
    {"name": "Кровавый закат", "id": "#c92a3a", "price": 120},
    {"name": "Молочный", "id": "#f5efe0", "price": 120},
    {"name": "Угольный", "id": "#2a2f36", "price": 140},
    {"name": "Электрик", "id": "#33ccff", "price": 140},
    {"name": "Закат", "id": "grad_sunset", "price": 180},
    {"name": "Морская волна", "id": "grad_ocean", "price": 180},
    {"name": "Токсичный", "id": "grad_toxic", "price": 200},
    {"name": "Конфетта", "id": "grad_candy", "price": 200},
    {"name": "Золотой перелив", "id": "grad_gold", "price": 220},
    {"name": "Аврора", "id": "grad_aurora", "price": 240},
]

GRADIENTS = {
    "grad_sunset": ("#ff5c5c", "#ffa657"),
    "grad_ocean": ("#58a6ff", "#39d2c0"),
    "grad_toxic": ("#a4f24a", "#00e5ff"),
    "grad_candy": ("#f778ba", "#d2a8ff"),
    "grad_gold": ("#e3b341", "#fff3c4"),
    "grad_aurora": ("#3fff9e", "#58a6ff"),
}

THEMES = [
    {"name": "Ночь", "id": "night", "price": 0, "bonus": 1.0, "level": 1, "decor": "stars",
     "grid_a": "#0f1418", "grid_b": "#121a22", "border": "#30363d"},
    {"name": "Поляна", "id": "meadow", "price": 60, "bonus": 1.1, "level": 3, "decor": "flowers",
     "grid_a": "#94c96b", "grid_b": "#9ed476", "border": "#5d8f3e"},
    {"name": "Лес", "id": "forest", "price": 80, "bonus": 1.15, "level": 5, "decor": "bushes",
     "grid_a": "#26392b", "grid_b": "#2c4131", "border": "#44604a"},
    {"name": "Зима", "id": "winter", "price": 100, "bonus": 1.2, "level": 7, "decor": "snow",
     "grid_a": "#dce7f0", "grid_b": "#e7f0f7", "border": "#9fb6c9"},
    {"name": "Пустыня", "id": "desert", "price": 140, "bonus": 1.25, "level": 9, "decor": "stones",
     "grid_a": "#d9b56a", "grid_b": "#e0bd76", "border": "#a8823f"},
    {"name": "Неон", "id": "neon", "price": 180, "bonus": 1.3, "level": 12, "decor": "glow",
     "grid_a": "#170f2e", "grid_b": "#1c1438", "border": "#7c3aed"},
    {"name": "Космос", "id": "space", "price": 250, "bonus": 1.5, "level": 16, "decor": "stars",
     "grid_a": "#05060f", "grid_b": "#0a0d1f", "border": "#3b4a6b"},
    {"name": "Сакура", "id": "sakura", "price": 160, "bonus": 1.35, "level": 11, "decor": "petals",
     "grid_a": "#f6dfe9", "grid_b": "#fbe9f1", "border": "#c98bb0"},
    {"name": "Океан", "id": "ocean", "price": 200, "bonus": 1.4, "level": 13, "decor": "bubbles",
     "grid_a": "#14507a", "grid_b": "#185a88", "border": "#3f8fc0"},
    {"name": "Осень", "id": "autumn", "price": 210, "bonus": 1.4, "level": 14, "decor": "leaves",
     "grid_a": "#a86f2e", "grid_b": "#b27a36", "border": "#7a4e1d"},
    {"name": "Лава", "id": "lava", "price": 220, "bonus": 1.45, "level": 15, "decor": "embers",
     "grid_a": "#260d0d", "grid_b": "#2f1111", "border": "#8a2f1d"},
    {"name": "Аврора", "id": "aurora", "price": 260, "bonus": 1.6, "level": 18, "decor": "aurora",
     "grid_a": "#07131a", "grid_b": "#0a1a24", "border": "#2f6b5e"},
    {"name": "Мята", "id": "mint", "price": 90, "bonus": 1.15, "level": 4, "decor": "bubbles",
     "grid_a": "#0e2a22", "grid_b": "#123329", "border": "#2f6b5e"},
    {"name": "Кофе", "id": "coffee", "price": 120, "bonus": 1.2, "level": 6, "decor": "stones",
     "grid_a": "#2a1f16", "grid_b": "#31251a", "border": "#6b4e33"},
    {"name": "Роза", "id": "rose", "price": 150, "bonus": 1.25, "level": 8, "decor": "petals",
     "grid_a": "#2e1420", "grid_b": "#361826", "border": "#a34768"},
    {"name": "Изумруд", "id": "emerald", "price": 190, "bonus": 1.35, "level": 12, "decor": "bushes",
     "grad": ("#04170e", "#0c3a24"), "grid_a": "#04170e", "grid_b": "#0c3a24", "border": "#1d7a4a"},
    {"name": "Сапфир", "id": "sapphire", "price": 200, "bonus": 1.35, "level": 13, "decor": "stars",
     "grad": ("#040b1e", "#0c2450"), "grid_a": "#040b1e", "grid_b": "#0c2450", "border": "#2f5fc0"},
    {"name": "Закат", "id": "sunset_t", "price": 210, "bonus": 1.4, "level": 14, "decor": "embers",
     "grad": ("#1c0a20", "#4a1428"), "grid_a": "#1c0a20", "grid_b": "#4a1428", "border": "#a34768"},
    {"name": "Тропики", "id": "tropics", "price": 220, "bonus": 1.4, "level": 15, "decor": "flowers",
     "grad": ("#03221e", "#0a4a3a"), "grid_a": "#03221e", "grid_b": "#0a4a3a", "border": "#1d8a6b"},
    {"name": "Глубина", "id": "depth", "price": 230, "bonus": 1.45, "level": 16, "decor": "bubbles",
     "grad": ("#010614", "#062a4a"), "grid_a": "#010614", "grid_b": "#062a4a", "border": "#2f6b9e"},
    {"name": "Полночь", "id": "midnight", "price": 240, "bonus": 1.45, "level": 17, "decor": "stars",
     "grad": ("#050510", "#141433"), "grid_a": "#050510", "grid_b": "#141433", "border": "#3b3b6b"},
    {"name": "Неоновый город", "id": "neoncity", "price": 250, "bonus": 1.5, "level": 18, "decor": "glow",
     "grad": ("#0a0514", "#1f0a33"), "grid_a": "#0a0514", "grid_b": "#1f0a33", "border": "#c93ad6"},
    {"name": "Молочный туман", "id": "fog", "price": 260, "bonus": 1.5, "level": 19, "decor": "snow",
     "grad": ("#2a2f38", "#4a5462"), "grid_a": "#2a2f38", "grid_b": "#4a5462", "border": "#8b949e"},
    {"name": "Вишнёвый сад", "id": "cherryg", "price": 270, "bonus": 1.55, "level": 20, "decor": "petals",
     "grad": ("#1c0812", "#3d1024"), "grid_a": "#1c0812", "grid_b": "#3d1024", "border": "#c2417f"},
    {"name": "Стальной лёд", "id": "steelice", "price": 280, "bonus": 1.55, "level": 21, "decor": "snow",
     "grad": ("#0a1420", "#1c3a52"), "grid_a": "#0a1420", "grid_b": "#1c3a52", "border": "#5fa8d6"},
    {"name": "Золотой век", "id": "goldage", "price": 300, "bonus": 1.6, "level": 22, "decor": "embers",
     "grad": ("#140d02", "#3a2a05"), "grid_a": "#140d02", "grid_b": "#3a2a05", "border": "#b8860b"},
    {"name": "Полярная звезда", "id": "polaris", "price": 320, "bonus": 1.65, "level": 24, "decor": "aurora",
     "grad": ("#020810", "#0a2436"), "grid_a": "#020810", "grid_b": "#0a2436", "border": "#3fd0ff"},
]
THEME_BY_ID = {t["id"]: t for t in THEMES}

FOOD_ITEMS = [
    {"name": "Яблоко", "id": "apple", "price": 0, "value": 1, "chance": 1.0, "level": 1, "color": RED, "size": 1.0},
    {"name": "Вишня", "id": "cherry", "price": 30, "value": 2, "chance": 0.22, "level": 2, "color": "#ff4f7d", "size": 0.85},
    {"name": "Банан", "id": "banana", "price": 50, "value": 3, "chance": 0.16, "level": 3, "color": "#ffd33d", "size": 0.95},
    {"name": "Апельсин", "id": "orange", "price": 60, "value": 4, "chance": 0.12, "level": 4, "color": "#ff9f1c", "size": 0.95},
    {"name": "Малина", "id": "raspberry", "price": 60, "value": 4, "chance": 0.11, "level": 4, "color": "#e0356b", "size": 0.75},
    {"name": "Виноград", "id": "grape", "price": 70, "value": 5, "chance": 0.09, "level": 5, "color": "#a371f7", "size": 0.8},
    {"name": "Киви", "id": "kiwi", "price": 80, "value": 5, "chance": 0.08, "level": 6, "color": "#8ac24a", "size": 0.8},
    {"name": "Арбуз", "id": "melon", "price": 90, "value": 7, "chance": 0.06, "level": 7, "color": "#ff4f5e", "size": 1.05},
    {"name": "Манго", "id": "mango", "price": 110, "value": 8, "chance": 0.05, "level": 8, "color": "#ffb300", "size": 0.9},
    {"name": "Золотое яблоко", "id": "golden", "price": 120, "value": 10, "chance": 0.035, "level": 10, "color": GOLD, "size": 0.95},
    {"name": "Драконий фрукт", "id": "dragon", "price": 160, "value": 12, "chance": 0.025, "level": 12, "color": "#f04fd1", "size": 1.0},
    {"name": "Звезда", "id": "star", "price": 200, "value": 15, "chance": 0.02, "level": 14, "color": "#ffe14d", "size": 0.85},
    {"name": "Алмаз", "id": "diamond", "price": 260, "value": 20, "chance": 0.012, "level": 16, "color": "#7ee8ff", "size": 0.8},
    {"name": "Лимон", "id": "lemon", "price": 70, "value": 4, "chance": 0.10, "level": 5, "color": "#e8ff47", "size": 0.85},
    {"name": "Персик", "id": "peach", "price": 80, "value": 5, "chance": 0.09, "level": 6, "color": "#ffb38a", "size": 0.95},
    {"name": "Груша", "id": "pear", "price": 90, "value": 6, "chance": 0.08, "level": 7, "color": "#c7e85c", "size": 0.95},
    {"name": "Слива", "id": "plum", "price": 100, "value": 6, "chance": 0.07, "level": 8, "color": "#7a5cff", "size": 0.85},
    {"name": "Земляника", "id": "strawberry", "price": 110, "value": 7, "chance": 0.06, "level": 9, "color": "#ff4f6d", "size": 0.8},
    {"name": "Ананас", "id": "pineapple", "price": 130, "value": 9, "chance": 0.05, "level": 11, "color": "#ffd33d", "size": 1.05},
    {"name": "Кокос", "id": "coconut", "price": 140, "value": 10, "chance": 0.045, "level": 12, "color": "#b08d6a", "size": 1.05},
    {"name": "Гранат", "id": "pomegranate", "price": 150, "value": 11, "chance": 0.04, "level": 13, "color": "#d6336c", "size": 0.95},
    {"name": "Маракуйя", "id": "passion", "price": 170, "value": 12, "chance": 0.032, "level": 15, "color": "#ff8a3d", "size": 0.9},
    {"name": "Личи", "id": "lychee", "price": 180, "value": 13, "chance": 0.028, "level": 16, "color": "#ffb3c1", "size": 0.85},
    {"name": "Папайя", "id": "papaya", "price": 200, "value": 14, "chance": 0.024, "level": 18, "color": "#ff9f5c", "size": 1.0},
    {"name": "Инжир", "id": "fig", "price": 220, "value": 16, "chance": 0.02, "level": 20, "color": "#8e5cd9", "size": 0.85},
    {"name": "Ледяная ягода", "id": "iceberry", "price": 260, "value": 18, "chance": 0.016, "level": 22, "color": "#7ee8ff", "size": 0.8},
    {"name": "Солнечный фрукт", "id": "sunfruit", "price": 300, "value": 22, "chance": 0.012, "level": 25, "color": "#ffe14d", "size": 0.9},
    {"name": "Мифический фрукт", "id": "mythic", "price": 380, "value": 28, "chance": 0.008, "level": 30, "color": "#f04fd1", "size": 0.95},
]
FOOD_BY_ID = {f["id"]: f for f in FOOD_ITEMS}

ACCESSORIES = [
    {"name": "Без аксессуара", "id": "none", "price": 0, "level": 1},
    {"name": "Кепка", "id": "cap", "price": 60, "level": 2},
    {"name": "Шапка Деда Мороза", "id": "santa", "price": 80, "level": 3},
    {"name": "Рожки", "id": "horns", "price": 100, "level": 5},
    {"name": "Корона", "id": "crown", "price": 150, "level": 6},
    {"name": "Пропеллер", "id": "propeller", "price": 120, "level": 7},
    {"name": "Шляпа волшебника", "id": "wizard", "price": 180, "level": 9},
    {"name": "Нимб", "id": "halo", "price": 200, "level": 10},
    {"name": "Бантик", "id": "bow", "price": 70, "level": 4},
    {"name": "Наушники", "id": "headphones", "price": 130, "level": 8},
    {"name": "Цилиндр", "id": "tophat", "price": 170, "level": 11},
    {"name": "Ушки котика", "id": "catears", "price": 140, "level": 13},
    {"name": "Цветок", "id": "flower", "price": 90, "level": 4},
    {"name": "Листок", "id": "leaf", "price": 100, "level": 5},
    {"name": "Сердечко", "id": "heart", "price": 90, "level": 5},
    {"name": "Антенки", "id": "antenna", "price": 110, "level": 6},
    {"name": "Звезда", "id": "starhair", "price": 120, "level": 7},
    {"name": "Берет", "id": "beret", "price": 120, "level": 7},
    {"name": "Пчёлка", "id": "bee", "price": 150, "level": 8},
    {"name": "Колпак повара", "id": "chef", "price": 140, "level": 8},
    {"name": "Праздничный колпак", "id": "party", "price": 130, "level": 9},
    {"name": "Гриб", "id": "mushroom", "price": 130, "level": 9},
    {"name": "Тюрбан", "id": "turban", "price": 150, "level": 10},
    {"name": "Снежинка", "id": "snowflake", "price": 140, "level": 10},
    {"name": "Усы", "id": "whiskers", "price": 140, "level": 11},
    {"name": "Пиратская шляпа", "id": "pirate", "price": 160, "level": 11},
    {"name": "Шапочка выпускника", "id": "graduate", "price": 160, "level": 12},
    {"name": "Льдинка", "id": "ice", "price": 160, "level": 12},
    {"name": "Месяц", "id": "moon", "price": 170, "level": 12},
    {"name": "Шлем викинга", "id": "viking", "price": 180, "level": 13},
    {"name": "Самоцвет", "id": "gem", "price": 180, "level": 13},
    {"name": "Молния", "id": "bolt", "price": 190, "level": 14},
    {"name": "Огонёк", "id": "flame", "price": 200, "level": 14},
    {"name": "Искра", "id": "spark", "price": 210, "level": 15},
    {"name": "Сфера", "id": "orb", "price": 220, "level": 16},
    {"name": "Спутник", "id": "sat", "price": 240, "level": 17},
    {"name": "Корона льда", "id": "icecrown", "price": 260, "level": 19},
]
ACC_BY_ID = {a["id"]: a for a in ACCESSORIES}

MG_DIFF_ORDER = ("normal", "medium", "hard", "extreme")
MG2_SPOTS = ((0, 0), (0, COLS - 1), (ROWS - 1, 0), (ROWS - 1, COLS - 1),
             (0, COLS // 2), (ROWS - 1, COLS // 2), (ROWS // 2, 0),
             (ROWS // 2, COLS - 1))
MG3_ZONE_R = 78

WINDOW_SIZES = {"small": (800, 640), "medium": (900, 740),
                "large": (1000, 840)}
WINDOW_SIZE_LABELS = {"small": "Маленький", "medium": "Средний",
                      "large": "Большой"}
WINDOW_SIZE_ORDER = ("small", "medium", "large")

SFX_NAMES = ("click", "eat", "death", "coin", "levelup", "win", "lose")
SAMPLE_RATE = 22050


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
            out[start + j] += pad * 0.05 * _env(j, nbar, 0.18, 0.3)
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
                out[s0 + j] += (0.07 * math.sin(2 * math.pi * f * t)
                                * math.exp(-7 * t))
    peak = max(abs(s) for s in out) or 1.0
    if peak > 0.85:
        k = 0.85 / peak
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


def ensure_assets():
    try:
        SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        icon = IMAGES_DIR / "icon.png"
        if not icon.exists():
            _make_icon(icon)
        for name in SFX_NAMES + ("bg_music",):
            p = SOUNDS_DIR / f"{name}.wav"
            if not p.exists():
                samples = _make_music() if name == "bg_music" \
                    else _make_sfx(name)
                _wav_write(p, samples)
    except OSError:
        pass


class SoundManager:
    def __init__(self, save=None):
        self.save = save if save is not None else {}
        self._proc = deque()
        self._music_proc = None
        self._music_thread = None
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

    def _mci_open(self, path):
        try:
            import ctypes
            winmm = ctypes.windll.winmm
            winmm.mciSendStringW(f'open "{path}" alias snakeymusic',
                                 None, 0, 0)
            winmm.mciSendStringW("play snakeymusic repeat", None, 0, 0)
            return winmm
        except Exception:
            return None

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

    def start_music(self):
        if self._music_on or not self.save.get("music", True):
            return
        path = SOUNDS_DIR / "bg_music.wav"
        if not path.exists():
            return
        self._music_on = True
        if sys.platform == "win32":
            self._winmm = self._mci_open(path)
            if self._winmm is None:
                self._music_on = False
        elif self._backend:
            self._music_thread = threading.Thread(
                target=self._music_loop, args=(path,), daemon=True)
            self._music_thread.start()
        else:
            self._music_on = False

    def stop_music(self):
        self._music_on = False
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


SOUND = None


def sfx(name):
    if SOUND is not None:
        SOUND.play(name)

MINIGAMES = {
    "mg1": {
        "label": "СБОР ЯБЛОК",
        "icon": "🍎",
        "diffs": {
            "normal": {"speed": 125, "step": 3, "min": 95, "time": 90,
                       "wrap": True, "obstacles": 20, "poison": False,
                       "reward": 0.5, "exp_reward": 1.0, "level": 1},
            "medium": {"speed": 115, "step": 3, "min": 88, "time": 75,
                       "wrap": True, "obstacles": 24, "poison": False,
                       "reward": 0.65, "exp_reward": 1.3, "level": 5},
            "hard": {"speed": 105, "step": 4, "min": 80, "time": 60,
                     "wrap": True, "obstacles": 28, "poison": False,
                     "reward": 0.85, "exp_reward": 1.7, "level": 10},
            "extreme": {"speed": 95, "step": 5, "min": 70, "time": 45,
                        "wrap": True, "obstacles": 32, "poison": False,
                        "reward": 1.1, "exp_reward": 2.2, "level": 20},
        },
    },
    "mg2": {
        "label": "ПОПРОБУЙ ЗАПОМНИТЬ!",
        "icon": "🧠",
        "diffs": {
            "normal": {"speed": 150, "step": 2, "min": 120, "time": 0,
                       "wrap": True, "obstacles": 0, "poison": False,
                       "reward": 1.0, "exp_reward": 1.2, "level": 1,
                       "shade_step": 0.055},
            "medium": {"speed": 145, "step": 2, "min": 118, "time": 0,
                       "wrap": True, "obstacles": 0, "poison": False,
                       "reward": 1.15, "exp_reward": 1.5, "level": 5,
                       "shade_step": 0.038},
            "hard": {"speed": 140, "step": 2, "min": 115, "time": 0,
                     "wrap": True, "obstacles": 0, "poison": False,
                     "reward": 1.4, "exp_reward": 1.9, "level": 10,
                     "shade_step": 0.026},
            "extreme": {"speed": 135, "step": 2, "min": 112, "time": 0,
                        "wrap": True, "obstacles": 0, "poison": False,
                        "reward": 1.8, "exp_reward": 2.4, "level": 20,
                        "shade_step": 0.016},
        },
    },
    "mg3": {
        "label": "ЯБЛОЧНЫЙ СБОР",
        "icon": "🧺",
        "diffs": {
            "normal": {"speed": 150, "step": 0, "min": 150, "time": 60,
                       "wrap": False, "obstacles": 0, "poison": False,
                       "reward": 1.0, "exp_reward": 1.2, "level": 1},
            "medium": {"speed": 150, "step": 0, "min": 150, "time": 60,
                       "wrap": False, "obstacles": 0, "poison": False,
                       "reward": 1.15, "exp_reward": 1.5, "level": 5},
            "hard": {"speed": 150, "step": 0, "min": 150, "time": 60,
                     "wrap": False, "obstacles": 0, "poison": False,
                     "reward": 1.4, "exp_reward": 1.9, "level": 10},
            "extreme": {"speed": 150, "step": 0, "min": 150, "time": 60,
                        "wrap": False, "obstacles": 0, "poison": False,
                        "reward": 1.8, "exp_reward": 2.4, "level": 20},
        },
    },
}

ACHIEVEMENTS = [
    {"id": "first_game", "name": "Первые шаги", "desc": "Сыграй свою первую игру",
     "stat": "games", "goal": 1, "reward": {"coins": 15}},
    {"id": "score10", "name": "Десятка", "desc": "Набери 10 очков за одну игру",
     "stat": "best_score", "goal": 10, "reward": {"coins": 25}},
    {"id": "coins100", "name": "Первая копилка", "desc": "Заработай 100 монет",
     "stat": "coins_earned", "goal": 100, "reward": {"coins": 35}},
    {"id": "apples25", "name": "Фруктоед", "desc": "Собери 25 фруктов",
     "stat": "apples", "goal": 25, "reward": {"item": ("food", "cherry")}},
    {"id": "games10", "name": "Постоянный игрок", "desc": "Сыграй 10 игр",
     "stat": "games", "goal": 10, "reward": {"item": ("acc", "cap")}},
    {"id": "level5", "name": "Пятый уровень", "desc": "Достигни 5 уровня",
     "stat": "level", "goal": 5, "reward": {"coins": 70}},
    {"id": "skins3", "name": "Модник", "desc": "Купи 3 скина",
     "stat": "skins", "goal": 3, "reward": {"coins": 45}},
    {"id": "mg1_10", "name": "Сборщик", "desc": "Собери 10 яблок за игру «Сбор яблок»",
     "stat": "mg1_best", "goal": 10, "reward": {"coins": 60}},
    {"id": "mg2_first", "name": "Хорошая память", "desc": "Победи в «Попробуй запомнить!»",
     "stat": "mg2_wins", "goal": 1, "reward": {"coins": 60}},
    {"id": "mg3_5", "name": "Курьер", "desc": "Принеси 5 яблок за одну игру «Яблочный сбор»",
     "stat": "mg3_best", "goal": 5, "reward": {"coins": 70}},
    {"id": "score25", "name": "Разогрев", "desc": "Набери 25 очков за одну игру",
     "stat": "best_score", "goal": 25, "reward": {"item": ("color", "#a4f24a")}},
    {"id": "score50", "name": "Первая полсотни", "desc": "Набери 50 очков за одну игру",
     "stat": "best_score", "goal": 50, "reward": {"coins": 60}},
    {"id": "coins200", "name": "Серьёзные сбережения", "desc": "Заработай 200 монет",
     "stat": "coins_earned", "goal": 200, "reward": {"item": ("food", "kiwi")}},
    {"id": "games25", "name": "Ветеран аркад", "desc": "Сыграй 25 игр",
     "stat": "games", "goal": 25, "reward": {"item": ("acc", "bow")}},
    {"id": "apples100", "name": "Фруктовый фанат", "desc": "Собери 100 фруктов",
     "stat": "apples", "goal": 100, "reward": {"item": ("food", "mango")}},
    {"id": "mg1_18", "name": "Спринтер", "desc": "Собери 18 яблок за игру «Сбор яблок»",
     "stat": "mg1_best", "goal": 18, "reward": {"item": ("food", "melon")}},
    {"id": "mg2_5", "name": "Эйдетик", "desc": "Победи 5 раз в «Попробуй запомнить!»",
     "stat": "mg2_wins", "goal": 5, "reward": {"item": ("color", "#4655ff")}},
    {"id": "mg3_12", "name": "Яблочный экспресс", "desc": "Принеси 12 яблок за одну игру «Яблочный сбор»",
     "stat": "mg3_best", "goal": 12, "reward": {"coins": 160}},
    {"id": "level10", "name": "Опытный змей", "desc": "Достигни 10 уровня",
     "stat": "level", "goal": 10, "reward": {"item": ("acc", "catears")}},
    {"id": "skins8", "name": "Гардероб", "desc": "Купи 8 скинов",
     "stat": "skins", "goal": 8, "reward": {"item": ("theme", "ocean")}},
    {"id": "score100", "name": "Сотка!", "desc": "Набери 100 очков за одну игру",
     "stat": "best_score", "goal": 100, "reward": {"item": ("color", "#7fe8c3")}},
    {"id": "coins1000", "name": "Магнат", "desc": "Заработай 1000 монет",
     "stat": "coins_earned", "goal": 1000, "reward": {"item": ("acc", "halo")}},
    {"id": "games100", "name": "Легенда аркад", "desc": "Сыграй 100 игр",
     "stat": "games", "goal": 100, "reward": {"coins": 320}},
    {"id": "apples500", "name": "Гроза фруктов", "desc": "Собери 500 фруктов",
     "stat": "apples", "goal": 500, "reward": {"item": ("color", "#9d3ff2")}},
    {"id": "mg1_28", "name": "Легенда сбора", "desc": "Собери 28 яблок за игру «Сбор яблок»",
     "stat": "mg1_best", "goal": 28, "reward": {"coins": 260}},
    {"id": "mg2_15", "name": "Абсолютная память", "desc": "Победи 15 раз в «Попробуй запомнить!»",
     "stat": "mg2_wins", "goal": 15, "reward": {"item": ("acc", "crown")}},
    {"id": "mg3_20", "name": "Мастер доставки", "desc": "Принеси 20 яблок за одну игру «Яблочный сбор»",
     "stat": "mg3_best", "goal": 20, "reward": {"coins": 320}},
    {"id": "mg3_total", "name": "Плодовоз", "desc": "Принеси 150 яблок в зону сбора всего",
     "stat": "mg3_apples", "goal": 150, "reward": {"item": ("food", "dragon")}},
    {"id": "score200", "name": "Легенда поля", "desc": "Набери 200 очков за одну игру",
     "stat": "best_score", "goal": 200, "reward": {"coins": 220}},
    {"id": "coins3000", "name": "Золотой запас", "desc": "Заработай 3000 монет",
     "stat": "coins_earned", "goal": 3000, "reward": {"coins": 420}},
    {"id": "level20", "name": "Мастер", "desc": "Достигни 20 уровня",
     "stat": "level", "goal": 20, "reward": {"item": ("theme", "lava")}},
    {"id": "skins15", "name": "Коллекционер", "desc": "Купи 15 скинов",
     "stat": "skins", "goal": 15, "reward": {"coins": 260}},
    {"id": "skins25", "name": "Все скины мира", "desc": "Купи 25 скинов",
     "stat": "skins", "goal": 25, "reward": {"item": ("color", "#00e5ff")}},
]


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
             "food": FOOD_ITEMS, "acc": ACCESSORIES}
    kindname = {"color": "цвет", "theme": "фон",
                "food": "еда", "acc": "аксессуар"}[kind]
    name = next(it["name"] for it in table[kind] if it["id"] == iid)
    return f"{kindname} «{name}»"


def grant_ach_reward(save, ach):
    r = ach["reward"]
    if "coins" in r:
        save["coins"] = save.get("coins", 0) + r["coins"]
    else:
        kind, iid = r["item"]
        key = {"color": "owned", "theme": "owned_themes",
               "food": "owned_foods", "acc": "owned_acc"}[kind]
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

DIFFICULTIES = {
    "normal": {"label": "Обычная", "speed": 150, "step": 3, "min": 85,
               "wrap": True, "obstacles": 0, "poison": False, "time": 0,
               "reward": 1.0, "exp_reward": 1.2, "level": 1, "note": ""},
    "medium": {"label": "Средняя", "speed": 135, "step": 4, "min": 75,
               "wrap": True, "obstacles": 0, "poison": False, "time": 0,
               "reward": 1.15, "exp_reward": 1.4, "level": 5, "note": "быстрее обычной"},
    "hard": {"label": "Сложная", "speed": 120, "step": 5, "min": 65,
             "wrap": False, "obstacles": 0, "poison": False, "time": 0,
             "reward": 1.35, "exp_reward": 1.7, "level": 10, "note": "стены смертельны!"},
    "extreme": {"label": "Экстремальная", "speed": 110, "step": 6, "min": 50,
                "wrap": False, "obstacles": 24, "poison": True, "time": 0,
                "reward": 1.8, "exp_reward": 2.4, "level": 20,
                "note": "стены и ядовитые фрукты!"},
}

KEY_ALIASES = {
    "cyrillic_tse": "w", "cyrillic_ef": "a", "cyrillic_yeru": "s",
    "cyrillic_ve": "d", "cyrillic_ka": "r", "cyrillic_ze": "p",
    "cyrillic_es": "c",
    "ц": "w", "ф": "a", "ы": "s", "в": "d", "к": "r", "з": "p", "с": "c",
}

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




class RoundButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=200, height=44,
                 radius=16, bg=PANEL, fg=TEXT, app_bg=BG, font=None,
                 outline=None):
        super().__init__(master, width=width, height=height, bg=app_bg,
                         highlightthickness=0,
                         cursor="hand2" if command else "arrow")
        self.command = command
        self.radius = radius
        self.text = text
        self.base_bg = bg
        self.base_fg = fg
        self.app_bg = app_bg
        self.outline = outline
        self.font = font or ("Segoe UI", 12, "bold")
        self._width = width
        self._height = height
        self.disabled = command is None
        self.hover_bg = blend(bg, "#ffffff", 0.12)
        self.press_bg = blend(bg, "#000000", 0.18)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)
        self.bind("<Enter>", lambda e: None if self.disabled
                  else self._paint(self.hover_bg))
        self.bind("<Leave>", lambda e: self._paint(self.base_bg))
        self._paint(self.base_bg)

    def repaint(self):
        self._paint(self.base_bg)

    def _paint(self, bg=None):
        if bg is None:
            bg = self.base_bg
        self.delete("all")
        w, h, r = self._width, self._height, self.radius
        if self.disabled:
            round_rect(self, 1, 1, w - 1, h - 1, r, fill=bg,
                       outline=self.outline or BORDER)
        else:
            round_rect(self, 2, 5, w - 2, h + 1, r, fill="#000000",
                       stipple="gray25", outline="")
            round_rect(self, 1, 1, w - 1, h - 1, r, fill=bg,
                       outline=self.outline or blend(bg, "#000000", 0.3))
            round_rect(self, 4, 3, w - 4, h * 0.42, max(4, r - 6),
                       fill=blend(bg, "#ffffff", 0.10), outline="")
        self.create_text(w / 2, h / 2 - 1, text=self.text, font=self.font,
                         fill=self.base_fg)

    def _press(self, _event=None):
        if not self.disabled:
            self._paint(self.press_bg)

    def _release(self, event):
        if self.disabled:
            return
        self._paint(self.base_bg)
        if 0 <= event.x <= self._width and 0 <= event.y <= self._height \
                and self.command:
            sfx("click")
            self.command()


class GradientBG(tk.Canvas):
    def __init__(self, master, c1, c2, accent=ACCENT, steps=20):
        super().__init__(master, width=100, height=100, bg=c1,
                         highlightthickness=0)
        self.g1, self.g2, self.accent = c1, c2, accent
        self.steps = steps
        self.phase = 0.0
        self.job = None
        self.bands = []
        bh = 2004 / steps
        for i in range(steps):
            self.bands.append(self.create_rectangle(-4, i * bh - 2, 2004,
                                                    (i + 1) * bh + 2,
                                                    outline="", tags="band"))
        self._paint_bands()

    def _paint_bands(self):
        n = max(1, self.steps - 1)
        for i, item in enumerate(self.bands):
            t = i / n
            col = blend(self.g1, self.g2, t)
            wave = math.sin(self.phase + t * 4.0) * 0.05
            if wave > 0:
                col = blend(col, self.accent, wave)
            self.itemconfig(item, fill=col)

    def set_animated(self, on):
        if on and self.job is None:
            self._tick()
        elif not on and self.job is not None:
            self.after_cancel(self.job)
            self.job = None

    def _tick(self):
        self.phase += 0.045
        self._paint_bands()
        # noinspection PyArgumentList
        self.job = self.after(90, self._tick)


class Screen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=BG)
        self.app = app

    def on_show(self):
        pass

    def on_hide(self):
        pass

    def on_key(self, event):
        pass

    def on_wheel(self, event):
        scroller = getattr(self, "scroller", None)
        if not hasattr(scroller, "yview_scroll"):
            return
        num = getattr(event, "num", 0)
        if num == 4:
            scroller.yview_scroll(-2, "units")
        elif num == 5:
            scroller.yview_scroll(2, "units")
        else:
            scroller.yview_scroll(-2 if getattr(event, "delta", 0) > 0 else 2,
                                  "units")

    def _raise_window(self, attr):
        win = self.__dict__.get(attr)
        if win is None:
            return False
        try:
            alive = win.winfo_exists()
        except tk.TclError:
            alive = False
        if alive:
            win.deiconify()
            win.lift()
            win.focus_force()
            return True
        return False

    @staticmethod
    def _center_window(win):
        win.update_idletasks()
        ww = win.winfo_reqwidth()
        wh = win.winfo_reqheight()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = max(0, (sw - ww) // 2)
        y = max(0, (sh - wh) // 2 - 20)
        win.geometry(f"+{x}+{y}")

    def _borderless(self, win, title, width, wbg, on_close=None):
        close = on_close or win.destroy
        win.title(title)
        try:
            win.overrideredirect(True)
            if not win.overrideredirect():
                return None
        except Exception:
            return None
        bar = tk.Canvas(win, width=width, height=42, bg=wbg,
                        highlightthickness=0)
        bar.pack(fill="x")
        round_rect(bar, 1, 1, width - 2, 41, 12, fill=PANEL, outline=BORDER)
        bar.create_oval(14, 13, 28, 27, fill=ACCENT, outline="")
        bar.create_text(38, 21, text=title, anchor="w",
                        font=(self.app.font_ui, 11, "bold"), fill=TEXT)
        bar.create_oval(width - 34, 10, width - 12, 32,
                        fill=blend(PANEL, "#ffffff", 0.08), outline=BORDER)
        bar.create_text(width - 23, 21, text="\u2715",
                        font=(self.app.font_ui, 10, "bold"), fill=DIM)
        state = {"off": None}

        def press(event):
            if event.x >= width - 36:
                close()
                return
            state["off"] = (event.x, event.y)
            win.focus_force()

        def drag(event):
            off = state["off"]
            if off is not None:
                win.geometry(f"+{event.x_root - off[0]}"
                             f"+{event.y_root - off[1]}")

        bar.bind("<Button-1>", press)
        bar.bind("<B1-Motion>", drag)
        bar.bind("<ButtonRelease-1>",
                 lambda e: state.__setitem__("off", None))
        try:
            win.bind("<Escape>", lambda e: close())
        except Exception:
            pass
        return bar


class MenuScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.bg = GradientBG(self, BG, "#121c2c")
        self.bg.pack(fill="both", expand=True)
        self.bg.bind("<Configure>", lambda e: self._layout())
        self.anim_t = 0.0
        self.anim_job = None
        self._btn_ids = {}
        self._levelup_win = None
        self._ach_win = None
        self._changelog_win = None
        self._layout()

    def _geom(self):
        w = self.bg.winfo_width() or 0
        h = self.bg.winfo_height() or 0
        if w < 50:
            w = 900
        if h < 50:
            h = 740
        return w, h

    def _btn(self, key, cx, cy, bw, bh, text, cmd, bg=PANEL, fg=TEXT,
             fsize=12):
        tag = f"btn_{key}"
        x1, y1 = cx - bw / 2.0, cy - bh / 2.0
        x2, y2 = cx + bw / 2.0, cy + bh / 2.0
        r = min(bh / 2.0, 18)
        poly = round_rect(self.bg, x1, y1, x2, y2, r, fill=bg,
                          outline=blend(bg, "#ffffff", 0.28),
                          tags=("menu", tag))
        round_rect(self.bg, x1 + 4, y1 + 3, x2 - 4, y1 + bh * 0.42,
                   max(4, r - 6), fill=blend(bg, "#ffffff", 0.10),
                   outline="", tags=("menu", tag))
        self.bg.create_text(cx, cy + 1, text=text,
                            font=(self.app.font_ui, fsize, "bold"), fill=fg,
                            tags=("menu", tag))
        self._btn_ids[key] = (poly, bg)
        self.bg.tag_bind(tag, "<Enter>",
                         lambda e, k=key: self._hover(k, True))
        self.bg.tag_bind(tag, "<Leave>",
                         lambda e, k=key: self._hover(k, False))
        self.bg.tag_bind(tag, "<Button-1>", lambda e, cb=cmd: cb())

    def _hover(self, key, on):
        info = self._btn_ids.get(key)
        if not info:
            return
        try:
            self.bg.itemconfig(info[0],
                               fill=blend(info[1], "#ffffff", 0.16 if on else 0.0))
        except tk.TclError:
            pass

    def _layout(self):
        w, h = self._geom()
        self.bg.delete("menu")
        self._btn_ids = {}
        round_rect(self.bg, 10, 6, 74, 30, 12, fill=PANEL, outline=BORDER,
                   tags="menu")
        self.bg.create_text(42, 18, text=f"v{VERSION}",
                            font=(self.app.font_ui, 9, "bold"), fill=GOLD,
                            tags="menu")
        self._btn("log", 152, 18, 116, 24, "update log",
                  self._open_changelog, bg=PANEL, fg=DIM, fsize=8)
        self._draw_title(w, h)
        self._draw_level(w, h)
        self.bg.create_text(w / 2, h * 0.455,
                            text=f"\u25c9  {self.app.save['coins']} \u043c\u043e\u043d\u0435\u0442",
                            font=(self.app.font_ui, 13, "bold"), fill=GOLD,
                            tags="menu")
        y0 = h * 0.52
        self._btn("play", w / 2, y0, 260, 54, "\u0418\u0413\u0420\u0410\u0422\u042c",
                  self._play_classic, bg=ACCENT, fg="#06220c", fsize=15)
        self._btn("mini", w / 2, y0 + 56, 260, 48, "\u041c\u0418\u041d\u0418-\u0418\u0413\u0420\u042b",
                  lambda: self.app.show("MiniScreen"), bg=BLUE, fg="#061224",
                  fsize=13)
        self._btn("ach", w / 2, y0 + 112, 260, 48, "\u0414\u041e\u0421\u0422\u0418\u0416\u0415\u041d\u0418\u042f",
                  lambda: self.app.show("AchScreen"), bg="#8957e5",
                  fg="#f4efff", fsize=13)
        self._btn("shop", w / 2, y0 + 168, 260, 48, "\u041c\u0410\u0413\u0410\u0417\u0418\u041d",
                  lambda: self.app.show("ShopScreen"), fsize=13)
        self._btn("set", w / 2, y0 + 224, 260, 48, "\u041d\u0410\u0421\u0422\u0420\u041e\u0419\u041a\u0418",
                  lambda: self.app.show("SettingsScreen"), fsize=13)
        self.bg.create_text(w / 2, h * 0.94,
                            text=f"\u0420\u0435\u043a\u043e\u0440\u0434: {self.app.save['highscore']}",
                            font=(self.app.font_ui, 11), fill=DIM, tags="menu")
        self.bg.create_text(w / 2, h * 0.975,
                            text="WASD / \u0441\u0442\u0440\u0435\u043b\u043a\u0438 \u00b7 P \u2014 \u043f\u0430\u0443\u0437\u0430 \u00b7 R \u2014 \u0437\u0430\u043d\u043e\u0432\u043e",
                            font=(self.app.font_ui, 9), fill="#3a4149",
                            tags="menu")

    def _play_classic(self):
        self.app.next_mode = "classic"
        self.app.show("GameScreen")

    def on_show(self):
        self._layout()
        if not self.app.save.get("low_spec"):
            self.bg.set_animated(True)
            self._start_anim()
        if not self._maybe_show_levelup():
            self._maybe_show_achievements()

    def on_hide(self):
        self.bg.set_animated(False)
        if self.anim_job is not None:
            self.after_cancel(self.anim_job)
            self.anim_job = None

    def _draw_title(self, w=None, h=None):
        if w is None:
            w, h = self._geom()
        self.bg.delete("title")
        t = self.anim_t
        cy = h * 0.16
        font = (self.app.font_title, 46, "bold")
        for i, ch in enumerate("SNAKEY"):
            glow = 0.15 + 0.75 * (0.5 + 0.5 * math.sin(t * 0.12 - i * 0.7))
            color = blend(ACCENT, ACCENT_BRIGHT, glow)
            x = w / 2 - 110 + i * 44
            y = cy + math.sin(t * 0.08 + i * 0.6) * 3
            self.bg.create_text(x + 3, y + 3, text=ch, font=font,
                                fill="#0e4415", tags=("menu", "title"))
            self.bg.create_text(x, y, text=ch, font=font, fill=color,
                                tags=("menu", "title"))
        self.bg.create_text(w / 2, cy + 44,
                            text="\u0441\u043e\u0431\u0438\u0440\u0430\u0439 \u0435\u0434\u0443 \u2014 \u0441\u0442\u0430\u043d\u044c \u0441\u0430\u043c\u043e\u0439 \u0434\u043b\u0438\u043d\u043d\u043e\u0439 \u0437\u043c\u0435\u0439\u043a\u043e\u0439",
                            font=(self.app.font_ui, 10), fill=DIM,
                            tags=("menu", "title"))
        for i in range(15):
            x = w / 2 - 132 + i * 18
            y = cy + 76 + math.sin(t * 0.15 + i * 0.5) * 4
            if i == 14:
                self.bg.create_oval(x - 9, y - 9, x + 9, y + 9,
                                    fill=ACCENT_BRIGHT, outline="",
                                    tags=("menu", "title"))
                for ex in (x + 3, x + 7):
                    self.bg.create_oval(ex - 2, y - 5, ex + 2, y - 1,
                                        fill="#06220c", outline="",
                                        tags=("menu", "title"))
            else:
                self.bg.create_oval(x - 7, y - 7, x + 7, y + 7,
                                    fill=blend(ACCENT, BG, 0.04 * i),
                                    outline="", tags=("menu", "title"))

    def _draw_level(self, w=None, h=None):
        if w is None:
            w, h = self._geom()
        self.bg.delete("level")
        exp = self.app.save.get("exp", 0)
        level = level_from_exp(exp)
        cur = exp_for_level(level)
        nxt = exp_for_level(level + 1)
        frac = max(0.0, min(1.0, (exp - cur) / (nxt - cur)))
        cx = w / 2
        bx0, by = cx - 170, h * 0.35 - 32
        bx1, by1 = cx + 170, h * 0.35 + 32
        round_rect(self.bg, bx0, by, bx1, by1, 16, fill=PANEL,
                   outline=blend(ACCENT, BG, 0.5), tags=("menu", "level"))
        self.bg.create_oval(bx0 + 10, by + 10, bx0 + 50, by + 50,
                            fill=ACCENT_DARK, outline=ACCENT,
                            tags=("menu", "level"))
        self.bg.create_text(bx0 + 30, by + 31, text=str(level),
                            font=(self.app.font_title, 16, "bold"),
                            fill=ACCENT_BRIGHT, tags=("menu", "level"))
        self.bg.create_text(bx0 + 62, by + 15, text=f"\u0423\u0420\u041e\u0412\u0415\u041d\u042c {level}",
                            anchor="w", font=(self.app.font_ui, 11, "bold"),
                            fill=TEXT, tags=("menu", "level"))
        self.bg.create_text(bx0 + 62, by + 33,
                            text=f"{exp} EXP \u00b7 \u0434\u043e \u0443\u0440. {level + 1}: {nxt - exp}",
                            anchor="w", font=(self.app.font_ui, 8), fill=DIM,
                            tags=("menu", "level"))
        px0, py0, px1, py1 = bx0 + 64, by + 44, bx1 - 12, by + 53
        round_rect(self.bg, px0, py0, px1, py1, 4, fill=LOCKED_BG,
                   outline="", tags=("menu", "level"))
        if frac > 0:
            width = (px1 - px0) * frac
            seg_w = width / 6
            for k in range(6):
                col = blend(GOLD, ACCENT_BRIGHT, k / 5)
                round_rect(self.bg, px0 + k * seg_w, py0,
                           px0 + (k + 1) * seg_w, py1, 3, fill=col,
                           outline="", tags=("menu", "level"))
            if not self.app.save.get("low_spec"):
                span = max(1, (px1 - px0 - 16))
                sx = px0 + (self.anim_t * 4) % span
                self.bg.create_rectangle(sx, py0 + 1, sx + 14, py1 - 1,
                                         fill=blend(GOLD, "#ffffff", 0.45),
                                         outline="", tags=("menu", "level"))

    def _maybe_show_levelup(self):
        pending = self.app.save.get("pending_level", 0)
        if not pending:
            return False
        if self._raise_window("_levelup_win"):
            return True
        self.app.save["pending_level"] = 0
        self.app.commit()
        sfx("levelup")
        unlocked = [f"\u0421\u043b\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u00ab{cfg['label']}\u00bb"
                    for cfg in DIFFICULTIES.values() if cfg["level"] == pending]
        for item in THEMES:
            if item.get("level") == pending and item["price"] > 0:
                unlocked.append(f"\u0424\u043e\u043d \u00ab{item['name']}\u00bb")
        for item in FOOD_ITEMS:
            if item.get("level") == pending and item["price"] > 0:
                unlocked.append(f"\u0415\u0434\u0430 \u00ab{item['name']}\u00bb")
        for item in ACCESSORIES:
            if item.get("level") == pending and item["price"] > 0:
                unlocked.append(f"\u0410\u043a\u0441\u0435\u0441\u0441\u0443\u0430\u0440 \u00ab{item['name']}\u00bb")
        win = tk.Toplevel(self)
        self._levelup_win = win
        win.title("\u041d\u043e\u0432\u044b\u0439 \u0443\u0440\u043e\u0432\u0435\u043d\u044c!")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self.app)
        self._borderless(win, "\u2728 \u041d\u043e\u0432\u044b\u0439 \u0443\u0440\u043e\u0432\u0435\u043d\u044c!", 380, BG)
        cv = tk.Canvas(win, width=380, height=210, bg=BG, highlightthickness=0)
        cv.pack()
        cx, cyc = 190, 106
        for k in range(16):
            a = math.radians(k * 22.5)
            col = GOLD if k % 2 else ACCENT
            cv.create_line(cx + math.cos(a) * 70, cyc + math.sin(a) * 70,
                           cx + math.cos(a) * 98, cyc + math.sin(a) * 98,
                           fill=col, width=2)
        cv.create_oval(120, 36, 260, 176, outline=blend(GOLD, BG, 0.4),
                       width=2)
        cv.create_oval(126, 42, 254, 170, fill=ACCENT_DARK, outline=ACCENT,
                       width=3)
        cv.create_oval(138, 54, 242, 158,
                       fill=blend(ACCENT_DARK, "#000000", 0.3), outline="")
        cv.create_text(cx, cyc - 2, text=str(pending),
                       font=(self.app.font_title, 44, "bold"),
                       fill=ACCENT_BRIGHT)
        cv.create_text(cx, 192, text="\u0423\u0420\u041e\u0412\u0415\u041d\u042c \u041f\u041e\u0412\u042b\u0428\u0415\u041d!",
                       font=(self.app.font_title, 16, "bold"), fill=GOLD)
        tk.Label(win, text=f"\u0422\u0435\u043f\u0435\u0440\u044c \u0443 \u0442\u0435\u0431\u044f {self.app.save.get('exp', 0)} EXP",
                 bg=BG, fg=TEXT, font=(self.app.font_ui, 11, "bold")).pack()
        if unlocked:
            tk.Label(win, text="\u041d\u041e\u0412\u041e\u0415 \u0414\u041e\u0421\u0422\u0423\u041f\u041d\u041e:", bg=BG, fg=ACCENT,
                     font=(self.app.font_ui, 10, "bold")).pack(pady=(8, 0))
            for line in unlocked[:6]:
                tk.Label(win, text=f"\u2605  {line}", bg=PANEL, fg=TEXT,
                         font=(self.app.font_ui, 9, "bold")).pack(
                             pady=1, ipadx=10, ipady=2)
        RoundButton(win, "\u041a\u0440\u0443\u0442\u043e!", win.destroy, width=150, height=40,
                    bg=ACCENT, fg="#06220c", app_bg=BG,
                    font=(self.app.font_ui, 12, "bold")).pack(pady=14)
        self._center_window(win)
        return True

    def _maybe_show_achievements(self):
        pending = self.app.save.get("pending_ach", [])
        if not pending:
            return False
        if self._raise_window("_ach_win"):
            return True
        self.app.save["pending_ach"] = []
        self.app.commit()
        sfx("win")
        win = tk.Toplevel(self)
        self._ach_win = win
        win.title("\u0414\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u0435 \u043f\u043e\u043b\u0443\u0447\u0435\u043d\u043e!")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self.app)
        self._borderless(win, "\u2605 \u0414\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u0435 \u043f\u043e\u043b\u0443\u0447\u0435\u043d\u043e!", 380, BG)
        cv = tk.Canvas(win, width=380, height=170, bg=BG, highlightthickness=0)
        cv.pack()
        cx, cyc = 190, 78
        for k in range(14):
            a = math.radians(k * (360 / 14))
            col = "#8957e5" if k % 2 else "#c9a8ff"
            cv.create_line(cx + math.cos(a) * 52, cyc + math.sin(a) * 52,
                           cx + math.cos(a) * 72, cyc + math.sin(a) * 72,
                           fill=col, width=2)
        cv.create_oval(138, 26, 242, 130, fill="#3a2a5e", outline="#8957e5",
                       width=3)
        cv.create_text(cx, cyc - 2, text="\u2605",
                       font=(self.app.font_title, 40, "bold"), fill="#c9a8ff")
        cv.create_text(cx, 152, text="\u0414\u041e\u0421\u0422\u0418\u0416\u0415\u041d\u0418\u0415 \u041f\u041e\u041b\u0423\u0427\u0415\u041d\u041e!",
                       font=(self.app.font_title, 15, "bold"), fill="#c9a8ff")
        for name in pending[:5]:
            tk.Label(win, text=f"\u2605  {name}", bg=BG, fg=TEXT,
                     font=(self.app.font_ui, 10, "bold")).pack()
        RoundButton(win, "\u041e\u0442\u043b\u0438\u0447\u043d\u043e!", win.destroy, width=150, height=40,
                    bg="#8957e5", fg="#f4efff", app_bg=BG,
                    font=(self.app.font_ui, 12, "bold")).pack(pady=12)
        self._center_window(win)
        return True

    def on_wheel(self, event):
        win = self.__dict__.get("_changelog_win")
        canvas = self.__dict__.get("_changelog_canvas")
        if win is not None and canvas is not None:
            try:
                alive = win.winfo_exists()
            except tk.TclError:
                alive = False
            if alive:
                num = getattr(event, "num", 0)
                if num == 4:
                    canvas.yview_scroll(-2, "units")
                elif num == 5:
                    canvas.yview_scroll(2, "units")
                else:
                    canvas.yview_scroll(
                        -2 if getattr(event, "delta", 0) > 0 else 2, "units")
                return
        super().on_wheel(event)

    def _start_anim(self):
        if self.anim_job is None:
            self._animate()

    def _animate(self):
        self.anim_t += 1
        self._draw_title()
        self._draw_level()
        # noinspection PyArgumentList
        self.anim_job = self.after(60, self._animate)

    def _open_changelog(self):
        if self._raise_window("_changelog_win"):
            return
        wbg = "#0b1420"
        win = tk.Toplevel(self)
        self._changelog_win = win
        win.title("Update log \u2014 SNAKEY")
        win.configure(bg=wbg)
        win.resizable(False, False)
        win.transient(self.app)

        def close():
            win.destroy()

        self._borderless(win, "Update log \u2014 SNAKEY", 560, wbg, on_close=close)
        cv = tk.Canvas(win, width=560, height=88, bg=wbg, highlightthickness=0)
        cv.pack()
        gradient_bands(cv, 0, 0, 560, 88, wbg, "#16233a", 12)
        cx, cyc = 280, 40
        for k in range(16):
            a = math.radians(k * 22.5)
            cv.create_line(cx + math.cos(a) * 42, cyc + math.sin(a) * 42,
                           cx + math.cos(a) * 60, cyc + math.sin(a) * 60,
                           fill=blend(GOLD, wbg, 0.4), width=2)
        cv.create_text(cx + 2, cyc + 1, text="UPDATE LOG",
                       font=(self.app.font_title, 20, "bold"), fill="#3a2a05")
        cv.create_text(cx, cyc, text="UPDATE LOG",
                       font=(self.app.font_title, 20, "bold"), fill=GOLD)
        cv.create_text(cx, cyc + 26, text="\u0438\u0441\u0442\u043e\u0440\u0438\u044f \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0439 SNAKEY",
                       font=(self.app.font_ui, 9), fill=DIM)
        body = tk.Frame(win, bg=wbg)
        body.pack(fill="both", expand=True)
        canvas = tk.Canvas(body, width=560, height=540, bg=wbg,
                           highlightthickness=0)
        bar = tk.Scrollbar(body, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self._changelog_canvas = canvas
        inner = tk.Frame(canvas, bg=wbg)
        canvas.create_window((0, 0), window=inner, anchor="nw", width=540)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        for ver, items in CHANGELOG:
            pill = tk.Canvas(inner, width=540, height=30, bg=wbg,
                             highlightthickness=0)
            pill.pack(pady=(10, 0))
            round_rect(pill, 1, 1, 538, 29, 14, fill=PANEL,
                       outline=blend(GOLD, wbg, 0.4))
            pill.create_text(18, 15, text=f"v{ver}", anchor="w",
                             font=(self.app.font_ui, 11, "bold"), fill=GOLD)
            pill.create_text(522, 15, text=f"{len(items)} \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0439", anchor="e",
                             font=(self.app.font_ui, 8), fill=DIM)
            for line in items:
                row = tk.Frame(inner, bg=wbg)
                row.pack(fill="x", padx=30, pady=1)
                tk.Label(row, text="\uff0b", bg=wbg, fg=GOLD,
                         font=(self.app.font_ui, 10, "bold")).pack(
                             side="left", padx=(2, 7))
                tk.Label(row, text=line, bg=wbg, fg=TEXT, wraplength=450,
                         justify="left", font=(self.app.font_ui, 9),
                         anchor="w").pack(side="left")
        RoundButton(win, "\u0417\u0430\u043a\u0440\u044b\u0442\u044c", close, width=150, height=38,
                    app_bg=wbg, font=(self.app.font_ui, 10, "bold")).pack(pady=12)
        win.protocol("WM_DELETE_WINDOW", close)
        self._center_window(win)


class ShopCard(tk.Canvas):
    def __init__(self, master, app, kind, item, refresh, card_bg=BG):
        super().__init__(master, width=146, height=66, bg=card_bg,
                         highlightthickness=0, cursor="arrow")
        self.app = app
        self.kind = kind
        self.item = item
        self.refresh = refresh
        self.clickable = False
        self.tip = None
        self.bind("<Button-1>", self._click)
        self.bind("<Motion>", self._motion)
        self.bind("<Leave>", self._leave)
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
        if self.kind == "color":
            if iid == "rainbow":
                for k, hue in enumerate((0.0, 0.33, 0.66)):
                    c.create_arc(sw[0], sw[1], sw[2], sw[3], start=k * 120,
                                 extent=120, style="pieslice",
                                 fill=hsv_hex(hue, 0.85, 0.95), outline="")
            elif iid in GRADIENTS:
                g = GRADIENTS[iid]
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=0, extent=180,
                             style="pieslice", fill=g[0], outline="")
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=180,
                             extent=180, style="pieslice", fill=g[1],
                             outline="")
            else:
                c.create_oval(sw[0], sw[1], sw[2], sw[3], fill=iid,
                              outline=blend(iid, "#000000", 0.35))
        elif self.kind == "theme":
            t = THEME_BY_ID[iid]
            if t.get("grad"):
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=0, extent=180,
                             style="pieslice", fill=t["grad"][0], outline="")
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=180,
                             extent=180, style="pieslice", fill=t["grad"][1],
                             outline="")
            else:
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=0, extent=180,
                             style="pieslice", fill=t["grid_a"], outline="")
                c.create_arc(sw[0], sw[1], sw[2], sw[3], start=180,
                             extent=180, style="pieslice", fill=t["grid_b"],
                             outline="")
            c.create_oval(sw[0], sw[1], sw[2], sw[3], outline=t["border"])
        elif self.kind == "acc":
            if iid == "none":
                c.create_oval(sw[0], sw[1], sw[2], sw[3], outline=DIM)
                c.create_line(sw[0] + 3, sw[1] + 3, sw[2] - 3, sw[3] - 3,
                              fill=DIM)
                c.create_line(sw[0] + 3, sw[3] - 3, sw[2] - 3, sw[1] + 3,
                              fill=DIM)
            else:
                draw_acc(c, 23, 21, iid)
        else:
            draw_food(c, 23, 21, iid)

    def _paint(self):
        c = self
        c.delete("all")
        level = level_from_exp(self.app.save.get("exp", 0))
        owned, selected = self._state()
        locked = not owned and self.item.get("level", 1) > level
        round_rect(c, 1, 1, 145, 65, 13, fill=PANEL,
                   outline=ACCENT if selected else BORDER)
        sw = (12, 10, 34, 32)
        iid = self.item["id"]
        self._swatch(c, sw, iid)
        name = self.item["name"]
        if self.kind == "food":
            name = f"{name} +{self.item['value']}"
        c.create_text(40, 16, text=name, anchor="w",
                      font=(self.app.font_ui, 8, "bold"),
                      fill=DIM if locked else TEXT)
        c.create_oval(128, 4, 142, 18, fill=blend(PANEL, "#ffffff", 0.12),
                      outline=BORDER)
        c.create_text(135, 11, text="i",
                      font=(self.app.font_ui, 8, "bold"), fill=GOLD)
        if locked:
            self.clickable = False
            self.config(cursor="arrow")
            round_rect(c, 10, 38, 136, 58, 9, fill=LOCKED_BG, outline="")
            c.create_text(73, 48, text=f"\U0001f512 \u0443\u0440. {self.item['level']}",
                          font=(self.app.font_ui, 8, "bold"), fill=DIM)
            return
        if owned:
            if self.kind == "food":
                label, bg, clickable = "\u041a\u0443\u043f\u043b\u0435\u043d\u043e", BORDER, False
            elif selected:
                label, bg, clickable = "\u0412\u044b\u0431\u0440\u0430\u043d\u043e", ACCENT_DARK, False
            else:
                label, bg, clickable = "\u0412\u044b\u0431\u0440\u0430\u0442\u044c", BORDER, True
        else:
            label, bg, clickable = f"{self.item['price']} \u043c\u043e\u043d\u0435\u0442", GOLD, True
        round_rect(c, 10, 38, 136, 58, 9, fill=bg, outline="")
        if selected:
            fg = "#c9ffd4"
        elif clickable and not owned:
            fg = "#241a00"
        else:
            fg = TEXT
        c.create_text(73, 48, text=label, font=(self.app.font_ui, 8, "bold"),
                      fill=fg)
        self.clickable = clickable
        self.config(cursor="hand2" if clickable else "arrow")

    def _motion(self, event):
        if 124 <= event.x <= 146 and event.y <= 22:
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
            self.tip = win
        except tk.TclError:
            self.tip = None

    def _hide_tip(self):
        tip = self.tip
        self.tip = None
        if tip is not None:
            try:
                tip.destroy()
            except tk.TclError:
                pass

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
            self.app.commit()
            self.refresh("\u0412\u044b\u0431\u0440\u0430\u043d\u043e!")
            return
        if s["coins"] < self.item["price"]:
            self.refresh("\u041d\u0435 \u0445\u0432\u0430\u0442\u0430\u0435\u0442 \u043c\u043e\u043d\u0435\u0442!")
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
        check_achievements(s)
        self.app.commit()
        self.refresh(f"\u041a\u0443\u043f\u043b\u0435\u043d\u043e: {self.item['name']}!")


class ShopScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.mid = blend(BG, "#0f1d13", 0.55)
        self.bot = blend(BG, "#0f1d13", 0.85)
        self.bg = GradientBG(self, BG, "#0f1d13")
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=24, pady=(12, 0))
        tk.Label(head, text="\u041c\u0410\u0413\u0410\u0417\u0418\u041d", bg=BG, fg=ACCENT,
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

        self.inner = tk.Frame(self.scroller, bg=self.mid)
        self._win = self.scroller.create_window((0, 0), window=self.inner,
                                                anchor="nw", width=770)
        self.inner.bind("<Configure>",
                        lambda e: self.scroller.configure(
                            scrollregion=self.scroller.bbox("all")))
        self.scroller.bind("<Configure>", self._on_resize)
        self._cols = 5

        RoundButton(self, "\u2190  \u041d\u0430\u0437\u0430\u0434", lambda: app.show("MenuScreen"),
                    width=170, height=40, app_bg=self.bot,
                    font=(app.font_ui, 11, "bold")).pack(pady=(6, 10))

    def _on_resize(self, event):
        self.scroller.itemconfig(self._win,
                                 width=max(400, event.width - 22))
        cols = 5 if event.width >= 790 else 4
        if cols != self._cols:
            self._cols = cols
            self._rebuild()

    def on_show(self):
        self._rebuild()
        self.scroller.yview_moveto(0)
        self.bg.set_animated(not self.app.save.get("low_spec"))

    def on_hide(self):
        self.bg.set_animated(False)

    def _rebuild(self, status=""):
        self.coins_var.set(f"\u25c9  {self.app.save['coins']}")
        self.status_var.set(status)
        for w in self.inner.winfo_children():
            w.destroy()
        sections = [
            ("\u0426\u0432\u0435\u0442\u0430 \u0437\u043c\u0435\u0439\u043a\u0438", "color", COLORS),
            ("\u0424\u043e\u043d\u044b  (\u0434\u043e\u0440\u043e\u0436\u0435 \u0444\u043e\u043d \u2014 \u0432\u044b\u0448\u0435 \u043c\u043d\u043e\u0436\u0438\u0442\u0435\u043b\u044c \u043c\u043e\u043d\u0435\u0442)", "theme", THEMES),
            ("\u0415\u0434\u0430  (\u0434\u043e\u0440\u043e\u0436\u0435 \u0435\u0434\u0430 \u2014 \u0431\u043e\u043b\u044c\u0448\u0435 \u043e\u0447\u043a\u043e\u0432)", "food", FOOD_ITEMS),
            ("\u0410\u043a\u0441\u0435\u0441\u0441\u0443\u0430\u0440\u044b \u0434\u043b\u044f \u0433\u043e\u043b\u043e\u0432\u044b", "acc", ACCESSORIES),
        ]
        for title, kind, items in sections:
            head = tk.Canvas(self.inner, width=770, height=30, bg=self.mid,
                             highlightthickness=0)
            head.pack(pady=(10, 2))
            round_rect(head, 1, 1, 768, 29, 14, fill=PANEL, outline=BORDER)
            head.create_text(20, 15, text=title, anchor="w",
                             font=(self.app.font_ui, 11, "bold"), fill=ACCENT)
            grid = tk.Frame(self.inner, bg=self.mid)
            grid.pack()
            cols = self._cols
            for i, item in enumerate(items):
                card = ShopCard(grid, self.app, kind, item, self._rebuild,
                                card_bg=self.mid)
                card.grid(row=i // cols, column=i % cols, padx=3, pady=3,
                          sticky="nsew")


class SettingsScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.mid = blend(BG, "#0f1a26", 0.55)
        self.bot = blend(BG, "#0f1a26", 0.85)
        self.bg = GradientBG(self, BG, "#0f1a26", accent=BLUE)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Label(self, text="НАСТРОЙКИ", bg=BG, fg=ACCENT,
                 font=(app.font_title, 20, "bold")).pack(pady=(14, 2))
        self.preview = tk.Canvas(self, width=260, height=62, bg=BG,
                                 highlightthickness=0)
        self.preview.pack(pady=(2, 0))
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bg=BG, fg=DIM,
                 font=(app.font_ui, 10)).pack()

        body = tk.Frame(self, bg=self.mid)
        body.pack(fill="both", expand=True, padx=16)
        self.scroller = tk.Canvas(body, width=780, height=400, bg=self.mid,
                                  highlightthickness=0)
        bar = tk.Scrollbar(body, orient="vertical", command=self.scroller.yview)
        self.scroller.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.scroller.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.scroller, bg=self.mid)
        self._win = self.scroller.create_window((0, 0), window=self.inner,
                                                anchor="nw", width=770)
        self.inner.bind("<Configure>",
                        lambda e: self.scroller.configure(
                            scrollregion=self.scroller.bbox("all")))
        self.scroller.bind("<Configure>", self._on_resize)

        self._section("Цвет змейки")
        self.grid_frame = tk.Frame(self.inner, bg=self.mid)
        self.grid_frame.pack(padx=20)

        self._section("Сложность")
        self.diff_frame = tk.Frame(self.inner, bg=self.mid)
        self.diff_frame.pack()
        self.diff_info_var = tk.StringVar()
        tk.Label(self.inner, textvariable=self.diff_info_var, bg=self.mid, fg=WARN,
                 font=(app.font_ui, 10)).pack(pady=(4, 0))

        self._section("Размер экрана")
        self.size_frame = tk.Frame(self.inner, bg=self.mid)
        self.size_frame.pack()

        self._section("Производительность")
        self.low_btn = RoundButton(
            self.inner, "", self._toggle_low, width=380, height=42,
            app_bg=self.mid, font=(app.font_ui, 10, "bold"))
        self.low_btn.pack(pady=(2, 4))
        self.sound_btn = RoundButton(
            self.inner, "", self._toggle_sound, width=380, height=42,
            app_bg=self.mid, font=(app.font_ui, 10, "bold"))
        self.sound_btn.pack(pady=(2, 4))
        self.music_btn = RoundButton(
            self.inner, "", self._toggle_music, width=380, height=42,
            app_bg=self.mid, font=(app.font_ui, 10, "bold"))
        self.music_btn.pack(pady=(2, 4))
        tk.Label(self.inner,
                 text="Упрощает фон и графику для слабых устройств,"
                      " не меняя правила игры",
                 bg=self.mid, fg=DIM, font=(app.font_ui, 9)).pack()

        RoundButton(self, "←  Назад", lambda: app.show("MenuScreen"),
                    width=170, height=40, app_bg=self.bot,
                    font=(app.font_ui, 11, "bold")).pack(pady=(6, 10))

    def on_show(self):
        self._rebuild()
        self.bg.set_animated(not self.app.save.get("low_spec"))
        self.scroller.yview_moveto(0)

    def on_hide(self):
        self.bg.set_animated(False)

    def _on_resize(self, event):
        self.scroller.itemconfig(self._win, width=max(400, event.width - 22))

    def _section(self, title):
        cv = tk.Canvas(self.inner, width=340, height=30, bg=self.mid,
                       highlightthickness=0)
        cv.pack(pady=(10, 2))
        round_rect(cv, 1, 1, 338, 29, 14, fill=PANEL, outline=BORDER)
        cv.create_text(170, 15, text=title,
                       font=(self.app.font_ui, 11, "bold"), fill=ACCENT)

    def _paint_low(self):
        on = bool(self.app.save.get("low_spec", False))
        btn = self.low_btn
        btn.text = ("Режим для слабых устройств:  ВКЛ ✓" if on
                    else "Режим для слабых устройств:  ВЫКЛ ✗")
        btn.base_bg = ACCENT_DARK if on else PANEL
        btn.base_fg = "#c9ffd4" if on else TEXT
        btn.hover_bg = blend(btn.base_bg, "#ffffff", 0.12)
        btn.press_bg = blend(btn.base_bg, "#000000", 0.18)
        btn.repaint()

    def _toggle_low(self):
        self.app.save["low_spec"] = not self.app.save.get("low_spec", False)
        self.app.commit()
        self._paint_low()

    def _paint_sound(self):
        on = bool(self.app.save.get("sound", True))
        btn = self.sound_btn
        btn.text = ("Звуковые эффекты:  ВКЛ ✓" if on
                    else "Звуковые эффекты:  ВЫКЛ ✗")
        btn.base_bg = ACCENT_DARK if on else PANEL
        btn.base_fg = "#c9ffd4" if on else TEXT
        btn.hover_bg = blend(btn.base_bg, "#ffffff", 0.12)
        btn.press_bg = blend(btn.base_bg, "#000000", 0.18)
        btn.repaint()

    def _toggle_sound(self):
        self.app.save["sound"] = not self.app.save.get("sound", True)
        self.app.commit()
        self._paint_sound()

    def _paint_music(self):
        on = bool(self.app.save.get("music", True))
        btn = self.music_btn
        btn.text = "Фоновая музыка:  ВКЛ ✓" if on \
            else "Фоновая музыка:  ВЫКЛ ✗"
        btn.base_bg = ACCENT_DARK if on else PANEL
        btn.base_fg = "#c9ffd4" if on else TEXT
        btn.hover_bg = blend(btn.base_bg, "#ffffff", 0.12)
        btn.press_bg = blend(btn.base_bg, "#000000", 0.18)
        btn.repaint()

    def _toggle_music(self):
        on = not self.app.save.get("music", True)
        self.app.save["music"] = on
        self.app.commit()
        self._paint_music()
        snd = getattr(self.app, "sound", None)
        if snd is not None:
            snd.set_music(on)

    def _rebuild(self, status=""):
        self.status_var.set(status)
        self._paint_low()
        self._paint_sound()
        self._paint_music()
        p = self.preview
        p.delete("all")
        sel = self.app.save.get("selected", ACCENT)
        acc = self.app.save.get("accessory", "none")
        for i in range(3):
            x = 104 + i * 40
            color = seg_color(sel, i, 3, 0)
            round_rect(p, x - 15, 26, x + 15, 54, 8, fill=color, outline="")
        ring = (blend(GRADIENTS[sel][1], "#ffffff", 0.3) if sel in GRADIENTS
                else hsv_hex(0.0, 0.85, 0.95) if sel == "rainbow"
                else blend(sel, "#ffffff", 0.5))
        p.create_oval(87, 22, 121, 58, outline=ring, width=2)
        if acc != "none":
            draw_acc(p, 104, 40, acc)
        for w in self.grid_frame.winfo_children():
            w.destroy()
        owned_items = [it for it in COLORS if it["id"] in self.app.save["owned"]]
        for i, item in enumerate(owned_items):
            card = ShopCard(self.grid_frame, self.app, "color", item,
                            self._rebuild, card_bg=self.mid)
            card.grid(row=i // 5, column=i % 5, padx=4, pady=4, sticky="nsew")
        level = level_from_exp(self.app.save.get("exp", 0))
        for w in self.diff_frame.winfo_children():
            w.destroy()
        current = self.app.save.get("speed", "normal")
        if DIFFICULTIES.get(current, DIFFICULTIES["normal"])["level"] > level:
            current = "normal"
        cfg = DIFFICULTIES[current]
        for key, dcfg in DIFFICULTIES.items():
            if dcfg["level"] > level:
                btn = RoundButton(self.diff_frame, f"🔒 ур. {dcfg['level']}",
                                  width=126, height=42, bg=LOCKED_BG, fg=DIM,
                                  app_bg=self.mid,
                                  font=(self.app.font_ui, 10, "bold"))
            else:
                selected = key == current
                btn = RoundButton(
                    self.diff_frame, dcfg["label"],
                    command=(lambda k=key: self._set_speed(k)),
                    width=126, height=42,
                    bg=ACCENT_DARK if selected else PANEL,
                    fg="#c9ffd4" if selected else TEXT, app_bg=self.mid,
                    font=(self.app.font_ui, 10, "bold"))
            btn.pack(side="left", padx=4)
        for w in self.size_frame.winfo_children():
            w.destroy()
        cur_size = self.app.save.get("window_size", "medium")
        if cur_size not in WINDOW_SIZES:
            cur_size = "medium"
        for key in WINDOW_SIZE_ORDER:
            w_, h_ = WINDOW_SIZES[key]
            selected = key == cur_size
            btn = RoundButton(
                self.size_frame, f"{WINDOW_SIZE_LABELS[key]}  {w_}\u00d7{h_}",
                command=(lambda k=key: self._set_size(k)),
                width=150, height=42,
                bg=ACCENT_DARK if selected else PANEL,
                fg="#c9ffd4" if selected else TEXT, app_bg=self.mid,
                font=(self.app.font_ui, 10, "bold"))
            btn.pack(side="left", padx=4)
        theme = THEME_BY_ID.get(self.app.save.get("theme"), THEMES[0])
        total_c = cfg["reward"] * theme.get("bonus", 1.0)
        total_e = cfg["exp_reward"] * theme.get("bonus", 1.0)
        self.diff_info_var.set((cfg["note"] or "классические правила")
                               + f"  ·  монеты ×{total_c:g}  ·  опыт ×{total_e:g}")

    def _set_speed(self, key):
        level = level_from_exp(self.app.save.get("exp", 0))
        if DIFFICULTIES[key]["level"] > level:
            return
        self.app.save["speed"] = key
        self.app.commit()
        self._rebuild()

    def _set_size(self, key):
        self.app.set_window_size(key)
        self._rebuild()


class MiniScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.mid = blend(BG, "#0c1a30", 0.55)
        self.bot = blend(BG, "#0c1a30", 0.85)
        self.bg = GradientBG(self, BG, "#0c1a30", accent=BLUE)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Label(self, text="МИНИ-ИГРЫ", bg=BG, fg=BLUE,
                 font=(app.font_title, 20, "bold")).pack(pady=(12, 2))
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bg=BG, fg=DIM,
                 font=(app.font_ui, 10)).pack()
        self.card_holder = tk.Frame(self, bg=self.mid)
        self.card_holder.pack(pady=6, expand=True)
        RoundButton(self, "←  Назад", lambda: app.show("MenuScreen"),
                    width=170, height=40, app_bg=self.bot,
                    font=(app.font_ui, 11, "bold")).pack(pady=(6, 8))

    def on_show(self):
        self._rebuild()
        self.bg.set_animated(not self.app.save.get("low_spec"))

    def on_hide(self):
        self.bg.set_animated(False)

    def _stats(self):
        st = self.app.save.get("stats")
        return st if isinstance(st, dict) else {}

    def _rebuild(self, status=""):
        self.status_var.set(status)
        for w in self.card_holder.winfo_children():
            w.destroy()
        self._card_mg1()
        self._card_mg2()
        self._card_mg3()

    def _card_base(self, height):
        card = tk.Canvas(self.card_holder, width=700, height=height,
                         bg=self.mid, highlightthickness=0)
        card.pack(pady=4)
        round_rect(card, 1, 1, 698, height - 1, 16, fill=PANEL, outline=BLUE)
        round_rect(card, 9, 12, 14, height - 12, 3, fill=BLUE, outline="")
        return card

    def _play_btn(self, card, mg_key, x, y):
        btn = RoundButton(card, "ИГРАТЬ", lambda: self._play(mg_key),
                          width=130, height=42, bg=BLUE, fg="#061224",
                          app_bg=PANEL, font=(self.app.font_ui, 12, "bold"))
        card.create_window(x, y, window=btn)

    def _card_mg1(self):
        card = self._card_base(176)
        card.create_text(26, 30, text="🍎  СБОР ЯБЛОК", anchor="w",
                         font=(self.app.font_title, 15, "bold"), fill=BLUE)
        card.create_text(26, 58, text="Собери как можно больше яблок за отведённое время!",
                         anchor="w", font=(self.app.font_ui, 10, "bold"), fill=TEXT)
        card.create_text(26, 77, text="Препятствия и скорость зависят от сложности · границы проходимы",
                         anchor="w", font=(self.app.font_ui, 9), fill=DIM)
        mg1_best = self._stats().get("mg1_best", 0)
        card.create_text(26, 97, text=f"Рекорд: {mg1_best} яблок",
                         anchor="w", font=(self.app.font_ui, 11, "bold"), fill=GOLD)
        level = level_from_exp(self.app.save.get("exp", 0))
        current = self.app.save.get("mg1_diff", "normal")
        if current not in MINIGAMES["mg1"]["diffs"]:
            current = "normal"
        if MINIGAMES["mg1"]["diffs"][current]["level"] > level:
            current = "normal"
        row = tk.Frame(card, bg=PANEL)
        card.create_window(26, 140, window=row, anchor="w")
        for key in MG_DIFF_ORDER:
            dcfg = MINIGAMES["mg1"]["diffs"][key]
            if dcfg["level"] > level:
                btn = RoundButton(row, f"🔒 ур. {dcfg['level']}", width=118,
                                  height=32, bg=LOCKED_BG, fg=DIM, app_bg=PANEL,
                                  font=(self.app.font_ui, 9, "bold"))
            else:
                selected = key == current
                btn = RoundButton(
                    row, f"{DIFFICULTIES[key]['label']} · {dcfg['time']}с",
                    command=(lambda k=key: self._set_mg_diff(k)),
                    width=118, height=32,
                    bg=ACCENT_DARK if selected else "#1c2f4a",
                    fg="#c9ffd4" if selected else TEXT, app_bg=PANEL,
                    font=(self.app.font_ui, 9, "bold"))
            btn.pack(side="left", padx=3)
        self._play_btn(card, "mg1", 622, 96)

    def _card_mg2(self):
        card = self._card_base(122)
        card.create_text(26, 28, text="🧠  ПОПРОБУЙ ЗАПОМНИТЬ!", anchor="w",
                         font=(self.app.font_title, 15, "bold"), fill=BLUE)
        card.create_text(26, 54, text="Запомни цвет фрукта и найди его среди 8 оттенков!",
                         anchor="w", font=(self.app.font_ui, 10, "bold"), fill=TEXT)
        card.create_text(26, 73, text="Победа: 10 монет × множитель · неверный цвет — поражение",
                         anchor="w", font=(self.app.font_ui, 9), fill=DIM)
        wins = self._stats().get("mg2_wins", 0)
        card.create_text(26, 94, text=f"Побед: {wins}",
                         anchor="w", font=(self.app.font_ui, 11, "bold"), fill=GOLD)
        self._play_btn(card, "mg2", 622, 66)

    def _card_mg3(self):
        card = self._card_base(122)
        card.create_text(26, 28, text="🧺  ЯБЛОЧНЫЙ СБОР", anchor="w",
                         font=(self.app.font_title, 15, "bold"), fill=BLUE)
        card.create_text(26, 54, text="Приноси яблоки в зону сбора — размер змейки не меняется!",
                         anchor="w", font=(self.app.font_ui, 10, "bold"), fill=TEXT)
        card.create_text(26, 73, text="+12 монет за каждое яблоко × множитель · 60 секунд · граница — в начало",
                         anchor="w", font=(self.app.font_ui, 9), fill=DIM)
        mg3_best = self._stats().get("mg3_best", 0)
        card.create_text(26, 94, text=f"Рекорд: {mg3_best} яблок",
                         anchor="w", font=(self.app.font_ui, 11, "bold"), fill=GOLD)
        self._play_btn(card, "mg3", 622, 66)

    def _set_mg_diff(self, key):
        level = level_from_exp(self.app.save.get("exp", 0))
        if MINIGAMES["mg1"]["diffs"][key]["level"] > level:
            return
        self.app.save["mg1_diff"] = key
        self.app.commit()
        self._rebuild()

    def _play(self, mg_key):
        self.app.next_mode = mg_key
        if mg_key == "mg1":
            diff = self.app.save.get("mg1_diff", "normal")
            self.app.next_diff = (diff if diff in MINIGAMES["mg1"]["diffs"]
                                  else "normal")
        else:
            self.app.next_diff = "normal"
        self.app.show("GameScreen")

class AchCard(tk.Canvas):
    def __init__(self, master, app, ach, card_bg=BG):
        super().__init__(master, width=750, height=56, bg=card_bg,
                         highlightthickness=0)
        self.app = app
        self.ach = ach
        self._paint()

    def _paint(self):
        c = self
        ach = self.ach
        c.delete("all")
        done = ach["id"] in self.app.save.get("ach_done", [])
        val = ach_value(ach, self.app.save)
        goal = ach["goal"]
        frac = max(0.0, min(1.0, val / goal))
        round_rect(c, 1, 1, 749, 55, 13, fill=PANEL,
                   outline="#8957e5" if done else BORDER)
        c.create_oval(10, 10, 46, 46, fill="#8957e5" if done else "#3a2a5e",
                      outline="#a371f7")
        c.create_text(28, 28, text="✓" if done else "★",
                      font=(self.app.font_title, 14, "bold"),
                      fill="#ffffff" if done else "#c9a8ff")
        c.create_text(56, 16, text=ach["name"], anchor="w",
                      font=(self.app.font_ui, 10, "bold"),
                      fill="#e2d5ff" if done else TEXT)
        c.create_text(56, 32, text=ach["desc"], anchor="w",
                      font=(self.app.font_ui, 8), fill=DIM)
        round_rect(c, 56, 42, 356, 50, 4, fill=LOCKED_BG, outline="")
        if frac > 0:
            round_rect(c, 56, 42, int(56 + max(6, 300 * frac)), 50, 4,
                       fill="#a371f7", outline="")
        c.create_text(366, 46, text=f"{min(val, goal)}/{goal}", anchor="w",
                      font=(self.app.font_ui, 8, "bold"), fill=DIM)
        c.create_text(738, 20, text=f"🎁  {ach_reward_text(ach)}", anchor="e",
                      font=(self.app.font_ui, 9, "bold"), fill=GOLD)
        if done:
            c.create_text(738, 38, text="ПОЛУЧЕНО ✓", anchor="e",
                          font=(self.app.font_ui, 9, "bold"), fill="#7ee787")


class AchScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.mid = blend(BG, "#160f28", 0.55)
        self.bot = blend(BG, "#160f28", 0.85)
        self.bg = GradientBG(self, BG, "#160f28", accent="#8957e5")
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=24, pady=(12, 0))
        tk.Label(head, text="ДОСТИЖЕНИЯ", bg=BG, fg="#c9a8ff",
                 font=(app.font_title, 20, "bold")).pack(side="left")
        self.count_var = tk.StringVar()
        tk.Label(head, textvariable=self.count_var, bg=BG, fg="#a371f7",
                 font=(app.font_ui, 13, "bold")).pack(side="right")
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bg=BG, fg=DIM,
                 font=(app.font_ui, 10)).pack()
        self.prog = tk.Canvas(self, width=420, height=14, bg=BG,
                              highlightthickness=0)
        self.prog.pack(pady=(2, 0))
        body = tk.Frame(self, bg=self.mid)
        body.pack(fill="both", expand=True, padx=24)
        self.scroller = tk.Canvas(body, width=770, height=520, bg=self.mid,
                                  highlightthickness=0)
        bar = tk.Scrollbar(body, orient="vertical", command=self.scroller.yview)
        self.scroller.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.scroller.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.scroller, bg=self.mid)
        self._win = self.scroller.create_window((0, 0), window=self.inner,
                                                anchor="nw", width=754)
        self.inner.bind("<Configure>",
                        lambda e: self.scroller.configure(
                            scrollregion=self.scroller.bbox("all")))
        self.scroller.bind("<Configure>", self._on_resize)
        RoundButton(self, "←  Назад", lambda: app.show("MenuScreen"),
                    width=170, height=40, app_bg=self.bot,
                    font=(app.font_ui, 11, "bold")).pack(pady=(6, 10))

    def on_show(self):
        self._rebuild()
        self.bg.set_animated(not self.app.save.get("low_spec"))
        self.scroller.yview_moveto(0)

    def on_hide(self):
        self.bg.set_animated(False)

    def _on_resize(self, event):
        self.scroller.itemconfig(self._win, width=max(400, event.width - 22))

    def _rebuild(self, status=""):
        self.status_var.set(status)
        done = self.app.save.get("ach_done", [])
        self.count_var.set(f"{len(done)} / {len(ACHIEVEMENTS)}")
        frac = len(done) / max(1, len(ACHIEVEMENTS))
        p = self.prog
        p.delete("all")
        round_rect(p, 1, 1, 418, 13, 6, fill=LOCKED_BG, outline=BORDER)
        if frac > 0:
            width = max(14, round(418 * frac))
            seg_w = width / 5
            for k in range(5):
                col = blend("#8957e5", "#c9a8ff", k / 4)
                round_rect(p, 1 + k * seg_w, 1, 1 + (k + 1) * seg_w, 13, 5,
                           fill=col, outline="")
        for w in self.inner.winfo_children():
            w.destroy()
        for ach in ACHIEVEMENTS:
            AchCard(self.inner, self.app, ach, card_bg=self.mid).pack(
                fill="x", pady=3)


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
        global SOUND
        self.sound = SoundManager(self.save)
        SOUND = self.sound
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
    App().mainloop()
