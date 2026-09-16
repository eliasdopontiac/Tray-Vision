from dataclasses import dataclass
from typing import List, Optional
from PySide6.QtCore import QObject, Signal

@dataclass
class SlotState:
    index: int  # 1 to 12
    status: str = "EMPTY"  # "OK", "NG", "NA", "EMPTY"
    confidence: float = 0.0

class TrayModel(QObject):
    state_changed = Signal(list)  # list of SlotState
    
    def __init__(self, num_slots: int = 12):
        super().__init__()
        self.num_slots = num_slots
        self.slots: List[SlotState] = [
            SlotState(index=i+1) for i in range(num_slots)
        ]
        
    def reset(self):
        for slot in self.slots:
            slot.status = "EMPTY"
            slot.confidence = 0.0
        self.state_changed.emit(self.slots)
        
    def update_from_detection(self, detections: List[dict]):
        # detections is expected to be a list of dicts: 
        # {"slot_index": int, "status": str, "confidence": float}
        changed = False
        
        # Reset all first for simple full-frame evaluation, 
        # or we could only update detected ones. 
        # Let's reset the ones not detected to EMPTY or keep state?
        # Typically YOLO runs every frame, so we reset the state based on current frame.
        new_states = {d["slot_index"]: d for d in detections}
        
        for i in range(self.num_slots):
            idx = i + 1
            if idx in new_states:
                new_status = new_states[idx]["status"]
                new_conf = new_states[idx]["confidence"]
                if self.slots[i].status != new_status or abs(self.slots[i].confidence - new_conf) > 0.01:
                    self.slots[i].status = new_status
                    self.slots[i].confidence = new_conf
                    changed = True
            else:
                if self.slots[i].status != "EMPTY":
                    self.slots[i].status = "EMPTY"
                    self.slots[i].confidence = 0.0
                    changed = True
                    
        if changed:
            self.state_changed.emit(self.slots)

    @property
    def ok_count(self) -> int:
        return sum(1 for s in self.slots if s.status == "OK")
        
    @property
    def ng_count(self) -> int:
        return sum(1 for s in self.slots if s.status == "NG")
        
    @property
    def na_count(self) -> int:
        return sum(1 for s in self.slots if s.status == "NA")
        
    @property
    def has_defect(self) -> bool:
        return self.ng_count > 0
