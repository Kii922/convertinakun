import html
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

from states.convert import ConvertVPN
from keyboards.inline import (
    get_category_keyboard, get_domain_keyboard,
    resolve_category_from_hash, resolve_domain_from_hash
)
from database import db

router = Router(name="callback_router")

# ─────────────────────────────────────────────────────
# STEP 1: Pilih Mode (Wildcard / WS)
# ─────────────────────────────────────────────────────
@router.callback_query(ConvertVPN.waiting_for_mode, F.data.startswith("mode_"))
async def process_mode_selection(callback: types.CallbackQuery, state: FSMContext):
    """
    Handler untuk memproses ketika user memilih Mode (Wildcard / WS).
    Setelah mode dipilih, tampilkan daftar KATEGORI domain.
    """
    await callback.answer()
    mode = callback.data.split("mode_")[1]
    await state.update_data(mode=mode)
    await state.set_state(ConvertVPN.waiting_for_category_selection)

    domains = db.get_all_domains()

    await callback.message.edit_text(
        f"Mode <b>{mode.upper()}</b> dipilih. ✅\n\n"
        "Pilih <b>kategori</b> domain yang ingin digunakan:",
        reply_markup=get_category_keyboard(domains)
    )

# ─────────────────────────────────────────────────────
# STEP 2: Pilih Kategori → Tampilkan Domain dalam Kategori
# ─────────────────────────────────────────────────────
@router.callback_query(ConvertVPN.waiting_for_category_selection, F.data.startswith("cat_"))
async def process_category_selection(callback: types.CallbackQuery, state: FSMContext):
    """
    Ketika user memilih kategori, tampilkan domain-domain dalam kategori tersebut.
    """
    await callback.answer()
    hash_val = callback.data.split("cat_", 1)[1]
    domains = db.get_all_domains()

    category = resolve_category_from_hash(domains, hash_val)
    if not category:
        await callback.message.edit_text("❌ Kategori tidak ditemukan.")
        return

    await state.update_data(selected_category=category)
    await state.set_state(ConvertVPN.waiting_for_domain_selection)

    is_admin = db.is_admin(callback.from_user.id)

    await callback.message.edit_text(
        f"📁 Kategori: <b>{category}</b>\n\n"
        "Pilih domain yang akan digunakan untuk konversi:",
        reply_markup=get_domain_keyboard(domains, category=category, is_admin=is_admin)
    )

# ─────────────────────────────────────────────────────
# BACK: Kembali ke daftar kategori
# ─────────────────────────────────────────────────────
@router.callback_query(ConvertVPN.waiting_for_domain_selection, F.data == "back_to_category")
async def process_back_to_category(callback: types.CallbackQuery, state: FSMContext):
    """
    Tombol kembali dari daftar domain ke daftar kategori.
    """
    await callback.answer()
    await state.set_state(ConvertVPN.waiting_for_category_selection)
    domains = db.get_all_domains()

    user_data = await state.get_data()
    mode = user_data.get("mode", "")

    await callback.message.edit_text(
        f"Mode <b>{mode.upper()}</b> dipilih. ✅\n\n"
        "Pilih <b>kategori</b> domain yang ingin digunakan:",
        reply_markup=get_category_keyboard(domains)
    )

# ─────────────────────────────────────────────────────
# Custom Domain (bisa dari state kategori ATAU domain)
# ─────────────────────────────────────────────────────
@router.callback_query(ConvertVPN.waiting_for_category_selection, F.data == "domain_custom")
@router.callback_query(ConvertVPN.waiting_for_domain_selection, F.data == "domain_custom")
async def process_custom_domain_button(callback: types.CallbackQuery, state: FSMContext):
    """
    Ketika user memilih Custom Domain, arahkan ke state input manual.
    """
    await callback.answer()
    await state.set_state(ConvertVPN.waiting_for_custom_domain)
    await callback.message.edit_text(
        "Silakan ketik domain custom Anda:\n"
        "Contoh: <code>bug.example.com</code> atau <code>104.18.2.1</code>"
    )

# ─────────────────────────────────────────────────────
# STEP 3: Pilih Domain → Lakukan Konversi
# ─────────────────────────────────────────────────────
@router.callback_query(ConvertVPN.waiting_for_domain_selection, F.data.startswith("dom_"))
async def process_domain_selection(callback: types.CallbackQuery, state: FSMContext):
    """
    Ketika user memilih domain dari list, langsung lakukan konversi.
    """
    await callback.answer()

    hash_val = callback.data.split("dom_", 1)[1]
    domains = db.get_all_domains()
    domain = resolve_domain_from_hash(domains, hash_val)

    if not domain:
        await callback.message.edit_text("❌ Domain tidak ditemukan di database.")
        await state.clear()
        return

    await state.update_data(selected_domain=domain)

    user_data = await state.get_data()
    protocol = user_data.get("protocol")
    original_config = user_data.get("original_config")
    mode = user_data.get("mode")

    from services.converter import converter_service

    try:
        result = converter_service.convert(protocol, original_config, mode, domain)

        # Escape karakter HTML spesial (& < >) agar tidak merusak parsing Telegram
        safe_result = html.escape(result)

        text_result = (
            f"✅ <b>Konversi Berhasil!</b>\n\n"
            f"<b>Protokol:</b> {protocol.upper()}\n"
            f"<b>Mode:</b> {mode.upper()}\n"
            f"<b>Domain:</b> {domain}\n\n"
            f"<code>{safe_result}</code>"
        )
        await callback.message.edit_text(text_result)

        # Catat statistik
        try:
            with db._get_connection() as conn:
                conn.execute(
                    "INSERT INTO statistics (protocol, count) VALUES (?, 1) "
                    "ON CONFLICT(date, protocol) DO UPDATE SET count = count + 1",
                    (protocol,)
                )
                conn.commit()
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Konversi gagal untuk {protocol}: {e}")
        try:
            await callback.message.edit_text(f"❌ <b>Konversi Gagal:</b>\n{html.escape(str(e))}")
        except Exception:
            await callback.message.edit_text("❌ Terjadi kesalahan saat konversi.")

    finally:
        # [SECURITY] Wajib menghapus FSM setelah selesai
        await state.clear()

# ─────────────────────────────────────────────────────
# ADMIN: Tambah Bug (bisa dari level domain)
# ─────────────────────────────────────────────────────
@router.callback_query(ConvertVPN.waiting_for_domain_selection, F.data == "admin_add_bug")
async def process_admin_add_bug(callback: types.CallbackQuery, state: FSMContext):
    if not db.is_admin(callback.from_user.id):
        await callback.answer("Akses ditolak.", show_alert=True)
        return

    await callback.answer()
    await state.set_state(ConvertVPN.waiting_for_new_bug)
    await callback.message.edit_text(
        "Silakan ketik Bug baru yang ingin ditambahkan.\n"
        "Format: <code>domain.com Kategori</code>\n"
        "Contoh: <code>vclass.telkomsel.com Telkomsel</code>\n\n"
        "Jika tanpa kategori, otomatis masuk ke <b>Umum</b>."
    )
