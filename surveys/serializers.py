from rest_framework import serializers

from .models import NPSSurvey


class NPSSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = NPSSurvey
        fields = [
            "id",
            "score",
            "comment",
            "context_type",
            "context_id",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_score(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError("Le score doit être compris entre 0 et 10.")
        return value
