import os
import logging
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = -1003660151590

# ================= БАЗА ДАННЫХ =================
def init_db():
    conn = sqlite3.connect("bot_simple.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            verification TEXT DEFAULT '❌ Не пройден',
            discount TEXT DEFAULT '0%',
            payout TEXT DEFAULT 'Не указан'
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_profile_data(user_id):
    conn = sqlite3.connect("bot_simple.db")
    cursor = conn.cursor()
    cursor.execute("SELECT verification, discount, payout FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        row = ('❌ Не пройден', '0%', 'Не указан')
    conn.close()
    return row

# ================= REKVIZITY =================
BANKS = {
    "alfa": {"name": "Альфа-Банк", "icon": "🏦", "number": "4777 0000 0000 0000", "holder": "Вероника П."},
    "sbp": {"name": "ОПЛАТА ПО СБП", "icon": "📲", "number": "+79991234567", "holder": "Вероника П."},
    "card": {"name": "ОПЛАТА ПО КАРТЕ", "icon": "💳", "number": "2200 0000 0000 0000", "holder": "Вероника П."},
    "sber": {"name": "Сбер пей", "icon": "💚", "number": "+79997654321", "holder": "Вероника П."},
    "tbank": {"name": "Т-банк", "icon": "🏦", "number": "2200700924593303", "holder": "Вероника П."}
}

# ================= PRICE LIST =================
SO_PRICES = {
    "so_300": ("300 Gold", 250, 30), "so_500": ("500 Gold", 420, 50),
    "so_700": ("700 Gold", 580, 70), "so_900": ("900 Gold", 750, 90),
    "so_1100": ("1100 Gold", 920, 110), "so_1300": ("1300 Gold", 1080, 130),
    "so_1500": ("1500 Gold", 1250, 150), "so_1700": ("1700 Gold", 1420, 170),
    "so_1900": ("1900 Gold", 1580, 190), "so_2100": ("2100 Gold", 1750, 210),
    "so_2300": ("2300 Gold", 1920, 230), "so_2500": ("2500 Gold", 2080, 250),
    "so_2700": ("2700 Gold", 2250, 270), "so_2900": ("2900 Gold", 2420, 290),
    "so_3100": ("3100 Gold", 2580, 310), "so_3300": ("3300 Gold", 2750, 330),
    "so_3500": ("3500 Gold", 2920, 350), "so_3700": ("3700 Gold", 3080, 370),
    "so_3900": ("3900 Gold", 3250, 390), "so_4100": ("4100 Gold", 3420, 410),
    "so_4300": ("4300 Gold", 3580, 430), "so_4500": ("4500 Gold", 3750, 450),
    "so_4700": ("4700 Gold", 3920, 470), "so_4900": ("4900 Gold", 4080, 490),
    "so_5000": ("5000 Gold", 4170, 500)
}

SO_TABLE_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🧈 300G — 30смн / 250₽", callback_data="so_300"), InlineKeyboardButton("🧈 2700G — 270смн / 2250₽", callback_data="so_2700")],
    [InlineKeyboardButton("🧈 500G — 50смн / 420₽", callback_data="so_500"), InlineKeyboardButton("🧈 2900G — 290смн / 2420₽", callback_data="so_2900")],
    [InlineKeyboardButton("🧈 700G — 70смн / 580₽", callback_data="so_700"), InlineKeyboardButton("🧈 3100G — 310смн / 2580₽", callback_data="so_3100")],
    [InlineKeyboardButton("🧈 900G — 90смн / 750₽", callback_data="so_900"), InlineKeyboardButton("🧈 3300G — 330смн / 2750₽", callback_data="so_3300")],
    [InlineKeyboardButton("🧈 1100G — 110смн / 920₽", callback_data="so_1100"), InlineKeyboardButton("🧈 3500G — 350смн / 2920₽", callback_data="so_3500")],
    [InlineKeyboardButton("🧈 1300G — 130смн / 1080₽", callback_data="so_1300"), InlineKeyboardButton("🧈 3700G — 370смн / 3080₽", callback_data="so_3700")],
    [InlineKeyboardButton("🧈 1500G — 150смн / 1250₽", callback_data="so_1500"), InlineKeyboardButton("🧈 3900G — 390смн / 3250₽", callback_data="so_3900")],
    [InlineKeyboardButton("🧈 1700G — 170смн / 1420₽", callback_data="so_1700"), InlineKeyboardButton("🧈 4100G — 410смн / 3420₽", callback_data="so_4100")],
    [InlineKeyboardButton("🧈 1900G — 190смн / 1580₽", callback_data="so_1900"), InlineKeyboardButton("🧈 4300G — 430смн / 3580₽", callback_data="so_4300")],
    [InlineKeyboardButton("🧈 2100G — 210смн / 1750₽", callback_data="so_2100"), InlineKeyboardButton("🧈 4500G — 450смн / 3750₽", callback_data="so_4500")],
    [InlineKeyboardButton("🧈 2300G — 230смн / 1920₽", callback_data="so_2300"), InlineKeyboardButton("🧈 4700G — 470смн / 3920₽", callback_data="so_4700")],
    [InlineKeyboardButton("🧈 2500G — 250смн / 2080₽", callback_data="so_2500"), InlineKeyboardButton("🧈 4900G — 490смн / 4080₽", callback_data="so_4900")],
    [InlineKeyboardButton("🧈 5000G — 500смн / 4170₽", callback_data="so_5000")]
])

def inline_back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]])

def bank_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Альфа-Банк", callback_data="bank_alfa"), InlineKeyboardButton("ОПЛАТА ПО СБП", callback_data="bank_sbp")],
        [InlineKeyboardButton("ОПЛАТА ПО КАРТЕ", callback_data="bank_card"), InlineKeyboardButton("Сбер пей", callback_data="bank_sber")],
        [InlineKeyboardButton("Т-банк", callback_data="bank_tbank")],
        [InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu")]
    ])

def currency_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇹🇯 Сомони (TJS)", callback_data="curr_tjs")],
        [InlineKeyboardButton("🇷🇺 Рубли (RUB)", callback_data="curr_rub")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]
    ])

# STATES (УБРАЛ ШАГ ENTER_TG)
CHOOSE_PRODUCT, ENTER_ID, CHOOSE_BANK, CHOOSE_CURRENCY, WAIT_CHECK = range(5)

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("💰 Пополнить"), KeyboardButton("🆔 Профиль")],
        [KeyboardButton("💻 Поддержка"), KeyboardButton("Информ...я о боте")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚨 **Главное меню**\nДля взаимодействия с ботом используй клавиатуру.",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def handle_popolnit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 **Выберите количество Gold из прайс-листа:**",
        reply_markup=SO_TABLE_MENU,
        parse_mode="Markdown"
    )
    return CHOOSE_PRODUCT

async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.message.edit_text("👑 Выберите количество Gold из прайс-листа:", reply_markup=SO_TABLE_MENU)
    return CHOOSE_PRODUCT

async def back_to_currency_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text("💱 Выберите валюту для оплаты:", reply_markup=currency_menu())
    return CHOOSE_CURRENCY

async def product_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in SO_PRICES:
        product, price_rub, price_tjs = SO_PRICES[data]
        context.user_data["product"] = product
        context.user_data["price_rub"] = price_rub
        context.user_data["price_tjs"] = price_tjs
    else:
        return CHOOSE_PRODUCT

    # СРАЗУ ПЕРЕХОДИМ К ЗАПРОСУ ИГРОВОГО ID (ПРОПУСКАЯ ТЕЛЕГРАМ НИК)
    await query.message.edit_text(
        "🆔 Введите ваш игровой ID Standoff 2 (минимум 7 цифр):",
        reply_markup=inline_back_menu()
    )
    return ENTER_ID

async def enter_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if not text.isdigit() or len(text) < 7:
        await update.message.reply_text(
            "❌ Неверный ID!\nИгровой ID должен состоять только из цифр.\nПожалуйста, введите ваш ID заново:",
            reply_markup=inline_back_menu()
        )
        return ENTER_ID

    context.user_data["game_id"] = text
    await update.message.reply_text("Выберите способ оплаты 💳:", reply_markup=bank_menu())
    return CHOOSE_BANK

async def bank_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    bank_key = query.data.replace("bank_", "")
    bank = BANKS.get(bank_key)
    if not bank:
        return CHOOSE_BANK
        
    context.user_data["bank_key"] = bank_key
    context.user_data["bank_name"] = bank["name"]
    context.user_data["bank_icon"] = bank["icon"]
    context.user_data["bank_number"] = bank["number"]
    context.user_data["bank_holder"] = bank["holder"]

    await query.message.edit_text("💱 Выберите валюту для оплаты:", reply_markup=currency_menu())
    return CHOOSE_CURRENCY

async def currency_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    curr_type = query.data.replace("curr_", "")

    if curr_type == "tjs":
        amount = f"{context.user_data['price_tjs']} сомони"
    else:
        amount = f"{context.user_data['price_rub']} ₽"

    context.user_data["final_amount"] = amount

    payment_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Проблема с оплатой", callback_data="pay_problem")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
    ])

    receipt_text = (
        f"{context.user_data['bank_icon']} **Банк для оплаты: {context.user_data['bank_name']}**\n\n"
        f"Если нужен сбп, отпишите в лс владельцу\n\n"
        f"👤 **Получатель:** {context.user_data['bank_holder']}\n"
        f"💳 **Реквизиты:** `{context.user_data['bank_number']}`\n"
        f"💰 **Сумма:** {amount}\n\n"
        f"✅ **После оплаты отправьте скриншот чека** 👇"
    )

    await query.message.edit_text(receipt_text, parse_mode="Markdown", reply_markup=payment_keyboard)
    return WAIT_CHECK

async def get_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ Пожалуйста, отправьте именно фото или скриншот чека.")
        return WAIT_CHECK

    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name

    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"📌 Новый заказ [STANDOFF 2]:\n"
                f"🎮 Игра: STANDOFF 2\n"
                f"👤 Ник в TG: {username}\n"
                f"🆔 Игровой ID: {context.user_data.get('game_id','')}\n"
                f"💳 Банк оплаты: {context.user_data.get('bank_name','')}\n"
                f"💰 Товар: {context.user_data.get('product','')} — {context.user_data.get('final_amount','?')}"
    )
    
    await update.message.reply_text("✅ Оплата отправлена на проверку! Администратор скоро свяжется с вами.")
    context.user_data.clear()
    return ConversationHandler.END

# ================= GLOBAL MENU HANDLERS =================
async def global_menu_handlers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user = update.effective_user

    if user_text == "🆔 Профиль":
        verification, discount, payout = get_profile_data(user.id)
        username = f"@{user.username}" if user.username else user.first_name
        
        profile_text = (
            f"👤 **Никнейм:** {username} ({user.id})\n\n"
            f"🛡 **Статус верификации:** {verification}\n"
            f"📈 **Личная скидка:** {discount}\n"
            f"📥 **Способ вывода:** {payout}"
        )
        inline_profile_kbd = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Промокод", callback_data="profile_promo")],
            [InlineKeyboardButton("🔄 Изменить настройки", callback_data="edit_settings")]
        ])
        await update.message.reply_text(profile_text, reply_markup=inline_profile_kbd, parse_mode="Markdown")

    elif user_text == "💻 Поддержка":
        # СЛУЖБА ПОДДЕРЖКИ С ТВОИМ ЮЗЕРНЕЙМОМ
        await update.message.reply_text(
            "🛠 **Служба поддержки**\n\n"
            "Если у вас возникли какие-то проблемы или вопросы по поводу оплаты и получения товара, "
            "то сразу же обращайтесь к администратору: @mewik88",
            parse_mode="Markdown"
        )

    elif user_text == "Информ...я о боте":
        # БОЛЬШОЙ ИНФОРМАТИВНЫЙ БЛОК
        info_text = (
            "ℹ️ **Информация о нашем боте**\n\n"
            "🔥 **Добро пожаловать в самый надежный маркет золота Standoff 2!**\n\n"
            "⚡ **Почему выбирают именно нас:**\n"
            "• **Самые быстрые услуги:** Мы обрабатываем и отправляем заказы в рекордно короткие сроки.\n"
            "• **Моментальный прием:** Наши администраторы быстро принимают чеки и сразу берут заказ в работу.\n"
            "• **Полная безопасность:** Все транзакции защищены, а покупка игровой валюты происходит легально и без рисков для вашего аккаунта.\n"
            "• **Выгодный курс:** Самые честные и приятные цены на рынке как в рублях, так и в сомони!\n\n"
            "📈 Мы работаем каждый день, чтобы делать ваш игровой процесс лучше и комфортнее. Спасибо, что вы с нами!"
        )
        await update.message.reply_text(info_text, parse_mode="Markdown")

async def handle_inline_clicks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "pay_problem":
        await query.message.reply_text("⚠️ Возникли проблемы с платежом? Напишите сюда: @mewik88")

# ================= RUN =================
def main():
    if not TOKEN:
        print("Ошибка: Переменная TOKEN не задана!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.Text(["🆔 Профиль", "💻 Поддержка", "Информ...я о боте"]), global_menu_handlers))

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Text("💰 Пополнить"), handle_popolnit)
        ],
        states={
            CHOOSE_PRODUCT: [
                CallbackQueryHandler(product_choice, pattern="^so_"),
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$")
            ],
            ENTER_ID: [
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_id)
            ],
            CHOOSE_BANK: [
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"),
                CallbackQueryHandler(bank_choice, pattern="^bank_")
            ],
            CHOOSE_CURRENCY: [
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"),
                CallbackQueryHandler(currency_choice, pattern="^curr_")
            ],
            WAIT_CHECK: [
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"),
                CallbackQueryHandler(handle_inline_clicks, pattern="^pay_problem$"),
                MessageHandler(filters.PHOTO, get_check)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(handle_inline_clicks))
    
    print("🚀 Бот Standoff 2 успешно запущен с обновленным контентом!")
    app.run_polling()

if __name__ == "__main__":
    main()

