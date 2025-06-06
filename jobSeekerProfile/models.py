from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import os
import re

User = get_user_model()


def validate_resume_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".pdf", ".doc", ".docx"]
    if ext.lower() not in valid_extensions:
        raise ValidationError(
            "Unsupported file extension. Allowed formats: PDF, DOC, DOCX."
        )


def resume_upload_to(instance, filename):
    return f"resumes/{instance.user.id}/{filename}"


class JobSeekerProfile(models.Model):
    contact_num = models.CharField(max_length=15)
    resume = models.FileField(
        upload_to=resume_upload_to, validators=[validate_resume_file_extension]
    )
    location = models.CharField(
        max_length=255,
        help_text="Enter one or more cities seperated by commas or slashes",
    )
    skills = models.TextField(blank=True, null=True)
    experience_years = models.CharField(max_length=100, default="fresher")
    education = models.CharField(
        max_length=255,
        help_text="Enter your education. Be specific (e.g., Bachelor's Degree in Computer Science, High School, etc.)",
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if not re.fullmatch(r"^\+?\d{7,15}$", self.contact_num):
            raise ValidationError(
                {
                    "contact_num": "Enter a valid phone number (7 to 15 digits, optional +)."
                }
            )

        if self.location:
            locations = re.split(r"[,/]", self.location)  # split on comma or slash
            cleaned_locations = [
                loc.strip().title() for loc in locations if loc.strip()
            ]
            self.location = " / ".join(cleaned_locations)

    class Meta:
        db_table = "jobseekerprofile"
        verbose_name = "Jobseeker Profile"
        verbose_name_plural = "Jobseeker Profiles"

    def __str__(self):
        return f"{self.user.username}'s JobSeeker Profile"
