import logging
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from states.convert import ConvertVPN
from database import db

logger = logging.getLogger(__name__)
router = Router(name="start_router")

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    """
    Handler untuk merespons command /start.
    Memastikan state dibersihkan, mencatat user (statistik),
    dan meminta user mengirimkan konfigurasi VPN-nya.
    """
    # 1. Pastikan seluruh state (dan memori sementara) dihapus dari sesi sebelumnya
    await state.clear()

    # 2. Mencatat/update data pengunjung di tabel `users`.
    # Hanya untuk mengetahui siapa saja yang menggunakan bot, tanpa detail akun.
    try:
        with db._get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", 
                (message.from_user.id, message.from_user.username)
            )
            conn.commit()
    except Exception as e:
        logger.warning(f"Gagal mencatat user {message.from_user.id}: {e}")

    # 3. Masuk ke FSM untuk menunggu input config VPN
    await state.set_state(ConvertVPN.waiting_for_vpn_account)
    
    # 4. Kirim pesan sapaan
    welcome_text = (
        "Selamat datang.\n\n"
        "Silakan kirim akun VPN:\n"
        "• vmess://...\n"
        "• vless://...\n"
        "• trojan://..."
    )
    
    await message.answer(welcome_text)
