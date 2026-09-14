from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import Apprenant


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
        choices=[('', 'Toutes les formations')] + Apprenant.FORMATION_CHOICES,
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

