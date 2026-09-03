from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Devoir, Question, Soumission, ReponseApprenant


class QuestionInline(admin.TabularInline):
    """Permet d'ajouter les questions directement depuis la page du devoir."""
    model = Question
    extra = 5  # Affiche 5 lignes vides pour ajouter des questions
    fields = ['ordre', 'texte', 'choix_a', 'choix_b', 'choix_c', 'choix_d', 'bonne_reponse', 'justification']


@admin.register(Devoir)
class DevoirAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display  = ['titre', 'formation', 'session', 'total_questions', 'est_actif', 'date_creation']
    list_filter   = ['formation', 'est_actif','session']
    list_editable = ['est_actif','session']
    search_fields = ['titre','session','formation']
    date_hierarchy = 'date_creation'


class ReponseApprenantInline(admin.TabularInline):
    """Permet de voir les réponses d'une soumission."""
    model = ReponseApprenant
    extra = 0
    readonly_fields = ['question', 'reponse_choisie', 'est_correcte']
    can_delete = False


@admin.register(Soumission)
class SoumissionAdmin(admin.ModelAdmin):
    inlines       = [ReponseApprenantInline]
    list_display  = ['apprenant', 'devoir', 'note', 'date_soumission']
    list_filter   = ['devoir', 'date_soumission']
    search_fields = ['apprenant__nom', 'apprenant__prenom']
    readonly_fields = ['apprenant', 'devoir', 'note', 'date_soumission']
