
import os
import random
from datetime import date, time, timedelta
from zoneinfo import ZoneInfo

import src.core.env as env
from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    Defaults,
    MessageHandler,
    filters,
)

from src.agents.lead import LeadAgent
from src.core.artifacts import Artifact
from src.core.format import to_telegram_markdown
from src.repository.chat_repository import ChatRepository


timezone = ZoneInfo("Asia/Jakarta")

chat_repository = ChatRepository()

# Dipertahankan untuk fungsi report dan voice
# sesuai pemanggilan method pada kode sebelumnya.
lead_agent = LeadAgent(user_id=101010)

bot_config = Defaults(
    parse_mode=ParseMode.MARKDOWN_V2,
    tzinfo=timezone,
)


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_message is None or update.effective_user is None:
        return

    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name or "teman"
    chat_id = update.effective_chat.id

    try:
        chat_repository.save_user(
            user_id=user_id,
            username=username,
            chat_id=chat_id,
        )
    except Exception:
        logger.exception("Gagal menyimpan pengguna Telegram")

        await update.effective_message.reply_text(
            "Maaf, pendaftaran belum berhasil. Silakan coba lagi nanti.",
            parse_mode=None,
        )
        return

    welcome_text = (
        f"Halo! Selamat datang {username} di Mentor Bahasa Inggris Virtual.\n"
        "Aku siap membantu kamu belajar bahasa Inggris!\n"
        "Coba ketik pesan seperti ini:\n"
        "- *buatkan soal reading*\n"
        "- *periksa: I goes to school*\n"
        "- *kasih tips belajar*\n"
        "Kamu juga bisa ngobrol untuk melatih speaking atau writing.\n"
        "- Ketik /start untuk mendaftarkan akun\n"
        "- Ketik /report untuk membuat laporan belajar"
    )

    await update.effective_message.reply_text(
        to_telegram_markdown(welcome_text)
    )


async def report_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_message is None or update.effective_user is None:
        return

    await update.effective_message.reply_text(
        to_telegram_markdown("Laporan sedang kami buat, mohon tunggu...")
    )

    user_id = update.effective_user.id
    username = (
        update.effective_user.username
        or update.effective_user.first_name
        or "teman"
    )

    end_date = date.today()
    start_date = end_date - timedelta(days=7)

    try:
        report_file_path = lead_agent.handle_report(
            user_id=user_id,
            username=username,
            start_date=start_date,
            end_date=end_date,
        )

        if not os.path.exists(report_file_path):
            raise FileNotFoundError(
                f"File laporan tidak ditemukan: {report_file_path}"
            )

        with open(report_file_path, "rb") as report_pdf:
            await update.effective_message.reply_document(
                document=report_pdf,
                caption=to_telegram_markdown(
                    "Laporan belajar bahasa Inggris dari "
                    f"{start_date.isoformat()} sampai {end_date.isoformat()}"
                ),
            )

    except Exception:
        logger.exception("Gagal membuat laporan belajar")

        await update.effective_message.reply_text(
            "Maaf, laporan belum berhasil dibuat. Silakan coba lagi.",
            parse_mode=None,
        )


async def _send_artifact(
    update: Update,
    artifact: Artifact,
):
    if update.effective_message is None:
        return

    artifact_path = artifact.get("path")
    kind = artifact.get("kind")
    caption = artifact.get("caption") or ""

    if not artifact_path or not os.path.exists(artifact_path):
        logger.warning("File artifact tidak ditemukan: {}", artifact_path)
        return

    safe_caption_text = to_telegram_markdown(caption)

    try:
        with open(artifact_path, "rb") as artifact_file:
            if kind == "audio":
                await update.effective_message.reply_audio(
                    audio=artifact_file,
                    caption=safe_caption_text,
                )
            elif kind == "video":
                await update.effective_message.reply_video(
                    video=artifact_file,
                    caption=safe_caption_text,
                )
            else:
                await update.effective_message.reply_document(
                    document=artifact_file,
                    caption=safe_caption_text,
                )

    finally:
        if os.path.exists(artifact_path):
            os.remove(artifact_path)
            logger.info("File artifact dihapus: {}", artifact_path)


async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_message is None or update.effective_user is None:
        return

    message = update.effective_message

    reply_text = await message.reply_text(
        to_telegram_markdown(
            "Mentor sedang menyiapkan jawaban..."
        )
    )

    user_id = update.effective_user.id
    user_message = message.text or ""

    try:
        # Buat agent menggunakan ID Telegram pengguna saat ini.
        agent = LeadAgent(user_id=user_id)

        # handle_send_message menerima message_text,
        # sedangkan user_id sudah diberikan pada konstruktor.
        response = agent.handle_send_message(
            message_text=user_message
        )

        answer = response.get("text") or "Maaf, jawaban belum tersedia."
        safe_text = to_telegram_markdown(answer)

        await reply_text.edit_text(safe_text)

        for artifact_data in response.get("artifacts") or []:
            logger.debug("Artifact diterima: {}", artifact_data)

            artifact = Artifact(artifact_data)
            await _send_artifact(update, artifact)

    except Exception:
        logger.exception(
            "Gagal memproses pesan dari pengguna Telegram {}",
            user_id,
        )

        await reply_text.edit_text(
            "Maaf, terjadi kendala saat memproses pesan. "
            "Silakan coba lagi.",
            parse_mode=None,
        )


async def handle_voice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if (
        update.effective_message is None
        or update.effective_user is None
        or update.message is None
        or update.message.voice is None
    ):
        return

    message = update.effective_message

    reply_text = await message.reply_text(
        to_telegram_markdown(
            "Suara sedang kami proses, mohon tunggu..."
        )
    )

    user_id = update.effective_user.id
    voice_file_path = None

    try:
        env.TEMP.mkdir(parents=True, exist_ok=True)

        voice_file = await context.bot.get_file(
            update.message.voice.file_id
        )

        voice_file_path = (
            env.TEMP / f"{update.message.voice.file_id}.ogg"
        )

        await voice_file.download_to_drive(str(voice_file_path))

        evaluation_result = lead_agent.handle_send_voice(
            user_id=user_id,
            voice_file_path=voice_file_path,
        )

        await reply_text.edit_text(
            to_telegram_markdown(str(evaluation_result))
        )

    except Exception:
        logger.exception(
            "Gagal memproses voice note dari pengguna {}",
            user_id,
        )

        await reply_text.edit_text(
            "Maaf, voice note belum berhasil diproses. Silakan coba lagi.",
            parse_mode=None,
        )

    finally:
        if voice_file_path and os.path.exists(voice_file_path):
            os.remove(voice_file_path)


async def task_reminder(
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.info("[app.py][task_reminder]")

    try:
        users = chat_repository.get_users()
        skill_types = [
            "reading",
            "writing",
            "listening",
            "speaking",
        ]

        for user in users.data or []:
            user_id = user["user_id"]
            message = (
                "Pagi! ☀️ Yuk, luangkan 5 menit untuk latihan "
                f"{random.choice(skill_types)} hari ini."
            )

            try:
                chat_repository.save_message(
                    user_id=user_id,
                    role="model",
                    message_text=message,
                )

                await context.bot.send_message(
                    chat_id=user_id,
                    text=to_telegram_markdown(message),
                )

            except Exception:
                logger.exception(
                    "Gagal mengirim pengingat kepada pengguna {}",
                    user_id,
                )

    except Exception:
        logger.exception("Gagal menjalankan pengingat harian")


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.error("Error aplikasi: {}", context.error)

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Maaf, terjadi kesalahan pada aplikasi. Silakan coba lagi.",
                parse_mode=None,
            )
        except Exception:
            logger.exception("Gagal mengirim pesan error ke Telegram")


def run():
    app = (
        Application.builder()
        .token(env.TELEGRAM_BOT_TOKEN)
        .defaults(bot_config)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start_command)
    )
    app.add_handler(
        CommandHandler("report", report_command)
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text,
        )
    )
    app.add_handler(
        MessageHandler(filters.VOICE, handle_voice)
    )

    target_time = time(
        hour=10,
        minute=3,
        second=0,
        tzinfo=timezone,
    )

    app.job_queue.run_daily(
        callback=task_reminder,
        time=target_time,
        name="task_reminder",
    )

    app.add_error_handler(error_handler)

    print("Mentor Bahasa Inggris Virtual berhasil dijalankan...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        timeout=30,
    )
