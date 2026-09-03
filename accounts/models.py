from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class ApprenantManager(BaseUserManager):
    """Gestionnaire personnalisé pour le modèle Apprenant."""

    def create_user(self, whatsapp, password=None, **extra_fields):
        if not whatsapp:
            raise ValueError("Le numéro WhatsApp est obligatoire.")
        apprenant = self.model(whatsapp=whatsapp, **extra_fields)
        apprenant.set_password(password)
        apprenant.save(using=self._db)
        return apprenant

    def create_superuser(self, whatsapp, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('nom', 'Admin')
        extra_fields.setdefault('prenom', 'Super')
        return self.create_user(whatsapp, password, **extra_fields)


class Apprenant(AbstractBaseUser, PermissionsMixin):
    """
    Modèle principal représentant un apprenant de la plateforme.
    L'authentification se fait via le numéro WhatsApp.
    """

    FORMATION_CHOICES = [
        ('bureautique', 'Formation en bureautique'),
        ('maintenance', 'Formation en maintenance'),
        ('reseau', 'Formation en réseau'),
        ('initiation', 'Initiation en informatique'),
    ]

    SESSION_MOIS_CHOICES = [
        ('janvier', 'Janvier'),
        ('fevrier', 'Février'),
        ('mars', 'Mars'),
        ('avril', 'Avril'),
        ('mai', 'Mai'),
        ('juin', 'Juin'),
        ('juillet', 'Juillet'),
        ('aout', 'Août'),
        ('septembre', 'Septembre'),
        ('octobre', 'Octobre'),
        ('novembre', 'Novembre'),
        ('decembre', 'Décembre'),
    ]

    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    whatsapp = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Numéro WhatsApp",
        help_text="Ex: +22670000000"
    )
    formation = models.CharField(
        max_length=50,
        choices=FORMATION_CHOICES,
        verbose_name="Type de formation",
        default='initiation',
    )
    session = models.CharField(
        max_length=20,
        choices=SESSION_MOIS_CHOICES,
        verbose_name="Session (mois)",
        default='janvier',
    )
    date_inscription = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date d'inscription"
    )
    is_active = models.BooleanField(default=True, verbose_name="Compte actif")
    is_staff = models.BooleanField(default=False, verbose_name="Membre du staff")

    objects = ApprenantManager()

    USERNAME_FIELD = 'whatsapp'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'apprenant'
        verbose_name = 'Apprenant'
        verbose_name_plural = 'Apprenants'
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.whatsapp})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
