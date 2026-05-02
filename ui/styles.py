# ui/styles.py

GLOBAL_STYLE = """
QMainWindow { ... }   ← isi dari get_global_styles()
"""

def get_global_styles():
    return """
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #0a0f1e, stop:1 #1a2332);
        color: #e2e8f0;
    }
    QLabel  { color: #e2e8f0; font-weight: 500; }
    QFrame  {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1e293b, stop:1 #0f172a);
        border: 1px solid #334155;
        border-radius: 16px;
    }
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #3b82f6, stop:1 #1d4ed8);
        color: white;
        border: 2px solid #1e40af;
        border-radius: 10px;
        padding: 10px 16px;
        font-size: 13px;
        font-weight: 600;
        min-height: 40px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #60a5fa, stop:1 #3b82f6);
    }
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #2563eb, stop:1 #1d4ed8);
    }
    """

def cp_style_off():
    return """
        QPushButton {
            background: #1e293b;
            color: #64748b;
            border: 1px solid #334155;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
        }
        QPushButton:hover { border-color: #3b82f6; color: #93c5fd; }
    """


def cp_style_on():
    return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1d4ed8, stop:1 #1e3a8a);
            color: #bfdbfe;
            border: 2px solid #3b82f6;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
        }
    """
def _btn_start_active():
    return """
        QPushButton {
            background: rgba(16, 185, 129, 0.35);
            color: #d1fae5;
            border: 2px solid #34d399;
            border-radius: 10px;
            font-size: 14px; font-weight: 700;
            min-height: 48px;
        }
        QPushButton:hover { background: rgba(16, 185, 129, 0.45); }
    """
def _btn_start_dim():
    return """
        QPushButton {
            background: rgba(16, 185, 129, 0.10);
            color: #6ee7b7;
            border: 1px solid #10b981;
            border-radius: 10px;
            font-size: 14px; font-weight: 700;
            min-height: 48px;
        }
        QPushButton:hover { background: rgba(16, 185, 129, 0.20); color: #a7f3d0; }
    """
def _btn_stop_active():
    return """
        QPushButton {
            background: rgba(239, 68, 68, 0.35);
            color: #fee2e2;
            border: 2px solid #f87171;
            border-radius: 10px;
            font-size: 14px; font-weight: 700;
            min-height: 48px;
        }
        QPushButton:hover { background: rgba(239, 68, 68, 0.45); }
    """
def _btn_stop_dim():
    return """
        QPushButton {
            background: rgba(239, 68, 68, 0.10);
            color: #fca5a5;
            border: 1px solid #ef4444;
            border-radius: 10px;
            font-size: 14px; font-weight: 700;
            min-height: 48px;
        }
        QPushButton:hover { background: rgba(239, 68, 68, 0.20); color: #fecaca; }
    """

def _btn_retry_active():
    return """
        QPushButton {
            background: rgba(56, 189, 248, 0.35);
            color: #e0f2fe;
            border: 2px solid #7dd3fc;
            border-radius: 10px;
            font-size: 13px; font-weight: 600;
            min-height: 40px;
        }
    """

def _btn_retry_dim():
    return """
        QPushButton {
            background: rgba(56, 189, 248, 0.10);
            color: #7dd3fc;
            border: 1px solid #38bdf8;
            border-radius: 10px;
            font-size: 13px; font-weight: 600;
            min-height: 40px;
        }
        QPushButton:hover { background: rgba(56, 189, 248, 0.22); color: #bae6fd; }
    """
def _color_btn_style(self, color, active):
    if color == "red":
        if active:
            return "QPushButton { background: #dc2626; color: white; border: 2px solid #ef4444; border-radius: 8px; font-size: 13px; font-weight: 700; min-height: 40px; }"
            return "QPushButton { background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid #7f1d1d; border-radius: 8px; font-size: 13px; min-height: 40px; }"
    else:
        if active:
            return "QPushButton { background: #1d4ed8; color: white; border: 2px solid #3b82f6; border-radius: 8px; font-size: 13px; font-weight: 700; min-height: 40px; }"
            return "QPushButton { background: rgba(59,130,246,0.1); color: #93c5fd; border: 1px solid #1e3a5f; border-radius: 8px; font-size: 13px; min-height: 40px; }"

def _status_style(self, c1, c2):
    return f"""
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {c1},stop:1 {c2});
        border-radius: 12px; padding: 14px;
        font-size: 16px; font-weight: 700;
    """

