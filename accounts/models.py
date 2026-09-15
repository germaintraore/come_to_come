from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone



class Formation(models.Model):
    """Représente une formation gérée dynamiquement par l'administrateur."""
    
    code = models.SlugField(
        max_length=50, 
        unique=True, 
        verbose_name="Code / Identifiant (ex: dev-web, bureautique)",
        help_text="Identifiant unique sans espaces ni caractères spéciaux"
    )
    nom = models.CharField(
        max_length=150, 
        verbose_name="Nom complet de la formation"
    )
    description = models.TextField(
        blank=True, 
        verbose_name="Description de la formation"
    )
    est_active = models.BooleanField(
        default=True, 
        verbose_name="Formation active (visible aux inscriptions)"
    )
    date_creation = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création"
    )

    class Meta:
        db_table = 'formation'
        verbose_name = 'Formation'
        verbose_name_plural = 'Formations'
        ordering = ['nom']

    def __str__(self):
        return self.nom

    @classmethod
    def get_choices(cls, only_active=True):
        """Retourne la liste des tuples (code, nom) pour les formulaires Django."""
        qs = cls.objects.filter(est_active=True) if only_active else cls.objects.all()
        choices = [(f.code, f.nom) for f in qs]
        # Si la table est encore vide, on donne une valeur de secours
        return choices if choices else [('initiation', 'Initiation en informatique')]

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
    
    is_formateur = models.BooleanField(default=False, verbose_name="Membreee= des formateurs")
    formation_assignee=models.ForeignKey(Formation,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="formateurs",
    verbose_name="Formation assignée"
    )


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
    
    def get_formation_display(self):
        formation_obj = Formation.objects.filter(code=self.formation).first()
        return formation_obj.nom if formation_obj else self.formation


    
