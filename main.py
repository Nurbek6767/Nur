import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Настройка логирования для отслеживания работы бота в Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = -1003660151590

# ==================== BANKS ====================
# Алиф и Эсхата удалены. Оставлены только нужные вам банки:
BANKS = {
    "dc": {"name": "DC Wallet", "icon": "💳", "number": "+992927755444"},
    "tinkoff": {"name": "Тинькофф", "icon": "💛", "number": "4342 0000 0000 0000"},  # Укажите ваш номер карты
    "sber": {"name": "Сбербанк", "icon": "💚", "number": "2202 0000 0000 0000"},    # Укажите ваш номер карты
    "sbp": {"name": "СБП (Система быстрых платежей)", "icon": "📲", "number": "+79991234567"} # Укажите ваш СБП
}

# ==================== STANDOFF 2 PRICES ====================
SO_PRICES = {
    "so_300": {"name": "300 Gold", "rub": 250, "tjs": 30},
    "so_500": {"name": "500 Gold", "rub": 420, "tjs": 50},
    "so_700": {"name": "700 Gold", "rub": 580, "tjs": 70},
    "so_1000": {"name": "1000 Gold", "rub": 750, "tjs": 90}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовая команда бота /start"""
    keyboard = [
        [InlineKeyboardButton("Купить Gold ✨", callback_data="buy_gold")],
        [InlineKeyboardButton("Наши реквизиты 🏦", callback_data="show_banks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Я бот для покупки Gold в Standoff 2. Выберите действие:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на инлайн-кнопки меню"""
    query = update.callback_query
    await query.answer()

    if query.data == "buy_gold":
        keyboard = []
        for key, item in SO_PRICES.items():
            keyboard.append([InlineKeyboardButton(f"{item['name']} — {item['rub']}₽ / {item['tjs']}сн.", callback_data=f"item_{key}")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_start")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите необходимое количество Gold:", reply_markup=reply_markup)

    elif query.data == "show_banks":
        text = "🎯 Наши актуальные реквизиты для оплаты:\n\n"
        for key, bank in BANKS.items():
            text += f"{bank['icon']} *{bank['name']}:* `{bank['number']}`\n"
        text += "\nПосле оплаты перешлите скриншот чека администратору."
        
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "back_to_start":
        keyboard = [
            [InlineKeyboardButton("Купить Gold ✨", callback_data="buy_gold")],
            [InlineKeyboardButton("Наши реквизиты 🏦", callback_data="show_banks")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите действие:", reply_markup=reply_markup)

    elif query.data.startswith("item_"):
        item_key = query.data.replace("item_", "")
        context.user_data["selected_item"] = item_key
        
        # Запрашиваем у пользователя номер телефона кнопкой
        phone_button = [[KeyboardButton("Поделиться номером телефона 📱", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(phone_button, resize_keyboard=True, one_time_keyboard=True)
        
        await query.message.reply_text(
            "⚠️ Для оформления заказа нам необходим ваш номер телефона. Нажмите на кнопку ниже:",
            reply_markup=reply_markup
        )

async def save_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение контакта и вывод сообщения с кнопкой перехода к оплате"""
    user_phone = update.message.contact.phone_number
    item_key = context.user_data.get("selected_item", "so_300")
    item = SO_PRICES.get(item_key)

    # Вывод лога в консоль Railway, чтобы вы видели, кто и какой номер оставил
    logging.info(f"Пользователь {update.message.from_user.username} оставил телефон: {user_phone}")

    # Ссылка для кнопки оплаты (например, на СБП или вашу платежную страницу)
    pay_url = "https://nspk.ru" 

    text = (
        f"✅ Номер телефона получен: `{user_phone}`\n\n"
        f"🛒 Ваш заказ: *{item['name']}*\n"
        f"💵 К оплате: {item['rub']} RUB / {item['tjs']} TJS\n\n"
        f"Нажмите кнопку ниже для быстрой оплаты в приложении или отправьте перевод по номерам из раздела 'Наши реквизиты'."
    )

    keyboard = [
        [InlineKeyboardButton("Перейти к оплате 💳", url=pay_url)],
        [InlineKeyboardButton("Главное меню 🏠", callback_data="back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

def main():
    """Запуск приложения бота"""
    if not TOKEN:
        print("Ошибка: Переменная окружения TOKEN не задана на хостинге!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.CONTACT, save_contact))

    print("Бот успешно запущен в облаке!")
    application.run_polling()

if __name__ == "__main__":
    main()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(conv_handler)
    print("🚀 Бот Standoff 2 обновлен и запущен!")
    app.run_polling()
