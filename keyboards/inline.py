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

def get_category_keyboard(domains: List[dict], selected_mode: str = "all", is_admin: bool = False) -> InlineKeyboardMarkup:
    """
    Keyboard Tingkat 1: Menampilkan daftar KATEGORI sebagai tombol.
    Hanya menampilkan kategori yang memiliki domain sesuai dengan selected_mode (atau all).
    """
    builder = InlineKeyboardBuilder()

    # Kumpulkan semua kategori unik (urut)
    seen = set()
    categories = []
    for d in domains:
        d_mode = d.get("mode", "all")
        if d_mode != "all" and selected_mode != "all" and d_mode != selected_mode:
            continue # Skip domains that do not match the selected mode

        cat = d.get("category", "Umum")
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

def get_domain_keyboard(domains: List[dict], category: str, selected_mode: str = "all", is_admin: bool = False, delete_mode: bool = False) -> InlineKeyboardMarkup:
    """
    Keyboard Tingkat 2: Menampilkan daftar DOMAIN dalam satu kategori tertentu.
    Jika delete_mode=True, tombol-tombol akan berfungsi untuk menghapus domain.
    """
    builder = InlineKeyboardBuilder()

    # Filter domain berdasarkan kategori dan mode
    filtered = []
    for d in domains:
        d_cat = d.get("category", "Umum")
        d_mode = d.get("mode", "all")
        
        if d_cat == category and (d_mode == "all" or selected_mode == "all" or d_mode == selected_mode):
            filtered.append(d)

    for d in filtered:
        dom = d["domain"]
        title = d.get("title", "")
        
        # Format text tombol
        btn_text = f"{dom} ({title})" if title else dom
        if delete_mode:
            btn_text = f"❌ Hapus {dom}"
            
        callback_prefix = "deldom_" if delete_mode else "dom_"
        builder.button(text=btn_text, callback_data=f"{callback_prefix}{_short_hash(dom)}")

    # Tombol kembali ke daftar kategori
    if not delete_mode:
        builder.button(text="⬅️ Kembali ke Kategori", callback_data="back_to_category")

        if is_admin:
            builder.button(text="➕ Tambah Bug", callback_data="admin_add_bug")
            if filtered:
                builder.button(text="🗑️ Hapus Bug", callback_data=f"admin_del_bug_mode_{_short_hash(category)}")
    else:
        builder.button(text="Batal Hapus", callback_data=f"cat_{_short_hash(category)}")

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
