import os
from django.db import models
from accounts.models import Apprenant, Formation


def ressource_upload_path(instance, filename):
    """
    Détermine le chemin de stockage du fichier uploadé.
    Résultat : media/ressources/<formation>/<session>/<filename>
    Ex : media/ressources/dev-web/janvier/cours_python.pdf
    Cela organise les fichiers par formation puis par session,
    évitant les collisions de noms dans le dossier media/.
    """
    return f"ressources/{instance.formation}/{instance.session}/{filename}"


class Devoir(models.Model):
    """Un devoir QCM lié à un type de formation."""

  
        # ...
    def get_formation_display(self):
        f = Formation.objects.filter(code=self.formation).first()
        return f.nom if f else self.formation

    titre       = models.CharField(max_length=200, verbose_name="Titre du devoir")
    
    formation = models.CharField(
        max_length=50,
        verbose_name="Formation concernée",
        default='initiation'
    )
    session = models.CharField(max_length=20,choices=Apprenant.SESSION_MOIS_CHOICES,
                default='janvier',verbose_name="Session du devoir")
    description = models.TextField(blank=True, verbose_name="Description / consignes")
    est_actif   = models.BooleanField(default=True, verbose_name="Devoir actif")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Devoir"
        verbose_name_plural = "Devoirs"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.titre} ({self.get_formation_display()})"

    def total_questions(self):
        return self.questions.count()


class Question(models.Model):
    """Une question QCM appartenant à un devoir."""

    CHOIX = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]

    devoir        = models.ForeignKey(Devoir, on_delete=models.CASCADE, related_name='questions')
    texte         = models.TextField(verbose_name="Texte de la question")
    choix_a       = models.CharField(max_length=300, verbose_name="Choix A")
    choix_b       = models.CharField(max_length=300, verbose_name="Choix B")
    choix_c       = models.CharField(max_length=300, verbose_name="Choix C")
    choix_d       = models.CharField(max_length=300, verbose_name="Choix D")
    bonne_reponse = models.CharField(max_length=1, choices=CHOIX, verbose_name="Bonne réponse")
    justification = models.TextField(verbose_name="Justification (pour la correction)")
    ordre         = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ['ordre']
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return f"Q{self.ordre} — {self.texte[:60]}"

    def get_choix_texte(self, lettre):
        """Retourne le texte du choix selon la lettre (A, B, C ou D)."""
        mapping = {
            'A': self.choix_a,
            'B': self.choix_b,
            'C': self.choix_c,
            'D': self.choix_d,
        }
        return mapping.get(lettre, '')


class Soumission(models.Model):
    """Résultat d'un apprenant pour un devoir (1 seule tentative)."""

    apprenant       = models.ForeignKey(Apprenant, on_delete=models.CASCADE, related_name='soumissions')
    devoir          = models.ForeignKey(Devoir, on_delete=models.CASCADE, related_name='soumissions')
    note            = models.PositiveBigIntegerField(verbose_name="Note obtenue")
    date_soumission = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('apprenant', 'devoir')  # 1 seule tentative par devoir
        verbose_name = "Soumission"
        verbose_name_plural = "Soumissions"
        ordering = ['-date_soumission']

    def __str__(self):
        return f"{self.apprenant.nom_complet} — {self.devoir.titre} — {self.note}/{self.devoir.total_questions()}"


class ReponseApprenant(models.Model):
    """La réponse donnée par l'apprenant pour chaque question."""

    soumission      = models.ForeignKey(Soumission, on_delete=models.CASCADE, related_name='reponses')
    question        = models.ForeignKey(Question, on_delete=models.CASCADE)
    reponse_choisie = models.CharField(max_length=1)
    est_correcte    = models.BooleanField()

    class Meta:
        verbose_name = "Réponse apprenant"
        verbose_name_plural = "Réponses apprenants"

    def __str__(self):
        statut = "✓" if self.est_correcte else "✗"
        return f"{statut} Q{self.question.ordre} → {self.reponse_choisie}"


class RessourcePedagogique(models.Model):
    """
    Ressource pédagogique (PDF ou vidéo) déposée par un formateur
    pour une formation et une session donnée.
    Les apprenants de la même formation/session peuvent la télécharger.
    """

    TYPE_CHOICES = [
        ('pdf', 'Document PDF'),
        ('video', 'Vidéo de cours'),
    ]

    titre = models.CharField(
        max_length=200,
        verbose_name="Titre de la ressource"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description / résumé du cours"
    )
    fichier = models.FileField(
        upload_to=ressource_upload_path,   # Utilise la fonction définie en haut du fichier
        verbose_name="Fichier (PDF ou vidéo)"
    )
    type_fichier = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='pdf',
        verbose_name="Type de ressource"
    )
    formation = models.CharField(
        max_length=50,
        verbose_name="Formation concernée"
    )
    session = models.CharField(
        max_length=20,
        choices=Apprenant.SESSION_MOIS_CHOICES,
        default='janvier',
        verbose_name="Session concernée"
    )
    # Formateur qui a déposé la ressource — SET_NULL si le compte est supprimé
    formateur = models.ForeignKey(
        Apprenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ressources_deposees',
        verbose_name="Formateur dépositaire",
        limit_choices_to={'is_formateur': True}
    )
    date_ajout = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'ajout"
    )
    est_visible = models.BooleanField(
        default=True,
        verbose_name="Visible pour les apprenants"
    )

    class Meta:
        verbose_name = "Ressource pédagogique"
        verbose_name_plural = "Ressources pédagogiques"
        ordering = ['-date_ajout']

    def __str__(self):
        return f"{self.titre} ({self.formation} / {self.session})"

    def taille_lisible(self):
        """Retourne la taille du fichier en format lisible (ex: '4.2 Mo')."""
        try:
            taille = self.fichier.size  # taille en octets
            if taille < 1024:
                return f"{taille} o"
            elif taille < 1024 ** 2:
                return f"{taille / 1024:.1f} Ko"
            else:
                return f"{taille / (1024 ** 2):.1f} Mo"
        except Exception:
            return "Taille inconnue"

    def extension(self):
        """Retourne l'extension du fichier en minuscules (ex: 'pdf', 'mp4')."""
        _, ext = os.path.splitext(self.fichier.name)
        return ext.lower().lstrip('.')
