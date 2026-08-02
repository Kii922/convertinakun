from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseParser(ABC):
    """
    Interface dasar untuk semua parser protokol.
    Setiap parser harus mengimplementasikan fungsi `parse` yang menerima
    string konfigurasi raw dan mengembalikan dictionary terstruktur.
    """
    @abstractmethod
    def parse(self, config: str) -> Dict[str, Any]:
        pass
