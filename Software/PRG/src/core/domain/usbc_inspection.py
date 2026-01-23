"""
USB-C Inspection Domain Model
Spezialisierte Inspektion für USB-C Kabel
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from .inspection import Inspection


@dataclass
class ResistanceTest:
    """Widerstandsmessung für USB-C Pins"""
    pin_name: str
    resistance_value: float
    expected_min: float
    expected_max: float
    
    def is_passed(self) -> bool:
        """Prüfe, ob Messung im erwarteten Bereich liegt"""
        return self.expected_min <= self.resistance_value <= self.expected_max


@dataclass
class ProtocolTest:
    """Protokoll-Test für USB-C"""
    protocol_name: str
    supported: bool
    speed_mbps: Optional[int] = None
    power_delivery: bool = False
    max_power_w: Optional[int] = None


@dataclass
class USBCInspection(Inspection):
    """USB-C spezifische Inspektion"""
    device_functional: bool = False
    battery_checked: bool = False
    cable_visual_ok: bool = False
    cable_id: str = ""
    cable_connected: bool = False
    basic_functions_ok: bool = False
    resistance_tests: List[ResistanceTest] = field(default_factory=list)
    protocol_tests: List[ProtocolTest] = field(default_factory=list)
    pinout_photo_path: Optional[str] = None
    emarker_data: Optional[Dict] = None
    
    def all_tests_passed(self) -> bool:
        """Prüfe, ob alle Tests bestanden"""
        basic_checks = (
            self.device_functional and
            self.battery_checked and
            self.cable_visual_ok and
            self.cable_connected and
            self.basic_functions_ok
        )
        
        resistance_ok = all(
            test.is_passed() for test in self.resistance_tests
        ) if self.resistance_tests else True
        
        return basic_checks and resistance_ok
    
    def get_failed_tests(self) -> List[str]:
        """Gebe Liste fehlgeschlagener Tests zurück"""
        failed = []
        if not self.device_functional:
            failed.append("Gerät funktioniert nicht")
        if not self.battery_checked:
            failed.append("Batterie nicht geprüft")
        if not self.cable_visual_ok:
            failed.append("Kabel visuell nicht OK")
        if not self.cable_connected:
            failed.append("Kabel nicht verbunden")
        if not self.basic_functions_ok:
            failed.append("Grundfunktionen nicht OK")
        
        failed.extend([
            f"{test.pin_name} außerhalb des Bereichs"
            for test in self.resistance_tests
            if not test.is_passed()
        ])
        
        return failed
