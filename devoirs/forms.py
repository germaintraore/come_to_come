from django import forms
from .models import Devoir, Question


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
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'formation': forms.Select(attrs={'class': 'form-select'}),
            'session': forms.Select(attrs={'class': 'form-select'}),
        }

