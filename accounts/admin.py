from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Apprenant


@admin.register(Apprenant)
class ApprenantAdmin(UserAdmin):
    list_display = ('nom_complet', 'whatsapp', 'formation', 'session', 'date_inscription', 'is_active')
    list_filter = ('formation', 'session', 'is_active', 'is_staff', 'date_inscription')
    search_fields = ('nom', 'prenom', 'whatsapp')
    ordering = ('-date_inscription',)

    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'whatsapp', 'password')
        }),
        ('Formation', {
            'fields': ('formation', 'session'),
        }),
        ('Statut', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Dates', {
            'fields': ('date_inscription', 'last_login')
        }),
    )

    add_fieldsets = (
        ('Nouvel apprenant', {
            'classes': ('wide',),
            'fields': ('nom', 'prenom', 'whatsapp', 'formation', 'session', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('date_inscription', 'last_login')
