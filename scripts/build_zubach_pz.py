from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "docs" / "assets" / "zubach_pz"
OUTPUT = ROOT / "67_Зубач_ПЗ.docx"

PAGE_WIDTH = 1650
PAGE_HEIGHT = 980
WHITE = "#ffffff"
BLACK = "#262626"
GRAY = "#666666"
LIGHT = "#f1f1f1"
MID = "#d7d7d7"
ORANGE = "#ff6a00"


@dataclass
class UseCase:
    name: str
    actors: str
    summary: str
    goal: str
    kind: str
    success_actions: list[str]
    success_system: list[str]
    exception_actions: list[str]
    exception_system: list[str]


@dataclass
class TestCase:
    ident: str
    name: str
    goal: str
    preconditions: str
    actions: list[str]
    expected: str


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


FONT_20 = load_font(20)
FONT_24 = load_font(24)
FONT_28 = load_font(28)
FONT_32 = load_font(32, bold=True)
FONT_40 = load_font(40, bold=True)
FONT_18B = load_font(18, bold=True)


def canvas(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), WHITE)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((24, 24, PAGE_WIDTH - 24, PAGE_HEIGHT - 24), radius=28, outline=MID, width=3)
    draw.text((56, 48), title, fill=BLACK, font=FONT_32)
    return image, draw


def draw_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fill: str = WHITE, outline: str = MID, radius: int = 18, font=FONT_24, text_fill: str = BLACK) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=3)
    x1, y1, x2, y2 = box
    text_box = draw.multiline_textbbox((0, 0), text, font=font, spacing=6, align="center")
    tw = text_box[2] - text_box[0]
    th = text_box[3] - text_box[1]
    draw.multiline_text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2), text, fill=text_fill, font=font, spacing=6, align="center")


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], fill: str = BLACK, width: int = 4) -> None:
    draw.line((start, end), fill=fill, width=width)
    ex, ey = end
    sx, sy = start
    if abs(ex - sx) >= abs(ey - sy):
        direction = 1 if ex >= sx else -1
        draw.polygon([(ex, ey), (ex - 18 * direction, ey - 10), (ex - 18 * direction, ey + 10)], fill=fill)
    else:
        direction = 1 if ey >= sy else -1
        draw.polygon([(ex, ey), (ex - 10, ey - 18 * direction), (ex + 10, ey - 18 * direction)], fill=fill)


def save(image: Image.Image, name: str) -> Path:
    ensure_dir(ASSETS_DIR)
    path = ASSETS_DIR / name
    image.save(path)
    return path


def build_use_case_diagram() -> Path:
    image, draw = canvas("Диаграмма вариантов использования приложения «Тэона»")
    draw_box(draw, (70, 260, 250, 620), "Риелтор", fill="#fafafa", font=FONT_32)
    cases = [
        ((420, 120, 770, 210), "Авторизация"),
        ((420, 250, 770, 340), "Создание клиента"),
        ((420, 380, 770, 470), "Запуск поиска объектов"),
        ((900, 120, 1270, 210), "Просмотр найденных\nобъектов"),
        ((900, 250, 1270, 340), "Добавление объекта\nв подборку"),
        ((900, 380, 1270, 470), "Формирование текста\nподборки"),
        ((660, 560, 1030, 650), "Отметка статуса\n«Отправлено»"),
    ]
    for box, text in cases:
        draw_box(draw, box, text, fill="#fff9f4")
    for target_y in [165, 295, 425]:
        draw_arrow(draw, (250, 440), (420, target_y))
    draw_arrow(draw, (770, 295), (900, 295))
    draw_arrow(draw, (770, 425), (900, 425))
    draw_arrow(draw, (1085, 340), (1085, 380))
    draw_arrow(draw, (845, 470), (845, 560))
    return save(image, "01_use_case.png")


def build_activity_diagram() -> Path:
    image, draw = canvas("Блок-схема сценария подбора объектов")
    nodes = [
        ((650, 90, 1000, 170), "Начало работы."),
        ((620, 220, 1030, 320), "Действие №1. Риелтор вводит данные клиента."),
        ((620, 370, 1030, 470), "Действие №2. Система сохраняет клиента\nи профиль поиска."),
        ((620, 520, 1030, 620), "Действие №3. API запускает search-service."),
        ((620, 670, 1030, 770), "Действие №4. Search-service нормализует\nи фильтрует объекты."),
        ((620, 820, 1030, 920), "Действие №5. API сохраняет найденные\nобъекты и результаты поиска."),
    ]
    for box, text in nodes:
        draw_box(draw, box, text)
    for idx in range(len(nodes) - 1):
        start = ((nodes[idx][0][0] + nodes[idx][0][2]) // 2, nodes[idx][0][3])
        end = ((nodes[idx + 1][0][0] + nodes[idx + 1][0][2]) // 2, nodes[idx + 1][0][1])
        draw_arrow(draw, start, end)
    draw_box(draw, (160, 520, 500, 620), "Условие.\nНайденные объекты есть.", fill="#fff9f4")
    draw_arrow(draw, (620, 570), (500, 570))
    draw_box(draw, (1120, 520, 1470, 620), "Исключение.\nИсточники недоступны.", fill="#fff2f2")
    draw_arrow(draw, (1030, 570), (1120, 570))
    return save(image, "02_activity.png")


def build_architecture_diagram() -> Path:
    image, draw = canvas("Архитектурная схема системы")
    draw_box(draw, (120, 250, 430, 390), "Frontend\nReact + Vite", fill="#fff9f4", font=FONT_32)
    draw_box(draw, (540, 250, 890, 390), "Backend API\nNode.js + Express + pg", fill="#fff9f4", font=FONT_32)
    draw_box(draw, (1010, 160, 1440, 320), "Search-service\nPython + FastAPI", fill="#fff9f4", font=FONT_32)
    draw_box(draw, (1010, 420, 1440, 580), "PostgreSQL\nПостоянное хранение", fill="#fff9f4", font=FONT_32)
    draw_box(draw, (1010, 700, 1440, 860), "Внешние источники\nсайты новостроек и КП", fill="#fafafa", font=FONT_32)
    draw_arrow(draw, (430, 320), (540, 320))
    draw_arrow(draw, (890, 280), (1010, 240))
    draw_arrow(draw, (890, 360), (1010, 500))
    draw_arrow(draw, (1225, 320), (1225, 420))
    draw_arrow(draw, (1225, 700), (1225, 580))
    draw.text((150, 500), "Frontend отвечает за интерфейс,\nмаршруты и отображение данных.", font=FONT_24, fill=GRAY, spacing=8)
    draw.text((540, 640), "API хранит клиентов, найденные объекты,\nподборки, тексты сообщений и историю поиска.", font=FONT_24, fill=GRAY, spacing=8)
    return save(image, "03_architecture.png")


def build_er_schema() -> Path:
    image, draw = canvas("Схема базы данных PostgreSQL")
    boxes = {
        "users": (70, 120, 390, 330),
        "clients": (430, 120, 780, 360),
        "client_search_profiles": (820, 80, 1220, 340),
        "properties": (1260, 80, 1600, 360),
        "client_found_properties": (820, 420, 1220, 670),
        "shortlist_items": (1260, 420, 1600, 610),
        "share_messages": (430, 470, 780, 650),
        "search_runs": (70, 470, 390, 650),
    }
    content = {
        "users": "users\nid\nlogin\npassword_hash\nname\nemail\nphone",
        "clients": "clients\nid\nrealtor_id\nname\nphone\nstatus\nproperty_type",
        "client_search_profiles": "client_search_profiles\nid\nclient_id\nbudget_min / max\nrooms_min / max\narea_min / max\ndistricts[]",
        "properties": "properties\nid\nsource_url\ntitle\nprice\narea\nrooms\nimages[]",
        "client_found_properties": "client_found_properties\nid\nclient_id\nproperty_id\nmatch_score\nmatch_reasons[]",
        "shortlist_items": "shortlist_items\nid\nclient_id\nproperty_id\nnote",
        "share_messages": "share_messages\nid\nclient_id\nchannel\nmessage_text\nsent_marked_at",
        "search_runs": "search_runs\nid\nclient_id\nstatus\ntotal_found\ntotal_saved",
    }
    for key, box in boxes.items():
        draw_box(draw, box, content[key], font=FONT_20)
    draw_arrow(draw, (390, 220), (430, 220))
    draw_arrow(draw, (780, 220), (820, 210))
    draw_arrow(draw, (780, 255), (1260, 220))
    draw_arrow(draw, (605, 360), (605, 470))
    draw_arrow(draw, (220, 330), (220, 470))
    draw_arrow(draw, (1020, 340), (1020, 420))
    draw_arrow(draw, (1380, 360), (1380, 420))
    draw_arrow(draw, (1220, 540), (1260, 520))
    return save(image, "04_er_schema.png")


def wireframe_frame(draw: ImageDraw.ImageDraw, title: str, subtitle: str, areas: list[tuple[tuple[int, int, int, int], str]]) -> None:
    draw.text((300, 125), title, fill=BLACK, font=FONT_40)
    draw.text((300, 182), subtitle, fill=GRAY, font=FONT_24)
    for box, label in areas:
        draw_box(draw, box, label, fill="#fafafa", font=FONT_20)


def build_wireframe_login() -> Path:
    image, draw = canvas("Wireframe окна авторизации")
    draw_box(draw, (80, 120, 760, 860), "Информационный блок\nлоготип\nописание системы", fill="#fafafa", font=FONT_28)
    areas = [
        ((960, 180, 1510, 280), "Логотип"),
        ((930, 330, 1540, 430), "Поле логина"),
        ((930, 470, 1540, 570), "Поле пароля"),
        ((930, 620, 1540, 720), "Кнопка «Войти»"),
        ((930, 760, 1540, 840), "Сообщение об ошибке / подсказка"),
    ]
    wireframe_frame(draw, "Экран входа", "Доступ к рабочему пространству риелтора.", areas)
    return save(image, "05_wireframe_login.png")


def build_wireframe_dashboard() -> Path:
    image, draw = canvas("Wireframe главной страницы")
    areas = [
        ((60, 120, 260, 900), "Боковое меню"),
        ((300, 120, 1590, 210), "Верхняя панель поиска и профиля"),
        ((300, 250, 600, 430), "KPI 1"),
        ((630, 250, 930, 430), "KPI 2"),
        ((960, 250, 1260, 430), "KPI 3"),
        ((1290, 250, 1590, 430), "KPI 4"),
        ((300, 470, 1170, 890), "График активности за 7 дней"),
        ((1200, 470, 1590, 650), "Блок внимания"),
        ((1200, 690, 1590, 890), "Последние клиенты"),
    ]
    wireframe_frame(draw, "Главная страница", "KPI, график активности и клиенты, требующие внимания.", areas)
    return save(image, "06_wireframe_dashboard.png")


def build_wireframe_clients() -> Path:
    image, draw = canvas("Wireframe списка клиентов")
    areas = [
        ((60, 120, 260, 900), "Боковое меню"),
        ((300, 120, 1590, 210), "Верхняя панель"),
        ((300, 250, 1590, 340), "Фильтр и строка поиска"),
        ((300, 380, 1590, 890), "Таблица клиентов\nФИО | Профиль | Статус | Дата | Действие"),
    ]
    wireframe_frame(draw, "Список клиентов", "Просмотр базы клиентов и быстрый переход в карточку.", areas)
    return save(image, "07_wireframe_clients.png")


def build_wireframe_client_card() -> Path:
    image, draw = canvas("Wireframe карточки клиента")
    areas = [
        ((60, 120, 260, 900), "Боковое меню"),
        ((300, 120, 1590, 210), "Верхняя панель"),
        ((300, 250, 980, 430), "Параметры клиента и действия"),
        ((300, 470, 1180, 900), "Найденные объекты"),
        ((1220, 250, 1590, 900), "Подборка клиента\nКнопка генерации сообщения"),
    ]
    wireframe_frame(draw, "Карточка клиента", "Поиск, результаты, shortlist и подготовка сообщения.", areas)
    return save(image, "08_wireframe_client_card.png")


def build_assets() -> dict[str, Path]:
    return {
        "use_case": build_use_case_diagram(),
        "activity": build_activity_diagram(),
        "architecture": build_architecture_diagram(),
        "er": build_er_schema(),
        "wf_login": build_wireframe_login(),
        "wf_dashboard": build_wireframe_dashboard(),
        "wf_clients": build_wireframe_clients(),
        "wf_client": build_wireframe_client_card(),
    }


def set_text_style(run, size: int = 14, bold: bool = False, italic: bool = False, font_name: str = "Times New Roman") -> None:
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def configure_styles(document: Document) -> None:
    for section in document.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(3)
        section.right_margin = Cm(1.5)
    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(14)
    pf = normal.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(0)
    pf.first_line_indent = Cm(1.25)
    for style_name, size in [("Title", 16), ("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 14)]:
        style = document.styles[style_name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.bold = True


def set_paragraph(paragraph, center: bool = False, indent: bool = True) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.first_line_indent = Cm(1.25) if indent and not center else Pt(0)


def add_text(document: Document, text: str, *, center: bool = False, bold: bool = False, italic: bool = False, indent: bool = True, size: int = 14) -> None:
    paragraph = document.add_paragraph()
    run = paragraph.add_run(text)
    set_text_style(run, size=size, bold=bold, italic=italic)
    set_paragraph(paragraph, center=center, indent=indent)


def add_heading(document: Document, text: str, level: int = 1) -> None:
    paragraph = document.add_paragraph(style=f"Heading {min(level, 3)}")
    run = paragraph.add_run(text)
    set_text_style(run, size=16 if level == 1 else 14, bold=True)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.first_line_indent = Pt(0)
    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(0)


def add_page_break(document: Document) -> None:
    document.add_page_break()


def add_toc(document: Document) -> None:
    p = document.add_paragraph()
    set_paragraph(p, indent=False)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), 'TOC \\o "1-3" \\h \\z \\u')
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "Обновите содержание в Word: правой кнопкой по содержанию -> Обновить поле."
    r.append(t)
    fld.append(r)
    p._p.append(fld)


def add_page_number(section) -> None:
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run = p.add_run()
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)
    set_text_style(run, size=12)


def add_figure(document: Document, caption: str, image_path: Path, width_cm: float = 15.5) -> None:
    p = document.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(image_path), width=Cm(width_cm))
    caption_p = document.add_paragraph()
    caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_p.paragraph_format.first_line_indent = Pt(0)
    caption_run = caption_p.add_run(caption)
    set_text_style(caption_run, italic=True)


def style_table(table) -> None:
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for row in table.rows:
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.first_line_indent = Pt(0)
                for run in paragraph.runs:
                    set_text_style(run, size=12)


def add_caption(document: Document, text: str) -> None:
    p = document.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    run = p.add_run(text)
    set_text_style(run, italic=True)


def add_key_value_table(document: Document, caption: str, rows: list[tuple[str, str]]) -> None:
    add_caption(document, caption)
    table = document.add_table(rows=0, cols=2)
    for left, right in rows:
        row = table.add_row().cells
        row[0].text = left
        row[1].text = right
    style_table(table)


def add_scenario_table(document: Document, caption: str, actions: list[str], system: list[str]) -> None:
    add_caption(document, caption)
    table = document.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Действия актера"
    table.rows[0].cells[1].text = "Отклик системы"
    for action, response in zip(actions, system):
        cells = table.add_row().cells
        cells[0].text = action
        cells[1].text = response
    style_table(table)


def add_testcase_table(document: Document, caption: str, case: TestCase) -> None:
    add_caption(document, caption)
    table = document.add_table(rows=0, cols=2)
    for left, right in [
        ("Идентификатор", case.ident),
        ("Название", case.name),
        ("Цель", case.goal),
        ("Предусловия", case.preconditions),
        ("Шаги выполнения", "\n".join(case.actions)),
        ("Ожидаемый результат", case.expected),
    ]:
        cells = table.add_row().cells
        cells[0].text = left
        cells[1].text = right
    style_table(table)


def write_title_page(document: Document) -> None:
    add_text(document, "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ", center=True, bold=True, indent=False)
    add_text(document, "Пояснительная записка к дипломному проекту", center=True, bold=True, indent=False)
    add_text(document, "по теме: «Разработка веб-приложения “Тэона” для автоматизации подбора недвижимости клиентам риелтора»", center=True, bold=True, indent=False)
    for _ in range(10):
        document.add_paragraph("")
    add_text(document, "Студент: Зубач Н.", indent=False)
    add_text(document, "Группа: ____________", indent=False)
    add_text(document, "Руководитель: ____________", indent=False)
    for _ in range(8):
        document.add_paragraph("")
    add_text(document, "2026", center=True, indent=False)
    add_page_break(document)


def write_intro(document: Document) -> None:
    add_heading(document, "Введение")
    paragraphs = [
        "В условиях роста объема предложений на рынке недвижимости риелтору требуется быстро подбирать объекты по параметрам клиента, фиксировать результаты поиска и формировать подборку для отправки. При работе вручную специалисту приходится параллельно вести клиентскую базу, просматривать сайты застройщиков и агрегаторов, сравнивать найденные предложения и собирать текст сообщения клиенту.",
        "Актуальность темы обусловлена необходимостью сокращения времени на рутинные операции риелтора и уменьшения количества ручных ошибок при подборе объектов недвижимости. Использование единого веб-приложения позволяет централизованно хранить параметры клиентов, результаты поиска, выбранные объекты и историю действий.",
        "Целью дипломного проекта является разработка веб-приложения «Тэона», обеспечивающего автоматизацию работы риелтора при подборе недвижимости. Для достижения поставленной цели необходимо решить задачи проектирования архитектуры системы, выбора стека технологий, разработки пользовательского интерфейса, реализации серверной логики, интеграции с PostgreSQL, настройки контейнерного развертывания и подготовки эксплуатационной документации.",
    ]
    for paragraph in paragraphs:
        add_text(document, paragraph)


def write_section_1(document: Document) -> None:
    add_heading(document, "1 Назначение и цели разработки")
    content = [
        "Разрабатываемое веб-приложение предназначено для автоматизации процессов работы риелтора с клиентскими заявками на подбор недвижимости. Система должна обеспечивать единое рабочее пространство, в котором специалист может авторизоваться, создать карточку клиента, сохранить параметры поиска, запустить подбор объектов, сформировать shortlist и подготовить текст сообщения для клиента.",
        "Пользователем системы является риелтор, сопровождающий клиентов на этапах первичного запроса, поиска объектов и подготовки персональной подборки. Приложение ориентировано на рынок новостроек и загородной недвижимости Краснодара и прилегающих территорий.",
        "Основной целью разработки является создание прикладного программного средства, сокращающего трудозатраты на поиск и систематизацию объектов недвижимости. Частные задачи проекта включают обеспечение постоянного хранения данных в PostgreSQL, поддержку работы через Docker Compose, нормализацию карточек объектов из внешних источников и предоставление понятного интерфейса для ежедневной работы.",
    ]
    for paragraph in content:
        add_text(document, paragraph)


def use_cases() -> list[UseCase]:
    return [
        UseCase(
            name="Поиск объектов для клиента",
            actors="Риелтор",
            summary="Риелтор вводит параметры клиента и инициирует подбор объектов недвижимости.",
            goal="Получить список релевантных объектов и сохранить результаты в базе данных.",
            kind="Базовый",
            success_actions=[
                "Действие №1. Риелтор авторизуется в приложении.",
                "Действие №2. Риелтор создает карточку клиента и заполняет параметры поиска.",
                "Действие №3. Риелтор подтверждает запуск поиска объектов.",
                "Действие №4. Риелтор просматривает найденные объекты.",
            ],
            success_system=[
                "Действие №1. Система открывает рабочее пространство риелтора.",
                "Действие №2. Система сохраняет клиента и профиль поиска в PostgreSQL.",
                "Действие №3. Система передает параметры в search-service, сохраняет search run и найденные объекты.",
                "Действие №4. Система отображает карточки объектов с ценой, площадью, источником и процентом совпадения.",
            ],
            exception_actions=[
                "Действие №1. Риелтор запускает поиск при временной недоступности части источников.",
                "Действие №2. Риелтор повторно открывает карточку клиента.",
            ],
            exception_system=[
                "Действие №1. Система пропускает недоступные источники, продолжает поиск по оставшимся и сохраняет только валидные результаты.",
                "Действие №2. Система показывает уже сохраненные найденные объекты и историю запусков поиска.",
            ],
        ),
        UseCase(
            name="Формирование подборки и подготовка сообщения",
            actors="Риелтор",
            summary="Риелтор отбирает подходящие объекты и формирует текст сообщения для отправки клиенту.",
            goal="Подготовить персональную подборку и сохранить ее в системе.",
            kind="Базовый",
            success_actions=[
                "Действие №1. Риелтор открывает карточку клиента.",
                "Действие №2. Риелтор добавляет объекты в подборку.",
                "Действие №3. Риелтор нажимает кнопку подготовки сообщения.",
                "Действие №4. Риелтор копирует телефон и текст сообщения.",
            ],
            success_system=[
                "Действие №1. Система отображает найденные объекты и текущую подборку.",
                "Действие №2. Система сохраняет shortlist_items в PostgreSQL.",
                "Действие №3. Система генерирует текст подборки, сохраняет share_message и показывает модальное окно.",
                "Действие №4. Система позволяет отметить подборку как отправленную.",
            ],
            exception_actions=[
                "Действие №1. Риелтор пытается сформировать сообщение при пустой подборке.",
            ],
            exception_system=[
                "Действие №1. Система выводит сообщение о том, что подборка пока пустая, и не создает share_message.",
            ],
        ),
    ]


def testcases() -> list[TestCase]:
    return [
        TestCase(
            ident="Е.1",
            name="Успешная авторизация риелтора",
            goal="Проверить возможность входа в систему по корректным учетным данным.",
            preconditions="Docker Compose запущен. В базе данных существует тестовый пользователь test / test.",
            actions=[
                "Действие №1. Открыть страницу входа в приложение.",
                "Действие №2. Ввести логин test и пароль test.",
                "Действие №3. Нажать кнопку «Войти».",
            ],
            expected="Система открывает главную страницу, устанавливает сессионную cookie и отображает данные пользователя.",
        ),
        TestCase(
            ident="Е.2",
            name="Создание нового клиента",
            goal="Проверить сохранение карточки клиента и профиля поиска.",
            preconditions="Пользователь авторизован.",
            actions=[
                "Действие №1. Перейти на страницу создания клиента.",
                "Действие №2. Заполнить обязательные поля формы.",
                "Действие №3. Нажать кнопку сохранения клиента.",
            ],
            expected="Система создает записи в таблицах clients и client_search_profiles, открывает карточку нового клиента и запускает поиск.",
        ),
        TestCase(
            ident="Е.3",
            name="Запуск поиска объектов",
            goal="Проверить загрузку, фильтрацию и сохранение результатов поиска.",
            preconditions="В системе существует клиент с заполненным профилем поиска.",
            actions=[
                "Действие №1. Открыть карточку клиента.",
                "Действие №2. Нажать кнопку повторного запуска поиска.",
                "Действие №3. Дождаться завершения запроса.",
            ],
            expected="Система создает запись search_runs, получает результаты от search-service и сохраняет найденные объекты в PostgreSQL.",
        ),
        TestCase(
            ident="Е.4",
            name="Добавление объекта в подборку",
            goal="Проверить сохранение shortlist_items и изменение состояния карточки объекта.",
            preconditions="Для клиента уже найдены объекты.",
            actions=[
                "Действие №1. Открыть карточку клиента.",
                "Действие №2. Нажать кнопку «В подборку» на одной из карточек объектов.",
            ],
            expected="Система создает запись shortlist_items, а кнопка меняет состояние на «В подборке».",
        ),
        TestCase(
            ident="Е.5",
            name="Подготовка текста подборки",
            goal="Проверить генерацию сообщения и запись share_messages.",
            preconditions="Подборка клиента не пуста.",
            actions=[
                "Действие №1. Открыть карточку клиента.",
                "Действие №2. Нажать кнопку подготовки сообщения.",
                "Действие №3. Проверить содержимое модального окна.",
            ],
            expected="Система формирует текст подборки, сохраняет запись share_messages и отображает телефон клиента вместе с текстом сообщения.",
        ),
    ]


def add_sql_snippet(document: Document, title: str, lines: Iterable[str]) -> None:
    add_heading(document, title, level=3)
    for line in lines:
        p = document.add_paragraph()
        p.paragraph_format.first_line_indent = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        run = p.add_run(line)
        set_text_style(run, size=11, font_name="Courier New")


def build_document(asset_paths: dict[str, Path]) -> None:
    document = Document()
    configure_styles(document)
    add_page_number(document.sections[0])
    write_title_page(document)

    add_heading(document, "Содержание")
    add_toc(document)
    add_page_break(document)

    write_intro(document)
    write_section_1(document)

    add_heading(document, "2 Разработка технического проекта")
    add_heading(document, "2.1 Определение спецификаций программного обеспечения", level=2)
    add_text(document, "С целью формализации требований к приложению была построена диаграмма вариантов использования, отражающая взаимодействие риелтора с системой. Диаграмма демонстрирует ключевые операции: авторизацию, создание клиента, запуск поиска, просмотр найденных объектов, формирование подборки и подготовку сообщения.")
    add_figure(document, "Рисунок 1 – Диаграмма вариантов использования приложения «Тэона»", asset_paths["use_case"], width_cm=16)

    first, second = use_cases()
    add_text(document, "Для детализации основного варианта использования «Поиск объектов для клиента» была составлена его характеристика и сценарии выполнения.")
    add_key_value_table(document, "Таблица 1 – Основной вариант использования «Поиск объектов для клиента»", [
        ("Вариант использования (прецедент)", first.name),
        ("Актеры", first.actors),
        ("Краткое описание", first.summary),
        ("Цель", first.goal),
        ("Тип", first.kind),
    ])
    add_scenario_table(document, "Таблица 2 – Сценарий успешного выполнения варианта использования «Поиск объектов для клиента»", first.success_actions, first.success_system)
    add_scenario_table(document, "Таблица 3 – Сценарии обработки исключительных ситуаций для варианта использования «Поиск объектов для клиента»", first.exception_actions, first.exception_system)

    add_text(document, "На основе сценария подбора объектов была построена блок-схема, описывающая последовательность операций от создания клиента до сохранения найденных объектов.")
    add_figure(document, "Рисунок 2 – Блок-схема сценария подбора объектов", asset_paths["activity"], width_cm=16)

    add_text(document, "Вторым ключевым вариантом использования является формирование персональной подборки и подготовка сообщения для клиента.")
    add_key_value_table(document, "Таблица 4 – Основной вариант использования «Формирование подборки и подготовка сообщения»", [
        ("Вариант использования (прецедент)", second.name),
        ("Актеры", second.actors),
        ("Краткое описание", second.summary),
        ("Цель", second.goal),
        ("Тип", second.kind),
    ])
    add_scenario_table(document, "Таблица 5 – Сценарий успешного выполнения варианта использования «Формирование подборки и подготовка сообщения»", second.success_actions, second.success_system)
    add_scenario_table(document, "Таблица 6 – Сценарии обработки исключительных ситуаций для варианта использования «Формирование подборки и подготовка сообщения»", second.exception_actions, second.exception_system)

    add_heading(document, "2.2 Проектирование модели данных", level=2)
    add_text(document, "Модель данных спроектирована с учетом необходимости постоянного хранения клиентов, параметров поиска, найденных объектов, shortlist и истории запусков поиска. В отличие от временных in-memory структур, PostgreSQL обеспечивает сохранность данных после перезапуска контейнеров и позволяет централизованно хранить результат поиска по каждому клиенту.")
    add_figure(document, "Рисунок 3 – Архитектурная схема системы", asset_paths["architecture"], width_cm=16)
    add_figure(document, "Рисунок 4 – Схема базы данных PostgreSQL", asset_paths["er"], width_cm=16)

    add_heading(document, "2.3 Проектирование интерфейса пользователя", level=2)
    add_text(document, "Интерфейс приложения был спроектирован в виде набора wireframes, отражающих основные рабочие окна системы. Такой подход позволил определить расположение зон управления, таблиц, карточек и модальных окон до детализации визуального оформления.")
    add_figure(document, "Рисунок 5 – Wireframe окна авторизации", asset_paths["wf_login"], width_cm=16)
    add_figure(document, "Рисунок 6 – Wireframe главной страницы", asset_paths["wf_dashboard"], width_cm=16)
    add_figure(document, "Рисунок 7 – Wireframe списка клиентов", asset_paths["wf_clients"], width_cm=16)
    add_figure(document, "Рисунок 8 – Wireframe карточки клиента", asset_paths["wf_client"], width_cm=16)

    add_heading(document, "3 Рабочий проект")
    add_heading(document, "3.1 Обоснование выбора средств разработки", level=2)
    techs = [
        "Для реализации пользовательского интерфейса выбрана библиотека React и сборщик Vite. Такое решение обеспечивает компонентный подход, быстрый локальный запуск и удобную организацию SPA-приложения.",
        "Серверная часть разработана на Node.js и Express. Библиотека pg используется для прямого подключения к PostgreSQL, что соответствует целевой архитектуре проекта и исключает промежуточный ORM-слой.",
        "Поисковый сервис реализован на Python и FastAPI, так как этот стек удобен для обработки HTTP-запросов, парсинга HTML и нормализации данных из внешних источников. Для извлечения информации применяются httpx, BeautifulSoup4 и lxml.",
        "Развертывание выполняется через Docker Compose, что позволяет запускать frontend, backend, search-service и PostgreSQL как согласованный набор контейнеров. Такой подход упрощает перенос проекта на хостинг и его демонстрацию.",
    ]
    for paragraph in techs:
        add_text(document, paragraph)

    add_heading(document, "3.2 Разработка физической модели данных", level=2)
    add_text(document, "Физическая модель данных реализована в SQL-скрипте database/init.sql. Основные таблицы и их назначение представлены в таблице 7.")
    add_caption(document, "Таблица 7 – Назначение основных таблиц базы данных")
    table = document.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Таблица"
    table.rows[0].cells[1].text = "Назначение"
    for row in [
        ("users", "Хранение учетных записей риелторов."),
        ("clients", "Карточки клиентов и основные контактные данные."),
        ("client_search_profiles", "Параметры поиска клиента."),
        ("properties", "Нормализованные карточки объектов недвижимости."),
        ("client_found_properties", "Связь клиента с найденными объектами и match score."),
        ("shortlist_items", "Ручная подборка объектов для клиента."),
        ("share_messages", "Сгенерированные тексты сообщений для отправки клиенту."),
        ("search_runs", "История запусков поиска и агрегированные результаты."),
    ]:
        cells = table.add_row().cells
        cells[0].text = row[0]
        cells[1].text = row[1]
    style_table(table)

    add_heading(document, "3.3 Программная реализация модулей", level=2)
    modules = [
        "Frontend-модуль реализует экран авторизации, главную страницу с KPI, список клиентов, форму создания клиента, карточку клиента, модальные окна просмотра объекта и подготовки сообщения, а также вспомогательные страницы профиля, помощи и настроек.",
        "Backend API предоставляет маршруты /api/auth, /api/dashboard, /api/clients и /api/properties. Через эти маршруты выполняются аутентификация, загрузка KPI, управление клиентами, запуск поиска, сохранение shortlist и подготовка текста сообщения.",
        "Search-service получает параметры клиента, распределяет запрос по адаптерам источников, нормализует title и description, фильтрует некачественные изображения, рассчитывает соответствие объекта требованиям клиента и возвращает валидный набор результатов.",
        "Модуль хранения данных реализован на PostgreSQL и поддерживает постоянное хранение клиентов, найденных объектов, shortlist и истории поиска. Инициализация схемы базы данных выполняется через SQL-скрипт при запуске контейнеров.",
    ]
    for paragraph in modules:
        add_text(document, paragraph)

    add_heading(document, "3.4 Тестирование программных модулей", level=2)
    add_heading(document, "3.4.1 Модульное тестирование", level=3)
    add_text(document, "Для search-service разработаны модульные тесты, проверяющие корректность матчинга и нормализации карточек объектов. В тестах контролируется фильтрация служебных названий, работа с ценой и площадью, а также формирование структурированных карточек недвижимости.")
    add_caption(document, "Таблица 8 – Результаты автоматизированных проверок")
    checks = document.add_table(rows=1, cols=2)
    checks.rows[0].cells[0].text = "Проверка"
    checks.rows[0].cells[1].text = "Результат"
    for row in [
        ("npm run typecheck", "Пройдено."),
        ("npm run build", "Пройдено."),
        ("python -m unittest discover -s tests -v", "Пройдено."),
    ]:
        cells = checks.add_row().cells
        cells[0].text = row[0]
        cells[1].text = row[1]
    style_table(checks)

    add_heading(document, "3.4.2 Интеграционное тестирование", level=3)
    add_text(document, "Интеграционное тестирование ориентировано на проверку сквозных пользовательских сценариев: авторизации, создания клиента, запуска поиска, добавления объекта в подборку и подготовки текста сообщения. Подробные тест-кейсы приведены в приложении Е.")

    add_heading(document, "3.5 Разработка эксплуатационной документации", level=2)
    add_text(document, "Для проекта подготовлена эксплуатационная документация, предназначенная для демонстрации и развертывания системы. В корне проекта размещены файлы PROD_COMMANDS.md, README.md, ARCHITECTURE.md и ITERATION_SUMMARY.md, позволяющие быстро поднять окружение, понять состав контейнеров и восстановить контекст предыдущих итераций.")

    add_heading(document, "Заключение")
    add_text(document, "В результате дипломного проекта разработано веб-приложение «Тэона», предназначенное для автоматизации работы риелтора при подборе недвижимости. Система объединяет клиентскую базу, параметры поиска, live-поиск по внешним источникам, формирование shortlist и подготовку текста сообщения для клиента.")
    add_text(document, "В ходе работы были спроектированы архитектура и модель данных, реализованы frontend, backend API и search-service, настроено постоянное хранение данных в PostgreSQL через Docker Compose, а также подготовлена эксплуатационная документация. Реализованная система может использоваться как основа для дальнейшего развития CRM-функций, подключения дополнительных источников недвижимости и развертывания на серверной инфраструктуре.")

    add_heading(document, "Список использованных источников")
    sources = [
        "ГОСТ 19.201-78. Единая система программной документации. Техническое задание. Требования к содержанию и оформлению.",
        "ГОСТ Р 59795-2021. Информационные технологии. Комплекс стандартов на автоматизированные системы. Требования к содержанию документов.",
        "Node.js Documentation: [сайт]. URL: https://nodejs.org/en/docs/ (дата обращения: 21.05.2026).",
        "React Documentation: [сайт]. URL: https://react.dev/ (дата обращения: 21.05.2026).",
        "FastAPI Documentation: [сайт]. URL: https://fastapi.tiangolo.com/ (дата обращения: 21.05.2026).",
        "PostgreSQL Documentation: [сайт]. URL: https://www.postgresql.org/docs/ (дата обращения: 21.05.2026).",
        "Docker Documentation: [сайт]. URL: https://docs.docker.com/ (дата обращения: 21.05.2026).",
        "Beautiful Soup Documentation: [сайт]. URL: https://www.crummy.com/software/BeautifulSoup/bs4/doc/ (дата обращения: 21.05.2026).",
    ]
    for source in sources:
        add_text(document, source, indent=False)

    add_page_break(document)
    add_heading(document, "Приложение А", level=1)
    add_text(document, "(обязательное)", center=True, indent=False)
    add_heading(document, "Требования к приложению", level=2)
    appendix_a = [
        "Приложение должно обеспечивать авторизацию риелтора, создание карточек клиентов, ввод параметров поиска, запуск поиска объектов, сохранение результатов в PostgreSQL, формирование shortlist и подготовку текста сообщения для клиента.",
        "Система должна поддерживать два типа недвижимости: квартиры и дома.",
        "Данные клиента, параметры поиска, найденные объекты, подборка и история поиска должны сохраняться после перезапуска контейнеров.",
        "Интерфейс должен предоставлять понятные страницы: вход, главная, список клиентов, карточка клиента, профиль, помощь, настройки и аналитика.",
        "Приложение должно запускаться в production-режиме через Docker Compose.",
    ]
    for paragraph in appendix_a:
        add_text(document, paragraph)

    add_page_break(document)
    add_heading(document, "Приложение Б", level=1)
    add_text(document, "(справочное)", center=True, indent=False)
    add_heading(document, "Руководство по стилю", level=2)
    for paragraph in [
        "Основная тема интерфейса светлая. В качестве акцентного цвета используется оранжевый цвет, применяемый к primary-кнопкам, активным элементам и индикаторам совпадения.",
        "Навигация организована через фиксированный sidebar и верхнюю панель, а таблицы и карточки построены в спокойном CRM-стиле без декоративных элементов.",
        "Для карточек найденных объектов используется четкая иерархия: заголовок, источник, цена, базовые характеристики, процент совпадения, шкала совпадения, кнопки «Подробнее» и «В подборку».",
    ]:
        add_text(document, paragraph)

    add_page_break(document)
    add_heading(document, "Приложение В", level=1)
    add_text(document, "(обязательное)", center=True, indent=False)
    add_heading(document, "SQL-скрипты таблиц базы данных", level=2)
    add_sql_snippet(document, "Основные фрагменты SQL-схемы", [
        "CREATE TABLE IF NOT EXISTS clients (",
        "  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),",
        "  realtor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,",
        "  name VARCHAR(160) NOT NULL,",
        "  phone VARCHAR(40) NOT NULL,",
        "  status VARCHAR(40) NOT NULL DEFAULT 'new',",
        "  property_type VARCHAR(20) NOT NULL",
        ");",
        "",
        "CREATE TABLE IF NOT EXISTS properties (",
        "  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),",
        "  source_url TEXT UNIQUE NOT NULL,",
        "  property_type VARCHAR(20) NOT NULL,",
        "  title TEXT NOT NULL,",
        "  price NUMERIC,",
        "  area NUMERIC,",
        "  rooms INTEGER,",
        "  images TEXT[] NOT NULL DEFAULT '{}'",
        ");",
    ])

    add_page_break(document)
    add_heading(document, "Приложение Г", level=1)
    add_text(document, "(справочное)", center=True, indent=False)
    add_heading(document, "Программный код модулей системы", level=2)
    add_text(document, "Структура проекта организована по модулям apps/web, apps/api и apps/search-service. Ниже приведены фрагменты, отражающие точки входа в систему.")
    add_sql_snippet(document, "Фрагмент backend API", [
        "app.use('/api/auth', authRouter);",
        "app.use('/api/dashboard', dashboardRouter);",
        "app.use('/api/clients', clientsRouter);",
        "app.use('/api/properties', propertiesRouter);",
    ])
    add_sql_snippet(document, "Фрагмент Docker Compose", [
        "services:",
        "  postgres:",
        "  search-service:",
        "  api:",
        "  web:",
    ])

    add_page_break(document)
    add_heading(document, "Приложение Д", level=1)
    add_text(document, "(справочное)", center=True, indent=False)
    add_heading(document, "Формы выходных документов", level=2)
    add_text(document, "Результатом работы системы для риелтора являются сформированная подборка и текст сообщения для клиента. Пример структуры сообщения приведен ниже.")
    add_sql_snippet(document, "Пример текста подборки", [
        "Здравствуйте. Подобрал для вас несколько вариантов.",
        "1. ЖК «Nova Vita», 1-комн., 40.6 м², 5 275 000 ₽.",
        "2. ЖК «Точно», 2-комн., 53.8 м², 6 540 000 ₽.",
        "Если хотите, могу уточнить детали по каждому варианту.",
    ])

    add_page_break(document)
    add_heading(document, "Приложение Е", level=1)
    add_text(document, "(обязательное)", center=True, indent=False)
    add_heading(document, "Тест-кейсы", level=2)
    for case in testcases():
        add_testcase_table(document, f"Таблица {case.ident} – {case.name}", case)

    add_page_break(document)
    add_heading(document, "Приложение Ж", level=1)
    add_text(document, "(обязательное)", center=True, indent=False)
    add_heading(document, "Руководство пользователя", level=2)
    guide = [
        "Действие №1. Установить Docker Desktop на ноутбук и запустить приложение.",
        "Действие №2. В корне проекта выполнить команды cp .env.example .env и npm run prod:up.",
        "Действие №3. Открыть приложение по адресу http://localhost:5002.",
        "Действие №4. Выполнить вход с тестовыми учетными данными test / test.",
        "Действие №5. Создать нового клиента и заполнить параметры поиска.",
        "Действие №6. Дождаться результатов поиска и при необходимости повторно запустить поиск из карточки клиента.",
        "Действие №7. Добавить подходящие объекты в подборку, сформировать сообщение и скопировать текст для отправки клиенту.",
        "Действие №8. Для остановки системы выполнить команду npm run prod:down.",
    ]
    for line in guide:
        add_text(document, line, indent=False)

    document.save(OUTPUT)


def main() -> None:
    assets = build_assets()
    build_document(assets)


if __name__ == "__main__":
    main()
