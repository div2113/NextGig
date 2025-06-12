from django.db import models
from django.contrib.auth import get_user_model
from employerProfile.models import EmployerProfile
from taggit.managers import TaggableManager
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re
from datetime import date

User = get_user_model()


class JobListing(models.Model):

    JOB_TYPE_CHOICE = [
        ("full-time", "Full-Time"),
        ("part-time", "Part Time"),
        ("internship", "Internship"),
        ("contract", "Contract"),
    ]

    WORK_MODE_CHOICE = [
        ("on-site", "On-site"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
    ]

    EXPERIENCE_LEVEL_CHOICE = [
        ("entry-level", "Entry Level"),
        ("mid-level", "Mid Level"),
        ("senior-level", "Senior Level"),
    ]

    employer = models.ForeignKey(
        EmployerProfile, on_delete=models.CASCADE, related_name="job_listings"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    education_requirements = models.CharField(max_length=255, blank=True, null=True)
    experience_level = models.CharField(
        max_length=20, choices=EXPERIENCE_LEVEL_CHOICE, default="entry-level"
    )
    skills = models.TextField(blank=True, null=True)
    responsibilities = models.TextField()
    location = models.CharField(max_length=255)
    job_type = models.CharField(
        max_length=20, choices=JOB_TYPE_CHOICE, default="full-time"
    )
    work_mode = models.CharField(
        max_length=15, choices=WORK_MODE_CHOICE, default="on-site"
    )
    salary_range = models.CharField(max_length=100)
    application_deadline = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=[("active", "Active"), ("closed", "Closed")]
    )
    remote_available = models.BooleanField(default=False)
    openings = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiry_date = models.DateField(blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)
    tags = TaggableManager(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "joblisting"
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return f"{self.title} at {self.employer.company_name}"

    def clean(self):
        super().clean()
        if self.location:
            locations = re.split(r"[,/]", self.location)  # split on comma or slash
            cleaned_locations = [
                loc.strip().title() for loc in locations if loc.strip()
            ]
            self.location = " / ".join(cleaned_locations)

        if self.application_deadline and self.application_deadline < now().date():
            raise ValidationError("The application deadline cannot be in the past.")

        if self.salary_range:
            salary_pattern = r"^\d+(\.\d{1,2})?\s*-\s*\d+(\.\d{1,2})?$"
            if not re.match(salary_pattern, self.salary_range):
                raise ValidationError(
                    "Invalid salary range format. Use 'min - max' format."
                )

    def update_status(self):
        today = date.today()
        if self.expiry_date and today > self.expiry_date:
            self.status = "closed"
        elif self.application_deadline and today > self.application_deadline:
            self.status = "closed"
        else:
            self.status = "active"

    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)


class JobViewLog(models.Model):
    job = models.ForeignKey(
        JobListing, on_delete=models.CASCADE, related_name="view_logs"
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        unique_together = ("job", "user")
        db_table = "job_view_log"
        indexes = [models.Index(fields=["viewed_at"])]

    def __str__(self):
        return f"Viewed: {self.job.title} by {self.user or self.ip_address}"
