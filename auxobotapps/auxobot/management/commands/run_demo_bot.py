from django.core.management.base import BaseCommand
from auxobotapps.auxobot.demo_trading import _run_demo_bot
from auxobotapps.auxobot.models import DemoBotConfig

class Command(BaseCommand):
    help = 'Runs a single demo trading bot for an active user'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='User ID to run the bot for')

    def handle(self, *args, **options):
        user_id = options['user_id']

        try:
            config = DemoBotConfig.objects.get(user_id=user_id, is_active=True)
        except DemoBotConfig.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No active demo bot config for user ID {user_id}"))
            return

        username = config.user.username
        config_data = {
            'instrument': config.instrument,
            'custom_quantity': str(config.custom_quantity) if config.custom_quantity else None,
            'demo_api_key': config.demo_api_key or '',
            'demo_api_secret': config.demo_api_secret or '',
        }

        self.stdout.write(self.style.SUCCESS(f"Starting demo bot for user {username} (ID: {user_id})"))
        _run_demo_bot(user_id, username, config_data)