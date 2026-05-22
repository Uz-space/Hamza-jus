import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "8512672849:AAEMkycjhp6M5CyrQDjEs6ua-lfCqxc0Hso"
ADMIN_ID  = 7399101034

BROADCAST, SET_CHANNEL, SET_GROUP = range(3)

def db_init():
    conn = sqlite3.connect("bot.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("INSERT OR IGNORE INTO settings VALUES ('channel', 'https://t.me/yourchannel')")
    conn.execute("INSERT OR IGNORE INTO settings VALUES ('group', 'https://t.me/yourgroup')")
    conn.commit()
    conn.close()

def get(key):
    conn = sqlite3.connect("bot.db")
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else ""

def set_val(key, value):
    conn = sqlite3.connect("bot.db")
    conn.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()

def save_user(uid):
    conn = sqlite3.connect("bot.db")
    conn.execute("INSERT OR IGNORE INTO users VALUES (?)", (uid,))
    conn.commit()
    conn.close()

def all_users():
    conn = sqlite3.connect("bot.db")
    rows = conn.execute("SELECT id FROM users").fetchall()
    conn.close()
    return [r[0] for r in rows]

def main_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Open App", url="https://t.me/AlphaRatesBot?startapp")],
        [InlineKeyboardButton("📢 Kanal", url=get("channel")),
         InlineKeyboardButton("💬 Guruh", url=get("group"))]
    ])

def admin_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("📢 Kanal linkini o'zgartir", callback_data="set_channel")],
        [InlineKeyboardButton("💬 Guruh linkini o'zgartir", callback_data="set_group")],
        [InlineKeyboardButton("👥 Foydalanuvchilar soni", callback_data="stats")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    await update.message.reply_text("👋 Xush kelibsiz! 👇", reply_markup=main_buttons())

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        f"⚙️ Admin panel\n👥 Foydalanuvchilar: {len(all_users())}",
        reply_markup=admin_buttons()
    )

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "stats":
        await q.message.reply_text(f"👥 Jami foydalanuvchilar: {len(all_users())}")
    elif q.data == "broadcast":
        await q.message.reply_text("📨 Broadcast xabarini yozing:")
        context.user_data["state"] = BROADCAST
    elif q.data == "set_channel":
        await q.message.reply_text("📢 Yangi kanal linkini yuboring:")
        context.user_data["state"] = SET_CHANNEL
    elif q.data == "set_group":
        await q.message.reply_text("💬 Yangi guruh linkini yuboring:")
        context.user_data["state"] = SET_GROUP

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    state = context.user_data.get("state")

    if state == BROADCAST:
        ok, fail = 0, 0
        for uid in all_users():
            try:
                await context.bot.copy_message(uid, update.effective_chat.id, update.message.message_id)
                ok += 1
            except:
                fail += 1
        await update.message.reply_text(f"✅ Yuborildi: {ok}\n❌ Xato: {fail}")
        context.user_data["state"] = None

    elif state == SET_CHANNEL:
        set_val("channel", update.message.text.strip())
        await update.message.reply_text("✅ Kanal linki yangilandi!")
        context.user_data["state"] = None

    elif state == SET_GROUP:
        set_val("group", update.message.text.strip())
        await update.message.reply_text("✅ Guruh linki yangilandi!")
        context.user_data["state"] = None

def main():
    db_init()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_text))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
