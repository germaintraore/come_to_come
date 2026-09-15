from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import Apprenant,Formation


class InscriptionForm(forms.ModelForm):
    """Formulaire d'inscription d'un nouvel apprenant."""

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Créez un mot de passe fort',
            'id': 'id_password1',
        }),
        min_length=8,
        help_text="Minimum 8 caractères."
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Répétez votre mot de passe',
            'id': 'id_password2',
        })
    )

    class Meta:
        model = Apprenant
        fields = ['nom', 'prenom', 'whatsapp', 'formation', 'session']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Votre nom de famille',
                'autofocus': True,
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Votre prénom',
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '+22670000000',
            }),
            'formation': forms.Select(attrs={
                'class': 'form-control form-control-lg',
            }),
            'session': forms.Select(attrs={
                'class': 'form-control form-control-lg',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Charger les formations depuis la base de données 
        """
        super().__init__(*args, **kwargs)

        # --- 1. Récupération des formations actives ---
        # Utilise la méthode de classe ajoutée au modèle pour plus de propreté
        # Si la table est vide, on garde la valeur par défaut 'initiation'
        self.fields['formation'].widget = forms.Select(
            choices=Formation.get_choices(only_active=True),
            attrs={
                'class': 'form-control form-control-lg',
            }
        )

        # Si par défaut le champ est vide, on force l'option par défaut
        if not self.fields['formation'].initial:
             self.fields['formation'].initial = 'initiation'

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return p2

    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get('whatsapp')
        if whatsapp:
            whatsapp = whatsapp.strip()
        if Apprenant.objects.filter(whatsapp=whatsapp).exists():
            raise forms.ValidationError("Ce numéro WhatsApp est déjà enregistré.")
        return whatsapp

    def save(self, commit=True):
        apprenant = super().save(commit=False)
        apprenant.set_password(self.cleaned_data['password1'])
        if commit:
            apprenant.save()
        return apprenant


class ConnexionForm(forms.Form):
    """Formulaire de connexion avec numéro WhatsApp et mot de passe."""

    whatsapp = forms.CharField(
        label="Numéro WhatsApp",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '+22670000000',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Votre mot de passe',
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.apprenant_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        whatsapp = self.cleaned_data.get('whatsapp')
        password = self.cleaned_data.get('password')

        if whatsapp:
            whatsapp = whatsapp.strip()
            self.cleaned_data['whatsapp'] = whatsapp

        if whatsapp and password:
            self.apprenant_cache = authenticate(
                self.request,
                username=whatsapp,
                password=password
            )
            if self.apprenant_cache is None:
                raise forms.ValidationError(
                    "Numéro WhatsApp ou mot de passe incorrect."
                )
            if not self.apprenant_cache.is_active:
                raise forms.ValidationError("Ce compte est désactivé.")
        return self.cleaned_data

    def get_user(self):
        return self.apprenant_cache

# accounts/forms.py

class DiffusionWhatsAppForm(forms.Form):
    """Formulaire de diffusion WhatsApp par session avec pièce jointe (Image/PDF)."""
    
    session = forms.ChoiceField(
        choices=Apprenant.SESSION_MOIS_CHOICES,
        label="Session ciblée",
        widget=forms.Select(attrs={'class': 'form-control form-control-lg'})
    )
    
    formation = forms.ChoiceField(
        required=True,
        label="Type de formation *",
        widget=forms.Select(attrs={'class': 'form-control form-control-lg'})
    )
    
    message = forms.CharField(
        label="Message à envoyer",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': "Bonjour {prenom},\n\nNous vous rappelons que la séance de {formation} aura lieu demain.\n\nCordialement,\n2S Informatique Plus"
        }),
        help_text="Variables disponibles : {prenom}, {nom}, {formation}, {session}."
    )
    
    piece_jointe = forms.FileField(
        required=False,
        label="Pièce jointe (Image ou PDF)",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf, .jpeg, .png'
        }),
        help_text="Formats acceptés : PDF, JPG, PNG (Max 10 Mo)."
    )
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['formation'].choices=[('','Toutes les formations disponibles ')]+ Formation.get_choices(only_active=False)
    
class FormationForm(forms.ModelForm):
    """Formulaire pour créer ou modifier une formation."""
    class Meta:
        model = Formation
        fields = ['code', 'nom', 'description', 'est_active']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'ex: dev-web, bureautique (sans espaces)',
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Nom complet de la formation',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description sommaire des objectifs...',
            }),
            'est_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


# Dans accounts/forms.py

class FormateurCreationForm(forms.ModelForm):
    """Formulaire utilisé par le Super Admin pour créer un compte formateur."""
    
    password = forms.CharField(
        label="Mot de passe initial",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Mot de passe'})
    )
    formation_assignee = forms.ModelChoiceField(
        queryset=Formation.objects.filter(est_active=True),
        label="Formation assignée *",
        empty_label="Sélectionnez une formation",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )

    class Meta:
        model = Apprenant
        fields = ['nom', 'prenom', 'whatsapp', 'formation_assignee', 'password']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Prénom'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '+22670000000'}),
        }

    def save(self, commit=True):
        formateur = super().save(commit=False)
        formateur.is_formateur = True
        formateur.is_staff = False  # Pas d'accès au panneau global super-admin
        formateur.set_password(self.cleaned_data['password'])
        # On synchronise le code de formation avec formation_assignee
        if formateur.formation_assignee:
            formateur.formation = formateur.formation_assignee.code
        if commit:
            formateur.save()
        return formateur



