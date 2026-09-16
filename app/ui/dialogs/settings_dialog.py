from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QSizePolicy)
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.setMinimumSize(420, 300)
        self.setObjectName("settingsDialog")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        lbl_title = QLabel("Configurações do Sistema")
        lbl_title.setObjectName("trayTitle")
        layout.addWidget(lbl_title)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(div)

        # Info Items
        items = [
            ("•", "Câmera IP/URL", "Suporte a câmera RTSP e HTTP (futuro)"),
            ("•", "Diretório de Modelos", "Alterar pasta padrão de modelos .pt (futuro)"),
            ("•", "Alertas Sonoros", "Configurar arquivo WAV customizado (futuro)"),
            ("•", "Escala da Interface", "100% / 125% / 150% (futuro)"),
        ]

        for icon, title, desc in items:
            row = QFrame()
            row.setStyleSheet("background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:2px;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 10, 12, 10)

            lbl_icon = QLabel(icon)
            lbl_icon.setFixedWidth(24)

            col = QVBoxLayout()
            lbl_t = QLabel(title)
            lbl_t.setStyleSheet("font-weight: 600; color: #1E293B; font-size: 13px;")
            lbl_d = QLabel(desc)
            lbl_d.setStyleSheet("color: #64748B; font-size: 11px;")
            col.addWidget(lbl_t)
            col.addWidget(lbl_d)
            col.setSpacing(2)

            row_layout.addWidget(lbl_icon)
            row_layout.addLayout(col)
            layout.addWidget(row)

        layout.addStretch()

        btn_close = QPushButton("Fechar")
        btn_close.setProperty("class", "primary")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
