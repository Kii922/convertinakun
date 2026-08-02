import json
import base64
from typing import Dict, Any
from .parser import BaseParser

class VmessParser(BaseParser):
    def parse(self, config: str) -> Dict[str, Any]:
        """
        Memparsing URI vmess:// menjadi dictionary JSON.
        """
        if not config.startswith("vmess://"):
            raise ValueError("Konfigurasi bukan format VMess yang valid.")
            
        base64_str = config.replace("vmess://", "").strip()
        
        # Tambahkan padding Base64 jika kurang (mencegah binascii.Error: Incorrect padding)
        padding = len(base64_str) % 4
        if padding:
            base64_str += '=' * (4 - padding)
            
        try:
            # Decode dari Base64
            decoded_bytes = base64.b64decode(base64_str)
            decoded_str = decoded_bytes.decode('utf-8')
            
            # Parse string hasil decode menjadi dictionary JSON
            data = json.loads(decoded_str)
            return data
        except json.JSONDecodeError:
            raise ValueError("Gagal mem-parsing VMess: Hasil decode Base64 bukan JSON yang valid.")
        except Exception as e:
            raise ValueError(f"Gagal mem-parsing VMess: {str(e)}")
