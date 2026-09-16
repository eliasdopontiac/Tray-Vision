import numpy as np
import cv2
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QSizePolicy)
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PySide6.QtCore import Qt, QRect, QPoint

class ROIDialog(QDialog):
    def __init__(self, parent=None, current_frame: np.ndarray = None):
        super().__init__(parent)
        self.setWindowTitle("Configurar ROI")
        self.setMinimumSize(700, 520)
        self.setObjectName("roiDialog")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        lbl_title = QLabel("Configuração de ROI")
        lbl_title.setObjectName("trayTitle")
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("A grade de inspeção é determinada automaticamente pelo modelo YOLO. "
                         "O preview abaixo mostra o frame atual com a malha 4×3 sobreposta.")
        lbl_sub.setObjectName("traySubtitle")
        lbl_sub.setWordWrap(True)
        layout.addWidget(lbl_sub)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(div)

        # Camera preview
        self.lbl_preview = QLabel()
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet(
            "background-color: #0F172A; border-radius: 10px; min-height: 320px;"
        )
        self.lbl_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.lbl_preview, 1)

        if current_frame is not None:
            self._render_preview(current_frame)
        else:
            self.lbl_preview.setText("Nenhum frame disponível.\nInicie a câmera antes de abrir o ROI.")
            self.lbl_preview.setStyleSheet(
                "background-color: #0F172A; color: #64748B; border-radius: 10px; "
                "min-height: 320px; font-size: 14px;"
            )

        # Info banner
        info = QFrame()
        info.setStyleSheet(
            "background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px;"
        )
        info_layout = QHBoxLayout(info)
        info_layout.setContentsMargins(12, 10, 12, 10)
        lbl_info = QLabel(
            "A definição de ROI por arraste será implementada em versão futura. "
            "Atualmente o modelo YOLO detecta os slots automaticamente."
        )
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("color: #1D4ED8; font-size: 12px;")
        info_layout.addWidget(lbl_info)
        layout.addWidget(info)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Fechar")
        btn_close.setProperty("class", "primary")
        btn_close.setMinimumWidth(120)
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _render_preview(self, frame_bgr: np.ndarray):
        """Render frame with 4x3 grid overlay as ROI preview."""
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        qimg = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
        
        target_w = min(w, 660)
        pixmap = QPixmap.fromImage(qimg).scaledToWidth(target_w, Qt.SmoothTransformation)
        pw, ph = pixmap.width(), pixmap.height()

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Grid overlay — 4 cols x 3 rows
        grid_cols, grid_rows = 4, 3
        cell_w = pw / grid_cols
        cell_h = ph / grid_rows

        pen = QPen(QColor(59, 130, 246, 180))  # #3B82F6 semi-transparent
        pen.setWidth(2)
        painter.setPen(pen)

        for i in range(1, grid_cols):
            x = int(i * cell_w)
            painter.drawLine(x, 0, x, ph)
        for i in range(1, grid_rows):
            y = int(i * cell_h)
            painter.drawLine(0, y, pw, y)

        # Slot numbers
        painter.setPen(QColor(255, 255, 255, 200))
        for r in range(grid_rows):
            for c in range(grid_cols):
                num = (r * grid_cols) + c + 1
                painter.drawText(int(c * cell_w) + 6, int(r * cell_h) + 18, f"{num:02d}")

        painter.end()
        self.lbl_preview.setPixmap(pixmap)
