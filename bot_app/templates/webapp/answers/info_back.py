import asyncio
import logging
from datetime import datetime

# Глобальный список для хранения сообщений, которые нужно удалить
messages_to_delete = []

# Время, через которое сообщение считается старым (например, 5 секунд)
MESSAGE_LIFETIME = 5


async def track_and_delete_old_messages(context):
    """
    Проверяет все сообщения в списке и удаляет те, которые устарели.

    :param context: Контекст бота
    """
    while True:
        try:
            current_time = datetime.now()

            # Проходим по всем сообщениям в списке
            for chat_id, message_id, timestamp in list(messages_to_delete):
                # Проверяем, не прошло ли больше времени, чем указано в MESSAGE_LIFETIME
                if (current_time - timestamp).seconds > MESSAGE_LIFETIME:
                    # Удаляем сообщение, если оно устарело
                    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

                    # Убираем сообщение из списка
                    messages_to_delete.remove((chat_id, message_id, timestamp))

            # Задержка между проверками (например, 1 секунду)
            await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"Ошибка при проверке сообщений на удаление: {e}")


async def send_and_track_message(context, chat_id, message_text):
    """
    Отправляет сообщение, добавляет его в список для удаления и удаляет через указанное время.

    :param context: Контекст бота
    :param chat_id: ID чата, где отправлено сообщение
    :param message_text: Текст отправленного сообщения
    """
    try:
        # Отправляем сообщение
        sent_message = await context.bot.send_message(chat_id=chat_id, text=message_text)

        # Добавляем сообщение в список с временной меткой
        messages_to_delete.append((chat_id, sent_message.message_id, datetime.now()))

        # Запускаем процесс удаления старых сообщений
        await track_and_delete_old_messages(context)

    except Exception as e:
        logging.error(f"Ошибка при отправке и отслеживании сообщения: {e}")
