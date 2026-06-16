from rest_framework import serializers

from .models import (
    InsuranceProduct,
    InsuranceSubscription,
)


class InsuranceProductSerializer(serializers.ModelSerializer):

    class Meta:

        model = InsuranceProduct

        fields = [
            "id",
            "name",
            "description",
            "price",
            "duration_days",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class InsuranceSubscriptionSerializer(serializers.ModelSerializer):

    client = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:

        model = InsuranceSubscription

        fields = [
            "id",
            "client",
            "product",
            "start_date",
            "end_date",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "client",
            "status",
            "created_at",
        ]

    def create(self, validated_data):

        request = self.context["request"]

        subscription = InsuranceSubscription.objects.create(
            client=request.user,
            **validated_data,
        )

        return subscription


class InsuranceSubscriptionListSerializer(
    serializers.ModelSerializer
):

    product = serializers.StringRelatedField()

    class Meta:

        model = InsuranceSubscription

        fields = [
            "id",
            "product",
            "start_date",
            "end_date",
            "status",
        ]