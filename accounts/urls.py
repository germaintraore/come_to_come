from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('',               views.accueil,            name='accueil'),
    path('inscription/',   views.inscription,         name='inscription'),
    path('connexion/',     views.connexion,            name='connexion'),
    # Pages apprenant
    path('tableau-de-bord/', views.tableau_de_bord,  name='tableau_de_bord'),
    path('deconnexion/',   views.deconnexion,         name='deconnexion'),
    # Interface administrateur
    path('admin-panel/',         views.admin_dashboard,      name='admin_dashboard'),
    path('admin-panel/export/',  views.export_csv,           name='export_csv'),
    path('admin-panel/export-excel/', views.export_excel,    name='export_excel'),
    path('admin-panel/toggle/<int:pk>/', views.toggle_apprenant, name='toggle_apprenant'),
    path('admin-panel/supprimer/<int:pk>/', views.supprimer_apprenant, name='supprimer_apprenant'),
    path('admin-panel/reaffecter/<int:pk>/', views.reaffecter_apprenant, name='reaffecter_apprenant'),
    path('admin-panel/export-pdf/', views.export_pdf, name='export_pdf'),
    path('admin-panel/diffusion-whatsapp/', views.diffusion_whatsapp, name='diffusion_whatsapp'),

    # Gestion des Formations
    path('admin-panel/formations/', views.liste_formations, name='liste_formations'),
    path('admin-panel/formations/modifier/<int:pk>/', views.modifier_formation, name='modifier_formation'),
    path('admin-panel/formations/toggle/<int:pk>/', views.toggle_formation, name='toggle_formation'),
    path('admin-panel/formations/supprimer/<int:pk>/', views.supprimer_formation, name='supprimer_formation'),



]
