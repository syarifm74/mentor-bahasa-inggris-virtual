
import src.core.env as env
import src.core.supabase as supabase
import src.app as app_telegram_bot

from loguru import logger
from fastapi import FastAPI, Request, Response, status
from contextlib import asynccontextmanager

from src.repository.chat_repository import ChatRepository

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    Defaults,
)

from telegram.constants import ParseMode
from zoneinfo import ZoneInfo
from datetime import time


timezone = ZoneInfo("Asia/Jakarta")

bot_config = Defaults(
    parse_mode=ParseMode.MARKDOWN_V2,
    tzinfo=timezone,
)

app_bot = (
    Application.builder()
    .token(env.TELEGRAM_BOT_TOKEN)
    .defaults(bot_config)
    .build()
)

# Daftarkan handler Telegram
app_bot.add_handler(
    CommandHandler("start", app_telegram_bot.start_command)
)
app_bot.add_handler(
    CommandHandler("report", app_telegram_bot.report_command)
)
app_bot.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        app_telegram_bot.handle_text,
    )
)
app_bot.add_handler(
    MessageHandler(
        filters.VOICE,
        app_telegram_bot.handle_voice,
    )
)

# Pengingat harian
target_time = time(
    hour=8,
    minute=0,
    second=0,
    tzinfo=timezone,
)
app_bot.job_queue.run_daily(
    callback=app_telegram_bot.task_reminder,
    time=target_time,
    name="task_reminder",
)

# Error handler Telegram
app_bot.add_error_handler(app_telegram_bot.error_handler)

chat_repository = ChatRepository()
supabase_client = supabase.get_supabase_client()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Memulai aplikasi Telegram bot...")

    await app_bot.initialize()
    await app_bot.start()

    webhook_url = env.TELEGRAM_WEBHOOK_URL
    if not webhook_url:
        raise RuntimeError(
            "TELEGRAM_WEBHOOK_URL belum dikonfigurasi."
        )

    webhook_result = await app_bot.bot.set_webhook(
        url=webhook_url,
        secret_token=env.TELEGRAM_SECRET_TOKEN,
        connect_timeout=30,
    )

    logger.info(
        "Webhook Telegram dikonfigurasi. Hasil: {}",
        webhook_result,
    )

    logger.info("Aplikasi Telegram bot siap menerima pesan.")

    try:
        yield
    finally:
        logger.info("Menghentikan aplikasi Telegram bot...")

        await app_bot.bot.delete_webhook()
        await app_bot.stop()
        await app_bot.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "ini dari root"}


@app.get("/get")
async def endpoint_get():
    return {"http_method": "get"}


@app.post("/post")
async def endpoint_post():
    return {"http_method": "post"}


@app.post("/webhook")
async def telegram_webhook(request: Request):
    # Verifikasi secret token dari Telegram
    api_secret_token = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    )

    if api_secret_token != env.TELEGRAM_SECRET_TOKEN:
        logger.warning(
            "Webhook ditolak karena secret token tidak cocok."
        )
        return Response(
            status_code=status.HTTP_403_FORBIDDEN
        )

    try:
        req_body = await request.json()

        telegram_bot_data = Update.de_json(
            req_body,
            app_bot.bot,
        )

        if telegram_bot_data is None:
            logger.warning("Update Telegram kosong atau tidak valid.")
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST
            )

        message = telegram_bot_data.effective_message
        message_type = "tanpa pesan"

        if message is not None:
            if message.text:
                # Catat perintah saja, bukan isi percakapan pengguna.
                message_type = (
                    message.text.split()[0]
                    if message.text.startswith("/")
                    else "pesan teks biasa"
                )
            elif message.voice:
                message_type = "voice note"

        logger.info(
            "Update Telegram diterima: update_id={}, jenis={}",
            telegram_bot_data.update_id,
            message_type,
        )

        await app_bot.process_update(telegram_bot_data)

        logger.info(
            "Update Telegram selesai diproses: update_id={}",
            telegram_bot_data.update_id,
        )

        return Response(
            status_code=status.HTTP_200_OK
        )

    except Exception:
        logger.exception(
            "Terjadi kesalahan saat menerima atau memproses webhook Telegram."
        )
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
