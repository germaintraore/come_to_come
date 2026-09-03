from django.core.management.base import BaseCommand
from accounts.models import Apprenant


class Command(BaseCommand):
    help = "Cree ou met a jour le compte administrateur par defaut"

    def add_arguments(self, parser):
        parser.add_argument(
            '--whatsapp',
            type=str,
            default='70445566',
            help="Numero WhatsApp de l'administrateur (par defaut: 70445566)"
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Admin12345',
            help="Mot de passe de l'administrateur (par defaut: Admin12345)"
        )

    def handle(self, *args, **options):
        whatsapp = options['whatsapp']
        password = options['password']

        admin, created = Apprenant.objects.get_or_create(
            whatsapp=whatsapp,
            defaults={
                'nom': 'Admin',
                'prenom': 'Administrateur',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'formation': 'initiation',
                'session': 'janvier',
            }
        )

        admin.set_password(password)
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"[OK] Administrateur cree avec succes ! (WhatsApp: {whatsapp})"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"[OK] Administrateur existant mis a jour avec succes ! (WhatsApp: {whatsapp})"
                )
            )
