from rest_framework import serializers


class DashboardSerializer(serializers.Serializer):
    total_clients = serializers.IntegerField()
    total_agents = serializers.IntegerField()
    total_credits = serializers.IntegerField()
    soumis = serializers.IntegerField()
    en_analyse = serializers.IntegerField()
    approuves = serializers.IntegerField()
    rejetes = serializers.IntegerField()
    decaisses = serializers.IntegerField()
    montant_total_prete = serializers.CharField()
    total_rembourse = serializers.CharField()
    taux_approbation = serializers.IntegerField()
    taux_recouvrement = serializers.IntegerField()
    assurances_actives = serializers.IntegerField()
    conversations_ouvertes = serializers.IntegerField()
    evolution = serializers.ListField()
    regions = serializers.ListField()
