import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# ===== НАСТРОЙКИ =====
BOT_NAME = "КотоБаг"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL = "@kotobag_news"
CHANNEL_URL = "https://t.me/kotobag_news"
POSTER = "https://upload.wikimedia.org/wikipedia/en/thumb/c/c1/Miraculous_Ladybug_and_Cat_Noir_logo.png/250px-Miraculous_Ladybug_and_Cat_Noir_logo.png"

# ===== СЕРИИ 1 СЕЗОНА =====
EPISODES = []
for i in range(1, 26):
    ep_num = f"{i:02d}"
    EPISODES.append({
        "name": f"Серия {i}",
        "url": f"https://miraculous-world.online/?watch=s1-e{ep_num}"
    })

# ===== ПРОВЕРКА ПОДПИСКИ =====
async def is_subscribed(ctx, uid):
    try:
        m = await ctx.bot.get_chat_member(CHANNEL, uid)
        return m.status in ("member", "administrator", "creator")
    except Exception:
        return False

# ===== КЛАВИАТУРЫ =====
def subscribe_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Подписаться", url=CHANNEL_URL)],
        [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")]
    ])

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📺 1 Сезон", callback_data="season:1")],
    ])

def episodes_kb():
    buttons, row = [], []
    for i, ep in enumerate(EPISODES):
        row.append(InlineKeyboardButton(ep["name"], callback_data=f"ep:{i}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="main")])
    return InlineKeyboardMarkup(buttons)

# ===== ХЕНДЛЕРЫ =====
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(ctx, update.effective_user.id):
        await update.message.reply_text(
            f"Привет! Это {BOT_NAME}.\nЧтобы смотреть, подпишись на канал:", 
            reply_markup=subscribe_kb()
        )
        return
    await update.message.reply_text(f"🐞🐱 {BOT_NAME}\nВыбери сезон:", reply_markup=main_menu_kb())

async def on_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    
    if data == "check_sub":
        if await is_subscribed(ctx, q.from_user.id):
            await q.edit_message_text("✅ Подписка подтверждена!\nВыбери сезон:", reply_markup=main_menu_kb())
        else:
            await q.edit_message_text("❌ Ты не подписался!", reply_markup=subscribe_kb())
        return
    
    if not await is_subscribed(ctx, q.from_user.id):
        await q.edit_message_text("Сначала подпишись на канал:", reply_markup=subscribe_kb())
        return

    if data == "main":
        await q.edit_message_text("Выбери сезон:", reply_markup=main_menu_kb())
    elif data == "season:1":
        await q.edit_message_text("1 Сезон - выбери серию:", reply_markup=episodes_kb())
    elif data.startswith("ep:"):
        idx = int(data.split(":")[1])
        ep = EPISODES[idx]
        
        # Отправляем картинку с кнопкой "Смотреть"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("▶️ Смотреть видео", url=ep["url"])],
            [InlineKeyboardButton("⬅️ Назад", callback_data="season:1")]
        ])
        
        await q.message.reply_photo(
            photo=POSTER,
            caption=f"📺 1 Сезон\n🎬 {ep['name']}",
            reply_markup=kb
        )
        # Удаляем сообщение с кнопками, чтобы чат не засорялся
        await q.message.delete()

async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Нажми /start 🙂")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.run_polling()

if __name__ == "__main__":
    main()
