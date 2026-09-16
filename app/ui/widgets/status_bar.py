import datetime
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QWidget
from PySide6.QtCore import Qt, QTimer

class StatusBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("statusBar")
        self.setFixedHeight(36)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        
        # Left side - Indicators
        self.lbl_cam_status = QLabel("🟢 Câmera OK")
        self.lbl_cam_status.setProperty("class", "statusItem")
        
        self.lbl_mod_status = QLabel("🟢 Modelo OK")
        self.lbl_mod_status.setProperty("class", "statusItem")
        
        self.lbl_gpu_status = QLabel("🟢 GPU OK")
        self.lbl_gpu_status.setProperty("class", "statusItem")
        
        layout.addWidget(self.lbl_cam_status)
        layout.addSpacing(12)
        layout.addWidget(self.lbl_mod_status)
        layout.addSpacing(12)
        layout.addWidget(self.lbl_gpu_status)
        layout.addStretch()
        
        # Center - Timestamp
        self.lbl_timestamp = QLabel("")
        self.lbl_timestamp.setProperty("class", "statusItem")
        layout.addWidget(self.lbl_timestamp)
        layout.addStretch()
        
        # Right - Metrics
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(8)
        
        lbl_cpu = QLabel("CPU")
        lbl_cpu.setProperty("class", "statusItem")
        self.val_cpu = QLabel("0%")
        self.val_cpu.setProperty("class", "statusItem")
        self.bar_cpu = QProgressBar()
        self.bar_cpu.setFixedSize(60, 4)
        
        lbl_gpu = QLabel("GPU")
        lbl_gpu.setProperty("class", "statusItem")
        self.val_gpu = QLabel("0%")
        self.val_gpu.setProperty("class", "statusItem")
        self.bar_gpu = QProgressBar()
        self.bar_gpu.setFixedSize(60, 4)
        
        metrics_layout.addWidget(lbl_cpu)
        metrics_layout.addWidget(self.val_cpu)
        metrics_layout.addWidget(self.bar_cpu)
        metrics_layout.addSpacing(16)
        metrics_layout.addWidget(lbl_gpu)
        metrics_layout.addWidget(self.val_gpu)
        metrics_layout.addWidget(self.bar_gpu)
        
        layout.addLayout(metrics_layout)
        
        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timestamp)
        self.timer.start(1000)
        self.update_timestamp()
        
    def update_timestamp(self):
        now = datetime.datetime.now()
        self.lbl_timestamp.setText(now.strftime("%d/%m/%Y %H:%M:%S"))
        
    def set_camera_status(self, is_ok: bool):
        self.lbl_cam_status.setText("🟢 Câmera OK" if is_ok else "🔴 Câmera Erro")
        
    def set_model_status(self, is_ok: bool):
        self.lbl_mod_status.setText("🟢 Modelo OK" if is_ok else "🔴 Modelo Erro")
        
    def update_metrics(self, cpu: int, gpu: int):
        self.val_cpu.setText(f"{cpu}%")
        self.bar_cpu.setValue(cpu)
        
        self.val_gpu.setText(f"{gpu}%")
        self.bar_gpu.setValue(gpu)
