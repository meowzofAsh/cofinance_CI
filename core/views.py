from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from decimal import Decimal, InvalidOperation

from django.db import models

from credits.models import Credit
from remboursements.models import Remboursement, RepaymentSchedule
from assurances.models import InsuranceProduct, InsuranceSubscription
from notifications.models import Notification
from support_chat.models import Conversation
from surveys.models import NPSSurvey


# ------------------------------------------------------------------
# AUTH
# ------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        return render(request, "auth/login.html", {"form_errors": True})
    return render(request, "auth/login.html")


def register_view(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name  = request.POST.get("last_name")
        email      = request.POST.get("email")
        phone      = request.POST.get("phone")
        password1  = request.POST.get("password1")
        password2  = request.POST.get("password2")
        errors = {}
        if password1 != password2:
            errors["password"] = "Les mots de passe ne correspondent pas."
        if User.objects.filter(email=email).exists():
            errors["email"] = "Cet email est déjà utilisé."
        if errors:
            return render(request, "auth/register.html", {"form_errors": errors})
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1,
        )
        user.phone_number = phone
        user.save()
        login(request, user)
        return redirect("dashboard")
    return render(request, "auth/register.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ------------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------------

@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if user.is_admin_role:
        # ---- ADMIN ----
        total_clients = User.objects.filter(role=User.CLIENT).count()
        total_agents = User.objects.filter(role=User.AGENT).count()
        total_credits = Credit.objects.count()
        soumis = Credit.objects.filter(status=Credit.SOUMISE).count()
        en_analyse = Credit.objects.filter(status=Credit.EN_ANALYSE).count()
        approuves = Credit.objects.filter(status=Credit.APPROUVEE).count()
        rejetes = Credit.objects.filter(status=Credit.REJETEE).count()
        decaisses = Credit.objects.filter(status=Credit.DECAISSEE).count()

        credits_decaisses_qs = Credit.objects.filter(status=Credit.DECAISSEE)
        montant_total_prete = sum(c.approved_amount for c in credits_decaisses_qs)

        total_rembourse = sum(r.amount_paid for r in Remboursement.objects.all())
        reste_total = montant_total_prete - total_rembourse if montant_total_prete else 0

        taux_approbation = int((approuves / total_credits * 100)) if total_credits else 0
        taux_recouvrement = int((total_rembourse / montant_total_prete * 100)) if montant_total_prete else 0

        actives = InsuranceSubscription.objects.filter(status="ACTIVE").count()
        ouvertes = Conversation.objects.filter(status=Conversation.OPEN).count()

        # Statistiques NPS
        nps_total = NPSSurvey.objects.count()
        nps_promoters = NPSSurvey.objects.filter(score__gte=9).count()
        nps_detractors = NPSSurvey.objects.filter(score__lte=6).count()
        nps_score = round(
            (nps_promoters / nps_total * 100) - (nps_detractors / nps_total * 100), 1
        ) if nps_total else None
        nps_recent = NPSSurvey.objects.select_related("user").order_by("-created_at")[:5]

        # Évolution mensuelle (6 derniers mois)
        mois_evolution = []
        from datetime import datetime
        for i in range(5, -1, -1):
            mois = today.month - i
            annee = today.year
            if mois < 1:
                mois += 12
                annee -= 1
            debut = timezone.make_aware(datetime(annee, mois, 1))
            if mois == 12:
                fin = timezone.make_aware(datetime(annee + 1, 1, 1))
            else:
                fin = timezone.make_aware(datetime(annee, mois + 1, 1))
            crees = Credit.objects.filter(created_at__gte=debut, created_at__lt=fin).count()
            remb = Remboursement.objects.filter(created_at__gte=debut, created_at__lt=fin).count()
            sousc = InsuranceSubscription.objects.filter(created_at__gte=debut, created_at__lt=fin).count()
            mois_evolution.append({
                "mois": f"{mois:02d}/{annee}",
                "credits": crees,
                "remboursements": remb,
                "souscriptions": sousc,
            })

        filter_periode = request.GET.get("periode", "")
        filter_region = request.GET.get("region", "")
        regions = User.objects.filter(role=User.CLIENT).values_list("region", flat=True).distinct()

        stats = {
            "total_clients": total_clients,
            "total_agents": total_agents,
            "total_credits": total_credits,
            "credits_soumis": soumis,
            "en_analyse": en_analyse,
            "approuves": approuves,
            "rejetes": rejetes,
            "decaisses": decaisses,
            "montant_total_prete": f"{montant_total_prete:,.0f}",
            "total_rembourse": f"{total_rembourse:,.0f}",
            "reste_total": f"{reste_total:,.0f}",
            "taux_approbation": taux_approbation,
            "taux_recouvrement": taux_recouvrement,
            "assurances_actives": actives,
            "conversations_ouvertes": ouvertes,
            "nps_score": nps_score,
            "nps_total": nps_total,
            "nps_promoters": nps_promoters,
            "nps_detractors": nps_detractors,
        }

        derniers_credits = Credit.objects.all().order_by("-created_at")[:10]
        dernieres_notifications = Notification.objects.all().order_by("-created_at")[:5]

        return render(request, "dashboard/dashboard_admin.html", {
            "stats": stats,
            "derniers_credits": derniers_credits,
            "dernieres_notifications": dernieres_notifications,
            "mois_evolution": mois_evolution,
            "regions": regions,
            "filter_periode": filter_periode,
            "filter_region": filter_region,
            "nps_recent": nps_recent,
        })

    elif user.is_agent:
        # ---- AGENT ----
        total_clients = User.objects.filter(role=User.CLIENT).count()
        a_traiter = Credit.objects.filter(status__in=[Credit.SOUMISE, Credit.EN_ANALYSE]).count()
        ouvertes = Conversation.objects.filter(status=Conversation.OPEN).count()

        total_credits = Credit.objects.count()
        total_decaisses = Credit.objects.filter(status=Credit.DECAISSEE).count()
        total_remboursements = Remboursement.objects.count()
        souscriptions_actives = InsuranceSubscription.objects.filter(status="ACTIVE").count()
        credit_moyen = Credit.objects.filter(status=Credit.DECAISSEE).aggregate(
            avg=models.Avg("approved_amount")
        )["avg"] or 0

        credits_a_traiter = Credit.objects.filter(
            status__in=[Credit.SOUMISE, Credit.EN_ANALYSE]
        ).order_by("-created_at")[:10]

        derniers_remboursements = Remboursement.objects.select_related(
            "credit__client"
        ).order_by("-created_at")[:10]

        stats = {
            "total_clients": total_clients,
            "credits_a_traiter": a_traiter,
            "conversations_ouvertes": ouvertes,
            "total_credits": total_credits,
            "total_decaisses": total_decaisses,
            "total_remboursements": total_remboursements,
            "souscriptions_actives": souscriptions_actives,
            "credit_moyen": f"{credit_moyen:,.0f}",
        }

        return render(request, "dashboard/dashboard_agent.html", {
            "stats": stats,
            "credits_a_traiter": credits_a_traiter,
            "derniers_remboursements": derniers_remboursements,
        })

    else:
        # ---- CLIENT ----
        credits_actifs = Credit.objects.filter(client=user, status__in=[
            Credit.SOUMISE, Credit.EN_ANALYSE, Credit.APPROUVEE, Credit.DECAISSEE
        ]).count()
        credits_decaisses = Credit.objects.filter(client=user, status=Credit.DECAISSEE)
        montant_total = sum(c.approved_amount for c in credits_decaisses)
        nb_rembours = Remboursement.objects.filter(credit__client=user).count()
        nb_assurances = InsuranceSubscription.objects.filter(client=user, status="ACTIVE").count()

        total_paye_client = sum(r.amount_paid for r in Remboursement.objects.filter(credit__client=user))
        reste_client = montant_total - total_paye_client

        prochaine_echeance = None
        from remboursements.models import RepaymentSchedule
        echeances = RepaymentSchedule.objects.filter(
            credit__client=user,
            status=RepaymentSchedule.EN_ATTENTE,
        ).order_by("due_date")
        if echeances.exists():
            prochaine_echeance = echeances.first()

        derniers_credits = Credit.objects.filter(client=user).order_by("-created_at")[:5]
        dernieres_notifications = Notification.objects.filter(user=user).order_by("-created_at")[:5]

        stats = {
            "credits_actifs": credits_actifs,
            "total_decaisse": f"{montant_total:,.0f}",
            "remboursements": nb_rembours,
            "assurances": nb_assurances,
            "total_paye": f"{total_paye_client:,.0f}",
            "reste": f"{reste_client:,.0f}",
        }

        return render(request, "dashboard/dashboard.html", {
            "stats": stats,
            "derniers_credits": derniers_credits,
            "dernieres_notifications": dernieres_notifications,
            "prochaine_echeance": prochaine_echeance,
        })


# ------------------------------------------------------------------
# PROFIL
# ------------------------------------------------------------------

@login_required
def profile(request):
    if request.method == "POST":
        user = request.user
        user.first_name   = request.POST.get("first_name", user.first_name)
        user.last_name    = request.POST.get("last_name", user.last_name)
        user.phone_number = request.POST.get("phone_number", user.phone_number)
        user.address      = request.POST.get("address", user.address)
        user.save()
        return redirect("profile")
    return render(request, "auth/profile.html")


# ------------------------------------------------------------------
# CREDITS
# ------------------------------------------------------------------

@login_required
def credits(request):
    user = request.user
    if user.role in ["ADMIN", "AGENT"]:
        object_list = Credit.objects.all().order_by("-created_at")
    else:
        object_list = Credit.objects.filter(client=user).order_by("-created_at")
    return render(request, "credits/list.html", {"object_list": object_list})


@login_required
def credit_create(request):
    if request.method == "POST":
        Credit.objects.create(
            client        = request.user,
            amount        = request.POST.get("amount"),
            duration      = request.POST.get("duration"),
            purpose       = request.POST.get("purpose"),
            monthly_income= request.POST.get("monthly_income"),
        )
        return redirect("credit_list")
    return render(request, "credits/create.html")


@login_required
def credit_detail(request, pk):
    user = request.user
    if user.role in ["ADMIN", "AGENT"]:
        credit = get_object_or_404(Credit, pk=pk)
    else:
        credit = get_object_or_404(Credit, pk=pk, client=user)

    remboursements = credit.remboursements.all()
    schedules = credit.schedules.all().order_by("due_date")

    total_paye = sum(r.amount_paid for r in remboursements)
    total_du = sum(s.amount_due for s in schedules)
    montant_reference = total_du if total_du else credit.amount
    progression = int((total_paye / montant_reference * 100)) if montant_reference else 0
    reste = montant_reference - total_paye

    # Stats pour l'échéancier
    echeances_payees = schedules.filter(status=RepaymentSchedule.PAYEE).count()
    echeances_retard = schedules.filter(status=RepaymentSchedule.RETARD).count()
    echeances_total = schedules.count()

    return render(request, "credits/detail.html", {
        "object": credit,
        "schedules": schedules,
        "progression": progression,
        "reste": reste,
        "total_paye": total_paye,
        "montant_reference": montant_reference,
        "echeances_payees": echeances_payees,
        "echeances_retard": echeances_retard,
        "echeances_total": echeances_total,
    })


@login_required
def credit_update(request, pk):
    user = request.user
    if user.role in ["ADMIN", "AGENT"]:
        credit = get_object_or_404(Credit, pk=pk)
    else:
        credit = get_object_or_404(Credit, pk=pk, client=user)

    if request.method == "POST":
        credit.amount         = request.POST.get("amount", credit.amount)
        credit.duration       = request.POST.get("duration", credit.duration)
        credit.purpose        = request.POST.get("purpose", credit.purpose)
        credit.monthly_income = request.POST.get("monthly_income", credit.monthly_income)
        credit.save()
        return redirect("credit_detail", pk=credit.pk)
    return render(request, "credits/update.html", {"credit": credit})
# ------------------------------------------------------------------
# REMBOURSEMENTS
# ------------------------------------------------------------------

@login_required
def remboursements(request):
    user = request.user
    is_staff = user.role in ["ADMIN", "AGENT"]

    if request.method == "POST":
        credit_pk = request.POST.get("credit")
        schedule_pk = request.POST.get("schedule")
        montant = request.POST.get("montant")

        credit = get_object_or_404(Credit, pk=credit_pk)

        if not is_staff and credit.client != user:
            return redirect("remboursement_list")

        if not montant:
            return render(request, "remboursements/list.html", {
                "form_errors": "Veuillez entrer un montant.",
            })

        try:
            montant_dec = Decimal(str(montant))
        except InvalidOperation:
            montant_dec = Decimal("0")

        schedule = None
        if schedule_pk:
            try:
                schedule = RepaymentSchedule.objects.get(pk=schedule_pk, credit=credit)
            except RepaymentSchedule.DoesNotExist:
                pass

        Remboursement.objects.create(
            credit=credit,
            schedule=schedule,
            amount_paid=montant_dec,
            payment_date=timezone.now().date(),
            comments=request.POST.get("comments", ""),
        )
        return redirect("remboursement_list")

    # GET : liste des remboursements
    if is_staff:
        object_list = Remboursement.objects.all().order_by("-payment_date")
        credits_dispo = list(Credit.objects.filter(status=Credit.DECAISSEE).order_by("-created_at"))
    else:
        object_list = Remboursement.objects.filter(credit__client=user).order_by("-payment_date")
        credits_dispo = list(Credit.objects.filter(client=user, status=Credit.DECAISSEE).order_by("-created_at"))

    for c in credits_dispo:
        total_paye_c = sum(r.amount_paid for r in c.remboursements.all())
        total_du_c = sum(s.amount_due for s in c.schedules.all())
        c.reste = (total_du_c if total_du_c else c.approved_amount or c.amount) - total_paye_c
        c.schedules_list = c.schedules.all().order_by("due_date")

    total_recu = sum(r.amount_paid for r in object_list)

    return render(request, "remboursements/list.html", {
        "object_list": object_list,
        "credits_dispo": credits_dispo,
        "stats": {"recus": f"{total_recu:,.0f}"},
    })


# ------------------------------------------------------------------
# ASSURANCES
# ------------------------------------------------------------------

@login_required
def assurances(request):
    products = InsuranceProduct.objects.all()
    if request.user.role in ["ADMIN", "AGENT"]:
        subscriptions = InsuranceSubscription.objects.select_related("client", "product").all()
    else:
        subscriptions = InsuranceSubscription.objects.filter(client=request.user).select_related("product")
    return render(request, "assurances/list.html", {
        "products": products,
        "subscriptions": subscriptions,
    })


@login_required
def assurance_subscribe(request, pk):
    product = get_object_or_404(InsuranceProduct, pk=pk)
    if request.method == "POST":
        from datetime import date, timedelta
        start = date.today()
        end = start + timedelta(days=product.duration_days)
        sub = InsuranceSubscription.objects.create(
            client=request.user,
            product=product,
            start_date=start,
            end_date=end,
        )
        return redirect("assurance_list")
    return render(request, "assurances/subscribe.html", {"product": product})


# ------------------------------------------------------------------
# NOTIFICATIONS
# ------------------------------------------------------------------

@login_required
def notifications(request):
    object_list  = Notification.objects.filter(user=request.user)
    unread_count = object_list.filter(is_read=False).count()
    return render(request, "notifications/list.html", {
        "object_list":  object_list,
        "unread_count": unread_count,
    })


@login_required
def notification_mark_all(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("notification_list")


# ------------------------------------------------------------------
# CHAT
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# NPS SURVEY
# ------------------------------------------------------------------

@login_required
def nps_submit(request):
    if request.method == "POST":
        score = request.POST.get("score")
        comment = request.POST.get("comment", "")
        context_type = request.POST.get("context_type", "CREDIT")
        context_id = request.POST.get("context_id")
        try:
            NPSSurvey.objects.create(
                user=request.user,
                score=int(score),
                comment=comment,
                context_type=context_type,
                context_id=int(context_id) if context_id else None,
            )
        except (ValueError, TypeError):
            pass
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


# ------------------------------------------------------------------
# CHAT
# ------------------------------------------------------------------

@login_required
def chat_conversations(request):
    if request.method == "POST" and request.user.role == "CLIENT":
        conv = Conversation.objects.create(client=request.user)
        return redirect("chat_room", pk=conv.id)

    if request.user.role in ["ADMIN", "AGENT"]:
        conversations = Conversation.objects.all()
    else:
        conversations = Conversation.objects.filter(client=request.user)
    return render(request, "chat/conversations.html", {"conversations": conversations})


@login_required
def support_chat(request, pk):
    from support_chat.models import Conversation, Message
    
    # L'admin/agent a le droit de voir toutes les conversations
    if request.user.role in ["ADMIN", "AGENT"]:
        conversation = get_object_or_404(Conversation, pk=pk)
        conversations = Conversation.objects.all()
    else:
        conversation = get_object_or_404(Conversation, pk=pk, client=request.user)
        conversations = Conversation.objects.filter(client=request.user)
        
    # Fallback HTTP POST si WebSocket indisponible
    if request.method == "POST":
        content = request.POST.get("message", "").strip()
        if content:
            msg = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
            )
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                from django.http import JsonResponse
                return JsonResponse({
                    "id": msg.id,
                    "content": msg.content,
                    "sender_id": msg.sender_id,
                    "time": msg.sent_at.strftime("%H:%M"),
                })
        return redirect("chat_room", pk=pk)
        
    messages_list = conversation.messages.all()
    return render(request, "chat/room.html", {
        "conversation":  conversation,
        "messages_list": messages_list,
        "conversations": conversations,
    })

# ------------------------------------------------------------------
# ADMIN PANEL VIEWS
# ------------------------------------------------------------------

@login_required
def admin_users(request):
    if not request.user.is_admin_role:
        return redirect("dashboard")
    from django.contrib.auth import get_user_model
    User = get_user_model()
    agents = User.objects.filter(role=User.AGENT)
    clients = User.objects.filter(role=User.CLIENT)
    return render(request, "admin_panel/users.html", {"agents": agents, "clients": clients})

@login_required
def admin_credits(request):
    if not request.user.is_admin_role:
        return redirect("dashboard")
    credits_list = Credit.objects.all().order_by("-created_at")
    return render(request, "admin_panel/credits.html", {"credits_list": credits_list})

@login_required
def credit_change_status(request, pk):
    if request.user.role not in ["ADMIN", "AGENT"]:
        return redirect("dashboard")
    credit = get_object_or_404(Credit, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Credit.STATUS_CHOICES):
            credit.status = new_status
            if new_status == Credit.DECAISSEE and credit.approved_amount == 0:
                credit.approved_amount = credit.amount
            if new_status == Credit.REJETEE:
                credit.notes = (
                    request.POST.get("notes", "")
                    or "Demande rejetée"
                )
            credit.save()
    return redirect("admin_credits" if request.user.is_admin_role else "dashboard")