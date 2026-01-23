"""
File Storage Port
Definiert die Schnittstelle für Dateispeicherung
"""
from abc import ABC, abstractmethod
from typing import Optional


class FileStorage(ABC):
    """Port für Dateispeicherung"""
    
    @abstractmethod
    def upload(self, file_content: bytes, filename: str, subfolder: str = "") -> str:
        """Speichere Datei und gebe Pfad zurück"""
        pass
    
    @abstractmethod
    def delete(self, filepath: str) -> None:
        """Lösche Datei"""
        pass
    
    @abstractmethod
    def exists(self, filepath: str) -> bool:
        """Prüfe, ob Datei existiert"""
        pass
    
    @abstractmethod
    def get_url(self, filepath: str) -> str:
        """Gebe öffentliche URL für Datei zurück"""
        pass
