from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from accounts.models import Apprenant, Formation
from devoirs.models import Devoir, Question, Soumission
from accounts.views import admin_dashboard, dashboard_formateur, tableau_de_bord
from devoirs.views import gerer_devoir, passer_devoir, soumettre_devoir, telecharger_devoir_pdf


class RoleBasedAccessControlTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # 1. Création des formations
        self.formation_web = Formation.objects.create(
            code='dev-web',
            nom='Développement Web',
            est_active=True
        )
        self.formation_bureau = Formation.objects.create(
            code='bureautique',
            nom='Bureautique Pro',
            est_active=True
        )

        # 2. Utilisateur Super-Admin
        self.admin = Apprenant.objects.create_superuser(
            whatsapp='+22670000001',
            password='AdminPassword123!',
            nom='Admin',
            prenom='Principal'
        )

        # 3. Formateur Web
        self.formateur_web = Apprenant.objects.create_user(
            whatsapp='+22670000002',
            password='FormateurPassword123!',
            nom='Traore',
            prenom='Formateur',
            is_formateur=True,
            formation_assignee=self.formation_web,
            formation='dev-web'
        )

        # 4. Apprenant Web
        self.apprenant_web = Apprenant.objects.create_user(
            whatsapp='+22670000003',
            password='StudentPassword123!',
            nom='Ouedraogo',
            prenom='Eleve',
            formation='dev-web',
            session='janvier'
        )

        # 5. Devoir pour Dev Web
        self.devoir_web = Devoir.objects.create(
            titre='QCM HTML & CSS',
            formation='dev-web',
            session='janvier',
            est_actif=True
        )
        self.q1 = Question.objects.create(
            devoir=self.devoir_web,
            texte='Que signifie HTML ?',
            choix_a='Hyper Text Markup Language',
            choix_b='High Text Machine Language',
            choix_c='Hyper Transfer Protocol',
            choix_d='Home Tool Markup Language',
            bonne_reponse='A',
            justification='HTML = Hyper Text Markup Language.',
            ordre=1
        )

        # 6. Devoir pour Bureautique
        self.devoir_bureau = Devoir.objects.create(
            titre='Test Excel Avancé',
            formation='bureautique',
            session='janvier',
            est_actif=True
        )

    def _setup_request(self, request, user):
        request.user = user
        request.session = SessionStore()
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_apprenant_cannot_access_admin_panel(self):
        """Un apprenant est bloqué et redirigé hors du panel admin."""
        request = self.factory.get('/admin-panel/')
        self._setup_request(request, self.apprenant_web)
        response = admin_dashboard(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/tableau-de-bord/')

    def test_apprenant_cannot_access_formateur_space(self):
        """Un apprenant est bloqué et redirigé hors de l'espace formateur."""
        request = self.factory.get('/espace-formateur/')
        self._setup_request(request, self.apprenant_web)
        response = dashboard_formateur(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/tableau-de-bord/')

    def test_formateur_cannot_access_other_formation_devoirs(self):
        """Un formateur ne peut pas gérer un devoir d'une autre filière."""
        request = self.factory.get(f'/devoirs/{self.devoir_bureau.pk}/gerer/')
        self._setup_request(request, self.formateur_web)
        response = gerer_devoir(request, pk=self.devoir_bureau.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/espace-formateur/')

    def test_formateur_can_manage_own_formation_devoir(self):
        """Un formateur peut gérer le devoir de sa filière assignée."""
        request = self.factory.get(f'/devoirs/{self.devoir_web.pk}/gerer/')
        self._setup_request(request, self.formateur_web)
        response = gerer_devoir(request, pk=self.devoir_web.pk)
        self.assertEqual(response.status_code, 200)

    def test_apprenant_passer_et_soumettre_devoir(self):
        """L'apprenant passe son devoir et télécharge son PDF de correction."""
        # 1. Accès au devoir
        req_passer = self.factory.get(f'/devoirs/{self.devoir_web.pk}/')
        self._setup_request(req_passer, self.apprenant_web)
        resp_passer = passer_devoir(req_passer, pk=self.devoir_web.pk)
        self.assertEqual(resp_passer.status_code, 200)

        # 2. Soumission
        req_submit = self.factory.post(
            f'/devoirs/{self.devoir_web.pk}/soumettre/',
            {f'question_{self.q1.id}': 'A'}
        )
        self._setup_request(req_submit, self.apprenant_web)
        resp_submit = soumettre_devoir(req_submit, pk=self.devoir_web.pk)
        self.assertEqual(resp_submit.status_code, 302)

        # 3. Vérification note
        soumission = Soumission.objects.get(apprenant=self.apprenant_web, devoir=self.devoir_web)
        self.assertEqual(soumission.note, 1)

        # 4. Téléchargement PDF
        req_pdf = self.factory.get(f'/devoirs/{self.devoir_web.pk}/pdf/')
        self._setup_request(req_pdf, self.apprenant_web)
        resp_pdf = telecharger_devoir_pdf(req_pdf, pk=self.devoir_web.pk)
        self.assertEqual(resp_pdf.status_code, 200)
        self.assertEqual(resp_pdf['Content-Type'], 'application/pdf')
