from django.core.management.base import BaseCommand
# from .models import DemoBotLog
from  auxobot.models import DemoBotLog

class Command(BaseCommand):
    help = 'Delete all DemoBotLog entries'

    def handle(self, *args, **options):
        count = DemoBotLog.objects.count()
        DemoBotLog.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} demo bot logs')
        )