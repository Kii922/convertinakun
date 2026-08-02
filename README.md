# 🚀 VPN Converter Bot

Telegram bot modern untuk mengonversi konfigurasi VPN (Vmess, Vless, Trojan) ke berbagai mode (Wildcard, WS, dll). Bot ini dibuat menggunakan **Python** 🐍 dengan framework **Aiogram 3** 🤖.

---

## ✨ Fitur Unggulan
- ♻️ **Konversi Multipel:** Mendukung penuh konversi konfigurasi Vmess, Vless, dan Trojan.
- 🛠️ **Kustomisasi Mode:** Mudah mengubah mode seperti Wildcard dan WebSocket.
- 🌐 **Domain Manager:** Input dan kelola domain kustom Anda sendiri.
- 🛡️ **Privasi Terjamin:** Menggunakan memori sementara (RAM/FSM) untuk pemrosesan, sehingga data Anda tidak tersimpan secara permanen.

---

## 📋 Prasyarat (Lokal)
- 🐍 Python 3.9+
- 🔑 Token Bot Telegram dari [@BotFather](https://t.me/BotFather).

---



## 🐳 Deployment di VPS (menggunakan Docker)

Cara terbaik untuk menjalankan bot secara terus-menerus (24/7) di VPS adalah dengan **Docker**. File `Dockerfile` dan `docker-compose.yml` sudah kami siapkan.

### 1️⃣ Persiapan VPS
Pastikan VPS Anda (Ubuntu/Debian) sudah terinstall Docker. Jika belum, jalankan:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### 2️⃣ Clone Repositori di VPS
Masuk ke VPS via SSH, lalu clone repositori GitHub Anda:
```bash
git clone https://github.com/Kii922/convertinakun.git
cd convertinakun
```

### 3️⃣ Konfigurasi Bot
Buat file `.env` berdasarkan template:
```bash
cp .env.example .env
nano .env # Masukkan BOT_TOKEN dan konfigurasi lainnya
```

### 4️⃣ Jalankan Bot (Background)
Gunakan Docker Compose untuk mem-build dan menjalankan bot di latar belakang:
```bash
docker compose up -d --build
```

### 5️⃣ Manajemen Bot
- 📜 **Melihat Log Bot (Real-time):**
  ```bash
  docker compose logs -f
  ```
- 🛑 **Menghentikan Bot:**
  ```bash
  docker compose down
  ```
- 🔄 **Restart Bot (setelah ubah `.env` atau kode):**
  ```bash
  docker compose up -d --build
  ```

---

## 👨‍💻 Credits

Proyek ini dibuat dan dikembangkan dengan bangga oleh:

- 👤 **[kii922](https://github.com/kii922)** — *Developer Utama*
- ✨ **[Gemini AI](https://gemini.google.com/)** — *Asisten AI*
