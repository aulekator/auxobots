from django.core.management.base import BaseCommand
from auxobotapps.auxobot.models import DemoBotConfig
from auxobotapps.auxobot.core.trading.demo_trading import _run_demo_bot
import multiprocessing
import time
import os

class Command(BaseCommand):
    help = 'Runs demo trading bots for all active users (main systemd entry point)'

    def handle(self, *args, **options):
        self.stdout.write("Auxobot Demo Bot Runner started — monitoring active users...")

        processes = {}

        while True:
            try:
                active_configs = DemoBotConfig.objects.filter(is_active=True)

                active_user_ids = set(config.user_id for config in active_configs)

                # Start new bots with ENVIRONMENT ISOLATION
                for config in active_configs:
                    user_id = config.user_id
                    if user_id not in processes or not processes[user_id].is_alive():
                        config_data = {
                            'instrument': config.instrument,
                            'custom_quantity': str(config.custom_quantity) if config.custom_quantity else None,
                            'demo_api_key': config.demo_api_key or '',
                            'demo_api_secret': config.demo_api_secret or '',
                        }
                        
                        # Create isolated environment for each process
                        env = os.environ.copy()
                        env['USER_SESSION_ID'] = str(user_id)  # Pass user ID as env variable
                        
                        p = multiprocessing.Process(
                            target=_run_demo_bot,
                            args=(user_id, config.user.username, config_data),
                            daemon=True
                        )
                        p.start()
                        processes[user_id] = p
                        self.stdout.write(self.style.SUCCESS(f"Started bot for user {config.user.username} (ID: {user_id})"))

                # Stop removed bots
                for user_id in list(processes.keys()):
                    if user_id not in active_user_ids:
                        p = processes[user_id]
                        if p.is_alive():
                            p.terminate()
                            p.join(timeout=10)
                            if p.is_alive():
                                p.kill()
                        del processes[user_id]
                        self.stdout.write(self.style.WARNING(f"Stopped bot for user ID {user_id}"))

                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error in bot runner: {e}"))
                time.sleep(30)  # Wait longer on error