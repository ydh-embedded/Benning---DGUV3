"""
QR Generator Port
Definiert die Schnittstelle für QR-Code Generierung
"""
from abc import ABC, abstractmethod


class QRGenerator(ABC):
    """Port für QR-Code Generierung"""
    
    @abstractmethod
    def generate(self, data: str) -> bytes:
        """Generiere QR-Code und gebe PNG-Bytes zurück"""
        pass
