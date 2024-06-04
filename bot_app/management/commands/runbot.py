from django.core.management.base import BaseCommand

from bot_app.worker import main


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **kwargs):
        main()
