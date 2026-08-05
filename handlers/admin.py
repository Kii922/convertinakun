from aiogram import Router, types
from aiogram.filters import Command
from config import config
from database import db

router = Router(name="admin_router")

def check_admin(message: types.Message) -> bool:
    """Filter sederhana untuk memeriksa hak akses Admin/Owner."""
    return db.is_admin(message.from_user.id)

@router.message(Command("listdomain"))
async def cmd_listdomain(message: types.Message):
    """Menampilkan semua domain yang tersimpan di database."""
    if not check_admin(message):
        return
        
    domains = db.get_all_domains()
    if not domains:
        await message.answer("ℹ️ Daftar domain saat ini kosong.")
        return
        
    text = "🌐 <b>Daftar Domain Tersedia:</b>\n\n"
    
    # Kelompokkan berdasarkan kategori
    grouped = {}
    for d in domains:
        cat = d['category']
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(d)
        
    for cat, doms in grouped.items():
        text += f"📁 <b>{cat}</b>\n"
        for idx, d_info in enumerate(doms, 1):
            title = d_info.get('title', '')
            mode = d_info.get('mode', 'all')
            title_str = f" ({title})" if title else ""
            mode_str = f"[{mode}] " if mode != 'all' else ""
            text += f"  {idx}. {mode_str}<code>{d_info['domain']}</code>{title_str}\n"
        text += "\n"
        
    await message.answer(text)

@router.message(Command("adddomain"))
async def cmd_adddomain(message: types.Message):
    """Menambahkan domain baru (Hanya Admin)."""
    if not check_admin(message):
        return
        
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ <b>Format Salah</b>\n\nGunakan format:\n<code>/adddomain [domain] [mode (opsional)] [kategori (opsional)] [judul (opsional)]</code>\n\nContoh:\n<code>/adddomain 104.17.3.81 ws Edukasi Edukasi_Zoom</code>")
        return
        
    domain = args[1].lower()
    mode = args[2].lower() if len(args) > 2 else "all"
    category = args[3].strip().title() if len(args) > 3 else "Umum"
    title = " ".join(args[4:]).strip() if len(args) > 4 else ""
    
    if db.add_domain(domain, category, mode, title):
        title_str = f" ({title})" if title else ""
        await message.answer(f"✅ Domain <b>{domain}</b>{title_str} (Mode: {mode}, Kategori: {category}) berhasil ditambahkan ke database.")
    else:
        await message.answer(f"❌ Domain <b>{domain}</b> gagal ditambahkan. (Mungkin sudah terdaftar).")

@router.message(Command("deldomain"))
async def cmd_deldomain(message: types.Message):
    """Menghapus domain dari database (Hanya Admin)."""
    if not check_admin(message):
        return
        
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ <b>Format Salah</b>\n\nGunakan format:\n<code>/deldomain [nama.domain.com]</code>")
        return
        
    domain = args[1].strip().lower()
    
    if db.delete_domain(domain):
        await message.answer(f"✅ Domain <b>{domain}</b> berhasil dihapus dari database.")
    else:
        await message.answer(f"❌ Domain <b>{domain}</b> tidak ditemukan di database.")
