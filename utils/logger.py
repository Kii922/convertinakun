import logging
import re
import sys
from config import config

class SensitiveDataFilter(logging.Filter):
    """
    Filter custom untuk mencegah bocornya link VPN (vmess/vless/trojan)
    atau konfigurasi sensitif lainnya ke dalam log.
    """
    def filter(self, record):
        if isinstance(record.msg, str):
            # Masking link yang mengandung vmess://, vless://, trojan://
            record.msg = re.sub(
                r'(vmess|vless|trojan)://[^\s]+',
                r'\1://[REDACTED]',
                record.msg,
                flags=re.IGNORECASE
            )
        return True

def setup_logger():
    """Inisialisasi sistem logging aplikasi."""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))

    # Hapus handler bawaan agar tidak log ganda
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    
    logger.addHandler(console_handler)
    return logger
