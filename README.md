# 🤖 Mentor Bahasa Inggris Virtual

**AI-powered English Learning Telegram Bot** built with Python, Google Gemini AI, and Supabase.

Mentor Bahasa Inggris Virtual adalah bot Telegram berbasis kecerdasan buatan yang dirancang untuk membantu pengguna belajar bahasa Inggris secara interaktif. Bot ini dikembangkan sebagai proyek pembelajaran Python Agentic AI.

## ✨ Fitur Utama

- **AI Learning Assistant** — berinteraksi dengan pengguna melalui Telegram menggunakan Google Gemini AI.
- **Reading** — membuat latihan membaca bahasa Inggris beserta pertanyaannya.
- **Writing & Grammar** — mendukung latihan menulis dan pemeriksaan tata bahasa.
- **Speaking** — mendukung pemrosesan voice note untuk latihan berbicara.
- **Listening** — mendukung pengembangan latihan bahasa Inggris untuk keterampilan menyimak.
- **Learning Report** — menyediakan perintah untuk membuat laporan belajar dalam format PDF.
- **Daily Reminder** — mengirim pengingat rutin agar pengguna tetap konsisten belajar.
- **Conversation History** — menggunakan Supabase untuk menyimpan data pengguna dan riwayat percakapan.

## 🛠️ Teknologi

| Teknologi | Kegunaan |
|---|---|
| Python | Bahasa pemrograman utama |
| Google Gemini AI | Pemrosesan bahasa dan kecerdasan buatan |
| python-telegram-bot | Integrasi bot dengan Telegram |
| Supabase | Database dan penyimpanan riwayat percakapan |
| uv | Manajemen dependensi dan lingkungan Python |
| Git & GitHub | Version control dan pengelolaan kode sumber |

## 📋 Persyaratan

Sebelum menjalankan proyek, siapkan:

- Python sesuai versi yang ditentukan pada `.python-version`.
- [uv](https://docs.astral.sh/uv/)
- Token bot Telegram dari [@BotFather](https://t.me/BotFather).
- API key Google Gemini dari [Google AI Studio](https://aistudio.google.com/).
- Project Supabase beserta tabel dan konfigurasi akses database yang sesuai.

## 🚀 Instalasi

### 1. Clone repository

```bash
git clone git@github.com:syarifm74/mentor-bahasa-inggris-virtual.git
```

Masuk ke direktori proyek:

```bash
cd mentor-bahasa-inggris-virtual
```

### 2. Instal dependensi

```bash
uv sync
```

### 3. Konfigurasi environment

Buat file `.env` di direktori utama proyek. Isi dengan kredensial milikmu:

```dotenv
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key

GEMINI_MODEL=your_supported_gemini_model
GEMINI_MODEL_TTS=your_supported_tts_model

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_api_key
```

Ganti nilai placeholder dengan konfigurasi yang sesuai. Nama model harus didukung oleh API Gemini yang digunakan.

**Penting:** Jangan mengunggah `.env`, API key, token bot Telegram, private key, atau kredensial database ke GitHub.

### 4. Jalankan aplikasi

```bash
uv run main.py
```

Jika konfigurasi sudah sesuai, bot akan berjalan dan menunggu pesan dari Telegram.

## 💬 Cara Menggunakan

1. Buka bot Mentor Bahasa Inggris Virtual di Telegram.
2. Kirim perintah `/start` untuk memulai.
3. Kirim pesan untuk meminta bantuan belajar bahasa Inggris.

Contoh perintah atau pesan:

```text
/start
```

```text
Buatkan soal reading tingkat pemula.
```

```text
Periksa grammar: I goes to school.
```

```text
Berikan saya tips belajar bahasa Inggris.
```

Gunakan `/report` untuk meminta laporan belajar sesuai fitur yang tersedia pada aplikasi.

## 🔐 Keamanan

- Simpan seluruh kredensial dalam file `.env`.
- Pastikan `.env` diabaikan oleh `.gitignore`.
- Jangan menonaktifkan Row Level Security (RLS) Supabase untuk sekadar mengatasi error.
- Gunakan kebijakan akses database yang sesuai dengan kebutuhan aplikasi.
- Jika token atau API key terekspos, cabut atau rotasi kredensial tersebut.

## 🎯 Tujuan Proyek

Proyek ini dikembangkan untuk mempraktikkan Python, AI Agent, integrasi API, pengelolaan database, pembuatan bot Telegram, serta penggunaan Git dan GitHub dalam pengembangan perangkat lunak.

## 📌 Status Proyek

**Dalam pengembangan.**

Fitur dan konfigurasi dapat berubah seiring proses pembelajaran dan pengembangan berikutnya.

---

*Mentor Bahasa Inggris Virtual — Your AI Companion for English Learning.*
