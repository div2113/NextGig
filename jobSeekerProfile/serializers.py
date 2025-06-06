from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import JobSeekerProfile
from rest_framework.exceptions import PermissionDenied
from user.serializers import UserResponseSerializer

User = get_user_model()


class JobSeekerProfileSerializer(serializers.ModelSerializer):
    user = UserResponseSerializer(read_only=True)

    class Meta:
        model = JobSeekerProfile
        fields = [
            "id",
            "contact_num",
            "resume",
            "location",
            "skills",
            "experience_years",
            "education",
            "user",
            "is_deleted",
            "is_active",
        ]
        read_only_fields = ["id", "user", "is_deleted", "is_active"]

    def validate_resume(self, value):
        max_size = 5 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("Resume file size should not exceed 5MB.")
        return value

    def create(self, validated_data):
        # Get the logged-in user (employer) from request context
        user = self.context.get("request").user
        validated_data.pop("user", None)

        soft_deleted_profile = JobSeekerProfile.objects.filter(
            user=user, is_deleted=True
        ).first()

        if soft_deleted_profile:
            # reactivate the soft_deleted profile
            for attr, value in validated_data.items():
                setattr(soft_deleted_profile, attr, value)
            soft_deleted_profile.is_deleted = False
            soft_deleted_profile.is_active = True
            soft_deleted_profile.full_clean()
            soft_deleted_profile.save()
            return soft_deleted_profile
        else:
            employer = JobSeekerProfile.objects.create(user=user, **validated_data)
            return employer

    def update(self, instance, validated_data):

        # Do not allow the 'user' field to be updated directly
        validated_data.pop("user", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.full_clean()
        instance.save()
        return instance
