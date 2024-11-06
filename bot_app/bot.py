import os
import django
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from telegram.ext import CallbackQueryHandler
from django.conf import settings
from telegram import Update

# Настройка окружения и Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goabay_bot.settings')
django.setup()

# Импортируйте ваши обработчики после настройки Django
from bot_app.templates.webapp.buttons.button_handler import button_handler
from bot_app.templates.webapp.microns.commands import start, help
from bot_app.templates.webapp.microns.echo import echo
from bot_app.templates.profile_date import profile_button_handler
from bot_app.templates.registrations_store import store_registration_handler

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Функция для обработки ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логирует ошибки и отправляет сообщение разработчику."""
    logger.error(f"Произошла ошибка: {context.error}")
    await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")


# Основная функция для запуска бота
def main() -> None:
    application = Application.builder().token(settings.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))

    # ConversationHandler для регистрации в магазине
    store_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & filters.Regex("^(Личный кабинет 👤)$"), store_registration_handler),
            MessageHandler(filters.TEXT & filters.Regex("^(✏️ Редактировать данные)$"), store_registration_handler)
        ],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
        },
        fallbacks=[],
    )

    application.add_handler(store_conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("👳‍♂️ Мои данные"), profile_button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Регистрация обработчика ошибок
    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
