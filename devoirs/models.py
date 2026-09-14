from django.db import models
from accounts.models import Apprenant,Formation


class Devoir(models.Model):
    """Un devoir QCM lié à un type de formation."""

  
        # ...
    def get_formation_display(self):
        f = Formation.objects.filter(code=self.formation).first()
        return f.nom if f else self.formation

    titre       = models.CharField(max_length=200, verbose_name="Titre du devoir")
    
    formation=models.CharField(max_length=50,
    verbose_name="Formation concernée",
    default='initation en informatique')
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
