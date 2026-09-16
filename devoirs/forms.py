from django import forms
from .models import Devoir, Question, RessourcePedagogique
from accounts.models import Formation


TAILLE_MAX_OCTETS = 50 * 1024 * 1024  # 50 Mo en octets
EXTENSIONS_AUTORISEES = ['.pdf', '.mp4', '.mov', '.avi', '.mkv', '.webm']


class DevoirForm(forms.ModelForm):
    class Meta:
        model = Devoir
        fields = ['titre', 'formation', 'session', 'description', 'est_actif']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Donnez le titre du devoir',
            }),
            'formation': forms.Select(attrs={
                'class': 'form-select',
            }),
            'session': forms.Select(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Consignes du devoir...',
            }),
            'est_actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['formation'].widget = forms.Select(
            choices=Formation.get_choices(only_active=True),
            attrs={'class': 'form-select'}
        )


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['texte', 'choix_a', 'choix_b', 'choix_c', 'choix_d', 'bonne_reponse', 'justification', 'ordre']
        widgets = {
            'texte': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "Énoncé de la question...",
            }),
            'choix_a': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option A',
            }),
            'choix_b': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option B',
            }),
            'choix_c': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option C',
            }),
            'choix_d': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option D',
            }),
            'bonne_reponse': forms.Select(attrs={
                'class': 'form-select',
            }),
            'justification': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Justification / explication de la réponse...',
            }),
            'ordre': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1, 2, 3...',
            }),
        }


class DupliquerDevoirForm(forms.ModelForm):
    class Meta:
        model = Devoir
        fields = ['titre', 'formation', 'session']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Donnez le titre du devoir',
            }),
            'formation': forms.Select(attrs={
                'class': 'form-select',
            }),
            'session': forms.Select(attrs={
                'class': 'form-control',
            }),

        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['formation'].widget = forms.Select(
            choices=Formation.get_choices(only_active=True),
            attrs={'class': 'form-select'}
        )


class RessourceForm(forms.ModelForm):
    """
    Formulaire pour qu'un formateur uploade une ressource pédagogique.
    La validation de taille et d'extension se fait côté serveur dans clean_fichier().
    """
    class Meta:
        model = RessourcePedagogique
        fields = ['titre', 'description', 'fichier', 'type_fichier', 'formation', 'session']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'placeholder': 'Ex: Cours Introduction Python — Chapitre 1'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'rows': 3,
                'placeholder': 'Résumé du contenu de ce fichier (optionnel)'
            }),
            'fichier': forms.FileInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'accept': '.pdf,.mp4,.mov,.avi,.mkv,.webm'
            }),
            'type_fichier': forms.Select(attrs={
                'class': 'form-select bg-dark text-white border-secondary'
            }),
            'session': forms.Select(attrs={
                'class': 'form-select bg-dark text-white border-secondary'
            }),
        }

    def __init__(self, *args, formateur=None, **kwargs):
        """
        formateur : l'utilisateur formateur connecté.
        Si une formation lui est assignée, le champ 'formation' est pré-rempli
        et verrouillé (l'utilisateur ne peut pas changer de filière).
        """
        super().__init__(*args, **kwargs)

        # Construction dynamique des choix de formations
        formation_choices = [('', '-- Choisir une formation --')] + Formation.get_choices(only_active=False)
        self.fields['formation'].widget = forms.Select(
            choices=formation_choices,
            attrs={'class': 'form-select bg-dark text-white border-secondary'}
        )

        # Si le formateur a une formation assignée : pré-remplir et verrouiller
        if formateur and formateur.formation_assignee:
            code = formateur.formation_assignee.code
            self.fields['formation'].initial = code
            self.fields['formation'].widget.attrs['disabled'] = 'disabled'
            # Champ caché car les champs "disabled" ne sont pas soumis dans le POST
            self.fields['formation_hidden'] = forms.CharField(
                initial=code,
                widget=forms.HiddenInput()
            )

    def clean_fichier(self):
        """
        Validation serveur du fichier uploadé :
        1. Vérifie que le fichier existe
        2. Vérifie la taille (max 50 Mo)
        3. Vérifie l'extension (pdf, mp4, mov, avi, mkv, webm)
        """
        import os
        fichier = self.cleaned_data.get('fichier')

        if not fichier:
            raise forms.ValidationError("Vous devez sélectionner un fichier.")

        # Vérification de la taille
        if fichier.size > TAILLE_MAX_OCTETS:
            taille_mo = fichier.size / (1024 ** 2)
            raise forms.ValidationError(
                f"Le fichier est trop volumineux ({taille_mo:.1f} Mo). La limite est de 50 Mo."
            )

        # Vérification de l'extension
        _, ext = os.path.splitext(fichier.name)
        if ext.lower() not in EXTENSIONS_AUTORISEES:
            raise forms.ValidationError(
                f"Format non autorisé : '{ext}'. "
                f"Formats acceptés : PDF, MP4, MOV, AVI, MKV, WEBM."
            )

        return fichier

    def clean(self):
        """
        Si le champ 'formation' est disabled, il ne sera pas dans cleaned_data.
        On récupère la valeur depuis le champ caché formation_hidden.
        """
        cleaned = super().clean()
        if not cleaned.get('formation'):
            cleaned['formation'] = self.data.get('formation_hidden', '')
        return cleaned
