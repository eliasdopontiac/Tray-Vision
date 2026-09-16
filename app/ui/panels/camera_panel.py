import cv2
import numpy as np
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QSizePolicy
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont
from PySide6.QtCore import Qt, QRect

class CameraPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("cameraPanel")
        self.setProperty("class", "card")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # We need a container that keeps aspect ratio or fills nicely
        # For simplicity, we just use a QLabel with scaledContents and draw everything on it
        self.lbl_camera = QLabel()
        self.lbl_camera.setAlignment(Qt.AlignCenter)
        self.lbl_camera.setStyleSheet("background-color: #000000; border-radius: 12px;")
        
        layout.addWidget(self.lbl_camera)
        
        # HUD overlay
        self.hud = QWidget(self.lbl_camera)
        self.hud.setObjectName("hudOverlay")
        self.hud.setFixedHeight(32)
        # Position is managed in resizeEvent
        
        hud_layout = QHBoxLayout(self.hud)
        hud_layout.setContentsMargins(12, 0, 12, 0)
        
        self.lbl_hud_status = QLabel("● ATIVO")
        self.lbl_hud_status.setStyleSheet("color: #10B981; font-weight: bold; font-size: 11px;")
        
        self.lbl_hud_res = QLabel("Câmera 0 | 1920×1080")
        self.lbl_hud_res.setProperty("class", "hudText")
        
        self.lbl_hud_lat = QLabel("Latência: 0ms")
        self.lbl_hud_lat.setProperty("class", "hudText")
        
        self.lbl_hud_fps = QLabel("FPS: 0")
        self.lbl_hud_fps.setProperty("class", "hudText")
        
        hud_layout.addWidget(self.lbl_hud_status)
        hud_layout.addWidget(self.lbl_hud_res)
        hud_layout.addWidget(self.lbl_hud_lat)
        hud_layout.addWidget(self.lbl_hud_fps)
        
        self.current_frame = None
        self.current_results = None
        self.grid_rows = 3
        self.grid_cols = 4

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Center HUD at the top
        hud_w = 400
        self.hud.setGeometry((self.width() - hud_w) // 2, 16, hud_w, 32)
        
        # If we have a frame, redraw to keep aspect ratio and overlays aligned
        if self.current_frame is not None:
            self.update_frame(self.current_frame, self.current_results)

    def set_metrics(self, latency: float, fps: float):
        self.lbl_hud_lat.setText(f"Latência: {latency:.1f}ms")
        self.lbl_hud_fps.setText(f"FPS: {fps:.1f}")

    def update_frame(self, frame_bgr: np.ndarray, results=None):
        self.current_frame = frame_bgr
        self.current_results = results
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        
        qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale image to fit label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.lbl_camera.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # Draw Overlays
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate actual displayed image rect to map coordinates
        disp_w = pixmap.width()
        disp_h = pixmap.height()
        
        # Scale factors from original frame to displayed pixmap
        scale_x = disp_w / w
        scale_y = disp_h / h
        
        # 1. Draw Grid
        pen_grid = QPen(QColor("#3B82F6"))
        pen_grid.setWidth(1)
        # alpha
        c = pen_grid.color()
        c.setAlpha(150)
        pen_grid.setColor(c)
        painter.setPen(pen_grid)
        
        cell_w = disp_w / self.grid_cols
        cell_h = disp_h / self.grid_rows
        
        for i in range(1, self.grid_cols):
            x = int(i * cell_w)
            painter.drawLine(x, 0, x, disp_h)
            
        for i in range(1, self.grid_rows):
            y = int(i * cell_h)
            painter.drawLine(0, y, disp_w, y)
            
        # Draw cell numbers
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 180))
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                slot_num = (r * self.grid_cols) + c + 1
                painter.drawText(int(c * cell_w) + 4, int(r * cell_h) + 16, f"{slot_num:02d}")
        
        # 2. Draw Bounding Boxes from YOLO
        if results is not None:
            for box, cls_name, conf in zip(results.boxes, results.classes, results.confidences):
                x1, y1, x2, y2 = box
                
                # Scale coordinates
                x1 = int(x1 * scale_x)
                y1 = int(y1 * scale_y)
                x2 = int(x2 * scale_x)
                y2 = int(y2 * scale_y)
                
                # Colors
                if cls_name == "OK":
                    color = QColor("#16A34A")
                elif cls_name == "NG":
                    color = QColor("#B91C1C")
                else:
                    color = QColor("#94A3B8")
                    
                pen_box = QPen(color)
                pen_box.setWidth(3)
                painter.setPen(pen_box)
                
                # Draw Box
                rect = QRect(x1, y1, x2 - x1, y2 - y1)
                painter.drawRoundedRect(rect, 8, 8)
                
                # Draw Label Pill
                lbl_text = f"{cls_name} {int(conf*100)}%"
                
                fm = painter.fontMetrics()
                text_rect = fm.boundingRect(lbl_text)
                
                # Background rect for text
                bg_rect = QRect(x1, y1 - 20, text_rect.width() + 12, 20)
                
                painter.setPen(Qt.NoPen)
                painter.setBrush(color)
                painter.drawRoundedRect(bg_rect, 4, 4)
                
                # Text
                painter.setPen(QColor("#FFFFFF"))
                painter.drawText(x1 + 6, y1 - 5, lbl_text)
                
                # Overlay tint for NG
                if cls_name == "NG":
                    tint = QColor("#B91C1C")
                    tint.setAlpha(60)
                    painter.setBrush(tint)
                    painter.drawRoundedRect(rect, 8, 8)
                
        painter.end()
        self.lbl_camera.setPixmap(pixmap)
