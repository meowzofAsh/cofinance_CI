from django.shortcuts import render


def login_view(request):
    return render(request, "auth/login.html")


def register_view(request):
    return render(request, "auth/register.html")


def profile(request):
    return render(request, "auth/profile.html")


def dashboard(request):
    return render(request, "dashboard/dashboard.html")


def credits(request):
    return render(request, "credits/list.html")


def credit_create(request):
    return render(request, "credits/create.html")


def credit_detail(request, pk):
    return render(request, "credits/detail.html")


def credit_update(request, pk):
    return render(request, "credits/update.html")


def remboursements(request):
    return render(request, "remboursements/list.html")


def assurances(request):
    return render(request, "assurances/list.html")


def notifications(request):
    return render(request, "notifications/list.html")


def support_chat(request):
    return render(request, "chat/room.html")