from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Словарь для хранения данных пользователей
user_data = {}


# Функция для старта бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я бот для регистрации. Напишите /register, чтобы начать.')


# Функция для регистрации пользователя
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_data:
        await update.message.reply_text('Вы уже зарегистрированы!')
    else:
        await update.message.reply_text('Пожалуйста, введите ваше имя:')
        context.user_data['registering'] = True
        context.user_data['step'] = 1  # Установка первого этапа регистрации


# Функция для обработки текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if context.user_data.get('registering'):
        step = context.user_data.get('step')

        if step == 1:  # Запрос имени
            user_name = update.message.text
            user_data[user_id] = {'name': user_name}
            await update.message.reply_text('Спасибо! Теперь введите ваш email:')
            context.user_data['step'] = 2  # Переход ко второму этапу

        elif step == 2:  # Запрос email
            user_email = update.message.text
            user_data[user_id]['email'] = user_email
            await update.message.reply_text('Отлично! Теперь введите ваш телефонный номер:')
            context.user_data['step'] = 3  # Переход к третьему этапу

        elif step == 3:  # Запрос телефона
            user_phone = update.message.text
            user_data[user_id]['phone'] = user_phone
            await update.message.reply_text(f'Спасибо за регистрацию, {user_data[user_id]["name"]}! '
                                            f'Ваш email: {user_email}, телефон: {user_phone}.')
            context.user_data['registering'] = False  # Завершение регистрации
            context.user_data['step'] = None  # Сброс этапа


def main() -> None:
    # Замените 'YOUR_TOKEN' на токен вашего бота
    application = Application.builder().token("YOUR_TOKEN").build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
