

from devoirs.forms import DupliquerDevoirForm
from accounts.models import Apprenant
from django.http import HttpResponse
#from reportlab.platypus import doctemplate

from asyncio import queues

from reportlab.lib.colors import green
from django.db.models import aggregates
from asyncio import taskgroups
from openpyxl.utils import bound_dictionary
from reportlab.platypus import HRFlowable
import io 
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors 
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,HRFlowable

from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER,TA_LEFT,TA_RIGHT

from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Devoir ,Question,Soumission,ReponseApprenant
from .forms import DevoirForm,QuestionForm  ,DupliquerDevoirForm


def _est_formateur_ou_staff(user):
    """Retourne True si l'utilisateur est staff OU formateur."""
    return user.is_staff or user.is_superuser or user.is_formateur


@login_required
def liste_devoirs(request):
    devoir=Devoir.objects.filter(est_actif=True,formation=request.user.formation,session=request.user.session).order_by('-date_creation')
   

    devoir_utilisateur=[]
    for d in devoir:
        soumission=Soumission.objects.filter(devoir=d,apprenant=request.user).first()

        devoir_utilisateur.append({
            "devoir":d,
            "soumission":soumission,
            "meilleur_note": soumission.note if soumission else None,
        })

    return render(request,'devoirs/liste_devoirs.html',{
        'devoir_utilisateur':devoir_utilisateur,
    })

@login_required
def passer_devoir(request,pk):

    if not request.user.is_authenticated:
        return redirect('connexion')

    formation=request.user.formation
    session=request.user.session
    devoir=get_object_or_404(Devoir,pk=pk,est_actif=True,formation=formation,session=session)

    if not devoir:
        messages.error(request,"Vous n'avez pas accès à ce devoir")
        return redirect('liste_devoirs')

    if Soumission.objects.filter(apprenant=request.user,devoir=devoir).exists():
        return redirect('resultat_devoir',pk=pk)
        
    return render(request,'devoirs/passer_devoir.html',{
        'devoir':devoir,
        'questions':Question.objects.filter(devoir=devoir),   
    })

@login_required
def soumettre_devoir(request,pk):
    devoir=get_object_or_404(Devoir,pk=pk,est_actif=True)
    if request.method != 'POST':
        return redirect('passer_devoir',pk=pk)
    if Soumission.objects.filter(apprenant=request.user,devoir=devoir).exists():
        return redirect('resultat_devoir',pk=pk)

    questions=Question.objects.filter(devoir=devoir)
    note=0
    reponses_a_creer=[]
    
    for q in questions:
        reponse_utilisateur=request.POST.get(f'question_{q.id}')
        correcte=reponse_utilisateur==q.bonne_reponse

        if correcte:
            note+=1

    soumission=Soumission.objects.create(
        apprenant=request.user,
        devoir=devoir,
        note=note,
    )  
    for q in questions:
        reponse_utilisateur=request.POST.get(f'question_{q.id}')
        correcte=reponse_utilisateur==q.bonne_reponse

        ReponseApprenant.objects.create(
            soumission=soumission,
            question=q,
            reponse_choisie=reponse_utilisateur,
            est_correcte=correcte,
        )   
    

    return redirect('resultat_devoir',pk=pk)


@login_required 
def resultat_devoir(request,pk):
    devoir=get_object_or_404(Devoir,pk=pk)
    soumission=Soumission.objects.filter(apprenant=request.user,devoir=devoir).first()
    if not request.user.is_staff and not soumission:
        messages.error(request,"Accès refusé")
        return redirect('listes_devoirs')
    
    if soumission:
        reponses_utilisateur = ReponseApprenant.objects.filter(soumission=soumission)
    else:
        reponses_utilisateur = []
    questions = devoir.questions.all().order_by('ordre')
    return render(request, 'devoirs/resultat_devoir.html', {
        'devoir': devoir,
        'soumission': soumission,
        'reponses_utilisateur': reponses_utilisateur,
        'questions': questions,
    })

@login_required
def creer_devoir(request):
    if not request.user.is_staff:
        messages.error(request,"Vous devez etre admin pour creer un devoir")
        return redirect('tableau_de_bord')
    
    if request.method=='POST':
        form=DevoirForm(request.POST)
        if form.is_valid():
           devoir= form.save()
           messages.success(request,f" Le devoir {devoir.titre} pour la session  {devoir.get_session_display() } à été crée avec succès aller ajouter les questions")
           return redirect('gerer_devoir',pk=devoir.pk)
    else:
        form=DevoirForm()

    return render(request,'devoirs/creer_devoir.html',{'form':form})

@login_required
def gerer_devoir(request, pk):
    """Page d'administration d'un devoir : voir les questions et en ajouter d'autres"""
    if not request.user.is_staff:
        messages.error(request, "Accès réservé refusé")
        return redirect('tableau_de_bord')

    devoir = get_object_or_404(Devoir, pk=pk)
    questions = devoir.questions.all().order_by('ordre')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.devoir = devoir
            if not question.ordre or question.ordre == 0:
                question.ordre = questions.count() + 1
            question.save()
            messages.success(request, f"Question {question.ordre} ajoutée avec succès !")
            return redirect('gerer_devoir', pk=devoir.pk)
    else:
        prochaine_question = questions.count() + 1
        form = QuestionForm(initial={'ordre': prochaine_question})

    return render(request, 'devoirs/gerer_devoir.html', {
        'devoir': devoir,
        'questions': questions,
        'form': form,
    })


@login_required
def supprimer_question(request,pk):
    """ Supprimer une question précise d'un devoir"""
    if not request.user.is_staff:
        messages.error(request,"Action réfusé")
        return redirect('tableau_de_bord')
    question=get_object_or_404(Question,pk=pk)
    devoir_pk=question.devoir.pk
    question.delete()
    messages.success(request,"Question supprimée avec succès")
    return redirect('gerer_devoir',pk=devoir_pk)

@login_required
def supprimer_devoir(request,pk):
    """ Supprimer un devoir précis et toutes ces questions associées"""
    if not request.user.is_staff:
        messages.error(request,"Action réfusé")
        return redirect('tableau_de_bord')
    devoir=get_object_or_404(Devoir,pk=pk)
    titre=devoir.titre
    devoir.delete()
    messages.success(request,f" Devoir {titre} supprimée avec succès")
    return redirect('admin_dashboard')

@login_required
def modifier_question(request, pk):
    """Modifier une question existante et mettre à jour ses choix / explications."""
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('tableau_de_bord')

    question = get_object_or_404(Question, pk=pk)
    devoir = question.devoir

    if request.method == 'POST':
        # On passe 'instance=question' pour que Django sache qu'on MODIFIE cette question
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, f"Question #{question.ordre} modifiée avec succès !")
            return redirect('gerer_devoir', pk=devoir.pk)
    else:
        # En mode GET : charger le formulaire pré-rempli avec les données actuelles
        form = QuestionForm(instance=question)

    return render(request, 'devoirs/modifier_question.html', {
        'form': form,
        'question': question,
        'devoir': devoir,
    })



@login_required
def telecharger_devoir_pdf(request, pk):
    """Télécharger le corrigé d'un devoir au format PDF."""
    devoir = get_object_or_404(Devoir, pk=pk)
    soumission = None

    if not request.user.is_staff:
        soumission = Soumission.objects.filter(apprenant=request.user, devoir=devoir).first()
        if not soumission:
            messages.error(request, "Vous devez d'abord traiter et soumettre le devoir avant de pouvoir télécharger le corrigé.")
            return redirect('liste_devoirs')
    else:
        # Pour le staff, on peut récupérer sa soumission s'il en a une
        soumission = Soumission.objects.filter(apprenant=request.user, devoir=devoir).first()

    # Création du buffer pour le fichier PDF
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    # Styles
    styles = getSampleStyleSheet()

    primary_color = colors.HexColor('#006400')
    dark_color = colors.HexColor('#0a0e1a')
    gray_bg = colors.HexColor('#f8fafc')
    green_hex = '#10b981'
    red_hex = '#ef4444'

    style_titre = ParagraphStyle(
        'Titre',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceAfter=10,
        alignment=TA_CENTER
    )

    style_subtitle = ParagraphStyle(
        'subtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        textColor=colors.gray,
        fontSize=11,
        leading=14,
        spaceAfter=6,
        alignment=TA_CENTER
    )

    h2_style = ParagraphStyle(
        'h2_style',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=dark_color,
        fontName='Helvetica-Bold',
        leading=15,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'body_style',
        parent=styles['Normal'],
        fontSize=10,
        textColor=dark_color,
        leading=14
    )

    elements = []
    elements.append(Paragraph("Come To Code with 2S Informatique", style_titre))
    elements.append(Paragraph(f"Fiche de correction du devoir : {devoir.titre.upper()}", style_subtitle))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=15))

    info_data = [
        [
            Paragraph(f"<b>Formation :</b> {devoir.get_formation_display()}", body_style),
            Paragraph(f"<b>Session :</b> {devoir.get_session_display()}", body_style),
        ],
        [
            Paragraph(f"<b>Formateur :</b> {request.user.nom_complet}", body_style),
            Paragraph(f"<b>Tél :</b> {request.user.whatsapp}", body_style),
        ]
    ]


    if soumission:
        reponses_dict = {rep.question_id: rep for rep in soumission.reponses.all()}
        info_data.append([
            Paragraph(f"<b>Apprenant :</b> {soumission.apprenant.nom_complet}", body_style),
            Paragraph(f"<b>Note obtenue :</b> <font color='{green_hex}'><b>{int(soumission.note)} / {devoir.total_questions()}</b></font>", body_style),
        ])
    else:
        reponses_dict = {}
        info_data.append([
            Paragraph("<b>Mode :</b> Corrigé officiel (Staff)", body_style),
            Paragraph(f"<b>Total questions :</b> {devoir.total_questions()}", body_style),
        ])

    info_table = Table(info_data, colWidths=[9 * cm, 8.5 * cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), gray_bg),
        ('BOX', (0, 0), (-1, -1), 1, primary_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5 * cm))

    questions = devoir.questions.all().order_by('ordre')
    for q in questions:
        rep = reponses_dict.get(q.id)
        elements.append(Paragraph(f"<b>Question {q.ordre}.</b> {q.texte}", h2_style))
        elements.append(Spacer(1, 0.15 * cm))

        option_data = [
            [Paragraph(f"<b>A.</b> {q.choix_a}", body_style), Paragraph(f"<b>B.</b> {q.choix_b}", body_style)],
            [Paragraph(f"<b>C.</b> {q.choix_c}", body_style), Paragraph(f"<b>D.</b> {q.choix_d}", body_style)],
        ]

        options_table = Table(option_data, colWidths=[8.5 * cm, 8.5 * cm])
        options_table.setStyle(TableStyle([
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(options_table)
        elements.append(Spacer(1, 0.2 * cm))

        # Résultats et Justification
        correction_lines = []
        if rep:
            statut_color = green_hex if rep.est_correcte else red_hex
            statut_text = "✓ Correct" if rep.est_correcte else f"✗ Incorrect (Votre choix : {rep.reponse_choisie})"
            correction_lines.append(f"<b>Votre réponse :</b> <font color='{statut_color}'><b>{statut_text}</b></font> | ")

        bonne_choix_texte = q.get_choix_texte(q.bonne_reponse)
        correction_lines.append(f"<b>Bonne réponse :</b> <font color='{green_hex}'><b>{q.bonne_reponse}</b> ({bonne_choix_texte})</font>")
        elements.append(Paragraph("".join(correction_lines), body_style))

        if q.justification:
            justif_text = f"💡 <b>Explication :</b> {q.justification}"
            justif_table = Table([[Paragraph(justif_text, body_style)]], colWidths=[17 * cm])
            justif_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(Spacer(1, 0.15 * cm))
            elements.append(justif_table)

        elements.append(Spacer(1, 0.4 * cm))

    # Construction du document PDF
    pdf.build(elements)
    buffer.seek(0)

    nom_fichier_clean = "".join(c if c.isalnum() else "_" for c in devoir.titre)
    filename = f"Correction_{nom_fichier_clean}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def dupliquer_devoir(request,pk):
    if not request.user.is_staff:
        messages.error(request,"Accès refusé")
        return redirect('admin_dashboard')
    devoir_source=get_object_or_404(Devoir,pk=pk)
    if request.method=="POST":
        form=DupliquerDevoirForm(request.POST)
        if form.is_valid():
            nouveau_devoir=form.save(commit=False)
            nouveau_devoir.description=devoir_source.description
            nouveau_devoir.est_actif=True
            nouveau_devoir.save()
        
        
        questions=devoir_source.questions.all()
        for q in questions:
            Question.objects.create(
                devoir=nouveau_devoir,
                texte=q.texte,
                choix_a=q.choix_a,
                choix_b=q.choix_b,
                choix_c=q.choix_c,
                choix_d=q.choix_d,
                bonne_reponse=q.bonne_reponse,
                justification=q.justification,
                ordre=q.ordre,
            )
        messages.success(request,f"Devoir dupliqué avec succès pour la session '{nouveau_devoir.get_session_display()}' avec {questions.count()} questions (s) !!" )
        return redirect('admin_dashboard')
    else:
        form=DupliquerDevoirForm(instance=devoir_source)
        return render(request,'devoirs/dupliquer_devoir.html',{'devoir':devoir_source ,
        'form':form})

@login_required
def modifier_devoir(request, pk):
    """Modifier les attributs d'un devoir existant (titre, formation, session, consignes, statut)."""
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('tableau_de_bord')

    devoir = get_object_or_404(Devoir, pk=pk)

    if request.method == 'POST':
        # On passe instance=devoir pour mettre à jour l'enregistrement existant
        form = DevoirForm(request.POST, instance=devoir)
        if form.is_valid():
            devoir_modifie = form.save()
            messages.success(request, f"Le devoir « {devoir_modifie.titre} » a été mis à jour avec succès !")
            return redirect('admin_dashboard')
    else:
        # En mode GET : charge le formulaire pré-rempli avec les données actuelles du devoir
        form = DevoirForm(instance=devoir)

    return render(request, 'devoirs/modifier_devoir.html', {
        'form': form,
        'devoir': devoir,
    })

@login_required
def liste_soumission_devoir(request, pk):
    """Afficher la liste des apprénants ayant composé pour un devoir donné"""
    if not _est_formateur_ou_staff(request.user):
        messages.error(request, "Accès réfusé")
        return redirect('tableau_de_bord')
    
    devoir = get_object_or_404(Devoir, pk=pk)
    
    # Si c'est un formateur (pas staff), il ne peut voir que les devoirs de sa formation
    if request.user.is_formateur and not request.user.is_staff:
        formation_assignee = request.user.formation_assignee
        if not formation_assignee or devoir.formation != formation_assignee.code:
            messages.error(request, "Vous n'avez pas accès à ce devoir.")
            return redirect('dashboard_formateur')
    
    # recupère toutes les soummissions pour ce devoir avec les infos des apprenants
    soumissions=devoir.soumissions.select_related('apprenant').order_by('-date_soumission')
    total_soumissions=soumissions.count()
    moyenne=None
    if total_soumissions > 0:
        moyenne = round(sum(s.note for s in soumissions) / total_soumissions, 2)
    
    return render(
        request,
        'devoirs/liste_soumission_admin.html',
        {
            'devoir': devoir,
            'soumissions': soumissions,
            'total_soumissions': total_soumissions,
            'moyenne': moyenne,
        }
    )

@login_required
def detail_soumission_admin(request,pk):
    """Affiche les détails et les réponses complètes d'un élève pour une soumission donnée"""

    if not _est_formateur_ou_staff(request.user):
        messages.error(request, "Accès réfusé.")
        return redirect('tableau_de_bord')

    soumission = get_object_or_404(Soumission, pk=pk)

    # Formateur : vérifier que l'apprenant appartient bien à sa formation
    if request.user.is_formateur and not request.user.is_staff:
        formation_assignee = request.user.formation_assignee
        if not formation_assignee or soumission.devoir.formation != formation_assignee.code:
            messages.error(request, "Vous n'avez pas accès à cette soumission.")
            return redirect('dashboard_formateur')
    devoir = soumission.devoir
    apprenant = soumission.apprenant
    reponses = soumission.reponses.select_related('question').order_by('question_id')
    total_questions = devoir.total_questions()

    
    context = {
        'soumission': soumission,
        'devoir': devoir,
        'apprenant': apprenant,
        'reponses': reponses,
        'total_questions': total_questions,
        'note': soumission.note,
    }
    
    return render(request, 'devoirs/detail_soumission_admin.html', context)

      
