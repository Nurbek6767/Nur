import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
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

# ================= BANKS =================
# Сюда в параметры "link" вставь свои настоящие ссылки на оплату для каждого банка!
BANKS = {
    "dc": {"name": "Диси Кошелёк", "icon": "💳", "number": "+992927755444", "link": "https://dc.tj"},
    "tinkoff": {"name": "Тинькофф Банк", "icon": "💳", "number": "4342 0000 0000 0000", "link": "https://tinkoff.ru"},
    "sber": {"name": "Сбербанк", "icon": "💳", "number": "2202 0000 0000 0000", "link": "https://sberbank.ru"},
    "sbp": {"name": "СБП (Перевод по телефону)", "icon": "💳", "number": "+79991234567", "link": "https://nspk.ru"}
}

# ================= STANDOFF 2 PRICES =================
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

# Таблица цен
SO_TABLE_MENU = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🧈 300G — 30смн / 250₽", callback_data="so_300"),
        InlineKeyboardButton("🧈 2700G — 270смн / 2250₽", callback_data="so_2700")
    ],
    [
        InlineKeyboardButton("🧈 500G — 50смн / 420₽", callback_data="so_500"),
        InlineKeyboardButton("🧈 2900G — 290смн / 2420₽", callback_data="so_2900")
    ],
    [
        InlineKeyboardButton("🧈 700G — 70смн / 580₽", callback_data="so_700"),
        InlineKeyboardButton("🧈 3100G — 310смн / 2580₽", callback_data="so_3100")
    ],
    [
        InlineKeyboardButton("🧈 900G — 90смн / 750₽", callback_data="so_900"),
        InlineKeyboardButton("🧈 3300G — 330смн / 2750₽", callback_data="so_3300")
    ],
    [
        InlineKeyboardButton("🧈 1100G — 110смн / 920₽", callback_data="so_1100"),
        InlineKeyboardButton("🧈 3500G — 350смн / 2920₽", callback_data="so_3500")
    ],
    [
        InlineKeyboardButton("🧈 1300G — 130смн / 1080₽", callback_data="so_1300"),
        InlineKeyboardButton("🧈 3700G — 370смн / 3080₽", callback_data="so_3700")
    ],
    [
        InlineKeyboardButton("🧈 1500G — 150смн / 1250₽", callback_data="so_1500"),
        InlineKeyboardButton("🧈 3900G — 390смн / 3250₽", callback_data="so_3900")
    ],
    [
        InlineKeyboardButton("🧈 1700G — 170смн / 1420₽", callback_data="so_1700"),
        InlineKeyboardButton("🧈 4100G — 410смн / 3420₽", callback_data="so_4100")
    ],
    [
        InlineKeyboardButton("🧈 1900G — 190смн / 1580₽", callback_data="so_1900"),
        InlineKeyboardButton("🧈 4300G — 430смн / 3580₽", callback_data="so_4300")
    ],
    [
        InlineKeyboardButton("🧈 2100G — 210смн / 1750₽", callback_data="so_2100"),
        InlineKeyboardButton("🧈 4500G — 450смн / 3750₽", callback_data="so_4500")
    ],
    [
        InlineKeyboardButton("🧈 2300G — 230смн / 1920₽", callback_data="so_2300"),
        InlineKeyboardButton("🧈 4700G — 470смн / 3920₽", callback_data="so_4700")
    ],
    [
        InlineKeyboardButton("🧈 2500G — 250смн / 2080₽", callback_data="so_2500"),
        InlineKeyboardButton("🧈 4900G — 490смн / 4080₽", callback_data="so_4900")
    ],
    [
        InlineKeyboardButton("🧈 5000G — 500смн / 4170₽", callback_data="so_5000")
    ]
])

def inline_back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu")]])

def bank_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Диси Кошелёк", callback_data="bank_dc")],
        [InlineKeyboardButton("💳 Тинькофф", callback_data="bank_tinkoff")],
        [InlineKeyboardButton("💳 Сбербанк", callback_data="bank_sber")],
        [InlineKeyboardButton("💳 СБП", callback_data="bank_sbp")],
        [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu")]
    ])

def currency_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇹🇯 Сомони (TJS)", callback_data="curr_tjs")],
        [InlineKeyboardButton("🇷🇺 Рубли (RUB)", callback_data="curr_rub")],
        [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu")]
    ])

# ================= STATES =================
CHOOSE_PRODUCT, ENTER_TG, ENTER_ID, CHOOSE_BANK, CHOOSE_CURRENCY, WAIT_CHECK = range(6)
# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👑 Добро пожаловать! Выберите количество Gold из прайс-листа:", reply_markup=SO_TABLE_MENU)
    return CHOOSE_PRODUCT

async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.message.edit_text("👑 Выберите количество Gold из прайс-листа:", reply_markup=SO_TABLE_MENU)
    return CHOOSE_PRODUCT

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

    await query.message.edit_text(
        "👤 Введите ваш ник в Telegram (Обязательно с символом @ в начале, например: @mick):",
        reply_markup=inline_back_menu()
    )
    return ENTER_TG

async def enter_tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if not text.startswith("@") or len(text) < 2:
        await update.message.reply_text(
            "❌ Неверный Telegram ник!\n"
            "Пожалуйста, отправьте ваш никнейм правильно, начиная с символа @ (например: @mick):",
            reply_markup=inline_back_menu()
        )
        return ENTER_TG

    context.user_data["nick"] = text
    await update.message.reply_text("🆔 Введите ваш игровой ID Standoff 2 (минимум 7 цифр):", reply_markup=inline_back_menu())
    return ENTER_ID

async def enter_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if not text.isdigit() or len(text) < 7:
        await update.message.reply_text(
            "❌ Неверный ID!\n"
            "Игровой ID должен состоять только из цифр и содержать не менее 7 знаков.\n"
            "Пожалуйста, введите ваш ID заново:",
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
        
    context.user_data["bank_name"] = bank["name"]
    context.user_data["bank_icon"] = bank["icon"]
    context.user_data["bank_number"] = bank["number"]
    context.user_data["bank_link"] = bank["link"]  # Запоминаем ссылку конкретного банка

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

    # Подставляем индивидуальную ссылку выбранного банка (или базовую, если пустая)
    pay_url = context.user_data.get("bank_link", "https://nspk.ru")

    pay_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Перейти к оплате 💳", url=pay_url)],
        [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu")]
    ])

    await query.message.edit_text(
        f"{context.user_data['bank_icon']} *Банк:* {context.user_data['bank_name']}\n"
        f"📞 *Реквизиты:* `{context.user_data['bank_number']}`\n\n"
        f"📦 *Товар:* {context.user_data['product']}\n"
        f"💰 *Сумма к оплате:* *{amount}*\n\n"
        "Пожалуйста, нажмите на кнопку ниже для быстрой оплаты или переведите сумму по реквизитам вручную. "
        "После перевода отправьте скриншот/фото чека прямо сюда:",
        parse_mode="Markdown",
        reply_markup=pay_keyboard
    )
    return WAIT_CHECK

async def get_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ Пожалуйста, отправьте фото или скриншот чека.", reply_markup=inline_back_menu())
        return WAIT_CHECK

    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"📌 Новый заказ [STANDOFF 2]:\n"
                f"🎮 Игра: STANDOFF 2\n"
                f"👤 Ник в TG: {context.user_data.get('nick','')}\n"
                f"🆔 Игровой ID: {context.user_data.get('game_id','')}\n"
                f"💳 Банк оплаты: {context.user_data.get('bank_name','')}\n"
                f"💰 Товар: {context.user_data.get('product','')} — {context.user_data.get('final_amount','?')}"
    )
    
    await update.message.reply_text("✅ Оплата отправлена на проверку! Администратор скоро свяжется с вами.")
    context.user_data.clear()
    return ConversationHandler.END

# ================= RUN =================
def main():
    if not TOKEN:
        print("Ошибка: Переменная TOKEN не задана!")
        return

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_PRODUCT: [CallbackQueryHandler(product_choice, pattern="^so_")],
            ENTER_TG: [
                CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_tg)
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
                MessageHandler(filters.PHOTO, get_check)
            ],
        },
        fallbacks=[],
    )

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(conv_handler)
    print("🚀 Бот Standoff 2 обновлен и запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()

