"""
Inspection Domain Model
Repräsentiert eine Geräteinspektionen
"""
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Optional


@dataclass
class Inspection:
    """Inspection Entity"""
    id: Optional[int]
    device_id: str
    inspection_date: date
    inspector_name: str
    result: str  # 'passed', 'failed', 'pending'
    notes: str
    next_inspection_date: date
    created_at: datetime
    
    def is_passed(self) -> bool:
        """Prüfe, ob Inspektion bestanden"""
        return self.result == 'passed'
    
    def is_failed(self) -> bool:
        """Prüfe, ob Inspektion nicht bestanden"""
        return self.result == 'failed'
    
    def schedule_next_inspection(self, interval_days: int = 365) -> date:
        """Plane nächste Inspektion"""
        return self.inspection_date + timedelta(days=interval_days)
