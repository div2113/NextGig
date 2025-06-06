from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()

CITY_CHOICES = [
    ("mumbai", "Mumbai"),
    ("bangalore", "Bangalore"),
    ("hyderabad", "Hyderabad"),
    ("delhi", "Delhi"),
    ("pune", "Pune"),
    ("chennai", "Chennai"),
    ("gurgaon", "Gurgaon"),
    ("noida", "Noida"),
    ("ahmedabad", "Ahmedabad"),
    ("kolkata", "Kolkata"),
    ("remote", "Remote"),
    ("other", "Other"),
]


class EmployerProfile(models.Model):
    company_name = models.CharField(max_length=100)
    company_info = models.TextField(blank=True)
    email = models.EmailField(default="employer@gmail.com")
    website = models.URLField(blank=True)
    contact_number = models.CharField(max_length=15, blank=False, null=False)
    location = models.CharField(
        max_length=20, choices=CITY_CHOICES, blank=False, null=False, default="mumbai"
    )
    industry_type = models.CharField(max_length=100, default="other")
    company_logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employer_profile"
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "employer_profile"
        verbose_name = "Employer Profile"
        verbose_name_plural = "Employer Profiles"

    def __str__(self):
        return f"{self.company_name}({self.user.username})"

    def clean(self):
        super().clean()
        if not re.fullmatch(r"^\+?\d{7,15}$", self.contact_number):
            raise ValidationError(
                {
                    "contact_number": "Enter a valid phone number (7 to 15 digits, optional +)."
                }
            )

        if not self.company_name.strip():
            raise ValidationError(
                {"company_name": "Company name cannot be empty or only spaces."}
            )

        if self.company_info and len(self.company_info) > 1000:
            raise ValidationError(
                {"company_info": "Company info should not exceed 1000 characters."}
            )

        if self.website and not self.website.startswith("https://"):
            raise ValidationError(
                {"website": "Website must start with https:// for better security."}
            )
