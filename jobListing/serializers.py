from rest_framework import serializers
from .models import JobListing, JobViewLog
from taggit.serializers import TagListSerializerField
from employerProfile.models import EmployerProfile
from django.utils import timezone
import re
from employerProfile.serializers import EmployerResponseSerializer


class JobListingSerializer(serializers.ModelSerializer):
    employer_user = EmployerResponseSerializer(source="employer", read_only=True)

    # employer = serializers.PrimaryKeyRelatedField(
    #    read_only=True
    # )
    employer_company_name = serializers.CharField(
        source="employer.company_name", read_only=True
    )
    company_location = serializers.CharField(source="employer.location", read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = JobListing
        fields = [
            "id",
            "employer_company_name",
            "company_location",
            "title",
            "description",
            "education_requirements",
            "experience_level",
            "skills",
            "responsibilities",
            "location",
            "job_type",
            "work_mode",
            "salary_range",
            "application_deadline",
            "status",
            "remote_available",
            "openings",
            "created_at",
            "updated_at",
            "expiry_date",
            "views_count",
            "applications_count",
            "tags",
            "ip_address",
            "employer_user",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
            "views_count",
            "applications_count",
            "employer_company_name",
            "company_location",
            "employer_user",
        ]

    def validate_application_deadline(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Application deadline must be in future.")
        return value

    def validate_salary_range(self, value):
        try:
            min_salary, max_salary = map(int, value.split("-"))
            if min_salary < 0 or max_salary < 0:
                raise serializers.ValidationError("Salary range must be positive.")
            if min_salary > max_salary:
                raise serializers.ValidationError(
                    "Minimum salary cannot be greater than maximum salary."
                )
        except ValueError:
            raise serializers.ValidationError(
                "Invalid salary range format. Use 'min - max' format."
            )
        return value

    def validate_openings(self, value):
        if value < 1:
            raise serializers.ValidationError("Number of openings must be at least 1.")
        return value

    def validate(self, attrs):
        app_deadline = attrs.get("application_deadline")
        expiry = attrs.get("expiry_date")
        if app_deadline and expiry and expiry < app_deadline:
            raise serializers.ValidationError(
                "Expiry date must be after application deadline."
            )
        return attrs


class JobViewLogSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = JobViewLog
        fields = [
            "id",
            "job",
            "user",
            "job_title",
            "user_email",
            "viewed_at",
            "ip_address",
        ]
        read_only_fields = ["viewed_at"]

    def validate_ip_address(self, value):
        pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError("Invalid IP address format.")
        return value
