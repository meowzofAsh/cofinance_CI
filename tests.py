"""
Tests unitaires COFINANCE CI
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# ================================================================
# MODELS
# ================================================================

class TestUserModel(TestCase):
    """Test du modèle User"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testclient",
            password="testpass123",
            role=User.CLIENT,
            phone_number="+2250101020304",
        )

    def test_user_creation(self):
        assert self.user.role == "CLIENT"
        assert self.user.is_client is True
        assert self.user.is_agent is False
        assert self.user.is_admin_role is False
        assert str(self.user) == "testclient (CLIENT)"

    def test_full_name_property(self):
        self.user.first_name = "Jean"
        self.user.last_name = "Kouassi"
        self.user.save()
        assert self.user.full_name == "Jean Kouassi"
        assert self.user.full_name.strip() != ""

    def test_notifications_count(self):
        from notifications.models import Notification
        Notification.objects.create(user=self.user, title="Test", message="Hello")
        assert self.user.notifications_count == 1
        n = Notification.objects.get(user=self.user)
        n.is_read = True
        n.save()
        # invalidé car propriété recalcule à chaque appel
        assert self.user.notifications_count == 0

    def test_is_online_default(self):
        assert self.user.is_online is False
        assert self.user.last_seen is None


class TestCreditModel(TestCase):
    """Test du modèle Credit"""

    def setUp(self):
        self.client_user = User.objects.create_user(
            username="emile", password="pass", role=User.CLIENT
        )

    def test_create_credit(self):
        from credits.models import Credit
        c = Credit.objects.create(
            client=self.client_user,
            amount=Decimal("500000"),
            duration=6,
            purpose="Achat matériel",
            monthly_income=Decimal("300000"),
        )
        assert c.status == Credit.SOUMISE
        assert c.eligibility_score == 0
        assert str(c) == f"Crédit #{c.id} - emile"

    def test_eligibility_score_higher_income(self):
        from credits.models import Credit
        c = Credit.objects.create(
            client=self.client_user,
            amount=Decimal("200000"),
            duration=6,
            purpose="Test",
            monthly_income=Decimal("500000"),
        )
        score = c.calculate_eligibility_score()
        assert score == 100  # 50 + 30 (revenu > montant) + 20 (durée ≤ 6)

    def test_eligibility_score_low_income(self):
        from credits.models import Credit
        c = Credit.objects.create(
            client=self.client_user,
            amount=Decimal("1000000"),
            duration=12,
            purpose="Test",
            monthly_income=Decimal("100000"),
        )
        score = c.calculate_eligibility_score()
        assert score == 50  # seulement le socle


class TestRepaymentSchedule(TestCase):
    """Test du modèle RepaymentSchedule"""

    def setUp(self):
        user = User.objects.create_user(username="client", password="pass", role=User.CLIENT)
        from credits.models import Credit
        self.credit = Credit.objects.create(
            client=user, amount=Decimal("300000"), duration=3,
            purpose="Test", monthly_income=Decimal("200000"),
        )
        # Passer en décaissé pour déclencher le signal une fois
        self.credit.status = Credit.DECAISSEE
        self.credit.approved_amount = Decimal("300000")
        self.credit.repayment_start_date = date.today()
        self.credit.save()

    def test_generate_schedules(self):
        from remboursements.models import RepaymentSchedule
        schedules = list(self.credit.schedules.all())
        assert len(schedules) == 3
        for s in schedules:
            assert s.amount_due > 0
            assert s.status == "EN_ATTENTE"

    def test_penalty_calculation(self):
        from remboursements.models import RepaymentSchedule
        s = RepaymentSchedule.objects.create(
            credit=self.credit,
            due_date=date.today() - timedelta(days=10),
            amount_due=Decimal("100000"),
        )
        assert s.days_late == 10
        expected = Decimal("100000") * Decimal("0.01") * Decimal("10")
        assert s.penalty == expected


class TestInsuranceSubscription(TestCase):
    """Test du modèle InsuranceSubscription"""

    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client", password="pass", role=User.CLIENT
        )
        from assurances.models import InsuranceProduct
        self.product = InsuranceProduct.objects.create(
            name="Assurance Santé", description="Couverture médicale",
            price=Decimal("5000"), duration_days=30,
        )

    def test_subscription_creation(self):
        from assurances.models import InsuranceSubscription
        sub = InsuranceSubscription.objects.create(
            client=self.client_user, product=self.product,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
        )
        assert sub.status == "ACTIVE"
        assert "Assurance Santé" in str(sub)


class TestConversation(TestCase):
    """Test du modèle Conversation"""

    def setUp(self):
        User = get_user_model()
        self.client_user = User.objects.create_user(
            username="client_chat", password="pass", role=User.CLIENT
        )

    def test_create_conversation(self):
        from support_chat.models import Conversation, Message
        conv = Conversation.objects.create(client=self.client_user)
        assert conv.status == Conversation.OPEN
        assert conv.agent is None
        assert conv.client_name == "client_chat"
        assert conv.agent_name == "Non assigné"

        msg = Message.objects.create(conversation=conv, sender=self.client_user, content="Bonjour")
        assert conv.last_message == msg


# ================================================================
# API VIEWS
# ================================================================

class TestCreditAPI(TestCase):
    """Test des endpoints API Crédits"""

    def setUp(self):
        self.client_user = User.objects.create_user(
            username="apiclient", password="pass", role=User.CLIENT
        )
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.client_user)
        self.token = str(refresh.access_token)
        self.auth_header = f"Bearer {self.token}"

    def test_create_credit_api(self):
        resp = self.client.post(
            "/api/credits/",
            {"amount": "250000", "duration": 6, "purpose": "Test API", "monthly_income": "150000"},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.auth_header,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "SOUMISE"

    def test_list_credits_authenticated(self):
        resp = self.client.get("/api/credits/list/", HTTP_AUTHORIZATION=self.auth_header)
        assert resp.status_code == 200

    def test_list_credits_unauthenticated(self):
        resp = self.client.get("/api/credits/list/")
        assert resp.status_code == 401


class TestAuthAPI(TestCase):
    """Test de l'authentification JWT"""

    def setUp(self):
        User = get_user_model()
        User.objects.create_user(username="logintest", password="secret123", role=User.CLIENT)

    def test_obtain_token(self):
        resp = self.client.post(
            "/api/accounts/login/",
            {"username": "logintest", "password": "secret123"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert "access" in resp.json()
        assert "refresh" in resp.json()

    def test_obtain_token_invalid(self):
        resp = self.client.post(
            "/api/accounts/login/",
            {"username": "logintest", "password": "wrong"},
            content_type="application/json",
        )
        assert resp.status_code == 401


class TestNotificationModel(TestCase):
    """Test du modèle Notification"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="notifuser", password="pass", role=User.CLIENT
        )

    def test_create_notification(self):
        from notifications.models import Notification
        n = Notification.objects.create(
            user=self.user, title="Test", message="Message de test"
        )
        assert n.is_read is False
        assert str(n) == "Test"
        assert n.created_at is not None


# ================================================================
# NPS
# ================================================================

class TestNPSSurvey(TestCase):
    """Tests du modèle et de l'API NPS"""

    def setUp(self):
        self.client_user = User.objects.create_user(
            username="npsclient", password="pass", role=User.CLIENT
        )
        from rest_framework_simplejwt.tokens import RefreshToken
        self.token = str(RefreshToken.for_user(self.client_user).access_token)
        self.auth = f"Bearer {self.token}"

    def test_nps_model_category_promoteur(self):
        from surveys.models import NPSSurvey
        s = NPSSurvey.objects.create(user=self.client_user, score=10, context_type="CREDIT")
        assert s.category == "Promoteur"
        assert s.category_class == "badge-success"

    def test_nps_model_category_passif(self):
        from surveys.models import NPSSurvey
        s = NPSSurvey.objects.create(user=self.client_user, score=7, context_type="CREDIT")
        assert s.category == "Passif"
        assert s.category_class == "badge-warning"

    def test_nps_model_category_detracteur(self):
        from surveys.models import NPSSurvey
        s = NPSSurvey.objects.create(user=self.client_user, score=4, context_type="CREDIT")
        assert s.category == "Détracteur"
        assert s.category_class == "badge-danger"

    def test_nps_create_api(self):
        resp = self.client.post(
            "/api/surveys/",
            {"score": 9, "context_type": "CREDIT", "comment": "Très bon service"},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.auth,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["score"] == 9
        assert data["context_type"] == "CREDIT"

    def test_nps_create_api_unauthenticated(self):
        resp = self.client.post(
            "/api/surveys/",
            {"score": 9, "context_type": "CREDIT"},
            content_type="application/json",
        )
        assert resp.status_code == 401

    def test_nps_list_api(self):
        from surveys.models import NPSSurvey
        NPSSurvey.objects.create(user=self.client_user, score=8, context_type="CHAT")
        resp = self.client.get("/api/surveys/list/", HTTP_AUTHORIZATION=self.auth)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert len(data["results"]) == 1

    def test_nps_dashboard_api(self):
        from surveys.models import NPSSurvey
        admin = User.objects.create_superuser(
            username="npsadmin", password="adminpass", role=User.ADMIN
        )
        from rest_framework_simplejwt.tokens import RefreshToken
        admin_token = str(RefreshToken.for_user(admin).access_token)
        for score in [10, 9, 8, 6, 3]:
            NPSSurvey.objects.create(user=self.client_user, score=score, context_type="CREDIT")
        resp = self.client.get(
            "/api/surveys/dashboard/",
            HTTP_AUTHORIZATION=f"Bearer {admin_token}",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_responses"] == 5
        assert data["promoters"] == 2
        assert data["passives"] == 1
        assert data["detractors"] == 2
        assert data["nps_score"] is not None

    def test_nps_signal_credit_decaissement(self):
        """Vérifie qu'un décaissement de crédit crée un sondage NPS"""
        from credits.models import Credit
        from surveys.models import NPSSurvey
        c = Credit.objects.create(
            client=self.client_user, amount=Decimal("100000"),
            duration=3, purpose="Test", monthly_income=Decimal("200000"),
        )
        c.status = Credit.DECAISSEE
        c.approved_amount = Decimal("100000")
        c.repayment_start_date = date.today()
        c.save()
        assert NPSSurvey.objects.filter(
            context_type="CREDIT", context_id=c.pk
        ).exists()

    def test_nps_signal_assurance_souscription(self):
        """Vérifie qu'une souscription d'assurance crée un sondage NPS"""
        from assurances.models import InsuranceProduct, InsuranceSubscription
        from surveys.models import NPSSurvey
        product = InsuranceProduct.objects.create(
            name="Assurance Test", description="Test",
            price=Decimal("1000"), duration_days=30,
        )
        sub = InsuranceSubscription.objects.create(
            client=self.client_user, product=product,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
        )
        assert NPSSurvey.objects.filter(
            context_type="ASSURANCE", user=self.client_user
        ).exists()

    def test_nps_signal_chat_fermeture(self):
        """Vérifie que la fermeture d'un chat crée un sondage NPS"""
        from support_chat.models import Conversation
        from surveys.models import NPSSurvey
        conv = Conversation.objects.create(client=self.client_user)
        conv.status = Conversation.CLOSED
        conv.save()
        assert NPSSurvey.objects.filter(
            context_type="CHAT", context_id=conv.pk
        ).exists()
