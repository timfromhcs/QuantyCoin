"""
QuantyCoin Native Qt Cyberpunk Dark Theme & Stylesheet (v4.0 Production)
Palette: Obsidian #0A0D14 | Card #121724 | Slate #1E2433 | Cyan #00F0FF | Violet #8A2BE2 | Green #00FF88 | Pink #FF007A
"""

CYBERPUNK_QSS = """
/* ========================================================================= */
/* GLOBAL APPLICATION STYLING                                                */
/* ========================================================================= */
QMainWindow, QDialog, QWidget {
    background-color: #0A0D14;
    color: #F1F5F9;
    font-family: 'Segoe UI', -apple-system, Roboto, sans-serif;
    font-size: 13px;
}

/* ========================================================================= */
/* TOOLBARS & STATUS BARS                                                    */
/* ========================================================================= */
QToolBar {
    background-color: #121724;
    border-bottom: 1px solid #1E293B;
    padding: 6px 12px;
    spacing: 8px;
}

QToolButton {
    background-color: transparent;
    color: #94A3B8;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
    font-size: 13px;
}

QToolButton:hover {
    background-color: #181F30;
    color: #00F0FF;
    border: 1px solid rgba(0, 240, 255, 0.4);
}

QToolButton:checked {
    background-color: rgba(0, 240, 255, 0.15);
    color: #00F0FF;
    border: 1px solid #00F0FF;
}

QStatusBar {
    background-color: #0E121A;
    color: #94A3B8;
    border-top: 1px solid #1E293B;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 12px;
}

/* ========================================================================= */
/* TAB WIDGET                                                                */
/* ========================================================================= */
QTabWidget::pane {
    border: 1px solid #1E293B;
    background-color: #0A0D14;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #121724;
    color: #94A3B8;
    border: 1px solid #1E293B;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 18px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:hover {
    background-color: #181F30;
    color: #00F0FF;
}

QTabBar::tab:selected {
    background-color: rgba(0, 240, 255, 0.12);
    color: #00F0FF;
    border: 1px solid rgba(0, 240, 255, 0.5);
    border-bottom: 2px solid #00F0FF;
}

/* ========================================================================= */
/* BUTTONS                                                                   */
/* ========================================================================= */
QPushButton {
    background-color: #1E2433;
    color: #F1F5F9;
    border: 1px solid #1E293B;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #262E40;
    border: 1px solid #00F0FF;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: rgba(0, 240, 255, 0.2);
}

QPushButton:disabled {
    background-color: #121724;
    color: #475569;
    border: 1px solid #1E293B;
}

QPushButton#btn-primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00F0FF, stop:1 #0099FF);
    color: #000000;
    border: none;
    font-weight: 700;
}

QPushButton#btn-primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #33F5FF, stop:1 #1AA3FF);
}

QPushButton#btn-violet {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8A2BE2, stop:1 #6A0DAD);
    color: #FFFFFF;
    border: none;
    font-weight: 700;
}

QPushButton#btn-violet:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #A14DF0, stop:1 #7D15C9);
}

QPushButton#btn-danger {
    background-color: rgba(255, 0, 122, 0.15);
    color: #FF007A;
    border: 1px solid rgba(255, 0, 122, 0.4);
    font-weight: 700;
}

QPushButton#btn-danger:hover {
    background-color: #FF007A;
    color: #FFFFFF;
}

/* ========================================================================= */
/* INPUTS & TEXT CONTROLS                                                    */
/* ========================================================================= */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #0E121A;
    color: #F1F5F9;
    border: 1px solid #1E293B;
    border-radius: 6px;
    padding: 8px 12px;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 13px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #00F0FF;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #121724;
    color: #F1F5F9;
    selection-background-color: rgba(0, 240, 255, 0.2);
    selection-color: #00F0FF;
    border: 1px solid #1E293B;
}

/* ========================================================================= */
/* TABLES & TREES                                                            */
/* ========================================================================= */
QTableView, QTableWidget, QTreeView, QTreeWidget, QListWidget {
    background-color: #121724;
    color: #F1F5F9;
    border: 1px solid #1E293B;
    border-radius: 6px;
    gridline-color: rgba(255, 255, 255, 0.05);
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 12px;
}

QHeaderView::section {
    background-color: #1E2433;
    color: #94A3B8;
    border: none;
    border-right: 1px solid #1E293B;
    border-bottom: 1px solid #1E293B;
    padding: 6px 10px;
    font-weight: 600;
}

QTableView::item:selected, QTableWidget::item:selected, QListWidget::item:selected {
    background-color: rgba(0, 240, 255, 0.15);
    color: #00F0FF;
}

/* ========================================================================= */
/* SCROLLBARS                                                                */
/* ========================================================================= */
QScrollBar:vertical {
    background-color: #0A0D14;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #1E2433;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00F0FF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #0A0D14;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #1E2433;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #00F0FF;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ========================================================================= */
/* FRAMES & GROUPBOXES                                                       */
/* ========================================================================= */
QGroupBox {
    border: 1px solid #1E293B;
    border-radius: 8px;
    margin-top: 18px;
    padding: 16px;
    font-weight: 700;
    color: #94A3B8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #00F0FF;
}

QFrame#card-frame {
    background-color: #121724;
    border: 1px solid #1E293B;
    border-radius: 10px;
    padding: 16px;
}

QFrame#card-frame:hover {
    border: 1px solid rgba(0, 240, 255, 0.3);
}

/* ========================================================================= */
/* PROGRESS BARS & SLIDERS                                                   */
/* ========================================================================= */
QProgressBar {
    background-color: #0E121A;
    border: 1px solid #1E293B;
    border-radius: 5px;
    text-align: center;
    color: #F1F5F9;
    font-family: 'JetBrains Mono', monospace;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00F0FF, stop:1 #8A2BE2);
    border-radius: 4px;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #1E2433;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #00F0FF;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #FFFFFF;
    border: 2px solid #00F0FF;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}
"""
