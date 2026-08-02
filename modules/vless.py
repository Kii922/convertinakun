import urllib.parse
from typing import Dict, Any
from .parser import BaseParser

class VlessParser(BaseParser):
    def parse(self, config: str) -> Dict[str, Any]:
        """
        Memparsing URI vless://uuid@host:port?params#ps
        menjadi dictionary terstruktur.
        """
        if not config.startswith("vless://"):
            raise ValueError("Konfigurasi bukan format VLESS yang valid.")
            
        try:
            # Menggunakan urlparse bawaan Python
            parsed_url = urllib.parse.urlparse(config)
            
            uuid = parsed_url.username
            host = parsed_url.hostname
            port = parsed_url.port
            
            if not uuid or not host or not port:
                raise ValueError("Format VLESS tidak lengkap (kehilangan UUID, Host, atau Port).")
            
            # Parse query parameters (seperti type, security, path, dll)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # parse_qs mengembalikan list untuk valuenya, kita ratakan menjadi single value
            params = {k: v[0] for k, v in query_params.items()}
            
            # Parse remarks/nama config di fragment (#)
            ps = urllib.parse.unquote(parsed_url.fragment) if parsed_url.fragment else ""
            
            return {
                "uuid": uuid,
                "host": host,
                "port": port,
                "params": params,
                "ps": ps
            }
        except Exception as e:
            raise ValueError(f"Gagal mem-parsing VLESS: {str(e)}")
