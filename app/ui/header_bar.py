import datetime
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget
from PySide6.QtCore import Qt, QTimer

class HeaderBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("headerBar")
        self.setFixedHeight(56)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)
        
        # Left side - Logo & Title
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        lbl_logo = QLabel("[]") # Placeholder for Samsung square brackets logo
        lbl_logo.setStyleSheet("color: #1428A0; font-weight: bold; font-size: 20px;")
        
        lbl_title = QLabel("TRAY VISION")
        lbl_title.setObjectName("logoText")
        
        lbl_subtitle = QLabel("Quality Inspection System")
        lbl_subtitle.setObjectName("subtitleText")
        
        title_layout.addWidget(lbl_logo)
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(lbl_subtitle)
        title_layout.addStretch()
        
        layout.addLayout(title_layout, 1)
        
        # Center - Status & Model
        center_layout = QHBoxLayout()
        center_layout.setSpacing(12)
        
        self.status_label = QLabel("● ACTIVE")
        self.status_label.setObjectName("versionBadge")
        self.status_label.setStyleSheet("background-color: #E6F6EC; color: #00A650;")
        
        self.model_chip = self.model_label = QLabel("Model: Nenhum 🟦")
        self.model_chip.setObjectName("versionBadge")
        
        center_layout.addWidget(self.status_label)
        center_layout.addWidget(self.model_chip)
        
        layout.addLayout(center_layout, 1)
        
        # Right side - Clock
        self.clock_label = QLabel()
        self.clock_label.setObjectName("clockText")
        self.clock_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        layout.addWidget(self.clock_label, 1)
        
        # Clock timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        

    def update_time(self):
        now = datetime.datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S"))
        
    def set_active_model(self, model_name: str):
        if not model_name:
            self.model_chip.setText("Nenhum modelo")
            self.model_chip.setStyleSheet("background: #F1F5F9; color: #64748B; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500;")
        else:
            self.model_chip.setText(model_name)
            self.model_chip.setStyleSheet("background: #DBEAFE; color: #1E40AF; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500;")
