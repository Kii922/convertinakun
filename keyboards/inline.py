import hashlib
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

def _short_hash(text: str, length: int = 8) -> str:
    """Buat hash pendek dari teks untuk callback data (mengatasi limit 64 byte Telegram)."""
    return hashlib.md5(text.encode()).hexdigest()[:length]

def get_mode_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard Inline untuk memilih mode konversi: Wildcard atau WS.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Wildcard", callback_data="mode_wildcard")
    builder.button(text="⚡ WS", callback_data="mode_ws")
    builder.adjust(2)
    return builder.as_markup()

def get_category_keyboard(domains: List[dict], is_admin: bool = False) -> InlineKeyboardMarkup:
    """
    Keyboard Tingkat 1: Menampilkan daftar KATEGORI sebagai tombol.
    Setiap tombol mewakili satu kelompok domain (mis: XL, Telkomsel, dll).
    """
    builder = InlineKeyboardBuilder()

    # Kumpulkan semua kategori unik (urut)
    seen = set()
    categories = []
    for d in domains:
        cat = d["category"] if isinstance(d, dict) else "Umum"
        if cat not in seen:
            seen.add(cat)
            categories.append(cat)

    # Emoji per kategori
    emoji_map = {
        "Telkomsel": "🔴",
        "XL": "🔵",
        "Axis": "🔵",
        "Indosat": "🟡",
        "Smartfren": "🟢",
        "Tri": "🟠",
        "Umum": "⚪",
    }

    for cat in categories:
        emoji = emoji_map.get(cat, "📁")
        # Gunakan hash untuk menghindari limit 64 byte callback data
        builder.button(text=f"{emoji} {cat}", callback_data=f"cat_{_short_hash(cat)}")

    # Tombol Custom Domain
    builder.button(text="✏️ Custom Domain", callback_data="domain_custom")

    builder.adjust(2)
    return builder.as_markup()

def get_domain_keyboard(domains: List[dict], category: str, is_admin: bool = False) -> InlineKeyboardMarkup:
    """
    Keyboard Tingkat 2: Menampilkan daftar DOMAIN dalam satu kategori tertentu.
    """
    builder = InlineKeyboardBuilder()

    # Filter domain berdasarkan kategori yang dipilih
    filtered = [
        d["domain"] if isinstance(d, dict) else d
        for d in domains
        if (d["category"] if isinstance(d, dict) else "Umum") == category
    ]

    for dom in filtered:
        # Gunakan hash untuk menghindari limit 64 byte callback data
        builder.button(text=dom, callback_data=f"dom_{_short_hash(dom)}")

    # Tombol kembali ke daftar kategori
    builder.button(text="⬅️ Kembali ke Kategori", callback_data="back_to_category")

    if is_admin:
        builder.button(text="➕ Tambah Bug (Admin)", callback_data="admin_add_bug")

    builder.adjust(1)
    return builder.as_markup()

def resolve_category_from_hash(domains: List[dict], hash_val: str) -> str:
    """Mencari nama kategori berdasarkan hash callback."""
    seen = set()
    for d in domains:
        cat = d["category"] if isinstance(d, dict) else "Umum"
        if cat not in seen:
            seen.add(cat)
            if _short_hash(cat) == hash_val:
                return cat
    return None

def resolve_domain_from_hash(domains: List[dict], hash_val: str) -> str:
    """Mencari nama domain berdasarkan hash callback."""
    for d in domains:
        dom = d["domain"] if isinstance(d, dict) else d
        if _short_hash(dom) == hash_val:
            return dom
    return None
