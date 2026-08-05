import html
import re
import time
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from states.convert import ConvertVPN
from keyboards.inline import get_mode_keyboard
from database import db

router = Router(name="message_router")

# ─────────────────────────────────────────────────────
# Menerima Config VPN
# ─────────────────────────────────────────────────────

async def _handle_vpn_input(message: types.Message, state: FSMContext):
    """
    Logic utama: deteksi protokol, simpan ke FSM, lanjut ke pemilihan mode.
    Dipanggil dari handler yang dalam state maupun yang tanpa state.
    """
    start_time = time.time()
    text = message.text.strip()

    # Deteksi protokol berdasarkan skema URI
    protocol = None
    if text.startswith("vmess://"):
        protocol = "vmess"
    elif text.startswith("vless://"):
        protocol = "vless"
    elif text.startswith("trojan://"):
        protocol = "trojan"

    if not protocol:
        await message.answer("❌ Format tidak dikenal atau tidak didukung.\nHarap kirimkan akun valid dengan awalan `vmess://`, `vless://`, atau `trojan://`.")
        return

    # [SECURITY] Reset state lama lalu simpan data baru ke FSM (hanya di RAM).
    await state.clear()
    await state.update_data(
        protocol=protocol,
        original_config=text
    )

    # Lanjut ke tahap berikutnya: Pemilihan Mode
    await state.set_state(ConvertVPN.waiting_for_mode)

    # Cek admin
    is_admin = db.is_admin(message.from_user.id)

    # Hitung ping dan format nama
    end_time = time.time()
    ping_ms = round((end_time - start_time) * 1000, 2)
    user_name = message.from_user.full_name
    username = f" (@{message.from_user.username})" if message.from_user.username else ""

    await message.answer(
        f"Halo <b>{user_name}</b>{username}! 👋\n"
        f"🏓 Ping: <code>{ping_ms} ms</code>\n\n"
        f"✅ Protokol <b>{protocol.upper()}</b> terdeteksi.\n\n"
        "Silakan pilih mode konversi di bawah ini:",
        reply_markup=get_mode_keyboard(is_admin=is_admin)
    )

@router.message(ConvertVPN.waiting_for_vpn_account, F.text)
async def process_vpn_account(message: types.Message, state: FSMContext):
    """
    Handler untuk menerima teks konfigurasi VPN saat user sudah di state waiting_for_vpn_account.
    """
    await _handle_vpn_input(message, state)

@router.message(F.text.startswith("vmess://"))
@router.message(F.text.startswith("vless://"))
@router.message(F.text.startswith("trojan://"))
async def process_vpn_account_anytime(message: types.Message, state: FSMContext):
    """
    Fallback: menangkap config VPN yang dikirim kapan saja (di luar state).
    State lama akan di-reset terlebih dahulu agar aman.
    """
    await _handle_vpn_input(message, state)

# ─────────────────────────────────────────────────────
# Custom Domain Input (Manual)
# ─────────────────────────────────────────────────────

@router.message(ConvertVPN.waiting_for_custom_domain, F.text)
async def process_custom_domain(message: types.Message, state: FSMContext):
    """
    Handler untuk menangkap input teks manual dari user jika memilih Custom Domain.
    """
    domain = message.text.strip().lower()

    # Validasi sederhana: pastikan tidak ada skema http/https dan memiliki panjang rasional
    if "://" in domain or len(domain) < 3:
        await message.answer("❌ Format domain tidak valid. Harap ketik ulang (contoh: bug.com).")
        return

    # Simpan ke state
    await state.update_data(selected_domain=domain)

    # Ambil seluruh data dari FSM
    user_data = await state.get_data()
    protocol = user_data.get("protocol")
    original_config = user_data.get("original_config")
    mode = user_data.get("mode")

    from services.converter import converter_service

    try:
        # Lakukan Konversi
        result = converter_service.convert(protocol, original_config, mode, domain)

        # Escape karakter HTML spesial (& < >)
        safe_result = html.escape(result)

        text_result = (
            f"✅ <b>Konversi Berhasil!</b>\n\n"
            f"<b>Protokol:</b> {protocol.upper()}\n"
            f"<b>Mode:</b> {mode.upper()}\n"
            f"<b>Domain (Custom):</b> {domain}\n\n"
            f"<code>{safe_result}</code>"
        )
        await message.answer(text_result)

        # Catat statistik
        try:
            from database import db
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
        await message.answer(f"❌ <b>Konversi Gagal:</b>\n{str(e)}")

    finally:
        # [SECURITY] Wajib menghapus FSM setelah selesai
        await state.clear()

# ─────────────────────────────────────────────────────
# Admin: Tambah Bug dari FSM
# ─────────────────────────────────────────────────────

@router.message(ConvertVPN.waiting_for_new_bug, F.text)
async def process_new_bug(message: types.Message, state: FSMContext):
    """
    Handler khusus admin untuk menambahkan bug baru di tengah FSM.
    Format input: "domain.com Kategori" atau hanya "domain.com" (default: Umum)
    """
    from database import db
    from keyboards.inline import get_category_keyboard

    if not db.is_admin(message.from_user.id):
        return

    args = message.text.strip().split()
    new_bug = args[0].lower()
    bug_mode = args[1].lower() if len(args) > 1 else "all"
    category = args[2].strip().title() if len(args) > 2 else "Umum"
    title = " ".join(args[3:]).strip() if len(args) > 3 else ""

    if db.add_domain(new_bug, category, bug_mode, title):
        title_str = f" ({title})" if title else ""
        await message.answer(f"✅ Bug <b>{new_bug}</b>{title_str} (Mode: <b>{bug_mode}</b>, Kategori: <b>{category}</b>) berhasil ditambahkan ke database!")
    else:
        await message.answer(f"❌ Bug <b>{new_bug}</b> gagal ditambahkan (mungkin sudah ada).")

    # Kembalikan user ke state pemilihan KATEGORI
    await state.set_state(ConvertVPN.waiting_for_category_selection)
    user_data = await state.get_data()
    mode = user_data.get("mode", "all")
    domains = db.get_all_domains()

    await message.answer(
        f"Mode <b>{mode.upper()}</b> dipilih. ✅\n\n"
        "Pilih <b>kategori</b> domain yang ingin digunakan:",
        reply_markup=get_category_keyboard(domains, selected_mode=mode, is_admin=True)
    )
