#!/usr/bin/env python3
"""
Генератор визуальных материалов для ПЗ по проекту «Тэона».
Скрипт создает SVG-файлы с диаграммами, wireframe-экранов, схемами БД и code screenshots.
"""

from __future__ import annotations

from pathlib import Path
from html import escape
import textwrap


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "PZ_Assets_Teona"


COLORS = {
    "bg": "#ffffff",
    "text": "#202124",
    "muted": "#6b7280",
    "line": "#374151",
    "light": "#d1d5db",
    "panel": "#f8fafc",
    "panel2": "#eef2f7",
    "accent": "#fd6000",
    "accent_soft": "#fff1e8",
    "success": "#16a34a",
    "warning": "#f59e0b",
    "danger": "#dc2626",
    "dark": "#111827",
    "dark2": "#1f2937",
    "code": "#0b1020",
    "code_text": "#e5e7eb",
    "code_muted": "#94a3b8",
    "code_title": "#f8fafc",
}


def ensure_dirs() -> dict[str, Path]:
    dirs = {
        "usecases": ASSETS / "01_Диаграммы_вариантов_использования",
        "diagrams": ASSETS / "02_Диаграммы_и_схемы",
        "algorithms": ASSETS / "03_Алгоритмы",
        "screens": ASSETS / "04_Экранные_формы",
        "database": ASSETS / "05_База_данных",
        "code": ASSETS / "06_Код",
        "tests": ASSETS / "07_Тесты",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def svg_start(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{COLORS["bg"]}"/>',
        """
        <defs>
          <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#374151" />
          </marker>
          <marker id="arrowAccent" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#fd6000" />
          </marker>
        </defs>
        """,
    ]


def svg_end(body: list[str]) -> str:
    return "\n".join(body + ["</svg>"])


def save_svg(path: Path, width: int, height: int, body: list[str]) -> None:
    path.write_text(svg_end(svg_start(width, height) + body), encoding="utf-8")


def text(x: int, y: int, value: str, size: int = 18, weight: str = "400", fill: str | None = None, anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" font-family="Inter, Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill or COLORS["text"]}" text-anchor="{anchor}">{escape(value)}</text>'


def multiline_text(x: int, y: int, value: str, width_chars: int = 36, size: int = 16, line_height: int = 22, weight: str = "400", fill: str | None = None) -> list[str]:
    lines: list[str] = []
    yy = y
    for raw in value.split("\n"):
        wrapped = textwrap.wrap(raw, width=width_chars) or [""]
        for line in wrapped:
            lines.append(text(x, yy, line, size=size, weight=weight, fill=fill))
            yy += line_height
    return lines


def rect(x: int, y: int, w: int, h: int, fill: str, stroke: str = "#374151", rx: int = 12, sw: int = 2) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def ellipse(x: int, y: int, rx: int, ry: int, fill: str, stroke: str = "#374151", sw: int = 2) -> str:
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def line(x1: int, y1: int, x2: int, y2: int, stroke: str = "#374151", sw: int = 2, dash: str | None = None, marker: bool = False) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    marker_attr = ' marker-end="url(#arrow)"' if marker else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{dash_attr}{marker_attr}/>'


def arrow(x1: int, y1: int, x2: int, y2: int, accent: bool = False, dash: str | None = None) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    marker_id = "arrowAccent" if accent else "arrow"
    stroke = COLORS["accent"] if accent else COLORS["line"]
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="2"{dash_attr} marker-end="url(#{marker_id})"/>'


def actor(x: int, y: int, label: str) -> list[str]:
    return [
        f'<circle cx="{x}" cy="{y}" r="18" fill="#fff" stroke="{COLORS["line"]}" stroke-width="2"/>',
        line(x, y + 18, x, y + 70),
        line(x - 24, y + 38, x + 24, y + 38),
        line(x, y + 70, x - 22, y + 100),
        line(x, y + 70, x + 22, y + 100),
        text(x, y + 128, label, size=17, anchor="middle"),
    ]


def usecase(x: int, y: int, w: int, h: int, label: str) -> list[str]:
    lines = [ellipse(x + w // 2, y + h // 2, w // 2, h // 2, "#fff7ed", stroke=COLORS["accent"])]
    ty = y + h // 2 - 10 * (label.count("\n"))
    for i, part in enumerate(label.split("\n")):
        lines.append(text(x + w // 2, ty + i * 20, part, size=15, anchor="middle"))
    return lines


def db_box(x: int, y: int, title_value: str, fields: list[str], width: int = 320) -> list[str]:
    header_h = 36
    row_h = 22
    h = header_h + len(fields) * row_h + 16
    body = [
        rect(x, y, width, h, "#ffffff", stroke=COLORS["line"], rx=10),
        rect(x, y, width, header_h, COLORS["accent_soft"], stroke=COLORS["line"], rx=10),
        text(x + 14, y + 24, title_value, size=17, weight="700"),
    ]
    for i, field in enumerate(fields):
        yy = y + header_h + 18 + i * row_h
        body.append(text(x + 16, yy, field, size=14, fill=COLORS["text"]))
        if i < len(fields) - 1:
            body.append(line(x + 10, yy + 8, x + width - 10, yy + 8, stroke=COLORS["light"], sw=1))
    return body


def footer_caption(width: int, height: int, caption: str) -> list[str]:
    return [
        line(40, height - 42, width - 40, height - 42, stroke=COLORS["light"], sw=1),
        text(width // 2, height - 14, caption, size=18, weight="600", anchor="middle"),
    ]


def screen_header(title_value: str, width: int = 1440, height: int = 900) -> list[str]:
    return [
        rect(18, 18, width - 36, height - 86, "#ffffff", stroke=COLORS["light"], rx=18),
        rect(18, 18, width - 36, 58, "#f8fafc", stroke=COLORS["light"], rx=18),
        text(48, 54, title_value, size=24, weight="700"),
    ]


def panel(x: int, y: int, w: int, h: int, title_value: str | None = None) -> list[str]:
    items = [rect(x, y, w, h, "#ffffff", stroke=COLORS["light"], rx=16)]
    if title_value:
        items.append(text(x + 18, y + 28, title_value, size=20, weight="700"))
    return items


def code_svg(output: Path, caption: str, snippets: list[tuple[str, Path, list[tuple[int, int]]]], width: int = 1600) -> None:
    panel_gap = 26
    top = 28
    title_h = 42
    line_h = 20
    margin = 18
    total_lines = 0
    rendered: list[tuple[str, list[str]]] = []
    for label, path, ranges in snippets:
        raw_lines = path.read_text(encoding="utf-8").splitlines()
        out_lines = [f"{label}"]
        for start, end in ranges:
            out_lines.append(f"--- {path.as_posix().replace(str(ROOT) + '/', '')}:{start}-{end} ---")
            for idx in range(start, min(end, len(raw_lines)) + 1):
                out_lines.append(f"{idx:>4}  {raw_lines[idx - 1]}")
            out_lines.append("")
        rendered.append((label, out_lines))
        total_lines += len(out_lines)
    height = 90 + total_lines * line_h + len(snippets) * panel_gap + 60
    body: list[str] = []
    y = top
    for label, lines_block in rendered:
        panel_h = title_h + len(lines_block) * line_h + 20
        body.append(rect(24, y, width - 48, panel_h, COLORS["code"], stroke=COLORS["dark2"], rx=18))
        body.append(rect(24, y, width - 48, title_h, COLORS["dark2"], stroke=COLORS["dark2"], rx=18))
        body.append(text(44, y + 28, label, size=18, weight="700", fill=COLORS["code_title"]))
        yy = y + 62
        for line_value in lines_block:
            fill = COLORS["code_muted"] if line_value.startswith("---") else COLORS["code_text"]
            body.append(f'<text x="{margin + 32}" y="{yy}" font-family="Menlo, Consolas, monospace" font-size="14" fill="{fill}">{escape(line_value[:180])}</text>')
            yy += line_h
        y += panel_h + panel_gap
    body.extend(footer_caption(width, height, caption))
    save_svg(output, width, height, body)


def terminal_svg(output: Path, caption: str, content: str, width: int = 1600) -> None:
    lines = content.strip("\n").splitlines()
    line_h = 20
    height = 90 + len(lines) * line_h + 60
    body = [
        rect(24, 24, width - 48, height - 100, COLORS["code"], stroke=COLORS["dark2"], rx=18),
        rect(24, 24, width - 48, 40, COLORS["dark2"], stroke=COLORS["dark2"], rx=18),
        text(44, 50, "terminal", size=18, weight="700", fill=COLORS["code_title"]),
    ]
    yy = 92
    for line_value in lines:
        body.append(f'<text x="42" y="{yy}" font-family="Menlo, Consolas, monospace" font-size="14" fill="{COLORS["code_text"]}">{escape(line_value[:185])}</text>')
        yy += line_h
    body.extend(footer_caption(width, height, caption))
    save_svg(output, width, height, body)


def write_readme() -> None:
    readme = ASSETS / "README.md"
    readme.write_text(
        """# PZ Assets Teona

Папка содержит готовые визуальные материалы для пояснительной записки по проекту `Тэона`.

## Структура

- `01_Диаграммы_вариантов_использования` — рисунки 1–5;
- `02_Диаграммы_и_схемы` — рисунки 6–10 и 24;
- `03_Алгоритмы` — рисунки 11–15;
- `04_Экранные_формы` — рисунки 16–21;
- `05_База_данных` — рисунки 22–23 и дополнительная полная схема БД;
- `06_Код` — рисунки `В.1–В.4`;
- `07_Тесты` — рисунки 25–27.

## Важно

- Все файлы подписаны номером рисунка, чтобы их было легко вставлять в Word.
- Формат файлов — `SVG`.
- Экранные формы сделаны как аккуратные wireframe-макеты.
- Реальные UI-скриншоты не были сняты автоматически, потому что на момент генерации не был запущен Docker daemon.
- Code screenshots собраны из реальных файлов проекта и соответствуют текущему коду.

## Порядок вставки

1. Рисунки 1–15 и 24 вставлять в основной текст ПЗ.
2. Рисунки 16–21 вставлять в подраздел про экранные формы.
3. Рисунки 22–23 вставлять в подраздел про разработку базы данных.
4. Рисунки `В.1–В.4` вставлять в приложение В.
5. Рисунки 25–27 вставлять в подраздел про модульное тестирование.
""",
        encoding="utf-8",
    )


def build_use_case_overview(path: Path) -> None:
    width, height = 1500, 980
    body: list[str] = []
    body.extend(actor(110, 160, "Риелтор"))
    body.append(rect(250, 60, 1180, 820, "#ffffff", stroke=COLORS["line"], rx=24))
    body.append(text(280, 100, "Система «Тэона»", size=22, weight="700"))
    items = [
        (340, 150, 220, 70, "Авторизоваться\nв системе"),
        (640, 150, 220, 70, "Просмотреть\ndashboard"),
        (940, 150, 220, 70, "Создать карточку\nклиента"),
        (1240, 150, 220, 70, "Изменить карточку\nклиента"),
        (340, 310, 220, 70, "Запустить поиск\nобъектов"),
        (640, 310, 220, 70, "Просмотреть найденные\nобъекты"),
        (940, 310, 220, 70, "Открыть подробности\nобъекта"),
        (1240, 310, 220, 70, "Добавить объект\nв подборку"),
        (490, 500, 220, 70, "Удалить объект\nиз подборки"),
        (790, 500, 220, 70, "Сформировать текст\nсообщения"),
        (1090, 500, 220, 70, "Отметить подборку\nкак отправленную"),
    ]
    centers: dict[str, tuple[int, int]] = {}
    for x, y, w, h, label in items:
        body.extend(usecase(x, y, w, h, label))
        centers[label] = (x + w // 2, y + h // 2)
        if label in {"Авторизоваться\nв системе", "Просмотреть\ndashboard", "Создать карточку\nклиента", "Изменить карточку\nклиента", "Запустить поиск\nобъектов", "Просмотреть найденные\nобъекты", "Добавить объект\nв подборку", "Сформировать текст\nсообщения", "Отметить подборку\nкак отправленную"}:
            body.append(line(134, 180, x, y + h // 2, stroke=COLORS["light"], sw=2))
    body.append(arrow(1050, 220, 1050, 310, accent=True, dash="6,4"))
    body.append(text(1070, 272, "<<include>>", size=14, fill=COLORS["accent"]))
    body.append(arrow(750, 380, 1050, 345, accent=True, dash="6,4"))
    body.append(text(860, 350, "<<extend>>", size=14, fill=COLORS["accent"]))
    body.append(arrow(1350, 380, 900, 500, accent=True, dash="6,4"))
    body.append(text(1120, 450, "<<include>>", size=14, fill=COLORS["accent"]))
    body.append(arrow(900, 570, 1200, 535, accent=True, dash="6,4"))
    body.append(text(1020, 520, "<<extend>>", size=14, fill=COLORS["accent"]))
    body.extend(footer_caption(width, height, "Рисунок 1 – Общая диаграмма вариантов использования программных модулей системы «Тэона»"))
    save_svg(path, width, height, body)


def build_use_case_module(path: Path, caption: str, title_value: str, items: list[str], includes: list[tuple[int, int, str]]) -> None:
    width, height = 1400, 900
    body: list[str] = []
    body.extend(actor(110, 170, "Риелтор"))
    body.append(rect(250, 70, 1080, 720, "#ffffff", stroke=COLORS["line"], rx=24))
    body.append(text(280, 110, title_value, size=22, weight="700"))
    coords = [(350, 180), (760, 180), (1160, 180), (350, 390), (760, 390), (1160, 390)]
    centers: list[tuple[int, int]] = []
    for idx, label in enumerate(items):
        x, y = coords[idx]
        body.extend(usecase(x, y, 240, 78, label.replace(" / ", "\n")))
        centers.append((x + 120, y + 39))
        if idx in {0, 1, 3, 4}:
            body.append(line(134, 190, x, y + 39, stroke=COLORS["light"], sw=2))
    for a, b, tag in includes:
        x1, y1 = centers[a]
        x2, y2 = centers[b]
        body.append(arrow(x1, y1 + 44, x2, y2 - 44, accent=True, dash="6,4"))
        body.append(text((x1 + x2) // 2 + 12, (y1 + y2) // 2, tag, size=14, fill=COLORS["accent"]))
    body.extend(footer_caption(width, height, caption))
    save_svg(path, width, height, body)


def build_activity(path: Path) -> None:
    width, height = 1660, 1760
    body: list[str] = []
    body.append(text(80, 70, "Диаграмма деятельности подбора объектов недвижимости по профилю клиента", size=28, weight="700"))
    lane_x = [40, 420, 800, 1180]
    lane_w = 340
    lane_titles = ["Риелтор", "API Server", "Search Service", "PostgreSQL"]
    for idx, title_value in enumerate(lane_titles):
        x = lane_x[idx]
        body.append(rect(x, 110, lane_w, 1460, "#ffffff", stroke=COLORS["light"], rx=18))
        body.append(rect(x, 110, lane_w, 56, COLORS["panel"], stroke=COLORS["light"], rx=18))
        body.append(text(x + lane_w // 2, 146, title_value, size=20, weight="700", anchor="middle"))

    nodes = [
        ("start", 170, 205, 210, 50, "Начало"),
        ("box", 90, 250, 240, 68, "Открыть форму нового клиента"),
        ("box", 90, 360, 240, 86, "Заполнить данные клиента и критерии поиска"),
        ("box", 470, 360, 240, 86, "Проверить обязательные поля и тип недвижимости"),
        ("diamond", 470, 500, 240, 110, "Данные формы\nкорректны?"),
        ("box", 470, 660, 240, 84, "Сохранить clients и client_search_profiles"),
        ("box", 1230, 660, 240, 84, "Подтвердить запись клиента и профиля"),
        ("box", 470, 790, 240, 84, "Создать search_run и статус searching"),
        ("box", 850, 790, 240, 84, "Принять запрос поиска по профилю клиента"),
        ("box", 850, 920, 240, 84, "Выбрать SourceConfig и стартовые URL"),
        ("box", 850, 1050, 240, 84, "Загрузить HTML, JSON-LD и карточки объявлений"),
        ("diamond", 850, 1180, 240, 110, "Есть price,\nsourceUrl и тип\nобъекта?"),
        ("diamond", 850, 1320, 240, 110, "Объект относится\nк Краснодару или\nрайону города?"),
        ("box", 850, 1460, 240, 84, "Нормализовать, рассчитать matchScore и причины"),
        ("box", 470, 1460, 240, 84, "Сохранить property и client_found_property"),
        ("box", 1230, 1460, 240, 84, "Зафиксировать total_found, total_saved и завершение"),
        ("start", 1330, 1605, 120, 50, "Конец"),
    ]
    centers: dict[str, tuple[int, int, int, int]] = {}
    for kind, x, y, w, h, label in nodes:
        if kind == "start":
            body.append(f'<circle cx="{x+w//2}" cy="{y+h//2}" r="22" fill="{COLORS["accent_soft"]}" stroke="{COLORS["accent"]}" stroke-width="2"/>')
            body.append(text(x + w // 2, y + h // 2 + 6, label, size=15, anchor="middle"))
        elif kind == "diamond":
            points = f"{x+w//2},{y} {x+w},{y+h//2} {x+w//2},{y+h} {x},{y+h//2}"
            body.append(f'<polygon points="{points}" fill="#fff7ed" stroke="{COLORS["accent"]}" stroke-width="2"/>')
            body.extend(multiline_text(x + 46, y + 44, label, width_chars=16, size=15, line_height=18))
        else:
            body.append(rect(x, y, w, h, "#ffffff", stroke=COLORS["line"], rx=14))
            body.extend(multiline_text(x + 20, y + 38, label, width_chars=22, size=16, line_height=19))
        centers[label] = (x, y, w, h)

    def mid(label: str) -> tuple[int, int]:
        x, y, w, h = centers[label]
        return x + w // 2, y + h // 2

    body.append(arrow(*mid("Начало"), 210, 250))
    body.append(arrow(210, 318, 210, 360))
    body.append(arrow(330, 403, 470, 403))
    body.append(arrow(590, 446, 590, 500))
    body.append(arrow(590, 610, 590, 660))
    body.append(text(612, 640, "да", size=14, fill=COLORS["accent"]))
    body.append(arrow(710, 702, 1230, 702))
    body.append(arrow(1350, 744, 1350, 790))
    body.append(arrow(710, 832, 850, 832))
    body.append(arrow(970, 874, 970, 920))
    body.append(arrow(970, 1004, 970, 1050))
    body.append(arrow(970, 1134, 970, 1180))
    body.append(arrow(970, 1290, 970, 1320))
    body.append(text(994, 1308, "да", size=14, fill=COLORS["accent"]))
    body.append(arrow(970, 1430, 970, 1460))
    body.append(text(994, 1448, "да", size=14, fill=COLORS["accent"]))
    body.append(arrow(850, 1502, 710, 1502))
    body.append(arrow(470 + 240, 1502, 1230, 1502))
    body.append(arrow(1350, 1544, 1350, 1605))

    body.append(arrow(470, 555, 170, 555, accent=True))
    body.append(text(300, 538, "нет", size=14, fill=COLORS["accent"]))
    body.append(rect(70, 518, 190, 72, "#fef2f2", stroke=COLORS["danger"], rx=12))
    body.extend(multiline_text(92, 554, "Показать ошибку и вернуть к форме", width_chars=18, size=15, line_height=18, fill=COLORS["danger"], weight="700"))

    body.append(arrow(850, 1235, 640, 1235, accent=True))
    body.append(text(740, 1218, "нет", size=14, fill=COLORS["accent"]))
    body.append(rect(430, 1198, 180, 72, "#fef2f2", stroke=COLORS["danger"], rx=12))
    body.extend(multiline_text(452, 1234, "Пропустить карточку", width_chars=15, size=15, line_height=18, fill=COLORS["danger"], weight="700"))

    body.append(arrow(850, 1375, 640, 1375, accent=True))
    body.append(text(740, 1358, "нет", size=14, fill=COLORS["accent"]))
    body.append(rect(430, 1338, 180, 72, "#fef2f2", stroke=COLORS["danger"], rx=12))
    body.extend(multiline_text(446, 1374, "Отклонить объект по географии", width_chars=17, size=15, line_height=18, fill=COLORS["danger"], weight="700"))

    body.append(rect(1200, 930, 270, 120, "#f8fafc", stroke=COLORS["light"], rx=14))
    body.append(text(1220, 968, "Параллельно внутри сервиса:", size=16, weight="700"))
    body.extend(multiline_text(1220, 998, "поиск картинок, очистка описания, выделение района, цены, площади, этажа, отделки", width_chars=27, size=14, line_height=18, fill=COLORS["muted"]))

    body.append(rect(1200, 1188, 270, 112, "#f8fafc", stroke=COLORS["light"], rx=14))
    body.append(text(1220, 1226, "Исключения поиска:", size=16, weight="700"))
    body.extend(multiline_text(1220, 1256, "таймаут источника, пустая выдача, ошибка адаптера, некорректный JSON-LD", width_chars=27, size=14, line_height=18, fill=COLORS["muted"]))

    body.append(rect(470, 1188, 240, 108, "#f8fafc", stroke=COLORS["light"], rx=14))
    body.append(text(490, 1226, "Итог по заявке:", size=16, weight="700"))
    body.extend(multiline_text(490, 1256, "found, no_results или error в зависимости от total_saved и результата вызова сервиса", width_chars=22, size=14, line_height=18, fill=COLORS["muted"]))

    body.extend(footer_caption(width, height, "Рисунок 6 – Диаграмма деятельности подбора объектов недвижимости по профилю клиента"))
    save_svg(path, width, height, body)


def build_state(path: Path) -> None:
    width, height = 1560, 980
    body = [text(80, 70, "Диаграмма состояний клиентской заявки", size=28, weight="700")]
    states = {
        "new": (160, 250, 180),
        "searching": (430, 250, 220),
        "found": (760, 140, 180),
        "no_results": (760, 340, 220),
        "error": (760, 560, 180),
        "shortlist_ready": (1090, 250, 260),
        "sent": (1390, 250, 140),
    }
    body.append(f'<circle cx="110" cy="287" r="20" fill="{COLORS["accent_soft"]}" stroke="{COLORS["accent"]}" stroke-width="2"/>')
    body.append(text(110, 293, "start", size=13, anchor="middle"))
    centers = {}
    for label, (x, y, w) in states.items():
        body.append(rect(x, y, w, 82, "#ffffff", stroke=COLORS["line"], rx=22))
        body.append(text(x + w // 2, y + 48, label, size=21, weight="700", anchor="middle"))
        centers[label] = (x + w // 2, y + 41, w)
    body.append(arrow(130, 287, 160, 287))

    transitions = [
        ("new", "searching", "создание клиента и запуск поиска"),
        ("searching", "found", "saved > 0"),
        ("searching", "no_results", "saved = 0"),
        ("searching", "error", "ошибка сервиса или таймаут"),
        ("found", "shortlist_ready", "объект добавлен в подборку"),
        ("shortlist_ready", "found", "последний объект удален из подборки"),
        ("shortlist_ready", "sent", "выполнена mark-sent"),
        ("found", "searching", "повторный запуск поиска"),
        ("no_results", "searching", "изменены параметры и поиск запущен повторно"),
        ("error", "searching", "повторный запуск после сбоя"),
        ("sent", "searching", "повторный поиск по той же карточке"),
    ]
    for a, b, label in transitions:
        x1, y1, w1 = centers[a]
        x2, y2, w2 = centers[b]
        if a == "found" and b == "searching":
            body.append(arrow(x1 - w1 // 2 + 20, y1, x2 + w2 // 2 - 20, y2 - 80, accent=True))
            body.append(text(590, 116, label, size=14, fill=COLORS["accent"], anchor="middle"))
        elif a == "no_results" and b == "searching":
            body.append(arrow(x1 - 40, y1 - 10, x2 + 40, y2 + 40, accent=True, dash="6,4"))
            body.append(text(560, 346, label, size=14, fill=COLORS["accent"], anchor="middle"))
        elif a == "error" and b == "searching":
            body.append(arrow(x1 - 30, y1 - 24, x2 + 20, y2 + 66, accent=True, dash="6,4"))
            body.append(text(560, 548, label, size=14, fill=COLORS["accent"], anchor="middle"))
        elif a == "sent" and b == "searching":
            body.append(arrow(x1 - 50, y1 + 84, x2 + 70, y2 + 84, accent=True, dash="6,4"))
            body.append(text(1020, 420, label, size=14, fill=COLORS["accent"], anchor="middle"))
        else:
            body.append(arrow(x1 + w1 // 2 - 90, y1 + 40, x2 - w2 // 2 + 22, y2))
            body.append(text((x1 + x2) // 2, (y1 + y2) // 2 - 14, label, size=14, fill=COLORS["muted"], anchor="middle"))

    body.append(rect(1050, 520, 430, 180, "#f8fafc", stroke=COLORS["light"], rx=16))
    body.append(text(1070, 560, "Пояснение по состояниям", size=18, weight="700"))
    body.extend(multiline_text(1070, 595, "new — карточка создана, поиск еще не завершен.\nfound — есть хотя бы один сохраненный объект.\nno_results — поиск завершен без сохраненных объектов.\nerror — search-service завершился ошибкой.\nshortlist_ready — в подборке есть хотя бы один объект.\nsent — риелтор отметил отправку подборки.", width_chars=42, size=15, line_height=22, fill=COLORS["muted"]))

    body.extend(footer_caption(width, height, "Рисунок 7 – Диаграмма состояний клиентской заявки"))
    save_svg(path, width, height, body)


def build_components(path: Path) -> None:
    width, height = 1660, 1080
    body = [text(80, 70, "Диаграмма компонентов программной системы «Тэона»", size=28, weight="700")]
    comps = [
        (70, 170, 270, 330, "Web Client", ["React pages", "LoginPage", "DashboardPage", "ClientsPage", "ClientPage", "StatusBadge / Cards"]),
        (410, 120, 320, 420, "API Server", ["Express app", "auth routes", "clients routes", "dashboard routes", "properties routes", "validation / serializers"]),
        (800, 120, 300, 220, "SQL Repository", ["listClients", "createClientWithProfile", "upsertProperty", "upsertClientFoundProperty", "markSent"]),
        (800, 390, 300, 250, "Search Service", ["FastAPI entrypoint", "SourceConfig", "BaseAdapter", "Normalizer", "Matcher"]),
        (1190, 120, 340, 260, "PostgreSQL", ["users", "clients", "client_search_profiles", "properties", "client_found_properties", "shortlist_items", "share_messages", "search_runs"]),
        (1190, 460, 340, 220, "External Websites", ["сайты застройщиков", "агрегаторы новостроек", "HTML-карточки", "JSON-LD блоки"]),
        (410, 620, 320, 180, "Session Layer", ["cookie-session", "requireAuth", "userId в запросе"]),
    ]
    for x, y, w, h, name, items in comps:
        body.append(rect(x, y, w, h, "#ffffff", stroke=COLORS["line"], rx=18))
        body.append(rect(x, y, w, 44, COLORS["accent_soft"], stroke=COLORS["line"], rx=18))
        body.append(text(x + 16, y + 30, name, size=20, weight="700"))
        yy = y + 76
        for item in items:
            body.append(text(x + 18, yy, f"• {item}", size=16))
            yy += 28

    body.append(arrow(340, 310, 410, 310))
    body.append(text(360, 292, "HTTP / JSON", size=14, fill=COLORS["muted"]))
    body.append(arrow(730, 250, 800, 250))
    body.append(text(748, 232, "SQL access", size=14, fill=COLORS["muted"]))
    body.append(arrow(730, 430, 800, 430))
    body.append(text(742, 412, "REST / search", size=14, fill=COLORS["muted"]))
    body.append(arrow(1100, 250, 1190, 250))
    body.append(text(1128, 232, "pg", size=14, fill=COLORS["muted"]))
    body.append(arrow(1100, 510, 1190, 560))
    body.append(text(1136, 520, "HTTP / HTML / JSON-LD", size=14, fill=COLORS["muted"]))
    body.append(arrow(570, 540, 570, 620))
    body.append(text(590, 590, "auth", size=14, fill=COLORS["muted"]))
    body.append(arrow(570, 620, 570, 540, accent=True, dash="6,4"))
    body.append(text(594, 646, "user context", size=14, fill=COLORS["accent"]))
    body.append(arrow(340, 420, 410, 700, accent=True, dash="6,4"))
    body.append(text(318, 560, "cookie", size=14, fill=COLORS["accent"]))

    body.append(rect(70, 560, 270, 200, "#f8fafc", stroke=COLORS["light"], rx=16))
    body.append(text(90, 598, "Пользовательские сценарии", size=18, weight="700"))
    body.extend(multiline_text(90, 630, "авторизация,\nсоздание клиента,\nповторный поиск,\nформирование подборки,\nподготовка сообщения", width_chars=18, size=16, line_height=24, fill=COLORS["muted"]))

    body.extend(footer_caption(width, height, "Рисунок 8 – Диаграмма компонентов программной системы «Тэона»"))
    save_svg(path, width, height, body)


def build_er_fragment1(path: Path) -> None:
    width, height = 1560, 1100
    body = [text(80, 70, "ER-диаграмма: пользователи, клиенты, профили поиска и история запусков", size=28, weight="700")]
    body.extend(db_box(80, 190, "users", ["PK id", "login", "password_hash", "name", "email", "phone", "created_at", "updated_at"], 280))
    body.extend(db_box(430, 170, "clients", ["PK id", "FK realtor_id", "name", "phone", "email", "send_channel", "send_contact", "status", "property_type", "comment", "created_at", "updated_at"], 320))
    body.extend(db_box(820, 120, "client_search_profiles", ["PK id", "UQ FK client_id", "budget_min / budget_max", "rooms_min / rooms_max", "area_min / area_max", "districts[]", "settlement_names[]", "completion_year_min / max", "finishing", "floor_min / floor_max", "house_area_min / max", "land_area_min / max", "bedrooms_min / max", "communications[]"], 340))
    body.extend(db_box(1180, 520, "search_runs", ["PK id", "FK client_id", "status", "property_type", "total_found", "total_saved", "error_message", "started_at", "finished_at"], 280))
    body.append(arrow(360, 320, 430, 320))
    body.append(text(392, 302, "1 : M", size=16, weight="700", fill=COLORS["accent"]))
    body.append(arrow(750, 300, 820, 300))
    body.append(text(782, 282, "1 : 1", size=16, weight="700", fill=COLORS["accent"]))
    body.append(arrow(590, 420, 1180, 600))
    body.append(text(860, 530, "1 : M", size=16, weight="700", fill=COLORS["accent"]))
    body.append(rect(80, 640, 520, 230, "#f8fafc", stroke=COLORS["light"], rx=16))
    body.append(text(100, 680, "Что важно подчеркнуть на схеме", size=18, weight="700"))
    body.extend(multiline_text(100, 716, "таблица clients является центром пользовательского контура;\nclient_search_profiles хранит один актуальный профиль поиска;\nsearch_runs фиксирует каждую попытку запуска поиска и ее результат;\nusers связана с клиентами через realtor_id.", width_chars=40, size=15, line_height=22, fill=COLORS["muted"]))
    body.extend(footer_caption(width, height, "Рисунок 9 – Фрагмент ER-диаграммы базы данных: пользователи системы, карточки клиентов, профили поиска и история запусков"))
    save_svg(path, width, height, body)


def build_er_fragment2(path: Path) -> None:
    width, height = 1760, 1160
    body = [text(80, 70, "ER-диаграмма: объекты, результаты поиска, подборки и сообщения", size=28, weight="700")]
    body.extend(db_box(70, 180, "clients", ["PK id", "status", "property_type"], 220))
    body.extend(db_box(350, 100, "properties", ["PK id", "external_id", "source_name", "source_url", "title", "complex_name", "developer_name", "description", "city", "district", "address", "settlement_name", "price", "price_per_meter", "area", "rooms", "floor", "floors_total", "house_area", "land_area", "bedrooms", "house_floors", "house_material", "communications[]", "completion_year", "finishing", "images[]"], 340))
    body.extend(db_box(800, 100, "client_found_properties", ["PK id", "FK client_id", "FK property_id", "match_score", "match_reasons[]", "mismatch_reasons[]", "is_hidden", "created_at"], 300))
    body.extend(db_box(1190, 100, "shortlist_items", ["PK id", "FK client_id", "FK property_id", "note", "created_at"], 250))
    body.extend(db_box(800, 700, "share_messages", ["PK id", "FK client_id", "channel", "contact", "message_text", "copied_at", "sent_marked_at", "created_at"], 310))
    body.append(arrow(290, 290, 350, 290))
    body.append(text(316, 272, "1 : M", size=16, weight="700", fill=COLORS["accent"]))
    body.append(arrow(690, 270, 800, 270))
    body.append(text(742, 252, "1 : M", size=16, weight="700", fill=COLORS["accent"]))
    body.append(arrow(690, 350, 1190, 270))
    body.append(text(952, 302, "1 : M", size=16, weight="700", fill=COLORS["accent"]))
    body.append(arrow(180, 360, 890, 700))
    body.append(text(510, 520, "1 : M", size=16, weight="700", fill=COLORS["accent"]))
    body.append(rect(1190, 470, 420, 220, "#f8fafc", stroke=COLORS["light"], rx=16))
    body.append(text(1210, 510, "Смысл второго фрагмента", size=18, weight="700"))
    body.extend(multiline_text(1210, 546, "properties хранит нормализованный общий каталог объектов;\nclient_found_properties связывает найденный объект с конкретным клиентом и хранит matchScore;\nshortlist_items отражает ручной выбор риелтора;\nshare_messages фиксирует подготовленный текст подборки.", width_chars=34, size=15, line_height=22, fill=COLORS["muted"]))
    body.extend(footer_caption(width, height, "Рисунок 10 – Фрагмент ER-диаграммы базы данных: объекты недвижимости, результаты поиска, подборки и сообщения"))
    save_svg(path, width, height, body)


def build_algorithm(path: Path, title_value: str, caption: str, blocks: list[str], branches: dict[int, tuple[str, str]] | None = None) -> None:
    width = 1360
    branches = branches or {}
    height = 180
    for idx, label in enumerate(blocks):
        if idx == 0 or idx == len(blocks) - 1:
            height += 82
        elif label.endswith("?"):
            height += 148
        else:
            height += 104
    height += 90
    body = [text(80, 70, title_value, size=28, weight="700")]
    x = 430
    y = 130
    prev = None
    for idx, label in enumerate(blocks):
        is_decision = label.endswith("?")
        if idx == 0 or idx == len(blocks) - 1:
            body.append(f'<circle cx="{x+180}" cy="{y+24}" r="24" fill="{COLORS["accent_soft"]}" stroke="{COLORS["accent"]}" stroke-width="2"/>')
            body.append(text(x + 180, y + 30, label, size=15, anchor="middle"))
            center = (x + 180, y + 24)
            y += 82
        elif is_decision:
            points = f"{x+180},{y} {x+360},{y+52} {x+180},{y+104} {x},{y+52}"
            body.append(f'<polygon points="{points}" fill="#fff7ed" stroke="{COLORS["accent"]}" stroke-width="2"/>')
            body.extend(multiline_text(x + 70, y + 48, label, width_chars=22, size=15, line_height=18))
            center = (x + 180, y + 52)
            branch = branches.get(idx)
            if branch:
                branch_label, branch_action = branch
                bx = 80
                by = y + 18
                body.append(arrow(x, y + 52, bx + 180, y + 52, accent=True))
                body.append(text(250, y + 36, branch_label, size=14, fill=COLORS["accent"]))
                body.append(rect(bx, by, 180, 70, "#fef2f2", stroke=COLORS["danger"], rx=12))
                body.extend(multiline_text(bx + 16, by + 38, branch_action, width_chars=16, size=15, line_height=18, fill=COLORS["danger"], weight="700"))
                body.append(text(x + 202, y + 124, "да", size=14, fill=COLORS["accent"]))
            y += 148
        else:
            body.append(rect(x, y, 360, 72, "#ffffff", stroke=COLORS["line"], rx=14))
            body.extend(multiline_text(x + 24, y + 42, label, width_chars=30, size=16, line_height=20))
            center = (x + 180, y + 36)
            y += 104
        if prev:
            body.append(arrow(prev[0], prev[1] + 26, center[0], center[1] - 38))
        prev = center
    body.extend(footer_caption(width, height, caption))
    save_svg(path, width, height, body)


def build_login_wireframe(path: Path) -> None:
    width, height = 1440, 920
    body = screen_header("Страница входа в систему", width, height)
    body.append(rect(420, 170, 600, 520, "#ffffff", stroke=COLORS["light"], rx=24))
    body.append(text(470, 240, "Тэона", size=36, weight="700"))
    body.append(text(470, 282, "Система сопровождения клиентских заявок риелтора", size=18, fill=COLORS["muted"]))
    for i, label in enumerate(["Логин", "Пароль"]):
        yy = 360 + i * 120
        body.append(text(470, yy, label, size=18, weight="600"))
        body.append(rect(470, yy + 18, 500, 60, "#ffffff", stroke=COLORS["light"], rx=14))
    body.append(rect(470, 620, 240, 64, COLORS["accent"], stroke=COLORS["accent"], rx=16))
    body.append(text(590, 660, "Войти", size=22, weight="700", fill="#ffffff", anchor="middle"))
    body.extend(footer_caption(width, height, "Рисунок 16 – Экранная форма страницы входа в систему"))
    save_svg(path, width, height, body)


def build_dashboard_wireframe(path: Path) -> None:
    width, height = 1520, 980
    body = screen_header("Главная страница со сводными показателями", width, height)
    body.append(rect(40, 100, 230, 760, "#f8fafc", stroke=COLORS["light"], rx=18))
    nav = ["Dashboard", "Клиенты", "Новый клиент", "Профиль", "Настройки"]
    yy = 150
    for i, item in enumerate(nav):
        fill = COLORS["accent_soft"] if i == 0 else "#ffffff"
        body.append(rect(58, yy - 28, 194, 48, fill, stroke=COLORS["light"], rx=12))
        body.append(text(80, yy, item, size=18, weight="600"))
        yy += 74
    cards = [("Клиенты в работе", "12"), ("Найдено объектов", "107"), ("В подборках", "7"), ("Готово к отправке", "5")]
    x = 310
    for label, value in cards:
        body.append(rect(x, 110, 270, 180, "#ffffff", stroke=COLORS["light"], rx=18))
        body.append(text(x + 26, 160, value, size=58, weight="700"))
        body.append(text(x + 26, 255, label, size=20))
        x += 290
    body.extend(panel(310, 330, 1140, 250, "Активность за 7 дней"))
    points = [(350, 520), (450, 470), (560, 490), (680, 430), (800, 460), (920, 380), (1050, 410), (1180, 360), (1310, 420)]
    polyline = " ".join(f"{x},{y}" for x, y in points)
    body.append(f'<polyline points="{polyline}" fill="none" stroke="{COLORS["accent"]}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
    body.extend(panel(310, 610, 1140, 250, "Клиенты, требующие внимания"))
    for row_y in [670, 730, 790]:
        body.append(line(340, row_y, 1410, row_y, stroke=COLORS["light"], sw=1))
        body.append(text(360, row_y - 16, "Иван Иванов", size=18, weight="600"))
        body.append(text(620, row_y - 16, "поиск завершен без результатов", size=16, fill=COLORS["muted"]))
        body.append(rect(1260, row_y - 40, 130, 40, "#ffffff", stroke=COLORS["accent"], rx=10))
        body.append(text(1325, row_y - 14, "Открыть", size=16, weight="600", fill=COLORS["accent"], anchor="middle"))
    body.extend(footer_caption(width, height, "Рисунок 17 – Экранная форма главной страницы со сводными показателями"))
    save_svg(path, width, height, body)


def build_clients_wireframe(path: Path) -> None:
    width, height = 1520, 980
    body = screen_header("Экранная форма списка клиентов", width, height)
    body.append(rect(40, 108, 320, 56, "#ffffff", stroke=COLORS["light"], rx=14))
    body.append(text(62, 143, "Поиск по имени или телефону", size=18, fill=COLORS["muted"]))
    filters = ["Все", "new", "found", "shortlist_ready", "sent", "error"]
    x = 390
    for i, item in enumerate(filters):
        fill = COLORS["accent_soft"] if i == 0 else "#ffffff"
        stroke = COLORS["accent"] if i == 0 else COLORS["light"]
        body.append(rect(x, 108, 140, 56, fill, stroke=stroke, rx=14))
        body.append(text(x + 70, 143, item, size=18, anchor="middle"))
        x += 156
    body.extend(panel(40, 200, 1440, 650, "Клиентские заявки"))
    for i in range(5):
        yy = 270 + i * 110
        body.append(line(70, yy + 52, 1440, yy + 52, stroke=COLORS["light"], sw=1))
        body.append(text(90, yy, f"Иван Иванов {i+1}", size=20, weight="700"))
        body.append(text(90, yy + 32, "до 8 млн ₽ · 1–2 комн. · Прикубанский, Центральный", size=16, fill=COLORS["muted"]))
        body.append(rect(870, yy - 18, 140, 42, "#ffffff", stroke=COLORS["light"], rx=10))
        body.append(text(940, yy + 9, "found", size=16, anchor="middle"))
        body.append(text(1080, yy + 4, "Найдено: 81", size=18))
        body.append(text(1230, yy + 4, "В подборке: 7", size=18))
        body.append(rect(1330, yy - 20, 100, 44, "#ffffff", stroke=COLORS["accent"], rx=10))
        body.append(text(1380, yy + 8, "Открыть", size=16, weight="600", fill=COLORS["accent"], anchor="middle"))
    body.extend(footer_caption(width, height, "Рисунок 18 – Экранная форма списка клиентов"))
    save_svg(path, width, height, body)


def build_create_client_wireframe(path: Path) -> None:
    width, height = 1520, 1040
    body = screen_header("Экранная форма создания нового клиента", width, height)
    body.extend(panel(40, 108, 700, 370, "Контактные данные"))
    labels = ["ФИО клиента", "Телефон", "Электронная почта", "Канал связи", "Комментарий"]
    for i, label in enumerate(labels):
        yy = 170 + i * 58
        body.append(text(70, yy, label, size=17, weight="600"))
        body.append(rect(260, yy - 26, 440, 42, "#ffffff", stroke=COLORS["light"], rx=10))
    body.extend(panel(780, 108, 700, 370, "Тип недвижимости и параметры поиска"))
    body.append(rect(810, 150, 220, 44, COLORS["accent_soft"], stroke=COLORS["accent"], rx=12))
    body.append(text(920, 178, "Квартира", size=18, weight="700", fill=COLORS["accent"], anchor="middle"))
    body.append(rect(1050, 150, 160, 44, "#ffffff", stroke=COLORS["light"], rx=12))
    body.append(text(1130, 178, "Дом", size=18, anchor="middle"))
    right_labels = ["Бюджет от", "Бюджет до", "Комнатность", "Площадь", "Районы"]
    for i, label in enumerate(right_labels):
        yy = 240 + i * 56
        body.append(text(810, yy, label, size=17, weight="600"))
        body.append(rect(1030, yy - 24, 410, 40, "#ffffff", stroke=COLORS["light"], rx=10))
    body.extend(panel(40, 520, 1440, 320, "Дополнительные параметры"))
    for i in range(3):
        body.append(rect(70 + i * 460, 600, 400, 56, "#ffffff", stroke=COLORS["light"], rx=12))
        body.append(rect(70 + i * 460, 690, 400, 56, "#ffffff", stroke=COLORS["light"], rx=12))
    body.append(rect(1080, 882, 360, 64, COLORS["accent"], stroke=COLORS["accent"], rx=16))
    body.append(text(1260, 922, "Сохранить и запустить поиск", size=22, weight="700", fill="#ffffff", anchor="middle"))
    body.extend(footer_caption(width, height, "Рисунок 19 – Экранная форма создания нового клиента"))
    save_svg(path, width, height, body)


def build_client_card_wireframe(path: Path) -> None:
    width, height = 1560, 1120
    body = screen_header("Экранная форма карточки клиента с найденными объектами", width, height)
    body.append(text(60, 130, "Иван Иванов", size=36, weight="700"))
    body.append(text(60, 168, "до 8 млн ₽ · 1–2 комн. · Прикубанский, Центральный", size=18, fill=COLORS["muted"]))
    body.append(rect(60, 200, 360, 84, "#ffffff", stroke=COLORS["light"], rx=16))
    body.append(text(90, 238, "В подборке", size=20))
    body.append(text(90, 272, "7 объектов", size=34, weight="700"))
    body.append(rect(450, 200, 360, 84, "#ffffff", stroke=COLORS["light"], rx=16))
    body.append(text(480, 238, "Найдено", size=20))
    body.append(text(480, 272, "81 объект", size=34, weight="700"))
    body.append(rect(1180, 212, 300, 56, "#ffffff", stroke=COLORS["accent"], rx=14))
    body.append(text(1330, 248, "Обновить поиск", size=20, weight="700", fill=COLORS["accent"], anchor="middle"))
    body.extend(panel(60, 320, 980, 710, "Найденные объекты"))
    card_x = 90
    card_y = 390
    for row in range(2):
        for col in range(2):
            x = card_x + col * 460
            y = card_y + row * 300
            body.append(rect(x, y, 410, 250, "#ffffff", stroke=COLORS["light"], rx=18))
            body.append(rect(x, y, 410, 110, "#f3f4f6", stroke=COLORS["light"], rx=18))
            body.append(text(x + 20, y + 140, "1-к квартира, 40.6 м²", size=22, weight="700"))
            body.append(text(x + 20, y + 174, "Прикубанский · 5 275 000 ₽", size=18, fill=COLORS["muted"]))
            body.append(text(x + 20, y + 206, "Совпадение: 68%", size=18))
            body.append(rect(x + 20, y + 216, 160, 14, COLORS["accent"], stroke=COLORS["accent"], rx=8))
            body.append(rect(x + 200, y + 216, 170, 14, "#e5e7eb", stroke="#e5e7eb", rx=8))
            body.append(rect(x + 20, y + 250 - 46, 150, 42, "#ffffff", stroke=COLORS["light"], rx=10))
            body.append(text(x + 95, y + 250 - 18, "Подробнее", size=16, anchor="middle"))
            body.append(rect(x + 220, y + 250 - 46, 150, 42, COLORS["accent"], stroke=COLORS["accent"], rx=10))
            body.append(text(x + 295, y + 250 - 18, "В подборку", size=16, weight="700", fill="#ffffff", anchor="middle"))
    body.extend(panel(1080, 320, 400, 710, "Подборка"))
    for i in range(4):
        yy = 390 + i * 120
        body.append(rect(1110, yy, 340, 90, "#ffffff", stroke=COLORS["light"], rx=14))
        body.append(text(1130, yy + 34, f"{i+1}-й объект", size=18, weight="700"))
        body.append(text(1130, yy + 62, "краткое описание и цена", size=16, fill=COLORS["muted"]))
    body.append(rect(1110, 930, 340, 54, COLORS["accent"], stroke=COLORS["accent"], rx=14))
    body.append(text(1280, 964, "Сформировать сообщение", size=20, weight="700", fill="#ffffff", anchor="middle"))
    body.extend(footer_caption(width, height, "Рисунок 20 – Экранная форма карточки клиента с найденными объектами"))
    save_svg(path, width, height, body)


def build_property_detail_wireframe(path: Path) -> None:
    width, height = 1440, 980
    body = screen_header("Экранная форма просмотра детальной информации об объекте недвижимости", width, height)
    body.append(rect(50, 110, 620, 380, "#f3f4f6", stroke=COLORS["light"], rx=20))
    body.append(text(360, 310, "Фото объекта", size=28, fill=COLORS["muted"], anchor="middle"))
    body.append(text(720, 140, "1-к квартира, 40.6 м²", size=34, weight="700"))
    body.append(text(720, 182, "5 275 000 ₽", size=30, weight="700", fill=COLORS["accent"]))
    attrs = [("Район", "Прикубанский"), ("Источник", "Домострой Краснодар"), ("Совпадение", "68%"), ("Комнат", "1"), ("Площадь", "40.6 м²"), ("Ссылка", "source_url")]
    x_positions = [720, 1030]
    y0 = 240
    idx = 0
    for row in range(3):
        for col in range(2):
            x = x_positions[col]
            y = y0 + row * 110
            label, value = attrs[idx]
            idx += 1
            body.append(rect(x, y, 280, 86, "#ffffff", stroke=COLORS["light"], rx=16))
            body.append(text(x + 20, y + 30, label, size=18, fill=COLORS["muted"]))
            body.append(text(x + 20, y + 62, value, size=22, weight="700"))
    body.extend(panel(50, 530, 1330, 220, "Описание"))
    body.extend(multiline_text(80, 590, "Краткое нормализованное описание объекта, сформированное после обработки внешнего объявления. Здесь должны быть отражены основные характеристики, район, площадь и ссылка на источник.", width_chars=95, size=18, line_height=28))
    body.extend(panel(50, 780, 1330, 110, "Причины совпадения"))
    reasons = ["Цена подходит", "Комнатность подходит", "Площадь подходит", "Район подходит"]
    x = 80
    for reason in reasons:
        body.append(rect(x, 826, 230, 34, COLORS["accent_soft"], stroke=COLORS["accent"], rx=18))
        body.append(text(x + 115, 849, reason, size=15, weight="600", fill=COLORS["accent"], anchor="middle"))
        x += 250
    body.extend(footer_caption(width, height, "Рисунок 21 – Экранная форма просмотра детальной информации об объекте недвижимости"))
    save_svg(path, width, height, body)


def build_db_list(path: Path) -> None:
    width, height = 1440, 920
    body = screen_header("Список таблиц базы данных в среде TablePlus", width, height)
    body.append(rect(40, 110, 320, 690, "#f8fafc", stroke=COLORS["light"], rx=18))
    body.append(text(70, 150, "Tables", size=22, weight="700"))
    tables = ["users", "clients", "client_search_profiles", "properties", "client_found_properties", "shortlist_items", "share_messages", "search_runs"]
    yy = 210
    for name in tables:
        body.append(rect(60, yy - 24, 280, 44, "#ffffff", stroke=COLORS["light"], rx=10))
        body.append(text(84, yy + 3, name, size=18))
        yy += 64
    body.append(rect(400, 110, 1000, 690, "#ffffff", stroke=COLORS["light"], rx=18))
    body.append(text(430, 150, "Schema preview", size=22, weight="700"))
    body.extend(db_box(440, 200, "clients", ["id", "realtor_id", "name", "phone", "send_channel", "status", "property_type"], 300))
    body.extend(db_box(780, 200, "properties", ["id", "source_url", "title", "district", "price", "area", "rooms"], 300))
    body.extend(db_box(1120, 200, "search_runs", ["id", "client_id", "status", "total_found", "total_saved", "error_message"], 240))
    body.extend(footer_caption(width, height, "Рисунок 22 – Список таблиц базы данных в среде TablePlus"))
    save_svg(path, width, height, body)


def build_db_content(path: Path) -> None:
    width, height = 1600, 980
    body = screen_header("Содержимое основных таблиц базы данных", width, height)
    # users/clients
    body.append(rect(40, 120, 720, 700, "#ffffff", stroke=COLORS["light"], rx=18))
    body.append(text(70, 156, "users", size=22, weight="700"))
    cols1 = ["login", "name", "email", "phone"]
    xs1 = [70, 240, 420, 610]
    for i, c in enumerate(cols1):
        body.append(text(xs1[i], 210, c, size=16, weight="700", fill=COLORS["muted"]))
    rows1 = [
        ["ivan.nikitin", "Иван Никитин", "ivan.nikitin@teona.local", "+7 (918) 111-11-01"],
        ["kirill.nabiev", "Кирилл Набиев", "kirill.nabiev@teona.local", "+7 (918) 111-11-02"],
    ]
    y = 250
    for row in rows1:
        body.append(line(60, y - 18, 730, y - 18, stroke=COLORS["light"], sw=1))
        for i, val in enumerate(row):
            body.append(text(xs1[i], y, val, size=15))
        y += 46
    body.append(text(70, 390, "clients", size=22, weight="700"))
    cols2 = ["name", "phone", "property_type", "status"]
    xs2 = [70, 250, 460, 620]
    for i, c in enumerate(cols2):
        body.append(text(xs2[i], 440, c, size=16, weight="700", fill=COLORS["muted"]))
    rows2 = [["Иван Иванов", "+79180000000", "apartment", "found"], ["Марина Соколова", "+79180000001", "house", "shortlist_ready"]]
    y = 480
    for row in rows2:
        body.append(line(60, y - 18, 730, y - 18, stroke=COLORS["light"], sw=1))
        for i, val in enumerate(row):
            body.append(text(xs2[i], y, val, size=15))
        y += 46
    # properties/found
    body.append(rect(800, 120, 760, 700, "#ffffff", stroke=COLORS["light"], rx=18))
    body.append(text(830, 156, "properties", size=22, weight="700"))
    cols3 = ["title", "district", "price", "area"]
    xs3 = [830, 1140, 1310, 1460]
    for i, c in enumerate(cols3):
        body.append(text(xs3[i], 210, c, size=16, weight="700", fill=COLORS["muted"]))
    rows3 = [
        ["1-к квартира, 40.6 м²", "Прикубанский", "5275000", "40.6"],
        ["Дом 128 м²", "Западный", "9350000", "128"],
    ]
    y = 250
    for row in rows3:
        body.append(line(820, y - 18, 1540, y - 18, stroke=COLORS["light"], sw=1))
        for i, val in enumerate(row):
            body.append(text(xs3[i], y, val, size=15))
        y += 46
    body.append(text(830, 390, "client_found_properties", size=22, weight="700"))
    cols4 = ["client_id", "property_id", "match_score", "is_hidden"]
    xs4 = [830, 1040, 1270, 1440]
    for i, c in enumerate(cols4):
        body.append(text(xs4[i], 440, c, size=16, weight="700", fill=COLORS["muted"]))
    rows4 = [["...", "...", "68", "false"], ["...", "...", "54", "false"]]
    y = 480
    for row in rows4:
        body.append(line(820, y - 18, 1540, y - 18, stroke=COLORS["light"], sw=1))
        for i, val in enumerate(row):
            body.append(text(xs4[i], y, val, size=15))
        y += 46
    body.extend(footer_caption(width, height, "Рисунок 23 – Содержимое основных таблиц базы данных"))
    save_svg(path, width, height, body)


def build_project_structure(path: Path) -> None:
    width, height = 1400, 980
    body = [text(80, 70, "Структура проекта", size=28, weight="700")]
    body.append(rect(80, 120, 1240, 760, "#ffffff", stroke=COLORS["light"], rx=20))
    tree = [
        "realestate",
        "├── apps",
        "│   ├── web",
        "│   │   ├── src/app",
        "│   │   ├── src/pages",
        "│   │   ├── src/components",
        "│   │   └── src/services",
        "│   ├── api",
        "│   │   ├── src/routes",
        "│   │   ├── src/services",
        "│   │   ├── src/repositories",
        "│   │   └── src/data",
        "│   └── search-service",
        "│       ├── app/adapters",
        "│       ├── app/services",
        "│       ├── app/schemas",
        "│       └── tests",
        "├── database",
        "│   └── init.sql",
        "├── scripts",
        "├── docker-compose.yml",
        "└── package.json",
    ]
    yy = 180
    for line_value in tree:
        body.append(f'<text x="120" y="{yy}" font-family="Menlo, Consolas, monospace" font-size="20" fill="{COLORS["text"]}">{escape(line_value)}</text>')
        yy += 32
    body.extend(footer_caption(width, height, "Рисунок 24 – Структура проекта"))
    save_svg(path, width, height, body)


def build_full_db_reference(path: Path) -> None:
    width, height = 1800, 1200
    body = [text(80, 70, "Справочно – Полная схема базы данных проекта «Тэона»", size=30, weight="700")]
    body.extend(db_box(60, 160, "users", ["id", "login", "password_hash", "name", "email", "phone"], 260))
    body.extend(db_box(380, 150, "clients", ["id", "realtor_id", "name", "phone", "send_channel", "status", "property_type"], 280))
    body.extend(db_box(720, 120, "client_search_profiles", ["id", "client_id", "budget_min / max", "rooms_min / max", "area_min / max", "districts[]", "settlement_names[]", "communications[]"], 300))
    body.extend(db_box(1120, 120, "properties", ["id", "source_url", "title", "district", "price", "area", "rooms", "house_area", "land_area", "images[]"], 300))
    body.extend(db_box(1480, 180, "client_found_properties", ["id", "client_id", "property_id", "match_score", "match_reasons[]", "mismatch_reasons[]"], 260))
    body.extend(db_box(1120, 610, "shortlist_items", ["id", "client_id", "property_id", "note", "created_at"], 260))
    body.extend(db_box(1480, 610, "share_messages", ["id", "client_id", "channel", "contact", "message_text", "sent_marked_at"], 260))
    body.extend(db_box(760, 720, "search_runs", ["id", "client_id", "status", "property_type", "total_found", "total_saved", "error_message"], 280))
    body.append(arrow(320, 280, 380, 280))
    body.append(text(345, 262, "1:M", size=16, weight="700", fill=COLORS["accent"]))
    body.append(arrow(660, 250, 720, 250))
    body.append(text(688, 232, "1:1", size=16, weight="700", fill=COLORS["accent"]))
    body.append(arrow(660, 330, 1480, 260))
    body.append(text(1050, 286, "1:M", size=16, weight="700", fill=COLORS["accent"]))
    body.append(arrow(1420, 280, 1480, 280))
    body.append(text(1450, 262, "1:M", size=16, weight="700", fill=COLORS["accent"]))
    body.append(arrow(580, 360, 1180, 610))
    body.append(text(850, 500, "1:M", size=16, weight="700", fill=COLORS["accent"]))
    body.append(arrow(560, 360, 820, 720))
    body.append(text(650, 560, "1:M", size=16, weight="700", fill=COLORS["accent"]))
    body.append(arrow(560, 360, 1560, 610))
    body.append(text(1080, 520, "1:M", size=16, weight="700", fill=COLORS["accent"]))
    body.extend(footer_caption(width, height, "Справочно – Полная схема БД проекта «Тэона»"))
    save_svg(path, width, height, body)


def generate_all() -> None:
    dirs = ensure_dirs()
    write_readme()

    build_use_case_overview(dirs["usecases"] / "Рисунок 01 - Общая диаграмма вариантов использования.svg")
    build_use_case_module(
        dirs["usecases"] / "Рисунок 02 - Модуль создания и ведения клиентских заявок.svg",
        "Рисунок 2 – Диаграмма вариантов использования модуля создания и ведения клиентских заявок",
        "Модуль создания и ведения клиентских заявок",
        [
            "Создать карточку / клиента",
            "Изменить карточку / клиента",
            "Сохранить профиль / поиска",
            "Запустить поиск / объектов",
            "Открыть карточку / клиента",
            "Повторно запустить / поиск",
        ],
        [(0, 2, "<<include>>"), (0, 3, "<<include>>"), (4, 5, "<<extend>>")],
    )
    build_use_case_module(
        dirs["usecases"] / "Рисунок 03 - Модуль поиска объектов недвижимости.svg",
        "Рисунок 3 – Диаграмма вариантов использования модуля поиска объектов недвижимости",
        "Модуль поиска объектов недвижимости",
        [
            "Запустить поиск / объектов",
            "Просмотреть найденные / объекты",
            "Отфильтровать по / Краснодару",
            "Нормализовать / объявления",
            "Рассчитать / matchScore",
            "Сохранить / результаты",
        ],
        [(0, 2, "<<include>>"), (0, 3, "<<include>>"), (0, 4, "<<include>>"), (0, 5, "<<include>>")],
    )
    build_use_case_module(
        dirs["usecases"] / "Рисунок 04 - Модуль формирования подборки.svg",
        "Рисунок 4 – Диаграмма вариантов использования модуля формирования подборки объектов",
        "Модуль формирования подборки объектов",
        [
            "Открыть карточку / клиента",
            "Просмотреть найденные / объекты",
            "Добавить объект / в подборку",
            "Удалить объект / из подборки",
            "Сформировать текст / сообщения",
            "Отметить / отправку",
        ],
        [(0, 1, "<<include>>"), (2, 4, "<<include>>"), (4, 5, "<<extend>>")],
    )
    build_use_case_module(
        dirs["usecases"] / "Рисунок 05 - Модуль аналитики.svg",
        "Рисунок 5 – Диаграмма вариантов использования модуля аналитики и контроля состояния заявок",
        "Модуль аналитики и контроля состояний",
        [
            "Просмотреть / dashboard",
            "Просмотреть число / клиентов",
            "Просмотреть число / найденных объектов",
            "Просмотреть число / объектов в подборках",
            "Просмотреть число / готово к отправке",
            "Перейти к заявкам / требующим внимания",
        ],
        [(0, 1, "<<include>>"), (0, 2, "<<include>>"), (0, 3, "<<include>>"), (0, 4, "<<include>>"), (0, 5, "<<extend>>")],
    )
    build_activity(dirs["diagrams"] / "Рисунок 06 - Диаграмма деятельности.svg")
    build_state(dirs["diagrams"] / "Рисунок 07 - Диаграмма состояний.svg")
    build_components(dirs["diagrams"] / "Рисунок 08 - Диаграмма компонентов.svg")
    build_er_fragment1(dirs["diagrams"] / "Рисунок 09 - ER пользователи клиенты профили.svg")
    build_er_fragment2(dirs["diagrams"] / "Рисунок 10 - ER объекты подборки сообщения.svg")
    build_full_db_reference(dirs["database"] / "Справочно - Полная схема БД.svg")

    build_algorithm(
        dirs["algorithms"] / "Рисунок 11 - Алгоритм поиска объектов.svg",
        "Блок-схема алгоритма поиска объектов недвижимости по профилю клиента",
        "Рисунок 11 – Блок-схема алгоритма поиска объектов недвижимости по профилю клиента",
        [
            "Старт",
            "Получение client_id, propertyType и searchProfile",
            "Загрузка актуального профиля клиента из БД",
            "Профиль найден?",
            "Определение списка SourceConfig по типу недвижимости",
            "Формирование набора стартовых URL",
            "HTTP-загрузка страниц источников",
            "Разбор JSON-LD и HTML-карточек",
            "Есть обязательные поля и sourceUrl?",
            "Проверка города, района и локации объекта",
            "Объект относится к Краснодару?",
            "Нормализация заголовка, описания и характеристик",
            "Проверка бюджета и типа объекта",
            "Расчет matchScore, matchReasons и mismatchReasons",
            "Upsert записи в properties",
            "Сохранение связи в client_found_properties",
            "Обновление total_found, total_saved и статуса клиента",
            "Конец",
        ],
        {
            3: ("нет", "Вернуть ошибку поиска профиля"),
            8: ("нет", "Пропустить карточку объекта"),
            10: ("нет", "Отклонить объект по географии"),
        },
    )
    build_algorithm(
        dirs["algorithms"] / "Рисунок 12 - Алгоритм нормализации объявления.svg",
        "Блок-схема алгоритма нормализации объявления недвижимости",
        "Рисунок 12 – Блок-схема алгоритма нормализации объявления недвижимости",
        [
            "Старт",
            "Получение rawData, title, description, address и images",
            "Очистка строк и HTML-маркеров",
            "Извлечение цены и площади",
            "Извлечение комнатности, района, этажа и отделки",
            "Заголовок выглядит как маркетинговый мусор?",
            "Собрать структурированный заголовок вида 1-к квартира, 40.6 м²",
            "Описание содержит шум, телефон или служебные фразы?",
            "Собрать запасное описание из нормализованных характеристик",
            "Отфильтровать логотипы, иконки и технические изображения",
            "Рассчитать price_per_meter при наличии цены и площади",
            "Сформировать единый объект SearchItem",
            "Конец",
        ],
        {
            5: ("да", "Заменить исходный title"),
            7: ("да", "Заменить описание запасным текстом"),
        },
    )
    build_algorithm(
        dirs["algorithms"] / "Рисунок 13 - Алгоритм фильтрации по Краснодару.svg",
        "Блок-схема алгоритма фильтрации объектов по городу Краснодару",
        "Рисунок 13 – Блок-схема алгоритма фильтрации объектов по городу Краснодару",
        [
            "Старт",
            "Объединение title, description, address, district и sourceUrl",
            "Нормализация регистра и удаление мусорных символов",
            "Поиск прямого указания на город Краснодар",
            "Найдено упоминание Краснодара?",
            "Поиск названий районов и микрорайонов города",
            "Найден район Краснодара?",
            "Поиск названий других городов Краснодарского края",
            "Обнаружен другой город края?",
            "Допустить объект к дальнейшей обработке",
            "Конец",
        ],
        {
            8: ("да", "Отклонить как нерелевантный объект"),
        },
    )
    build_algorithm(
        dirs["algorithms"] / "Рисунок 14 - Алгоритм расчета процента совпадения.svg",
        "Блок-схема алгоритма расчета процента совпадения",
        "Рисунок 14 – Блок-схема алгоритма расчета процента совпадения объекта требованиям клиента",
        [
            "Старт",
            "Выбор режима оценки: apartment или house",
            "Инициализация весов критериев",
            "Сравнение по бюджету",
            "Сравнение по площади и комнатности / площади дома",
            "Сравнение по району, поселку или локации",
            "Сравнение по отделке, этажу, сроку сдачи или коммуникациям",
            "Есть частично совпадающие критерии?",
            "Начисление баллов и частичных коэффициентов",
            "Формирование matchReasons и mismatchReasons",
            "Расчет итоговой формулы M = sum(w_i*k_i)/sum(w_i)",
            "Ограничение результата в диапазоне 0–100",
            "Вернуть matchScore и причины",
            "Конец",
        ],
        {
            7: ("нет", "Причина уходит в mismatchReasons"),
        },
    )
    build_algorithm(
        dirs["algorithms"] / "Рисунок 15 - Алгоритм формирования подборки и сообщения.svg",
        "Блок-схема алгоритма формирования подборки и текста сообщения",
        "Рисунок 15 – Блок-схема алгоритма формирования подборки объектов и текста сообщения",
        [
            "Старт",
            "Открытие карточки клиента",
            "Просмотр foundProperties и matchScore",
            "Ручной выбор подходящих объектов",
            "Добавление записей в shortlist_items",
            "Подборка не пуста?",
            "Проверка sendChannel и sendContact",
            "Построение краткого текста по каждому объекту",
            "Сборка общего сообщения для клиента",
            "Сохранение записи в share_messages",
            "Отметка факта отправки и статус sent",
            "Конец",
        ],
        {
            5: ("нет", "Показать сообщение «Подборка пока пустая»"),
        },
    )

    build_login_wireframe(dirs["screens"] / "Рисунок 16 - Страница входа.svg")
    build_dashboard_wireframe(dirs["screens"] / "Рисунок 17 - Dashboard.svg")
    build_clients_wireframe(dirs["screens"] / "Рисунок 18 - Список клиентов.svg")
    build_create_client_wireframe(dirs["screens"] / "Рисунок 19 - Создание клиента.svg")
    build_client_card_wireframe(dirs["screens"] / "Рисунок 20 - Карточка клиента.svg")
    build_property_detail_wireframe(dirs["screens"] / "Рисунок 21 - Детали объекта.svg")

    build_db_list(dirs["database"] / "Рисунок 22 - Список таблиц базы данных.svg")
    build_db_content(dirs["database"] / "Рисунок 23 - Содержимое основных таблиц базы данных.svg")
    build_project_structure(dirs["diagrams"] / "Рисунок 24 - Структура проекта.svg")

    code_svg(
        dirs["code"] / "Рисунок В.1 - Авторизация и создание клиента.svg",
        "Рисунок В.1 – Авторизация риелтора и создание клиентской заявки",
        [
            ("apps/api/src/data/realtors.ts", ROOT / "apps/api/src/data/realtors.ts", [(12, 47)]),
            ("apps/api/src/routes/auth.ts", ROOT / "apps/api/src/routes/auth.ts", [(22, 51)]),
            ("apps/api/src/routes/clients.ts", ROOT / "apps/api/src/routes/clients.ts", [(51, 89), (113, 119)]),
        ],
    )
    code_svg(
        dirs["code"] / "Рисунок В.2 - Поиск и сохранение результатов.svg",
        "Рисунок В.2 – Запуск поиска и сохранение результатов поиска",
        [
            ("apps/api/src/services/searchService.ts", ROOT / "apps/api/src/services/searchService.ts", [(77, 105), (140, 187)]),
            ("apps/api/src/routes/clients.ts", ROOT / "apps/api/src/routes/clients.ts", [(157, 163)]),
        ],
    )
    code_svg(
        dirs["code"] / "Рисунок В.3 - Нормализация и matchScore.svg",
        "Рисунок В.3 – Нормализация объявления и расчет процента совпадения",
        [
            ("apps/search-service/app/adapters/base.py", ROOT / "apps/search-service/app/adapters/base.py", [(115, 127), (158, 239)]),
            ("apps/search-service/app/adapters/base.py", ROOT / "apps/search-service/app/adapters/base.py", [(357, 381), (520, 529)]),
            ("apps/search-service/app/services/matcher.py", ROOT / "apps/search-service/app/services/matcher.py", [(24, 100)]),
        ],
    )
    code_svg(
        dirs["code"] / "Рисунок В.4 - Подборка сообщение аналитика.svg",
        "Рисунок В.4 – Формирование подборки, сообщения и сводных показателей",
        [
            ("apps/api/src/routes/clients.ts", ROOT / "apps/api/src/routes/clients.ts", [(188, 236)]),
            ("apps/api/src/services/messageService.ts", ROOT / "apps/api/src/services/messageService.ts", [(39, 74)]),
            ("apps/api/src/routes/dashboard.ts", ROOT / "apps/api/src/routes/dashboard.ts", [(13, 42)]),
        ],
    )
    code_svg(
        dirs["tests"] / "Рисунок 25 - Код тестов нормализации.svg",
        "Рисунок 25 – Фрагмент программного кода модульных тестов нормализации объявлений",
        [
            ("apps/search-service/tests/test_normalization.py", ROOT / "apps/search-service/tests/test_normalization.py", [(27, 37), (65, 86)]),
        ],
        width=1500,
    )
    code_svg(
        dirs["tests"] / "Рисунок 26 - Код тестов matchScore.svg",
        "Рисунок 26 – Фрагмент программного кода модульных тестов расчета процента совпадения",
        [
            ("apps/search-service/tests/test_matcher.py", ROOT / "apps/search-service/tests/test_matcher.py", [(15, 67)]),
        ],
        width=1500,
    )
    terminal_svg(
        dirs["tests"] / "Рисунок 27 - Результат запуска модульных тестов.svg",
        "Рисунок 27 – Результат успешного прохождения модульных тестов",
        """
test_apartment_filters_keep_apartment_context (test_matcher.MatcherTests.test_apartment_filters_keep_apartment_context) ... ok
test_house_filters_keep_house_context (test_matcher.MatcherTests.test_house_filters_keep_house_context) ... ok
test_bad_apartment_title_is_replaced_with_structured_title (test_normalization.NormalizationTests.test_bad_apartment_title_is_replaced_with_structured_title) ... ok
test_bad_image_url_is_rejected (test_normalization.NormalizationTests.test_bad_image_url_is_rejected) ... ok
test_city_district_and_characteristics_are_extracted (test_normalization.NormalizationTests.test_city_district_and_characteristics_are_extracted) ... ok
test_description_with_phone_is_rejected (test_normalization.NormalizationTests.test_description_with_phone_is_rejected) ... ok
test_house_title_uses_land_and_location (test_normalization.NormalizationTests.test_house_title_uses_land_and_location) ... ok
test_krasnodar_city_filter_accepts_city_district (test_normalization.NormalizationTests.test_krasnodar_city_filter_accepts_city_district) ... ok
test_krasnodar_city_filter_rejects_other_krai_cities (test_normalization.NormalizationTests.test_krasnodar_city_filter_rejects_other_krai_cities) ... ok
test_rooms_parser_ignores_apartment_count_phrase (test_normalization.NormalizationTests.test_rooms_parser_ignores_apartment_count_phrase) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.001s

OK
        """.strip(),
        width=1600,
    )


if __name__ == "__main__":
    generate_all()
    print(f"Assets generated in: {ASSETS}")
