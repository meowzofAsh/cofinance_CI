from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from credits.models import Credit
from assurances.models import InsuranceProduct, InsuranceSubscription
from notifications.models import Notification
from support_chat.models import Conversation, Message

User = get_user_model()


class Command(BaseCommand):
    help = "Peuple la base de données avec des données de démonstration"

    def handle(self, *args, **options):
        self.stdout.write("Création des données de démonstration...\n")

        # --- Utilisateurs ---
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@cofinance.ci",
                "first_name": "Admin",
                "last_name": "COFINANCE",
                "role": User.ADMIN,
                "phone_number": "+2250101020304",
                "is_verified": True,
            },
        )
        admin.set_password("admin123")
        admin.save()

        agent, _ = User.objects.get_or_create(
            username="agent1",
            defaults={
                "email": "agent1@cofinance.ci",
                "first_name": "Koffi",
                "last_name": "Koné",
                "role": User.AGENT,
                "phone_number": "+2250505060708",
                "is_verified": True,
                "region": "Abidjan",
            },
        )
        agent.set_password("agent123")
        agent.save()

        clients_data = [
            {
                "username": "client1",
                "email": "client1@example.com",
                "first_name": "Aminata",
                "last_name": "Diallo",
                "phone_number": "+2250708091011",
                "region": "Abidjan",
                "address": "Cocody, Angré",
            },
            {
                "username": "client2",
                "email": "client2@example.com",
                "first_name": "Mamadou",
                "last_name": "Traoré",
                "phone_number": "+2250712131415",
                "region": "Bouaké",
                "address": "Bouaké, Centre",
            },
            {
                "username": "client3",
                "email": "client3@example.com",
                "first_name": "Fatou",
                "last_name": "Sow",
                "phone_number": "+2250716171819",
                "region": "Yamoussoukro",
                "address": "Yamoussoukro, Quartier Administration",
            },
        ]

        clients = []
        for cdata in clients_data:
            client, _ = User.objects.get_or_create(
                username=cdata["username"],
                defaults={
                    "email": cdata["email"],
                    "first_name": cdata["first_name"],
                    "last_name": cdata["last_name"],
                    "role": User.CLIENT,
                    "phone_number": cdata["phone_number"],
                    "region": cdata["region"],
                    "address": cdata["address"],
                    "is_verified": True,
                },
            )
            client.set_password("client123")
            client.save()
            clients.append(client)

        # --- Produits d'assurance ---
        products_data = [
            {
                "name": "Assurance Vie Essentielle",
                "description": "Protection vie de base avec couverture décès et invalidité permanente.",
                "price": Decimal("2500"),
                "duration_days": 365,
            },
            {
                "name": "Assurance Décès-Invalidité Plus",
                "description": "Couverture renforcée incluant décès accidentel, invalidité totale et frais d'hospitalisation.",
                "price": Decimal("5000"),
                "duration_days": 365,
            },
            {
                "name": "Assurance Micro-Entrepreneur",
                "description": "Protection pour micro-entrepreneurs avec couverture du matériel professionnel.",
                "price": Decimal("7500"),
                "duration_days": 180,
            },
            {
                "name": "Assurance Agricole",
                "description": "Couverture des récoltes et du bétail pour les agriculteurs.",
                "price": Decimal("3500"),
                "duration_days": 180,
            },
        ]

        products = []
        for pd in products_data:
            product, _ = InsuranceProduct.objects.get_or_create(
                name=pd["name"],
                defaults=pd,
            )
            products.append(product)

        # --- Crédits ---
        credits_data = [
            {
                "client": clients[0],
                "amount": Decimal("200000"),
                "duration": 6,
                "purpose": "Achat de marchandises pour revente",
                "monthly_income": Decimal("150000"),
                "status": Credit.DECAISSEE,
                "approved_amount": Decimal("180000"),
                "interest_rate": Decimal("5.00"),
                "repayment_start_date": date.today() - timedelta(days=60),
            },
            {
                "client": clients[0],
                "amount": Decimal("350000"),
                "duration": 12,
                "purpose": "Agrandissement de boutique",
                "monthly_income": Decimal("250000"),
                "status": Credit.APPROUVEE,
                "approved_amount": Decimal("300000"),
                "interest_rate": Decimal("5.00"),
            },
            {
                "client": clients[1],
                "amount": Decimal("150000"),
                "duration": 3,
                "purpose": "Achat de semences et engrais",
                "monthly_income": Decimal("100000"),
                "status": Credit.EN_ANALYSE,
                "interest_rate": Decimal("5.00"),
            },
            {
                "client": clients[2],
                "amount": Decimal("500000"),
                "duration": 12,
                "purpose": "Financement équipement cuisine",
                "monthly_income": Decimal("400000"),
                "status": Credit.SOUMISE,
                "interest_rate": Decimal("5.00"),
            },
        ]

        for cd in credits_data:
            credit = Credit.objects.create(**cd)
            credit.eligibility_score = credit.calculate_eligibility_score()
            credit.save()

        # --- Souscriptions assurance ---
        today = date.today()
        InsuranceSubscription.objects.get_or_create(
            client=clients[0],
            product=products[0],
            defaults={
                "start_date": today - timedelta(days=30),
                "end_date": today + timedelta(days=335),
                "status": InsuranceSubscription.ACTIVE,
            },
        )
        InsuranceSubscription.objects.get_or_create(
            client=clients[0],
            product=products[1],
            defaults={
                "start_date": today - timedelta(days=150),
                "end_date": today + timedelta(days=215),
                "status": InsuranceSubscription.ACTIVE,
            },
        )
        InsuranceSubscription.objects.get_or_create(
            client=clients[1],
            product=products[2],
            defaults={
                "start_date": today - timedelta(days=200),
                "end_date": today - timedelta(days=20),
                "status": InsuranceSubscription.EXPIRED,
            },
        )

        # --- Notifications ---
        Notification.objects.get_or_create(
            user=clients[0],
            title="Bienvenue sur COFINANCE CI",
            defaults={
                "message": "Merci d'avoir rejoint notre plateforme de microfinance et d'assurance mobile.",
                "is_read": True,
            },
        )
        Notification.objects.get_or_create(
            user=clients[1],
            title="Bienvenue sur COFINANCE CI",
            defaults={
                "message": "Merci d'avoir rejoint notre plateforme.",
                "is_read": False,
            },
        )

        # --- Conversations ---
        conv, _ = Conversation.objects.get_or_create(
            client=clients[0],
            defaults={
                "agent": agent,
                "status": Conversation.OPEN,
            },
        )
        if conv.messages.count() == 0:
            Message.objects.create(
                conversation=conv,
                sender=clients[0],
                content="Bonjour, je souhaite des informations sur le remboursement de mon crédit.",
            )
            Message.objects.create(
                conversation=conv,
                sender=agent,
                content="Bonjour Aminata. Votre crédit #1 a été décaissé il y a 2 mois. Il vous reste 3 échéances. Puis-je vous aider ?",
            )

        self.stdout.write(self.style.SUCCESS(
            "Données de démonstration créées avec succès !\n\n"
            "Connexions de test :\n"
            "  Admin :   admin / admin123\n"
            "  Agent :   agent1 / agent123\n"
            "  Client 1 : client1 / client123\n"
            "  Client 2 : client2 / client123\n"
            "  Client 3 : client3 / client123\n"
        ))
