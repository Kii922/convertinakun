import urllib.parse
from typing import Dict, Any
from .parser import BaseParser

class TrojanParser(BaseParser):
    def parse(self, config: str) -> Dict[str, Any]:
        """
        Memparsing URI trojan://password@host:port?params#ps
        menjadi dictionary terstruktur.
        """
        if not config.startswith("trojan://"):
            raise ValueError("Konfigurasi bukan format Trojan yang valid.")
            
        try:
            # Format Trojan sangat mirip dengan VLESS, bedanya pada username/password
            parsed_url = urllib.parse.urlparse(config)
            
            password = parsed_url.username
            host = parsed_url.hostname
            port = parsed_url.port
            
            if not password or not host or not port:
                raise ValueError("Format Trojan tidak lengkap (kehilangan Password, Host, atau Port).")
            
            query_params = urllib.parse.parse_qs(parsed_url.query)
            params = {k: v[0] for k, v in query_params.items()}
            
            ps = urllib.parse.unquote(parsed_url.fragment) if parsed_url.fragment else ""
            
            return {
                "password": password,
                "host": host,
                "port": port,
                "params": params,
                "ps": ps
            }
        except Exception as e:
            raise ValueError(f"Gagal mem-parsing Trojan: {str(e)}")
