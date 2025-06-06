from rest_framework import serializers
from jobSeekerProfile.models import JobSeekerProfile
from jobListing.models import JobListing
from .models import JobApplication
from employerProfile.serializers import EmployerResponseSerializer


class jobseekerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    email = serializers.CharField(source="user.email")

    class Meta:
        model = JobSeekerProfile
        fields = ["id", "username", "email", "location", "contact_num"]


class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.ReadOnlyField(source="job.title")
    jobseeker_info = jobseekerProfileSerializer(
        source="jobseekerprofile", read_only=True
    )
    company_info = EmployerResponseSerializer(source="job.employer", read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "resume",
            "cover_letter",
            "status",
            "applied_at",
            "job_title",
            "jobseeker_info",
            "company_info",
        ]
        read_only_fields = ["applied_at", "status", "jobseekerprofile", "job"]

    def validate(self, attrs):
        # Retrieve the job and jobseekerprofile from the context
        job = self.context.get("job")
        jobseeker = self.context.get("jobseekerprofile")

        # check if the job seeker is applying for the same job
        if not job or not jobseeker:
            raise serializers.ValidationError(
                "Job or jobseeker profile is missing from context."
            )

        if job and jobseeker:
            if JobApplication.objects.filter(
                job=job, jobseekerprofile=jobseeker
            ).exists():
                raise serializers.ValidationError(
                    "You have already applied for this job."
                )
        return attrs

    def create(self, validated_data):
        validated_data.pop("jobseekerprofile", None)
        validated_data.pop("job", None)
        jobseekerprofile = self.context.get("jobseekerprofile")
        job = self.context.get("job")

        jobapplication = JobApplication.objects.create(
            jobseekerprofile=jobseekerprofile, job=job, **validated_data
        )
        return jobapplication

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            if attr in ["resume", "cover_letter"]:
                setattr(instance, attr, value)
            else:
                raise serializers.ValidationError(f"Field '{attr}' cannot be updated")

        instance.save()
        return instance
