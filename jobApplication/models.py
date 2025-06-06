from django.db import models
from jobListing.models import JobListing
from jobSeekerProfile.models import JobSeekerProfile
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import os

User = get_user_model()


def validate_resume_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".pdf", ".doc", ".docx"]
    if ext.lower() not in valid_extensions:
        raise ValidationError(
            "Unsupported file extension. Allowed formats: PDF, DOC, DOCX."
        )

    if value.size > 5 * 1024 * 1024:
        raise ValidationError("File size exceeds 5MB limit.")


def resume_upload_path(instance, filename):
    return f"resume/{instance.jobseekerprofile.user.username}/{filename}"


class JobApplication(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("shortlisted", "Shortlisted"),
        ("interview", "Interview"),
        ("hired", "Hired"),
        ("rejected", "Rejected"),
    ]

    resume = models.FileField(
        upload_to=resume_upload_path, validators=[validate_resume_file_extension]
    )
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    applied_at = models.DateTimeField(auto_now_add=True)
    jobseekerprofile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE)

    class Meta:
        db_table = "jobapplication"
        unique_together = ("jobseekerprofile", "job")
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["applied_at"]),
        ]

    def __str__(self):
        return f"{self.jobseekerprofile.user.username} - {self.job.title}"

    def clean(self):
        if (
            JobApplication.objects.filter(
                job=self.job, jobseekerprofile=self.jobseekerprofile
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("You have already applied for this job.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
