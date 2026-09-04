from devoirs import views
from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques pour les devoirs
    path('', views.liste_devoirs    , name='liste_devoirs'),
    # On charge les routes des autres apps (auth, contenu, quiz, etc.) à partir de main.
    
    path('<int:pk>/', views.passer_devoir, name='passer_devoir'),
    path('<int:pk>/soumettre/', views.soumettre_devoir, name='soumettre_devoir'),
    path('<int:pk>/resultat/', views.resultat_devoir, name='resultat_devoir'),

    path('creer/',views.creer_devoir,name='creer_devoir'),
    path('<int:pk>/gerer/',views.gerer_devoir,name='gerer_devoir'),
    path('questions/<int:pk>/supprimer/',views.supprimer_question,name='supprimer_question'),
    path('devoirs/<int:pk>/supprimer/',views.supprimer_devoir,name='supprimer_devoir'),

    path('<int:pk>/pdf/',views.telecharger_devoir_pdf,name='telecharger_devoir_pdf'),
    path('<int:pk>/dupliquer/',views.dupliquer_devoir,name='dupliquer_devoir'),
    
    path('questions/<int:pk>/modifier/', views.modifier_question, name='modifier_question'),
    path('devoirs/<int:pk>/modifier/', views.modifier_devoir, name='modifier_devoir'),



]
