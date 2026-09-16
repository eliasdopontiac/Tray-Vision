import os
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Slot, QTimer

from app.ui.header_bar import HeaderBar
from app.ui.panels.control_panel import ControlPanel
from app.ui.panels.camera_panel import CameraPanel
from app.ui.panels.tray_panel import TrayPanel
from app.ui.widgets.status_bar import StatusBar
from app.ui.dialogs.roi_dialog import ROIDialog
from app.ui.dialogs.settings_dialog import SettingsDialog

from app.core.camera_worker import CameraWorker
from app.core.detector_worker import DetectorWorker
from app.core.tray_model import TrayModel
from app.core.alert_manager import AlertManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tray Vision 2.0")
        self.setMinimumSize(1280, 720)
        self.setObjectName("root")
        
        # Core
        self.camera_worker = CameraWorker()
        self.detector_worker = DetectorWorker()
        self.tray_model = TrayModel(num_slots=12)
        self.alert_manager = AlertManager()
        
        # UI Setup
        self.setup_ui()
        self.connect_signals()
        
        # Scan cameras after the window is shown to avoid blocking startup
        QTimer.singleShot(200, self._scan_cameras)

    def setup_ui(self):
        # Main Widget & Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.header_bar = HeaderBar()
        main_layout.addWidget(self.header_bar)
        
        # Content Area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)
        
        # Panels
        self.control_panel = ControlPanel()
        self.camera_panel = CameraPanel()
        self.tray_panel = TrayPanel()
        
        # Shadows
        for panel in (self.control_panel, self.camera_panel, self.tray_panel):
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(16)
            shadow.setColor(Qt.black)
            shadow.setOffset(0, 4)
            # Alpha .08 roughly ~20/255
            color = shadow.color()
            color.setAlpha(20)
            shadow.setColor(color)
            panel.setGraphicsEffect(shadow)
            
        content_layout.addWidget(self.control_panel)
        content_layout.addWidget(self.camera_panel, 1) # flex
        content_layout.addWidget(self.tray_panel)
        
        main_layout.addWidget(content_widget, 1)
        
        # Status Bar
        self.status_bar_ui = StatusBar()
        main_layout.addWidget(self.status_bar_ui)

    def connect_signals(self):
        # Control Panel
        self.control_panel.start_clicked.connect(self.on_start)
        self.control_panel.stop_clicked.connect(self.on_stop)
        self.control_panel.model_selected.connect(self.on_model_selected)
        self.control_panel.camera_selected.connect(self.on_camera_selected)
        self.control_panel.conf_changed.connect(self.on_conf_changed)
        self.control_panel.btn_refresh_cam.clicked.connect(self._scan_cameras)
        self.control_panel.settings_clicked.connect(self.open_settings)
        self.control_panel.roi_clicked.connect(self.open_roi)
        
        # Camera Worker
        self.camera_worker.frame_ready.connect(self.on_frame_ready)
        self.camera_worker.connection_status.connect(self.status_bar_ui.set_camera_status)
        self.camera_worker.metrics_updated.connect(lambda lat: self.camera_panel.set_metrics(lat, 1000/lat if lat > 0 else 0))
        
        # Detector Worker
        self.detector_worker.detection_ready.connect(self.on_detection_ready)
        self.detector_worker.model_loaded.connect(self.status_bar_ui.set_model_status)
        
        # Tray Model
        self.tray_model.state_changed.connect(self.tray_panel.update_slots)
        self.tray_model.state_changed.connect(self.check_alerts)
        
        # Tray Panel
        self.tray_panel.reset_clicked.connect(self.reset_inspection)
        
        # Alert Manager
        self.alert_manager.visual_alert_triggered.connect(self.tray_panel.set_visual_alert)

    # Slots
    @Slot()
    def on_start(self):
        self.tray_model.reset()
        self.alert_manager.clear_alert()
        self.control_panel.set_running_state(True)
        self.header_bar.status_label.setText("🟢 Inspeção Ativa")
        
        self.detector_worker.start()
        self.camera_worker.start()

    @Slot()
    def on_stop(self):
        self.camera_worker.stop()
        self.detector_worker.stop()
        
        self.control_panel.set_running_state(False)
        self.header_bar.status_label.setText("🔴 Parado")

    @Slot(str)
    def on_model_selected(self, model_path: str):
        self.detector_worker.load_model(model_path)
        self.header_bar.set_active_model(os.path.basename(model_path))

    @Slot(int)
    def on_camera_selected(self, cam_idx: int):
        self.camera_worker.camera_id = cam_idx

    @Slot(float)
    def on_conf_changed(self, conf: float):
        self.detector_worker.conf_threshold = conf
        
    @Slot()
    def reset_inspection(self):
        self.tray_model.reset()
        self.alert_manager.clear_alert()

    @Slot()
    def _scan_cameras(self):
        """Runs camera scan off the critical path so startup/refresh don't block UI."""
        cameras = CameraWorker.get_available_cameras()
        self.control_panel.set_camera_list(cameras)

    @Slot(object)
    def on_frame_ready(self, frame):
        # Forward frame to detector for inference
        self.detector_worker.process_frame(frame)
        # Always render the raw frame — overlay is applied exclusively by on_detection_ready
        self.camera_panel.update_frame(frame, None)

    @Slot(object)
    def on_detection_ready(self, result):
        # Update camera overlay
        if self.camera_panel.current_frame is not None:
            self.camera_panel.update_frame(self.camera_panel.current_frame, result)
            
        # Update logic model
        self.tray_model.update_from_detection(result.mapped_slots)

    @Slot(list)
    def check_alerts(self, states):
        if self.tray_model.has_defect:
            self.alert_manager.trigger_ng_alert()
            
    @Slot()
    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
        
    @Slot()
    def open_roi(self):
        current_frame = self.camera_panel.current_frame  # may be None if camera not started
        dlg = ROIDialog(self, current_frame=current_frame)
        dlg.exec()
        
    def closeEvent(self, event):
        self.on_stop()
        event.accept()
