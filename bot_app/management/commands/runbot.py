import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BOT_DIR = os.path.join(BASE_DIR, 'bot_app', 'bot')

WORKER_DIR = os.path.join(BASE_DIR, 'bot_app', 'worker')

bot_process = subprocess.Popen(['python', os.path.join(BOT_DIR, 'bot.py')])
worker_process = subprocess.Popen(['python', os.path.join(WORKER_DIR, 'worker.py')])

if __name__ == '__main__':
    print("Бот и воркер запущены")
    sys.exit(0)
