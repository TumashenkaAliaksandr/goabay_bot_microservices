import os
import sys
import subprocess

# Получаем базовую директорию проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Указываем пути к файлам бота и воркера
BOT_PATH = os.path.join(BASE_DIR, '../bot.py')  # Путь к bot.py
WORKER_PATH = os.path.join(BASE_DIR, '../worker.py')  # Путь к worker.py

try:
    # Проверка существования файлов
    if not os.path.exists(BOT_PATH):
        print(f"Файл не найден: {BOT_PATH}")
        sys.exit(1)

    if not os.path.exists(WORKER_PATH):
        print(f"Файл не найден: {WORKER_PATH}")
        sys.exit(1)

    # Запускаем процессы бота и воркера
    bot_process = subprocess.Popen(['python', BOT_PATH])
    worker_process = subprocess.Popen(['python', WORKER_PATH])

    if __name__ == '__main__':
        print("Бот и воркер запущены")
        # Ожидаем завершения процессов (по желанию)
        bot_process.wait()
        worker_process.wait()

except FileNotFoundError as e:
    print(f"Ошибка: {e}")
except Exception as e:
    print(f"Произошла ошибка: {e}")
finally:
    sys.exit(0)
