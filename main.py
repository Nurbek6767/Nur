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

# Настройка логирования для Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = -1003660151590

# ==================== STANDOFF 2 PRICES (СТРОГО ПО ПРАЙСУ) ====================
SO_PRICES = {
    "so_300": {"name": "G 300", "rub": 250, "tjs": 30},
    "so_500": {"name": "G 500", "rub": 420, "tjs": 50},
    "so_700": {"name": "G 700", "rub": 580, "tjs": 70},
    "so_900": {"name": "G 900", "rub": 750, "tjs": 90},
    "so_1100": {"name": "G 1100", "rub": 920, "tjs": 110},
    "so_1300": {"name": "G 1300", "rub": 1080, "tjs": 130},
    "so_1500": {"name": "G 1500", "rub": 1250, "tjs": 150},
    "so_1700": {"name": "G 1700", "rub": 1420, "tjs": 170},
    "so_1900": {"name": "G 1900", "rub": 1580, "tjs": 190},
    "so_2100": {"name": "G 2100", "rub": 1750, "tjs": 210},
    "so_2300": {"name": "G 2300", "rub": 1920, "tjs": 230},
    "so_2500": {"name": "G 2500", "rub": 2080, "tjs": 250},
    "so_2700": {"name": "G 2700", "rub": 2250, "tjs": 270},
    "so_2900": {"name": "G 2900", "rub": 2420, "tjs": 290},
    "so_3100": {"name": "G 3100", "rub": 2580, "tjs": 310},
    "so_3300": {"name": "G 3300", "rub": 2750, "tjs": 330},
    "so_3500": {"name": "G 3500", "rub": 2920, "tjs": 350},
    "so_3700": {"name": "G 3700", "rub": 3080, "tjs": 370},
    "so_3900": {"name": "G 3900", "rub": 3250, "tjs": 390},
    "so_4100": {"name": "G 4100", "rub": 3420, "tjs": 410},
    "so_4300": {"name": "G 4300", "rub": 3580, "tjs": 430},
    "so_4500": {"name": "G 4500", "rub": 3750, "tjs": 450},
    "so_4700": {"name": "G 4700", "rub": 3920, "tjs": 470},
    "so_4900": {"name": "G 4900", "rub": 4080, "tjs": 490},
    "so_5000": {"name": "G 5000", "rub": 4170, "tjs": 500}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовая команда /start"""
    # Оставляем только кнопку покупки
    keyboard = [[InlineKeyboardButton("Купить Gold ✨", callback_data="buy_gold")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Я официальный бот MEWIK для покупки Gold в Standoff 2. Нажмите кнопку ниже, чтобы открыть прайс:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()

    if query.data == "buy_gold" or query.data == "back_to_gold":
        keyboard = []
        # Генерируем кнопки товаров строго по сетке цен
        for key, item in SO_PRICES.items():
            keyboard.append([InlineKeyboardButton(f"{item['name']} — {item['rub']}₽ / {item['tjs']} сомони", callback_data=f"item_{key}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🔥 Актуальный прайс на GOLD. Выберите нужный пак:", reply_markup=reply_markup)

    elif query.data.startswith("item_"):
        item_key = query.data.replace("item_", "")
        context.user_data["selected_item"] = item_key
        
        # Запрашиваем контакт для связи перед выдачей ссылки оплаты
        phone_button = [[KeyboardButton("Поделиться номером телефона 📱", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(phone_button, resize_keyboard=True, one_time_keyboard=True)
        
        await query.message.reply_text(
            "⚠️ Для оформления заказа и верификации платежа нам необходим ваш номер телефона. Нажмите на кнопку ниже:",
            reply_markup=reply_markup
        )

async def save_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение номера телефона и вывод кнопки перенаправления к оплате"""
    user_phone = update.message.contact.phone_number
    item_key = context.user_data.get("selected_item", "so_300")
    item = SO_PRICES.get(item_key)

    # Логируем данные покупателя для вашей безопасности
    logging.info(f"Покупатель {update.message.from_user.username} оставил телефон: {user_phone}")

    # Ваша ссылка для перенаправления в приложение СБП / Банка
    # Замените на свою реальную ссылку, когда она понадобится
    pay_url = "https://nspk.ru" 

    text = (
        f"✅ Ваш номер телефона успешно привязан к заказу: `{user_phone}`\n\n"
        f"🛒 Выбранный товар: *{item['name']}*\n"
        f"💵 Сумма к оплате: *{item['rub']} RUB* или *{item['tjs']} сомони*\n\n"
        f"Нажмите кнопку ниже, чтобы открыть приложение банка и совершить быструю оплату."
    )

    keyboard = [
        [InlineKeyboardButton("Перейти к оплате 💳", url=pay_url)],
        [InlineKeyboardButton("⬅️ Вернуться к прайсу", callback_data="back_to_gold")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

def main():
    """Запуск бота"""
    if not TOKEN:
        print("Ошибка: Переменная TOKEN не найдена!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.CONTACT, save_contact))

    print("Бот MEWIK успешно обновлен и работает!")
    application.run_polling()

if __name__ == "__main__":
    main()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(conv_handler)
    print("🚀 Бот Standoff 2 обновлен и запущен!")
    app.run_polling()
