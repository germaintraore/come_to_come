from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, password_validation
from .models import Apprenant, Formation


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
        required=False,
        label="Type de formation (optionnel)",
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['formation'].choices = [('', 'Toutes les formations')] + Formation.get_choices(only_active=False)
    
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


class FormateurCreationForm(forms.ModelForm):
    """Formulaire utilisé par le Super Admin pour créer un compte formateur."""
    
    password = forms.CharField(
        label="Mot de passe initial",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Mot de passe'}),
        min_length=8,
        help_text="Minimum 8 caractères."
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

    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get('whatsapp')
        if whatsapp:
            whatsapp = whatsapp.strip()
            if Apprenant.objects.filter(whatsapp=whatsapp).exists():
                raise forms.ValidationError("Ce numéro WhatsApp est déjà enregistré pour un autre utilisateur.")
        return whatsapp

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


# ============================================================
# FORMULAIRES DE GESTION DU PROFIL ET MOTS DE PASSE
# ============================================================

class ProfilUpdateForm(forms.ModelForm):
    """
    Formulaire permettant à un utilisateur (apprenant, formateur, admin)
    de modifier son nom, ses prénoms et sa photo de profil.
    """
    class Meta:
        model = Apprenant
        fields = ['nom', 'prenom', 'photo_profil']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'placeholder': 'Votre nom de famille'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'placeholder': 'Vos prénoms'
            }),
            'photo_profil': forms.FileInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'accept': 'image/jpeg,image/png,image/webp,image/gif'
            }),
        }

    def clean_photo_profil(self):
        photo = self.cleaned_data.get('photo_profil')
        if photo and hasattr(photo, 'size'):
            # Limite de 5 Mo pour la photo de profil
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("La photo de profil ne doit pas dépasser 5 Mo.")
        return photo


class ChangerMotDePasseForm(forms.Form):
    """
    Formulaire permettant à l'utilisateur connecté de changer son mot de passe
    en renseignant son mot de passe actuel puis le nouveau mot de passe.
    """
    ancien_mot_de_passe = forms.CharField(
        label="Mot de passe actuel",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'Saisissez votre mot de passe actuel',
            'autocomplete': 'current-password'
        })
    )
    nouveau_mot_de_passe = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'Minimum 8 caractères',
            'autocomplete': 'new-password'
        }),
        min_length=8
    )
    confirmation_mot_de_passe = forms.CharField(
        label="Confirmer le nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'Répétez le nouveau mot de passe',
            'autocomplete': 'new-password'
        }),
        min_length=8
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_ancien_mot_de_passe(self):
        ancien = self.cleaned_data.get('ancien_mot_de_passe')
        if not self.user.check_password(ancien):
            raise forms.ValidationError("Le mot de passe actuel est incorrect.")
        return ancien

    def clean(self):
        cleaned_data = super().clean()
        nouveau = cleaned_data.get('nouveau_mot_de_passe')
        confirmation = cleaned_data.get('confirmation_mot_de_passe')

        if nouveau and confirmation:
            if nouveau != confirmation:
                self.add_error('confirmation_mot_de_passe', "Les deux mots de passe ne correspondent pas.")
            else:
                try:
                    password_validation.validate_password(nouveau, self.user)
                except forms.ValidationError as error:
                    self.add_error('nouveau_mot_de_passe', error)

        return cleaned_data


class AdminResetPasswordForm(forms.Form):
    """
    Formulaire utilisé par le Super Admin pour réinitialiser le mot de passe
    d'un apprenant ou d'un formateur.
    """
    nouveau_mot_de_passe = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'Minimum 6 caractères (ex: Temp2026@)',
            'id': 'id_admin_nouveau_mdp'
        }),
        min_length=6,
        help_text="Définissez un mot de passe temporaire ou choisissez d'en générer un."
    )



