import json
import base64
import urllib.parse
from typing import Dict, Any

from modules.vmess import VmessParser
from modules.vless import VlessParser
from modules.trojan import TrojanParser

class ConfigConverter:
    def __init__(self):
        self.parsers = {
            "vmess": VmessParser(),
            "vless": VlessParser(),
            "trojan": TrojanParser()
        }

    def convert(self, protocol: str, config: str, mode: str, domain: str) -> str:
        """
        Fungsi utama untuk memproses, memodifikasi, dan membangun ulang config VPN.
        """
        parser = self.parsers.get(protocol)
        if not parser:
            raise ValueError(f"Protokol {protocol} tidak didukung oleh sistem.")

        # 1. Parse raw string ke dictionary
        parsed_data = parser.parse(config)

        # 2. Regenerate config sesuai dengan mode dan domain
        if protocol == "vmess":
            return self._build_vmess(parsed_data, mode, domain)
        elif protocol == "vless":
            return self._build_vless(parsed_data, mode, domain)
        elif protocol == "trojan":
            return self._build_trojan(parsed_data, mode, domain)
            
    def _extract_true_vpn_domain(self, address: str, ws_host: str, sni: str) -> str:
        """
        Mendeteksi dan mengekstrak domain asli (membuang bug lama jika ada).
        """
        address = address or ""
        ws_host = ws_host or ""
        sni = sni or ""
        
        target_host = ws_host or sni
        if not target_host:
            return address
            
        if address:
            if target_host == address:
                return address
                
            # Kasus 1: add = bug, host = bug.server.com
            if target_host.startswith(f"{address}."):
                return target_host[len(address) + 1:]
                
            # Kasus 2: add = server.com, host = bug.server.com
            if target_host.endswith(f".{address}"):
                return address
                
        # Jika tidak cocok pola manapun (misal add = IP), kita kembalikan target_host
        return target_host

    def _build_vmess(self, data: Dict[str, Any], mode: str, domain: str) -> str:
        # Ekstrak original vpn domain (bersihkan jika ada bug lama)
        original_address = data.get("add", "")
        original_ws_host = data.get("host", "")
        original_sni = data.get("sni", "")
        
        vpn_domain = self._extract_true_vpn_domain(original_address, original_ws_host, original_sni)
        
        # Domain dari argumen di sini berperan sebagai 'Bug'
        data["add"] = domain
        
        if mode == "wildcard":
            wildcard_url = f"{domain}.{vpn_domain}" if vpn_domain else domain
            data["host"] = wildcard_url
            data["sni"] = wildcard_url
            data["port"] = 443
            data["tls"] = "tls"
        else: # mode == "ws"
            data["host"] = vpn_domain
            data["sni"] = vpn_domain
            
        # Tambahkan label (remarks) untuk menandai hasil convert
        original_ps = data.get("ps", "VPN")
        data["ps"] = f"{original_ps} [{mode.upper()}]"

        # Encode kembali ke string JSON tanpa spasi ekstra, lalu base64
        json_str = json.dumps(data, separators=(',', ':'))
        base64_enc = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        return f"vmess://{base64_enc}"

    def _build_vless(self, data: Dict[str, Any], mode: str, domain: str) -> str:
        uuid = data["uuid"]
        port = data["port"]
        params = data["params"]
        
        original_address = data.get("host", "")
        original_ws_host = params.get("host", "")
        original_sni = params.get("sni", "")
        
        vpn_domain = self._extract_true_vpn_domain(original_address, original_ws_host, original_sni)
        host = domain
        
        if mode == "wildcard":
            wildcard_url = f"{domain}.{vpn_domain}" if vpn_domain else domain
            params["host"] = wildcard_url
            params["sni"] = wildcard_url
            port = 443
            params["security"] = "tls"
        else:
            params["host"] = vpn_domain
            params["sni"] = vpn_domain
            
        original_ps = data.get("ps", "VPN")
        ps = f"{original_ps} [{mode.upper()}]"
        
        # Build kembali URI-nya
        query = urllib.parse.urlencode(params, safe='')
        fragment = urllib.parse.quote(ps)
        
        return f"vless://{uuid}@{host}:{port}?{query}#{fragment}"

    def _build_trojan(self, data: Dict[str, Any], mode: str, domain: str) -> str:
        password = data["password"]
        port = data["port"]
        params = data["params"]
        
        original_address = data.get("host", "")
        original_ws_host = params.get("host", "")
        original_sni = params.get("sni", "")
        
        vpn_domain = self._extract_true_vpn_domain(original_address, original_ws_host, original_sni)
        host = domain
        
        if mode == "wildcard":
            wildcard_url = f"{domain}.{vpn_domain}" if vpn_domain else domain
            params["host"] = wildcard_url
            params["sni"] = wildcard_url
            port = 443
            params["security"] = "tls"
        else:
            params["host"] = vpn_domain
            params["sni"] = vpn_domain
            
        original_ps = data.get("ps", "VPN")
        ps = f"{original_ps} [{mode.upper()}]"
        
        # Build kembali URI-nya
        query = urllib.parse.urlencode(params, safe='')
        fragment = urllib.parse.quote(ps)
        
        return f"trojan://{password}@{host}:{port}?{query}#{fragment}"

converter_service = ConfigConverter()
