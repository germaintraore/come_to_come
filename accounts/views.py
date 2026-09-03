
import csv
import io
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from .forms import InscriptionForm, ConnexionForm
from .models import Apprenant
from devoirs.models import Devoir


class AdminFiltreForm(forms.Form):
    """Formulaire de filtrage pour le panneau d'administration."""
    formation = forms.ChoiceField(
        choices=[('', 'Toutes les formations')] + Apprenant.FORMATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control filter-select', 'onchange': 'this.form.submit()'})
    )
    session = forms.ChoiceField(
        choices=[('', 'Toutes les sessions')] + Apprenant.SESSION_MOIS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control filter-select', 'onchange': 'this.form.submit()'})
    )


def accueil(request):
    return render(request, 'accounts/accueil.html')


def inscription(request):
    if request.user.is_authenticated:
        return redirect('tableau_de_bord')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            apprenant = form.save()
            login(request, apprenant)
            messages.success(request,
                f"Bienvenue {apprenant.nom_complet} ! Votre compte a ete cree avec succes.")
            return redirect('tableau_de_bord')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = InscriptionForm()
    return render(request, 'accounts/inscription.html', {'form': form})


def connexion(request):
    if request.user.is_authenticated:
        return redirect('tableau_de_bord')
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            apprenant = form.get_user()
            login(request, apprenant)
            messages.success(request, f"Bon retour {apprenant.nom_complet} !")
            return redirect('tableau_de_bord')
        else:
            messages.error(request, "Identifiants incorrects. Veuillez reessayer.")
    else:
        form = ConnexionForm(request)
    return render(request, 'accounts/connexion.html', {'form': form})


@login_required
def tableau_de_bord(request):
    return render(request, 'accounts/tableau_de_bord.html', {'apprenant': request.user})


@login_required
def deconnexion(request):
    nom = request.user.nom_complet
    logout(request)
    messages.info(request, f"A bientot {nom} ! Vous avez ete deconnecte(e).")
    return redirect('accueil')


# ============================================================
# INTERFACE ADMIN PERSONNALISEE
# ============================================================

def admin_required(view_func):
    """Decorateur : reserve aux staff/superusers."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Connectez-vous d'abord.")
            return redirect('connexion')
        if not request.user.is_staff:
            messages.error(request, "Acces reserve aux administrateurs.")
            return redirect('tableau_de_bord')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


@admin_required
def admin_dashboard(request):
    """Tableau de bord administrateur avec statistiques et filtres."""
    apprenants = Apprenant.objects.filter(is_staff=False)
    devoirs=Devoir.objects.all().order_by('-date_creation')

    # Filtre par formation
    formation = request.GET.get('formation', '').strip()
    if formation:
        apprenants = apprenants.filter(formation=formation)

    # Filtre par session (mois)
    session = request.GET.get('session', '').strip()
    if session:
        apprenants = apprenants.filter(session=session)

    # Recherche textuelle
    search = request.GET.get('q', '').strip()
    if search:
        apprenants = apprenants.filter(
            nom__icontains=search
        ) | Apprenant.objects.filter(
            prenom__icontains=search, is_staff=False
        ) | Apprenant.objects.filter(
            whatsapp__icontains=search, is_staff=False
        )
        apprenants = apprenants.distinct()

    apprenants = apprenants.order_by('-date_inscription')
    total = apprenants.count()
    actifs = apprenants.filter(is_active=True).count()
    inactifs = total - actifs

    filtre_form = AdminFiltreForm(data=request.GET)

    context = {
        'apprenants':  apprenants,
        'devoirs':    devoirs,
        'total':       total,
        'actifs':      actifs,
        'inactifs':    inactifs,
        'search':      search,
        'filtre_form': filtre_form,
        'formation':   formation,
        'session':     session,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@admin_required
def toggle_apprenant(request, pk):
    """Activer / desactiver un compte apprenant."""
    try:
        apprenant = Apprenant.objects.get(pk=pk, is_staff=False)
        apprenant.is_active = not apprenant.is_active
        apprenant.save()
        etat = "active" if apprenant.is_active else "desactive"
        messages.success(request, f"Compte de {apprenant.nom_complet} {etat}.")
    except Apprenant.DoesNotExist:
        messages.error(request, "Apprenant introuvable.")
    return redirect('admin_dashboard')


@admin_required
def supprimer_apprenant(request, pk):
    """Supprimer un compte apprenant."""
    try:
        apprenant = Apprenant.objects.get(pk=pk, is_staff=False)
        nom = apprenant.nom_complet
        apprenant.delete()
        messages.success(request, f"Compte de {nom} supprime.")
    except Apprenant.DoesNotExist:
        messages.error(request, "Apprenant introuvable.")
    return redirect('admin_dashboard')


def _get_filtree_queryset(request):
    """Construit le QuerySet filtre selon la formation et la session (GET)."""
    qs = Apprenant.objects.filter(is_staff=False)
    formation = request.GET.get('formation', '').strip()
    session = request.GET.get('session', '').strip()
    if formation:
        qs = qs.filter(formation=formation)
    if session:
        qs = qs.filter(session=session)
    return qs.order_by('-date_inscription'), formation, session


def _label_formation(code):
    for val, label in Apprenant.FORMATION_CHOICES:
        if val == code:
            return label
    return code


def _label_session(code):
    for val, label in Apprenant.SESSION_MOIS_CHOICES:
        if val == code:
            return label
    return code


@admin_required
def export_csv(request):
    """Telecharger la liste des apprenants en CSV (filtree si parametres fournis)."""
    apprenants, formation, session = _get_filtree_queryset(request)

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    suffix = ""
    if formation:
        suffix += f"_{formation}"
    if session:
        suffix += f"_{session}"
    response['Content-Disposition'] = (
        f'attachment; filename="apprenants{suffix}_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
    )

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID', 'Nom', 'Prenom', 'WhatsApp', 'Type de formation', 'Session', "Date d'inscription", 'Statut'])

    for a in apprenants:
        writer.writerow([
            a.id,
            a.nom,
            a.prenom,
            a.whatsapp,
            a.get_formation_display(),
            a.get_session_display(),
            a.date_inscription.strftime('%d/%m/%Y %H:%M'),
            'Actif' if a.is_active else 'Inactif',
        ])

    return response


@admin_required
def export_excel(request):
    """Telecharger la liste des apprenants en fichier Excel (.xlsx) (filtree si parametres fournis)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    apprenants, formation, session = _get_filtree_queryset(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "Apprenants"

    headers = ['ID', 'Nom', 'Prenom', 'WhatsApp', 'Type de formation', 'Session', "Date d'inscription", 'Heure', 'Statut']
    ws.append(headers)

    # Style de l'en-tete
    header_fill = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    thin_border = Border(
        left=Side(style='thin', color='D1D5DB'),
        right=Side(style='thin', color='D1D5DB'),
        top=Side(style='thin', color='D1D5DB'),
        bottom=Side(style='thin', color='D1D5DB'),
    )

    for col_num, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    for row_num, a in enumerate(apprenants, 2):
        row = [
            a.id,
            a.nom,
            a.prenom,
            a.whatsapp,
            a.get_formation_display(),
            a.get_session_display(),
            a.date_inscription.strftime('%d/%m/%Y'),
            a.date_inscription.strftime('%H:%M'),
            'Actif' if a.is_active else 'Inactif',
        ]
        for col_num, value in enumerate(row, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.border = thin_border
            if col_num == 9:  # Colonne Statut
                cell.font = Font(
                    color="10B981" if value == 'Actif' else "EF4444",
                    bold=True
                )

    # Largeur des colonnes
    column_widths = [6, 20, 20, 20, 24, 14, 14, 10, 12]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[chr(64 + i)].width = width

    # Ligne de titre
    last_col_letter = chr(64 + len(headers))
    ws.insert_rows(1)
    ws.merge_cells(f'A1:{last_col_letter}1')
    title_cell = ws['A1']
    titre = "Liste des apprenants"
    if formation:
        titre += f" - {_label_formation(formation)}"
    if session:
        titre += f" - Session {_label_session(session)}"
    titre += f" ({apprenants.count()} inscrits)"
    title_cell.value = titre
    title_cell.font = Font(bold=True, size=13, color="1E2A3E")
    title_cell.alignment = Alignment(horizontal='center')
    ws.row_dimensions[1].height = 28

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    suffix = ""
    if formation:
        suffix += f"_{formation}"
    if session:
        suffix += f"_{session}"
    filename = f"apprenants{suffix}_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


