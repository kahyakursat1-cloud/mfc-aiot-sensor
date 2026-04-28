"""
Biyolüminesans Tema — Renk sabitleri ve QSS stil sayfası.
Mikroorganizmaların elektrik üretirken yaydığı ışıktan ilham alındı.
"""

# ── Renk Paleti ──────────────────────────────────────────────────────────────
C = {
    "BG_DEEP":    "#070d14",   # En derin arkaplan
    "BG_PANEL":   "#0d1a24",   # Panel arkaplanı
    "BG_CARD":    "#0f2030",   # Kart arkaplanı
    "BG_CARD2":   "#142840",   # Hover / seçili kart

    "ACCENT":     "#00e5a0",   # Biyolüminesans yeşil (ana vurgu)
    "ACCENT_DIM": "#00875f",   # Sönük yeşil
    "CYAN":       "#00b8d4",   # Siyano bakterisi mavisi
    "WARNING":    "#ffb300",   # Amber uyarı
    "DANGER":     "#ff3d71",   # Tehlike kırmızısı
    "OFFLINE":    "#3a4a5a",   # Çevrimdışı gri

    "TEXT_PRI":   "#e8f4f8",   # Birincil metin
    "TEXT_SEC":   "#7a9bb5",   # İkincil metin
    "TEXT_DIM":   "#3d5a6e",   # Soluk metin

    "BORDER":     "#1e3a4a",   # Kart kenarlığı
    "BORDER_ACC": "#00e5a0",   # Aktif kenarlık
    "BORDER_WRN": "#ffb300",   # Uyarı kenarlığı
    "BORDER_ERR": "#ff3d71",   # Hata kenarlığı

    "GRID":       "#0a1520",   # Arka plan grid
}

# ── Ana QSS Stil Sayfası ─────────────────────────────────────────────────────
QSS = f"""
/* ── Global ─────────────────────────────────────────────── */
QMainWindow, QWidget {{
    background-color: {C['BG_DEEP']};
    color: {C['TEXT_PRI']};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}}

QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: {C['BG_PANEL']};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {C['ACCENT_DIM']};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ── Header ──────────────────────────────────────────────── */
#header {{
    background-color: {C['BG_PANEL']};
    border-bottom: 1px solid {C['BORDER']};
    padding: 0 16px;
}}
#appTitle {{
    color: {C['ACCENT']};
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
}}
#appSubtitle {{
    color: {C['TEXT_SEC']};
    font-size: 10px;
    letter-spacing: 1px;
}}
#clockLabel {{
    color: {C['CYAN']};
    font-size: 13px;
    letter-spacing: 1px;
}}
#statusDot {{
    font-size: 18px;
}}
#nodeCountLabel {{
    color: {C['TEXT_SEC']};
    font-size: 11px;
}}

/* ── Kart (NodeCard) ─────────────────────────────────────── */
#nodeCard {{
    background-color: {C['BG_CARD']};
    border: 1px solid {C['BORDER']};
    border-radius: 12px;
    padding: 4px;
}}
#nodeCard[status="normal"] {{
    border-color: {C['BORDER']};
}}
#nodeCard[status="warning"] {{
    border-color: {C['WARNING']};
}}
#nodeCard[status="danger"] {{
    border-color: {C['DANGER']};
}}
#nodeCard[status="offline"] {{
    border-color: {C['OFFLINE']};
    background-color: #0a1520;
}}

#cardNodeId {{
    color: {C['ACCENT']};
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 1px;
}}
#cardOnlineDot {{ font-size: 10px; }}
#cardDecision {{
    color: {C['TEXT_SEC']};
    font-size: 10px;
    letter-spacing: 1px;
}}

/* ── Sensör değer etiketleri ─────────────────────────────── */
#sensorLabel {{
    color: {C['TEXT_SEC']};
    font-size: 10px;
}}
#sensorValue {{
    color: {C['TEXT_PRI']};
    font-size: 13px;
    font-weight: bold;
}}
#sensorValue[alert="warning"] {{ color: {C['WARNING']}; }}
#sensorValue[alert="danger"]  {{ color: {C['DANGER']};  }}
#sensorValue[alert="ok"]      {{ color: {C['ACCENT']};  }}

/* ── Bölüm başlıkları ────────────────────────────────────── */
#sectionTitle {{
    color: {C['TEXT_SEC']};
    font-size: 10px;
    letter-spacing: 2px;
    padding: 4px 0;
}}

/* ── Anomali Logu ────────────────────────────────────────── */
#anomalyLog {{
    background-color: {C['BG_PANEL']};
    border: 1px solid {C['BORDER']};
    border-radius: 8px;
}}
#anomalyTitle {{
    color: {C['DANGER']};
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
    padding: 8px 12px 4px 12px;
}}
QListWidget {{
    background-color: transparent;
    border: none;
    outline: none;
}}
QListWidget::item {{
    padding: 4px 8px;
    border-bottom: 1px solid {C['BG_DEEP']};
    color: {C['TEXT_SEC']};
    font-size: 11px;
}}
QListWidget::item:selected {{
    background-color: {C['BG_CARD2']};
    color: {C['TEXT_PRI']};
}}

/* ── Chart panel ─────────────────────────────────────────── */
#chartPanel {{
    background-color: {C['BG_PANEL']};
    border: 1px solid {C['BORDER']};
    border-radius: 8px;
}}
#chartTitle {{
    color: {C['TEXT_SEC']};
    font-size: 10px;
    letter-spacing: 2px;
    padding: 8px 12px 0 12px;
}}

/* ── Butonlar ────────────────────────────────────────────── */
QPushButton {{
    background-color: {C['BG_CARD']};
    color: {C['ACCENT']};
    border: 1px solid {C['ACCENT_DIM']};
    border-radius: 6px;
    padding: 4px 14px;
    font-size: 11px;
    letter-spacing: 1px;
}}
QPushButton:hover {{
    background-color: {C['BG_CARD2']};
    border-color: {C['ACCENT']};
}}
QPushButton:checked {{
    background-color: {C['ACCENT_DIM']};
    color: {C['BG_DEEP']};
}}
QPushButton:flat {{
    border: none;
    background: transparent;
}}

/* ── Ayırıcı ─────────────────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {C['BORDER']};
}}

/* ── Tooltip ─────────────────────────────────────────────── */
QToolTip {{
    background-color: {C['BG_CARD2']};
    color: {C['TEXT_PRI']};
    border: 1px solid {C['ACCENT_DIM']};
    padding: 4px;
    font-size: 11px;
}}
"""

# ── pyqtgraph renkleri ───────────────────────────────────────────────────────
PG_BACKGROUND = C["BG_PANEL"]
PG_FOREGROUND = C["TEXT_DIM"]

NODE_COLORS = [
    C["ACCENT"],     # Node 1 — yeşil
    C["CYAN"],       # Node 2 — camgöbeği
    "#b39ddb",       # Node 3 — lavanta
    "#ffd54f",       # Node 4 — sarı
]

CHART_METRICS = {
    "soil_moisture": ("Toprak Nemi",  "%",   0,   100, C["ACCENT"]),
    "ph":            ("pH",           "",    4,   10,  C["CYAN"]),
    "gas_ppm":       ("Gaz",          "ppm", 0,   800, "#b39ddb"),
    "temperature_c": ("Sıcaklık",     "°C",  -5,  50,  C["WARNING"]),
}
