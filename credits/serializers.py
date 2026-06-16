# credits/serializers.py

from rest_framework import serializers

from .models import Credit


class CreditSerializer(serializers.ModelSerializer):
    """
    Serializer principal des microcrédits
    """

    eligibility_score = serializers.ReadOnlyField()

    status = serializers.ReadOnlyField()

    client = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:

        model = Credit

        fields = [
            "id",
            "client",
            "amount",
            "duration",
            "purpose",
            "monthly_income",
            "supporting_document",
            "eligibility_score",
            "status",
            "approved_amount",
            "interest_rate",
            "repayment_start_date",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "client",
            "eligibility_score",
            "status",
            "approved_amount",
            "interest_rate",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):

        request = self.context["request"]

        credit = Credit(
            client=request.user,
            **validated_data
        )

        credit.eligibility_score = (
            credit.calculate_eligibility_score()
        )

        credit.save()

        return credit


class CreditStatusSerializer(serializers.ModelSerializer):
    """
    Utilisé par les agents/admin
    pour modifier le statut.
    """

    class Meta:

        model = Credit

        fields = [
            "status",
            "approved_amount",
            "notes",
        ]


class CreditListSerializer(serializers.ModelSerializer):

    client = serializers.StringRelatedField()

    class Meta:

        model = Credit

        fields = [
            "id",
            "client",
            "amount",
            "status",
            "eligibility_score",
            "created_at",
        ]