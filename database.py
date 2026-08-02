import sqlite3
import logging
from typing import List
from config import config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Inisialisasi tabel-tabel database yang diizinkan."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Tabel domains untuk menyimpan domain yang bisa dipilih
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS domains (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        domain TEXT UNIQUE NOT NULL,
                        category TEXT DEFAULT 'Umum'
                    )
                ''')
                
                # Migrasi untuk tambahkan kolom category jika belum ada (bagi db lama)
                try:
                    cursor.execute("ALTER TABLE domains ADD COLUMN category TEXT DEFAULT 'Umum'")
                except sqlite3.OperationalError:
                    pass # Kolom sudah ada

                
                # Tabel admins untuk menyimpan ID admin (Owner dipisah di config)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS admins (
                        user_id INTEGER PRIMARY KEY
                    )
                ''')
                
                # Tabel users hanya untuk tracking user yang pernah menggunakan bot
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Tabel statistics untuk menghitung jumlah konversi (tanpa data sensitif)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE DEFAULT CURRENT_DATE,
                        protocol TEXT NOT NULL,
                        count INTEGER DEFAULT 1,
                        UNIQUE(date, protocol)
                    )
                ''')

                conn.commit()
                logger.info("Database berhasil diinisialisasi.")
        except sqlite3.Error as e:
            logger.error(f"Gagal menginisialisasi database: {e}")

    def get_all_domains(self) -> List[dict]:
        """Mengambil seluruh daftar domain beserta kategorinya."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT domain, category FROM domains ORDER BY category, domain")
                rows = cursor.fetchall()
                return [{"domain": row["domain"], "category": row["category"] or "Umum"} for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching domains: {e}")
            return []

    def is_admin(self, user_id: int) -> bool:
        """Mengecek apakah user adalah Owner atau Admin."""
        if user_id == config.OWNER_ID:
            return True
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
                return cursor.fetchone() is not None
        except sqlite3.Error:
            return False

    def add_domain(self, domain: str, category: str = "Umum") -> bool:
        """Menambahkan domain baru ke database beserta kategorinya."""
        try:
            with self._get_connection() as conn:
                conn.execute("INSERT INTO domains (domain, category) VALUES (?, ?)", (domain, category))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False # Domain sudah ada
        except sqlite3.Error as e:
            logger.error(f"Error adding domain: {e}")
            return False

    def delete_domain(self, domain: str) -> bool:
        """Menghapus domain dari database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM domains WHERE domain = ?", (domain,))
                conn.commit()
                return cursor.rowcount > 0 # Return True jika ada row yang terhapus
        except sqlite3.Error as e:
            logger.error(f"Error deleting domain: {e}")
            return False

db = Database()
