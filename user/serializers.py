from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "is_employer",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        user.set_password(validated_data["password"])

        if "is_employer" in validated_data:
            user.is_employer = validated_data["is_employer"]
        user.save()
        return user

    def update(self, instance, validated_data):
        # prevent change the is_employer status
        validated_data.pop("is_employer", None)

        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        password = validated_data.get("password")
        if password:
            instance.set_password(password)
        instance.save()
        return instance
