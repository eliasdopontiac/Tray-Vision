from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication

class AlertManager(QObject):
    # Signals to UI
    visual_alert_triggered = Signal(bool) # True to start flash, False to stop
    
    def __init__(self):
        super().__init__()
        self._is_alerting = False
        
        # Timer for flashing visual alert
        self.flash_timer = QTimer()
        self.flash_timer.setInterval(500) # 500ms pulse
        self.flash_timer.timeout.connect(self._on_flash_toggle)
        self.flash_state = False
        
    def trigger_ng_alert(self):
        """Called when a NG is detected."""
        if not self._is_alerting:
            self._is_alerting = True
            
            # Sound alert (System beep for now, can be expanded to QSoundEffect)
            QApplication.beep()
            
            # Visual alert
            self.flash_state = True
            self.visual_alert_triggered.emit(True)
            self.flash_timer.start()
            
    def clear_alert(self):
        """Called when tray is reset or NG is resolved."""
        if self._is_alerting:
            self._is_alerting = False
            self.flash_timer.stop()
            self.visual_alert_triggered.emit(False)
            
    def _on_flash_toggle(self):
        self.flash_state = not self.flash_state
        self.visual_alert_triggered.emit(self.flash_state)
