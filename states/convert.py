from aiogram.fsm.state import State, StatesGroup

class ConvertVPN(StatesGroup):
    """
    FSM (Finite State Machine) untuk mengatur tahapan user
    saat melakukan konversi akun VPN.
    """
    waiting_for_vpn_account = State()
    waiting_for_mode = State()
    waiting_for_category_selection = State()   # Baru: pilih kategori dulu
    waiting_for_domain_selection = State()     # Pilih domain dalam kategori
    waiting_for_custom_domain = State()
    waiting_for_new_bug = State()
