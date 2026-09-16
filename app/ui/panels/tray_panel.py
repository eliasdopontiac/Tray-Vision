from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QWidget)
from PySide6.QtCore import Qt, Signal
from app.ui.widgets.slot_card import SlotCard
import datetime

class TrayPanel(QFrame):
    reset_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self.setObjectName("trayPanel")
        self.setProperty("class", "card")
        self.setFixedWidth(300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(16)
        
        # Header
        lbl_title = QLabel("TRAY STATUS")
        lbl_title.setObjectName("trayTitle")
        
        self.lbl_subtitle = QLabel("4×3 · 12 SLOTS")
        self.lbl_subtitle.setObjectName("traySubtitle")
        
        layout.addWidget(lbl_title)
        layout.addWidget(self.lbl_subtitle)
        
        # Grid
        grid_container = QWidget()
        self.grid = QGridLayout(grid_container)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(8)
        
        self.cards = []
        for i in range(12):
            card = SlotCard(i + 1)
            row = i // 3
            col = i % 3
            self.grid.addWidget(card, row, col)
            self.cards.append(card)
            
        layout.addWidget(grid_container)
        
        # Summary Row
        summary_layout = QHBoxLayout()
        summary_layout.setContentsMargins(0, 8, 0, 8)
        
        self.lbl_ok = QLabel("✓ OK: 0")
        self.lbl_ok.setProperty("class", "badge")
        self.lbl_ok.setProperty("type", "ok")
        
        self.lbl_ng = QLabel("✗ NG: 0")
        self.lbl_ng.setProperty("class", "badge")
        self.lbl_ng.setProperty("type", "ng")
        
        self.lbl_na = QLabel("— NA: 0")
        self.lbl_na.setProperty("class", "badge")
        self.lbl_na.setProperty("type", "na")
        
        summary_layout.addWidget(self.lbl_ok)
        summary_layout.addWidget(self.lbl_ng)
        summary_layout.addWidget(self.lbl_na)
        
        layout.addLayout(summary_layout)
        
        # Alert Banner
        self.alert_banner = QFrame()
        self.alert_banner.setObjectName("alertBanner")
        alert_layout = QHBoxLayout(self.alert_banner)
        alert_layout.setContentsMargins(12, 12, 12, 12)
        
        self.lbl_alert_icon = QLabel("⚠")
        self.lbl_alert_icon.setStyleSheet("color: #B91C1C; font-size: 16px;")
        
        self.lbl_alert_text = QLabel("Defeito detectado")
        self.lbl_alert_text.setObjectName("alertText")
        
        alert_layout.addWidget(self.lbl_alert_icon)
        alert_layout.addWidget(self.lbl_alert_text)
        alert_layout.addStretch()
        
        self.alert_banner.hide()
        layout.addWidget(self.alert_banner)
        
        layout.addStretch()
        
        # Reset Button
        self.btn_reset = QPushButton("NEW INSPECTION")
        self.btn_reset.setProperty("class", "primary") # using primary outlined style instead of toolBtn
        self.btn_reset.setStyleSheet("background-color: transparent; color: #1428A0; border: 1px solid #1428A0;")
        self.btn_reset.setMinimumHeight(44)
        self.btn_reset.clicked.connect(self.reset_clicked)
        layout.addWidget(self.btn_reset)
        
    def update_slots(self, states: list):
        ok = ng = na = 0
        ng_slots = []
        
        for state in states:
            idx = state.index - 1
            if 0 <= idx < 12:
                self.cards[idx].update_state(state.status, state.confidence)
                
                if state.status == "OK": ok += 1
                elif state.status == "NG": 
                    ng += 1
                    ng_slots.append(state.index)
                elif state.status == "NA": na += 1
                
        self.lbl_ok.setText(f"✓ {ok} OK")
        self.lbl_ng.setText(f"✗ {ng} NG")
        self.lbl_na.setText(f"— {na} NA")
        
        if ng > 0:
            slots_str = ", ".join([f"{s:02d}" for s in ng_slots])
            self.lbl_alert_text.setText(f"⚠ Defect detected — Slot {slots_str}")
            if self.alert_banner.isHidden():
                self.alert_banner.show()
        else:
            if not self.alert_banner.isHidden():
                self.alert_banner.hide()
                
    def set_visual_alert(self, is_active: bool):
        # Use dynamic property so QSS rules react cleanly without wiping global styles
        self.setProperty("alertActive", is_active)
        self.style().unpolish(self)
        self.style().polish(self)
