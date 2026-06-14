# accounts/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "region",
            "birth_date",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):

        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password": "Les mots de passe ne correspondent pas."
                }
            )

        return attrs

    def create(self, validated_data):

        validated_data.pop("password_confirm")

        password = validated_data.pop("password")

        user = User(**validated_data)

        # Par défaut tout nouvel utilisateur est CLIENT
        user.role = User.CLIENT

        user.set_password(password)

        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Consultation du profil
    """

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "phone_number",
            "address",
            "region",
            "birth_date",
            "profile_picture",
            "is_verified",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "role",
            "is_verified",
            "created_at",
        ]


class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    Modification du profil
    """

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "region",
            "birth_date",
            "profile_picture",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Changement du mot de passe
    """

    old_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    def validate(self, attrs):

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "confirm_password": "Les mots de passe ne correspondent pas."
                }
            )

        return attrs
