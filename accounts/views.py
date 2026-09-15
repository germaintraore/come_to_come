
import csv
import os
import io
import urllib.parse
from django.core.files.storage import default_storage
from django.conf import settings
from django import forms
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from .forms import InscriptionForm, ConnexionForm,DiffusionWhatsAppForm,FormationForm,FormateurCreationForm
from .models import Apprenant,Formation
from devoirs.models import Devoir


from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT



class AdminFiltreForm(forms.Form):
    """Formulaire de filtrage pour le panneau d'administration."""
    formation = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control filter-select', 'onchange': 'this.form.submit()'})
    )
    session = forms.ChoiceField(
        choices=[('', 'Toutes les sessions')] + Apprenant.SESSION_MOIS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control filter-select', 'onchange': 'this.form.submit()'})
    )
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['formation'].choices = [('','Toutes les formations disponibles ')] + Formation.get_choices(only_active=False)


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
            if apprenant.is_staff or apprenant.is_superuser:
                messages.success(request, f"Bon retour {apprenant.nom_complet} !")
                return redirect('admin_dashboard')
            elif apprenant.is_formateur:
                return redirect('dashboard_formateur')
            else:
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
    apprenants = Apprenant.objects.filter(is_staff=False, is_formateur=False)
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
            prenom__icontains=search, is_staff=False, is_formateur=False
        ) | Apprenant.objects.filter(
            whatsapp__icontains=search, is_staff=False, is_formateur=False
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
        'session_choices': Apprenant.SESSION_MOIS_CHOICES,
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

@admin_required
def reaffecter_apprenant(request, pk):
    """Changer la session d'un apprenant."""
    if request.method == 'POST':
        try:
            apprenant = Apprenant.objects.get(pk=pk, is_staff=False)
            nouvelle_session = request.POST.get('session', '').strip()
            valid_sessions = dict(Apprenant.SESSION_MOIS_CHOICES)
            if nouvelle_session in valid_sessions:
                ancienne_session_label = apprenant.get_session_display()
                apprenant.session = nouvelle_session
                apprenant.save()
                messages.success(
                    request,
                    f"Session de {apprenant.nom_complet} modifiée : {ancienne_session_label} ➔ {valid_sessions[nouvelle_session]}."
                )
            else:
                messages.error(request, "Session sélectionnée invalide.")
        except Apprenant.DoesNotExist:
            messages.error(request, "Apprenant introuvable.")
    return redirect('admin_dashboard')


def _get_filtree_queryset(request):
    """Construit le QuerySet filtre selon la formation et la session (GET)."""
    qs = Apprenant.objects.filter(is_staff=False, is_formateur=False)
    formation = request.GET.get('formation', '').strip()
    session = request.GET.get('session', '').strip()
    if formation:
        qs = qs.filter(formation=formation)
    if session:
        qs = qs.filter(session=session)
    return qs.order_by('-date_inscription'), formation, session


def _label_formation(code):
    formation_obj=Formation.objects.filter(code=code).first()
    return formation_obj.nom if formation_obj else code
    


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

@admin_required
def export_pdf(request):
    """Télécharger la liste des apprenants en PDF selon les filtres (session, formation)."""
    apprenants, formation, session = _get_filtree_queryset(request)

    buffer = io.BytesIO()
    # Format paysage (landscape) pour un tableau aéré et lisible
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()
    
    style_titre = ParagraphStyle(
        'TitreDoc',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        alignment=TA_CENTER,
        spaceAfter=4
    )

    style_sub = ParagraphStyle(
        'SousTitreDoc',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#64748B'),
        alignment=TA_CENTER,
        spaceAfter=15
    )

    style_cell = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontSize=12,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )

    style_header_cell = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        alignment=TA_CENTER
    )

    elements = []

    # Titre du document
    titre_texte = "COME TO CODE — LISTE DES APPRENANTS"
    elements.append(Paragraph(titre_texte, style_titre))

    # Détails du filtre
    sous_titre_parties = []
    if session:
        sous_titre_parties.append(f"Session : {_label_session(session).upper()}")
    else:
        sous_titre_parties.append("Toutes les sessions")

    if formation:
        sous_titre_parties.append(f"Formation : {_label_formation(formation)}")

    sous_titre_parties.append(f"Total : {apprenants.count()} apprenant(s)")
    sous_titre_parties.append(f"Généré le : {timezone.now().strftime('%d/%m/%Y à %H:%M')}")
    
    elements.append(Paragraph(" • ".join(sous_titre_parties), style_sub))

    # Construction du tableau
    headers = [
        Paragraph("N°", style_header_cell),
        Paragraph("Nom & Prénom", style_header_cell),
        Paragraph("WhatsApp", style_header_cell),
        Paragraph("Formation", style_header_cell),
        Paragraph("Session", style_header_cell),
        Paragraph("Date d'inscription", style_header_cell),
        Paragraph("Statut", style_header_cell)
    ]
    data = [headers]

    for idx, a in enumerate(apprenants, start=1):
        statut_label = "Actif" if a.is_active else "Inactif"
        data.append([
            Paragraph(str(idx), style_cell),
            Paragraph(f"<b>{a.nom_complet}</b>", style_cell),
            Paragraph(a.whatsapp, style_cell),
            Paragraph(a.get_formation_display(), style_cell),
            Paragraph(a.get_session_display(), style_cell),
            Paragraph(a.date_inscription.strftime('%d/%m/%Y'), style_cell),
            Paragraph(statut_label, style_cell)
        ])

    # Largeurs des colonnes (Total = ~26.7 cm pour A4 paysage)
    col_widths = [1.2 * cm, 5.5 * cm, 3.8 * cm, 6.0 * cm, 3.2 * cm, 3.8 * cm, 2.5 * cm]
    
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (4, 0), (6, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(t)
    doc.build(elements)

    buffer.seek(0)
    suffix = ""
    if session:
        suffix += f"_{session}"
    if formation:
        suffix += f"_{formation}"

    filename = f"liste_participants{suffix}_{timezone.now().strftime('%Y%m%d')}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def diffusion_whatsapp(request):
    """Générateur de messages WhatsApp ciblés par session avec support de pièce jointe."""
    if not request.user.is_staff:
        messages.error(request, "Accès réfusé.")
        return redirect('tableau_de_bord')
    destinataires = []
    fichier_url = None
    fichier_nom = None
    fichier_est_image = False
    if request.method == 'POST':
        form = DiffusionWhatsAppForm(request.POST, request.FILES)
        if form.is_valid():
            session = form.cleaned_data['session']
            formation = form.cleaned_data['formation']
            template_message = form.cleaned_data['message']
            piece_jointe = form.cleaned_data.get('piece_jointe')
            # 1. Gestion de la pièce jointe (Image ou PDF)
            if piece_jointe:
                fichier_nom = piece_jointe.name
                # Sauvegarde dans media/whatsapp_pieces_jointes/
                chemin_relatif = os.path.join('whatsapp_pieces_jointes', piece_jointe.name)
                chemin_sauvegarde = default_storage.save(chemin_relatif, piece_jointe)
                # URL absolue accessible depuis internet
                fichier_url = request.build_absolute_uri(settings.MEDIA_URL + chemin_sauvegarde)
                
                # Vérifier si c'est une image
                extensions_image = ('.jpg', '.jpeg', '.png', '.webp')
                fichier_est_image = any(piece_jointe.name.lower().endswith(ext) for ext in extensions_image)
            # 2. Récupérer les apprenants ciblés
            apprenants = Apprenant.objects.filter(session=session, is_active=True, is_formateur=False, is_staff=False)
            if formation:
                apprenants = apprenants.filter(formation=formation)
            apprenants = apprenants.order_by('nom', 'prenom')
            # 3. Préparer les messages personnalisés
            for a in apprenants:
                # Remplacement des balises personnalisées
                texte_perso = template_message.format(
                    prenom=a.prenom,
                    nom=a.nom,
                    formation=a.get_formation_display(),
                    session=a.get_session_display()
                )
                # Si une pièce jointe a été ajoutée, on insère le lien au message
                if fichier_url:
                    emoji = "🖼️ Image" if fichier_est_image else "📄 Document PDF"
                    texte_perso += f"\n\n{emoji} joint : {fichier_url}"
                # Nettoyage du numéro de téléphone WhatsApp
                numero_clean = a.whatsapp.replace(' ', '').replace('+', '').replace('-', '')
                
                # Encodage URL pour le lien WhatsApp
                message_encode = urllib.parse.quote(texte_perso)
                lien_whatsapp = f"https://wa.me/{numero_clean}?text={message_encode}"
                destinataires.append({
                    'apprenant': a,
                    'message_texte': texte_perso,
                    'lien_whatsapp': lien_whatsapp,
                })
            if not apprenants.exists():
                messages.warning(request, "Aucun apprenant actif trouvé pour les critères sélectionnés.")
    else:
        form = DiffusionWhatsAppForm()
    return render(request, 'accounts/diffusion_whatsapp.html', {
        'form': form,
        'destinataires': destinataires,
        'total_destinataires': len(destinataires),
        'fichier_url': fichier_url,
        'fichier_nom': fichier_nom,
        'fichier_est_image': fichier_est_image,
    })

@admin_required
def liste_formations(request):
    """Affiche toutes les formations, leurs statistiques et gère l'ajout d'une nouvelle."""
    formations = Formation.objects.all().order_by('nom')
    
    # On attache les compteurs d'apprenants et de devoirs pour chaque formation
    for f in formations:
        f.nb_apprenants = Apprenant.objects.filter(formation=f.code, is_staff=False, is_formateur=False).count()
        f.nb_devoirs = Devoir.objects.filter(formation=f.code).count()

    form = FormationForm()
    if request.method == 'POST':
        form = FormationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"La formation '{form.cleaned_data['nom']}' a été créée avec succès !")
            return redirect('liste_formations')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

    context = {
        'formations': formations,
        'form': form,
        'total_formations': formations.count(),
        'actives': formations.filter(est_active=True).count(),
    }
    return render(request, 'accounts/admin_formations.html', context)


@admin_required
def modifier_formation(request, pk):
    """Modifier les détails d'une formation existante."""
    formation = get_object_or_404(Formation, pk=pk)
    if request.method == 'POST':
        form = FormationForm(request.POST, instance=formation)
        if form.is_valid():
            form.save()
            messages.success(request, f"Formation '{formation.nom}' mise à jour avec succès.")
            return redirect('liste_formations')
    else:
        form = FormationForm(instance=formation)

    return render(request, 'accounts/modifier_formation.html', {
        'form': form,
        'formation': formation
    })


@admin_required
def toggle_formation(request, pk):
    """Activer ou désactiver rapidement une formation."""
    formation = get_object_or_404(Formation, pk=pk)
    formation.est_active = not formation.est_active
    formation.save()
    etat = "activée" if formation.est_active else "désactivée"
    messages.info(request, f"La formation '{formation.nom}' est maintenant {etat}.")
    return redirect('liste_formations')


@admin_required
def supprimer_formation(request, pk):
    """Supprimer une formation (uniquement si aucun apprenant ni devoir n'y est rattaché)."""
    formation = get_object_or_404(Formation, pk=pk)
    nb_apprenants = Apprenant.objects.filter(formation=formation.code).count()
    nb_devoirs = Devoir.objects.filter(formation=formation.code).count()

    # Règle d'or de sécurité en BDD : intégrité référentielle
    if nb_apprenants > 0 or nb_devoirs > 0:
        messages.error(
            request, 
            f"Impossible de supprimer '{formation.nom}' car {nb_apprenants} apprenant(s) "
            f"et {nb_devoirs} devoir(s) y sont rattachés. Désactivez-la plutôt !"
        )
    else:
        nom = formation.nom
        formation.delete()
        messages.success(request, f"La formation '{nom}' a été supprimée définitivement.")

    return redirect('liste_formations')


# Dans accounts/views.py

def formateur_required(view_func):
    """Décorateur : réservé aux formateurs ou super-administrateurs."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Veuillez vous connecter.")
            return redirect('connexion')
        if not (request.user.is_formateur or request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Accès réservé aux formateurs.")
            return redirect('tableau_de_bord')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

@admin_required
def liste_formateurs(request):
    """Gestion des formateurs par le Super Admin."""
    formateurs = Apprenant.objects.filter(is_formateur=True).select_related('formation_assignee')
    form = FormateurCreationForm()

    if request.method == 'POST':
        form = FormateurCreationForm(request.POST)
        if form.is_valid():
            f = form.save()
            messages.success(request, f"Le compte formateur pour {f.nom_complet} a été créé !")
            return redirect('liste_formateurs')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")

    return render(request, 'accounts/admin_formateurs.html', {
        'formateurs': formateurs,
        'form': form
    })

@formateur_required
def dashboard_formateur(request):
    """Espace réservé au formateur : liste uniquement les apprenants de sa filière."""
    formateur = request.user
    formation = formateur.formation_assignee

    if not formation:
        messages.warning(request, "Aucune formation ne vous est actuellement assignée.")
        return render(request, 'accounts/dashboard_formateur.html', {'apprenants': [], 'devoirs': []})

    # Filtrer les apprenants de SA formation uniquement
    apprenants = Apprenant.objects.filter(
        formation=formation.code,
        is_staff=False,
        is_formateur=False
    ).order_by('-date_inscription')

    # Filtre optionnel par session
    session = request.GET.get('session', '').strip()
    if session:
        apprenants = apprenants.filter(session=session)

    # Récupérer les devoirs de SA formation
    devoirs = Devoir.objects.filter(formation=formation.code).order_by('-date_creation')

    context = {
        'formateur': formateur,
        'formation': formation,
        'apprenants': apprenants,
        'devoirs': devoirs,
        'total_apprenants': apprenants.count(),
        'actifs': apprenants.filter(is_active=True).count(),
        'session_choices': Apprenant.SESSION_MOIS_CHOICES,
        'session_selectionnee': session,
    }
    return render(request, 'accounts/dashboard_formateur.html', context)


@formateur_required
def formateur_notes_apprenant(request, apprenant_pk):
    """Formateur voit toutes les notes d'un apprenant de sa formation."""
    formateur = request.user
    formation = formateur.formation_assignee

    if not formation:
        messages.warning(request, "Aucune formation ne vous est assignée.")
        return redirect('dashboard_formateur')

    # Sécurité : l'apprenant doit appartenir à la formation du formateur
    apprenant = get_object_or_404(
        Apprenant,
        pk=apprenant_pk,
        formation=formation.code,
        is_staff=False,
        is_formateur=False
    )

    from devoirs.models import Soumission
    soumissions = Soumission.objects.filter(
        apprenant=apprenant,
        devoir__formation=formation.code
    ).select_related('devoir').order_by('-date_soumission')

    total = soumissions.count()
    moyenne = round(sum(s.note for s in soumissions) / total, 1) if total > 0 else None

    context = {
        'formateur': formateur,
        'formation': formation,
        'apprenant_cible': apprenant,
        'soumissions': soumissions,
        'total_devoirs': total,
        'moyenne': moyenne,
    }
    return render(request, 'accounts/formateur_notes_apprenant.html', context)

