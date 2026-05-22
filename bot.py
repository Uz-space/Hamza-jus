import sqlite3                                                                   from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup          from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
                                                                                 BOT_TOKEN  = "8512672849:AAHzI5uSvTX5hzu8fdyL9BBsSk3esT4PBF4"
ADMIN_ID   = 7399101034  # O'z Telegram ID ingizni kiriting

# ── DB ───────────────────────────────────────                                  def db_init():
    conn = sqlite3.connect("bot.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")        conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT                                                                   )
    """)
    # Default linklar                                                                conn.execute("INSERT OR IGNORE INTO settings VALUES ('channel', 'https://t.me/yourchannel')")
    conn.execute("INSERT OR IGNORE INTO settings VALUES ('group',   'https://t.me/yourgroup')")
    conn.commit()                                                                    conn.close()
                                                                                 def get_setting(key):
    conn = sqlite3.connect("bot.db")                                                 row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else ""                                                                                                                                  def set_setting(key, value):
    conn = sqlite3.connect("bot.db")
    conn.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()

def save_user(user_id):                                                              conn = sqlite3.connect("bot.db")
    conn.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
    conn.commit()
    conn.close()                                                                 
def get_all_users():
    conn = sqlite3.connect("bot.db")                                                 rows = conn.execute("SELECT id FROM users").fetchall()                           conn.close()
    return [r[0] for r in rows]

# ── TUGMALAR ─────────────────────────────────
def main_button():
    return InlineKeyboardMarkup([                                                        [InlineKeyboardButton("📊 Open App", url="https://t.me/AlphaRatesBot?startapp")],
        [InlineKeyboardButton("📢 Kanal", url=get_setting("channel")),
         InlineKeyboardButton("💬 Guruh",  url=get_setting("group"))]
    ])

def admin_menu():                                                                    return InlineKeyboardMarkup([                                                        [InlineKeyboardButton("📨 Broadcast",      callback_data="broadcast")],
        [InlineKeyboardButton("📢 Kanal linkini o'zgartir", callback_data="set_channel")],
        [InlineKeyboardButton("💬 Guruh linkini o'zgartir",  callback_data="set_group")],
        [InlineKeyboardButton("👥 Foydalanuvchilar soni",   callback_data="stats")],                                                                                  ])
                                                                                 # ── CONVERSATION STATES ───────────────────────
BROADCAST, SET_CHANNEL, SET_GROUP = range(3)

# ── HANDLERLAR ────────────────────────────────                                 async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):                 save_user(update.effective_user.id)
    await update.message.reply_text("👋 Xush kelibsiz! 👇", reply_markup=main_button())

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return                                                                       users = get_all_users()
    await update.message.reply_text(
        f"⚙️ Admin panel\n👥 Foydalanuvchilar: {len(users)}",                             reply_markup=admin_menu()
    )
                                                                                 # Callback handler                                                               async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()                                                             
    if q.data == "stats":
        count = len(get_all_users())
        await q.message.reply_text(f"👥 Jami foydalanuvchilar: {count}")         
    elif q.data == "broadcast":
        await q.message.reply_text("📨 Broadcast xabarini yozing:")
        context.user_data["state"] = BROADCAST

    elif q.data == "set_channel":
        await q.message.reply_text("📢 Yangi kanal linkini yuboring:\nMisol: https://t.me/kanal")
        context.user_data["state"] = SET_CHANNEL

    elif q.data == "set_group":                                                          await q.message.reply_text("💬 Yangi guruh linkini yuboring:\nMisol: https://t.me/guruh")                                                                         context.user_data["state"] = SET_GROUP
                                                                                 async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):           if update.effective_user.id != ADMIN_ID:
        return

    state = context.user_data.get("state")

    if state == BROADCAST:
        users = get_all_users()                                                          ok, fail = 0, 0
        for uid in users:
            try:                                                                                 await context.bot.copy_message(uid, update.effective_chat.id, update.message.message_id)
                ok += 1                                                                      except:                                                                              fail += 1
        await update.message.reply_text(f"✅ Yuborildi: {ok}\n❌ Xato: {fail}")
        context.user_data["state"] = None                                                                                                                             elif state == SET_CHANNEL:
        set_setting("channel", update.message.text.strip())                              await update.message.reply_text("✅ Kanal linki yangilandi!")
        context.user_data["state"] = None

    elif state == SET_GROUP:
        set_setting("group", update.message.text.strip())                                await update.message.reply_text("✅ Guruh linki yangilandi!")
        context.user_data["state"] = None
                                                                                 # ── MAIN ──────────────────────────────────────
def main():
    db_init()
    from telegram.ext import CallbackQueryHandler                                    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))                                  app.add_handler(CallbackQueryHandler(callback))                                  app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("✅ Bot ishga tushdi!")
    app.run_polling()                                                                                                                                             if __name__ == "__main__":
    main()
