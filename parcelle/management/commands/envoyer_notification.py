from django.core.management.base import BaseCommand
from parcelle.utils import envoyer_notifications_culture

class Command(BaseCommand):
    help = "Envoie les notifications planifiées du jour pour chaque ferme"

    def handle(self, *args, **kwargs):
        envoyer_notifications_culture()
        self.stdout.write(self.style.SUCCESS(" Notifications envoyées avec succès."))
