from django.core.management.base import BaseCommand
from auxobotapps.auxobot.core.trading.live_trading_bot import _run_live_bot
from auxobotapps.auxobot.models import BotConfig

class Command(BaseCommand):
    help = 'Runs a single live trading bot for an active user'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='User ID to run the bot for')

    def handle(self, *args, **options):
        user_id = options['user_id']

        try:
            config = BotConfig.objects.get(user_id=user_id, is_active=True)
        except BotConfig.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No active Live bot config for user ID {user_id}"))
            return

        username = config.user.username
        config_data = {
            'instrument': config.instrument,
            'custom_quantity': str(config.custom_quantity) if config.custom_quantity else None,
            'api_key': config.api_key or '',
            'api_secret': config.api_secret or '',
        }

        self.stdout.write(self.style.SUCCESS(f"Starting live bot for user {username} (ID: {user_id})"))
        _run_live_bot(user_id, username, config_data)