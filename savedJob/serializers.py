from rest_framework import serializers
from .models import SavedJob


class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedJob
        fields = ["id", "job", "saved_at"]
        read_only_fields = ["id", "saved_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        job = attrs.get("job")

        # Only jobseekers with profile can save jobs
        if not hasattr(user, "is_employer") or user.is_employer:
            raise serializers.ValidationError(
                "Only valid jobseekers with profile can save jobs."
            )

        if not hasattr(user, "jobseekerprofile"):
            raise serializers.ValidationError(
                "Complete your jobseeker profile to save jobs."
            )

        # Prevent duplicate saved jobs
        if SavedJob.objects.filter(user=user, job=job).exists():
            raise serializers.ValidationError("You have already saved this job.")

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        return SavedJob.objects.create(**validated_data)
