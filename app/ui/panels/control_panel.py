import os
from glob import glob
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QSlider, QWidget, QSizePolicy)
from PySide6.QtCore import Qt, Signal

class ControlPanel(QFrame):
    start_clicked = Signal()
    stop_clicked = Signal()
    model_selected = Signal(str)
    camera_selected = Signal(int)
    conf_changed = Signal(float)
    settings_clicked = Signal()
    roi_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self.setObjectName("controlPanel")
        self.setProperty("class", "card")
        self.setFixedWidth(260)
        
        # Add shadow in main_window.py
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(16)
        
        # --- CONFIGURAÇÕES Header ---
        header_lbl = QLabel("CONFIGURAÇÕES")
        header_lbl.setProperty("class", "sectionHeader")
        layout.addWidget(header_lbl)
        
        # --- MODELO Section ---
        model_layout = QVBoxLayout()
        model_layout.setSpacing(6)
        
        lbl_model = QLabel("MODELO")
        lbl_model.setProperty("class", "inputLabel")
        model_layout.addWidget(lbl_model)
        
        self.combo_model = QComboBox()
        self.combo_model.currentTextChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.combo_model)
        
        # Chips (OK / NG / NA)
        chips_layout = QHBoxLayout()
        
        chip_ok = QLabel("OK")
        chip_ok.setProperty("class", "badge")
        chip_ok.setProperty("type", "ok")
        chip_ok.setAlignment(Qt.AlignCenter)
        
        chip_ng = QLabel("NG")
        chip_ng.setProperty("class", "badge")
        chip_ng.setProperty("type", "ng")
        chip_ng.setAlignment(Qt.AlignCenter)
        
        chip_na = QLabel("NA")
        chip_na.setProperty("class", "badge")
        chip_na.setProperty("type", "na")
        chip_na.setAlignment(Qt.AlignCenter)
        
        chips_layout.addWidget(chip_ok)
        chips_layout.addWidget(chip_ng)
        chips_layout.addWidget(chip_na)
        model_layout.addLayout(chips_layout)
        
        layout.addLayout(model_layout)
        
        # Divider
        div1 = QFrame()
        div1.setFrameShape(QFrame.HLine)
        div1.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(div1)
        
        # --- CAMERA Section ---
        cam_layout = QVBoxLayout()
        cam_layout.setSpacing(6)
        
        lbl_cam = QLabel("CÂMERA")
        lbl_cam.setProperty("class", "inputLabel")
        cam_layout.addWidget(lbl_cam)
        
        cam_row = QHBoxLayout()
        self.combo_cam = QComboBox()
        self.combo_cam.currentIndexChanged.connect(self._on_cam_changed)
        
        self.btn_refresh_cam = QPushButton("Atualizar")
        self.btn_refresh_cam.setFixedHeight(32)
        self.btn_refresh_cam.setProperty("class", "toolBtn")
        
        cam_row.addWidget(self.combo_cam)
        cam_row.addWidget(self.btn_refresh_cam)
        cam_layout.addLayout(cam_row)
        
        layout.addLayout(cam_layout)
        
        # --- LIMIAR Section ---
        lim_layout = QVBoxLayout()
        lim_layout.setSpacing(6)
        
        lim_header = QHBoxLayout()
        lbl_lim = QLabel("LIMIAR DE CONFIANÇA")
        lbl_lim.setProperty("class", "inputLabel")
        
        self.lbl_lim_val = QLabel("87%")
        self.lbl_lim_val.setStyleSheet("color: #1E40AF; font-weight: bold; font-size: 12px;")
        
        lim_header.addWidget(lbl_lim)
        lim_header.addStretch()
        lim_header.addWidget(self.lbl_lim_val)
        
        lim_layout.addLayout(lim_header)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(10, 99)
        self.slider.setValue(87)
        self.slider.valueChanged.connect(self._on_slider_changed)
        lim_layout.addWidget(self.slider)
        
        layout.addLayout(lim_layout)
        
        # Divider
        div2 = QFrame()
        div2.setFrameShape(QFrame.HLine)
        div2.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(div2)
        
        # --- ACTION BUTTONS ---
        self.btn_start = QPushButton("▶ INICIAR INSPEÇÃO")
        self.btn_start.setProperty("class", "primary")
        self.btn_start.clicked.connect(self.start_clicked)
        
        self.btn_stop = QPushButton("■ PARAR")
        self.btn_stop.setProperty("class", "danger")
        self.btn_stop.clicked.connect(self.stop_clicked)
        self.btn_stop.setEnabled(False) # Initial state
        
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        
        layout.addStretch()
        
        # --- FERRAMENTAS Section ---
        tools_layout = QHBoxLayout()
        
        self.btn_settings = QPushButton("⚙ Config")
        self.btn_settings.setProperty("class", "toolBtn")
        self.btn_settings.clicked.connect(self.settings_clicked)
        
        self.btn_roi = QPushButton("📐 ROI")
        self.btn_roi.setProperty("class", "toolBtn")
        self.btn_roi.clicked.connect(self.roi_clicked)
        
        tools_layout.addWidget(self.btn_settings)
        tools_layout.addWidget(self.btn_roi)
        
        layout.addLayout(tools_layout)
        
        # Initial population
        self.refresh_models()

    def refresh_models(self):
        self.combo_model.clear()
        models = glob("models/*.pt")
        if not models:
            self.combo_model.addItem("Nenhum modelo (.pt)")
            self.combo_model.setEnabled(False)
        else:
            self.combo_model.setEnabled(True)
            for m in models:
                self.combo_model.addItem(os.path.basename(m), m)

    def set_camera_list(self, cameras):
        self.combo_cam.blockSignals(True)
        self.combo_cam.clear()
        for i, name in cameras:
            self.combo_cam.addItem(name, i)
        self.combo_cam.blockSignals(False)
        
        # Trigger manually for first item if exists
        if cameras:
            self._on_cam_changed(0)
            
    def _on_model_changed(self, text):
        if self.combo_model.currentData():
            self.model_selected.emit(self.combo_model.currentData())
            
    def _on_cam_changed(self, index):
        if index >= 0:
            cam_idx = self.combo_cam.itemData(index)
            self.camera_selected.emit(cam_idx)
            
    def _on_slider_changed(self, val):
        self.lbl_lim_val.setText(f"{val}%")
        self.conf_changed.emit(val / 100.0)

    def set_running_state(self, is_running: bool):
        self.combo_model.setEnabled(not is_running)
        self.combo_cam.setEnabled(not is_running)
        self.btn_refresh_cam.setEnabled(not is_running)
        self.btn_start.setEnabled(not is_running)
        self.btn_stop.setEnabled(is_running)
