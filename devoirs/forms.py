from django import forms
from .models import Devoir, Question, RessourcePedagogique
from accounts.models import Formation, Apprenant


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

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_formateur and not (user.is_staff or user.is_superuser):
            pks = set()
            if getattr(user, 'formation_assignee_id', None):
                pks.add(user.formation_assignee_id)
            if getattr(user, 'formation', None):
                pks.update(Formation.objects.filter(code=user.formation).values_list('id', flat=True))
            if getattr(user, 'pk', None):
                pks.update(Formation.objects.filter(formateurs=user).values_list('id', flat=True))
            formations = list(Formation.objects.filter(id__in=pks))
            if formations:
                choices = [(f.code, f.nom) for f in formations]
                self.fields['formation'].initial = formations[0].code
            else:
                choices = [('', 'Aucune formation assignée')]
        else:
            choices = Formation.get_choices(only_active=True)

        self.fields['formation'].widget = forms.Select(
            choices=choices,
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

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_formateur and not (user.is_staff or user.is_superuser):
            pks = set()
            if getattr(user, 'formation_assignee_id', None):
                pks.add(user.formation_assignee_id)
            if getattr(user, 'formation', None):
                pks.update(Formation.objects.filter(code=user.formation).values_list('id', flat=True))
            if getattr(user, 'pk', None):
                pks.update(Formation.objects.filter(formateurs=user).values_list('id', flat=True))
            formations = list(Formation.objects.filter(id__in=pks))
            if formations:
                choices = [(f.code, f.nom) for f in formations]
                self.fields['formation'].initial = formations[0].code
            else:
                choices = [('', 'Aucune formation assignée')]
        else:
            choices = Formation.get_choices(only_active=True)

        self.fields['formation'].widget = forms.Select(
            choices=choices,
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
        Ne propose QUE la ou les formations assignées à ce formateur.
        Si une seule formation lui est assignée, elle est automatiquement présélectionnée.
        Pour un super-admin ou staff, toutes les formations actives sont proposées.
        """
        super().__init__(*args, **kwargs)
        self.formateur = formateur

        if formateur and not (formateur.is_staff or formateur.is_superuser):
            pks = set()
            if getattr(formateur, 'formation_assignee_id', None):
                pks.add(formateur.formation_assignee_id)
            if getattr(formateur, 'formation', None):
                pks.update(Formation.objects.filter(code=formateur.formation).values_list('id', flat=True))
            if getattr(formateur, 'pk', None):
                pks.update(Formation.objects.filter(formateurs=formateur).values_list('id', flat=True))

            formations_list = list(Formation.objects.filter(id__in=pks))

            if formations_list:
                if len(formations_list) == 1:
                    f_unique = formations_list[0]
                    formation_choices = [(f_unique.code, f_unique.nom)]
                    self.fields['formation'].initial = f_unique.code
                else:
                    formation_choices = [('', '-- Choisir parmi vos formations assignées --')] + [
                        (f.code, f.nom) for f in formations_list
                    ]
            else:
                formation_choices = [('', 'Aucune formation ne vous est assignée')]
        else:
            formation_choices = [('', '-- Choisir une formation --')] + Formation.get_choices(only_active=True)

        self.fields['formation'].widget = forms.Select(
            choices=formation_choices,
            attrs={'class': 'form-select bg-dark text-white border-secondary'}
        )

    def clean_formation(self):
        formation = self.cleaned_data.get('formation')
        if not formation:
            raise forms.ValidationError("Veuillez sélectionner une formation.")

        if self.formateur and not (self.formateur.is_staff or self.formateur.is_superuser):
            codes_autorises = set()
            if getattr(self.formateur, 'formation_assignee', None):
                codes_autorises.add(self.formateur.formation_assignee.code)
            if getattr(self.formateur, 'formation', None):
                codes_autorises.add(self.formateur.formation)
            if getattr(self.formateur, 'pk', None):
                codes_autorises.update(
                    Formation.objects.filter(formateurs=self.formateur).values_list('code', flat=True)
                )

            if formation not in codes_autorises:
                raise forms.ValidationError("Vous n'êtes pas autorisé à publier des ressources pour cette formation.")

        return formation

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


class ReaffecterRessourceForm(forms.Form):
    """
    Formulaire pour réaffecter une ressource pédagogique à une autre session.
    Offre deux modes :
    - Dupliquer : crée une nouvelle entrée pour la nouvelle session (la session actuelle conserve la ressource)
    - Déplacer : réassigne la ressource directement vers la nouvelle session
    """
    MODE_CHOICES = [
        ('dupliquer', 'Dupliquer pour la nouvelle session (Recommandé : la session actuelle conserve l\'accès)'),
        ('deplacer', 'Déplacer vers la nouvelle session (La session actuelle ne verra plus la ressource)'),
    ]

    session_cible = forms.ChoiceField(
        choices=Apprenant.SESSION_MOIS_CHOICES,
        label="Nouvelle session *",
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'})
    )
    mode = forms.ChoiceField(
        choices=MODE_CHOICES,
        initial='dupliquer',
        label="Mode de réaffectation *",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    nouveau_titre = forms.CharField(
        max_length=200,
        required=False,
        label="Titre pour la nouvelle session",
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'Conserver le même titre ou saisir un nouveau'
        }),
        help_text="Optionnel : vous pouvez préciser le titre (ex : « Cours Python — Février »)"
    )

    def __init__(self, *args, ressource_actuelle=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ressource_actuelle = ressource_actuelle
        if ressource_actuelle and not self.is_bound:
            self.fields['nouveau_titre'].initial = ressource_actuelle.titre

    def clean(self):
        cleaned_data = super().clean()
        session_cible = cleaned_data.get('session_cible')
        mode = cleaned_data.get('mode')

        if self.ressource_actuelle and session_cible == self.ressource_actuelle.session:
            if mode == 'deplacer':
                raise forms.ValidationError(
                    f"Cette ressource est déjà assignée à la session {self.ressource_actuelle.get_session_display()}. "
                    "Veuillez choisir une session différente pour la déplacer."
                )
        return cleaned_data


class ModifierRessourceForm(forms.ModelForm):
    """
    Formulaire permettant de modifier une ressource existante (titre, description, session, visibilité)
    avec possibilité de remplacer le fichier (utile en cas de perte de fichier ou nouvelle version).
    """
    fichier = forms.FileField(
        required=False,
        label="Remplacer le fichier (optionnel)",
        help_text="Laissez vide pour conserver le fichier actuel. Formats acceptés : PDF, MP4, MOV, AVI, MKV, WEBM (Max 50 Mo).",
        widget=forms.FileInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'id': 'id_fichier_remplacement'
        })
    )

    class Meta:
        model = RessourcePedagogique
        fields = ['titre', 'description', 'session', 'type_fichier', 'fichier', 'est_visible']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'placeholder': 'Titre de la ressource'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'rows': 3,
                'placeholder': 'Description / résumé'
            }),
            'session': forms.Select(attrs={
                'class': 'form-select bg-dark text-white border-secondary'
            }),
            'type_fichier': forms.Select(attrs={
                'class': 'form-select bg-dark text-white border-secondary'
            }),
            'est_visible': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        if not fichier:
            return fichier

        taille_max = 50 * 1024 * 1024  # 50 Mo
        if fichier.size > taille_max:
            taille_actuelle_mo = round(fichier.size / (1024 * 1024), 1)
            raise forms.ValidationError(
                f"Le fichier est trop volumineux ({taille_actuelle_mo} Mo). "
                f"La taille maximale autorisée est de 50 Mo."
            )

        _, ext = os.path.splitext(fichier.name)
        if ext.lower() not in EXTENSIONS_AUTORISEES:
            raise forms.ValidationError(
                f"Format non autorisé : '{ext}'. "
                f"Formats acceptés : PDF, MP4, MOV, AVI, MKV, WEBM."
            )

        return fichier

