import datetime
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget
from PySide6.QtCore import Qt, QTimer

class HeaderBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("headerBar")
        self.setFixedHeight(56)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        
        # Left side
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.logo_label = QLabel("📷 TRAY VISION")
        self.logo_label.setObjectName("appTitle")
        
        self.version_badge = QLabel("v2.0")
        self.version_badge.setObjectName("versionBadge")
        
        left_layout.addWidget(self.logo_label)
        left_layout.addWidget(self.version_badge)
        left_layout.addStretch()
        
        # Center side
        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(16)
        
        self.status_label = QLabel("🟢 Sistema Ativo")
        self.status_label.setObjectName("statusText")
        
        self.model_chip = QLabel("Nenhum modelo")
        self.model_chip.setStyleSheet("background: #DBEAFE; color: #1E40AF; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500;")
        
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setObjectName("clockText")
        
        center_layout.addWidget(self.status_label)
        center_layout.addWidget(self.model_chip)
        center_layout.addWidget(self.clock_label)
        
        # Clock timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        
        # Right side
        right_widget = QWidget()
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # We will use standard OS window controls, or add custom ones if borderless window
        # For now, let's just add a stretch to keep center centered
        right_layout.addStretch()
        
        # Set size policies to ensure center is truly centered
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        center_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        layout.addWidget(left_widget)
        layout.addWidget(center_widget)
        layout.addWidget(right_widget)
        
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
