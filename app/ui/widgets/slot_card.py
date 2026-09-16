from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property

class SlotCard(QFrame):
    def __init__(self, index: int):
        super().__init__()
        self.setObjectName(f"slotCard_{index}")
        self.setProperty("class", "slotCard")
        self.setProperty("state", "empty")
        
        self.setFixedSize(84, 84)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        
        # Header (number & conf)
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_num = QLabel(f"{index:02d}")
        self.lbl_num.setProperty("class", "slotNumber")
        
        self.lbl_conf = QLabel("")
        self.lbl_conf.setProperty("class", "slotConf")
        self.lbl_conf.setAlignment(Qt.AlignRight)
        
        header.addWidget(self.lbl_num)
        header.addWidget(self.lbl_conf)
        
        layout.addLayout(header)
        
        # Center Icon
        self.lbl_icon = QLabel("—")
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setStyleSheet("font-size: 24px; color: #94A3B8; font-weight: bold;")
        layout.addWidget(self.lbl_icon)
        
        # Bottom Label
        self.lbl_status = QLabel("EMPTY")
        self.lbl_status.setProperty("class", "slotLabel")
        self.lbl_status.setProperty("state", "empty")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)
        
    def update_state(self, status: str, conf: float):
        self.setProperty("state", status.lower())
        self.lbl_status.setProperty("state", status.lower())
        self.lbl_status.setText(status)
        
        if status == "EMPTY":
            self.lbl_conf.setText("")
            self.lbl_icon.setText("—")
            self.lbl_icon.setStyleSheet("font-size: 20px; color: #6B6B6B; font-weight: bold;")
        elif status == "OK":
            self.lbl_conf.setText(f"{int(conf*100)}%")
            self.lbl_icon.setText("✓")
            self.lbl_icon.setStyleSheet("font-size: 20px; color: #FFFFFF; background-color: #00A650; border-radius: 12px; margin: 4px; padding-bottom: 2px;")
        elif status == "NG":
            self.lbl_conf.setText(f"{int(conf*100)}%")
            self.lbl_icon.setText("✕")
            self.lbl_icon.setStyleSheet("font-size: 16px; color: #FFFFFF; background-color: #DA1E28; border-radius: 12px; margin: 4px;")
        elif status == "NA":
            self.lbl_conf.setText("")
            self.lbl_icon.setText("—")
            self.lbl_icon.setStyleSheet("font-size: 20px; color: #6B6B6B; font-weight: bold;")
            
        # Re-apply styles
        self.style().unpolish(self)
        self.style().polish(self)
        self.lbl_status.style().unpolish(self.lbl_status)
        self.lbl_status.style().polish(self.lbl_status)
