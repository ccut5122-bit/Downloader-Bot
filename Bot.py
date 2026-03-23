import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")  # Railway se aayega
CHANNEL = "@CashVault01"
ADMIN_ID = 8112333859

users = set()
mode = {}

# ---------------- JOIN CHECK ----------------
async def check_join(user, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    users.add(user)

    if not await check_join(user, context):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL.replace('@','')}")],
            [InlineKeyboardButton("✅ I Joined", callback_data="check")]
        ]
        await update.message.reply_text(
            "⚠️ पहले चैनल जॉइन करो",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    keyboard = [
        [InlineKeyboardButton("📥 YouTube", callback_data="yt")],
        [InlineKeyboardButton("📸 Instagram", callback_data="ig")],
        [InlineKeyboardButton("🎵 Audio", callback_data="audio")]
    ]

    await update.message.reply_text(
        "🚀 Premium Downloader Bot",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- BUTTON ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    if query.data == "check":
        if await check_join(user, context):
            await query.message.reply_text("✅ Access Granted\nअब link भेजो")
        else:
            await query.answer("❌ Join first", show_alert=True)
        return

    mode[user] = query.data
    await query.message.reply_text("🔗 अब link भेजो")

# ---------------- DOWNLOAD ----------------
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user = update.effective_user.id

    msg = await update.message.reply_text("⏳ Downloading...")

    try:
        folder = f"downloads/{user}"
        os.makedirs(folder, exist_ok=True)

        ydl_opts = {
            "outtmpl": f"{folder}/%(id)s.%(ext)s",
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True,
            "nocheckcertificate": True
        }

        if mode.get(user) == "audio":
            ydl_opts["format"] = "bestaudio"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3"
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

            if mode.get(user) == "audio":
                file = file.rsplit(".", 1)[0] + ".mp3"
            else:
                file = file.rsplit(".", 1)[0] + ".mp4"

        await msg.edit_text("📤 Uploading...")

        size = os.path.getsize(file)

        if size > 50 * 1024 * 1024:
            await update.message.reply_document(open(file, "rb"))
        else:
            if mode.get(user) == "audio":
                await update.message.reply_audio(open(file, "rb"))
            else:
                await update.message.reply_video(open(file, "rb"))

        os.remove(file)

        await update.message.reply_text("✅ Done!")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ---------------- ADMIN ----------------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"👥 Total Users: {len(users)}")

# ---------------- MAIN ----------------
app = Application.builder().token(TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("✅ Bot Running...")
app.run_polling()
