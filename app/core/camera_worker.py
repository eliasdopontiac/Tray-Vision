import cv2
import time
import numpy as np
from typing import List, Tuple
from PySide6.QtCore import QThread, Signal

class CameraWorker(QThread):
    # Signals
    frame_ready = Signal(np.ndarray)
    error_occurred = Signal(str)
    connection_status = Signal(bool)
    metrics_updated = Signal(float)  # Latency in ms
    
    def __init__(self, camera_id: int | str = 0, target_fps: int = 30):
        super().__init__()
        self.camera_id = camera_id
        self.target_fps = target_fps
        self._is_running = False
        self._frame_time = 1.0 / target_fps
        
    @staticmethod
    def get_available_cameras(max_tested: int = 5) -> List[Tuple[int, str]]:
        available = []
        for i in range(max_tested):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                available.append((i, f"USB Camera {i} ({w}x{h})"))
                cap.release()
        return available

    def run(self):
        self._is_running = True
        
        while self._is_running:
            cap = cv2.VideoCapture(self.camera_id)
            if not cap.isOpened():
                self.error_occurred.emit(f"Failed to open camera: {self.camera_id}")
                self.connection_status.emit(False)
                time.sleep(3)  # Wait before reconnecting
                continue
                
            self.connection_status.emit(True)
            
            while self._is_running:
                start_time = time.perf_counter()
                
                ret, frame = cap.read()
                if not ret:
                    self.error_occurred.emit("Lost camera connection")
                    self.connection_status.emit(False)
                    break
                    
                # Emit the raw BGR frame
                self.frame_ready.emit(frame)
                
                # FPS control
                elapsed = time.perf_counter() - start_time
                self.metrics_updated.emit(elapsed * 1000)
                
                sleep_time = self._frame_time - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            cap.release()
            
    def stop(self):
        self._is_running = False
        self.wait()
