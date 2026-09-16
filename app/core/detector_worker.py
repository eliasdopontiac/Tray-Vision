import time
import queue
import numpy as np
from typing import Dict, Any, List, Optional
from PySide6.QtCore import QThread, Signal
from ultralytics import YOLO

class DetectionResult:
    def __init__(self, boxes: List[tuple], classes: List[str], confidences: List[float], mapped_slots: List[dict]):
        self.boxes = boxes # (x1, y1, x2, y2)
        self.classes = classes # "OK", "NG", "NA"
        self.confidences = confidences
        self.mapped_slots = mapped_slots

class DetectorWorker(QThread):
    detection_ready = Signal(object) # DetectionResult
    model_loaded = Signal(bool)
    metrics_updated = Signal(float) # Inference latency in ms
    error_occurred = Signal(str)
    
    def __init__(self, model_path: Optional[str] = None):
        super().__init__()
        self.model_path = model_path
        self.model = None
        self.conf_threshold = 0.87
        
        self.frame_queue = queue.Queue(maxsize=1)
        self._is_running = False
        
        # Pending model load — set from UI thread, consumed inside run() loop
        self._pending_model_path: Optional[str] = None
        
        # Grid dimensions — determined dynamically by the AI model detections
        self.grid_rows = 3
        self.grid_cols = 4
        
    def load_model(self, path: str):
        """Schedule a model load from the UI thread. 
        Actual loading happens inside run() to avoid blocking the UI."""
        self._pending_model_path = path

    def _do_load_model(self, path: str):
        """Internal: called inside the worker thread."""
        try:
            self.model = YOLO(path)
            self.model_path = path
            self.model_loaded.emit(True)
        except Exception as e:
            self.error_occurred.emit(f"Failed to load model: {str(e)}")
            self.model_loaded.emit(False)
            self.model = None

    def process_frame(self, frame: np.ndarray):
        # Add frame to queue, drop oldest if full to prevent lag
        try:
            if self.frame_queue.full():
                self.frame_queue.get_nowait()
            self.frame_queue.put_nowait(frame)
        except queue.Full:
            pass

    def run(self):
        self._is_running = True
        
        # Load initial model if provided at construction time
        if self.model_path and self.model is None:
            self._do_load_model(self.model_path)
            
        while self._is_running:
            # Check for pending model load request (set from UI thread)
            if self._pending_model_path:
                self._do_load_model(self._pending_model_path)
                self._pending_model_path = None

            try:
                frame = self.frame_queue.get(timeout=0.1)
                
                if self.model is None:
                    continue
                    
                start_time = time.perf_counter()
                
                # Inference
                results = self.model.predict(frame, conf=self.conf_threshold, verbose=False)
                
                boxes = []
                classes = []
                confidences = []
                mapped_slots = []
                
                if len(results) > 0:
                    r = results[0]
                    img_h, img_w = frame.shape[:2]
                    
                    # Calculate grid cell dimensions
                    cell_w = img_w / self.grid_cols
                    cell_h = img_h / self.grid_rows
                    
                    class_names = r.names
                    
                    for box in r.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls_idx = int(box.cls[0].cpu().numpy())
                        cls_name = class_names.get(cls_idx, "UNKNOWN")
                        
                        # Map to class we expect ("OK", "NG", "NA")
                        if cls_name not in ["OK", "NG", "NA"]:
                            # Fallback logic if model outputs different classes
                            if "OK" in cls_name.upper(): cls_name = "OK"
                            elif "NG" in cls_name.upper(): cls_name = "NG"
                            else: cls_name = "NA"
                        
                        boxes.append((int(x1), int(y1), int(x2), int(y2)))
                        classes.append(cls_name)
                        confidences.append(conf)
                        
                        # Calculate center to map to slot
                        cx = (x1 + x2) / 2
                        cy = (y1 + y2) / 2
                        
                        col = int(cx / cell_w)
                        row = int(cy / cell_h)
                        
                        # Constrain
                        col = max(0, min(col, self.grid_cols - 1))
                        row = max(0, min(row, self.grid_rows - 1))
                        
                        slot_index = (row * self.grid_cols) + col + 1
                        mapped_slots.append({
                            "slot_index": slot_index,
                            "status": cls_name,
                            "confidence": conf
                        })
                
                latency = (time.perf_counter() - start_time) * 1000
                self.metrics_updated.emit(latency)
                
                result = DetectionResult(boxes, classes, confidences, mapped_slots)
                self.detection_ready.emit(result)
                
            except queue.Empty:
                pass
            except Exception as e:
                self.error_occurred.emit(f"Inference error: {str(e)}")
                
    def stop(self):
        self._is_running = False
        self.wait()
