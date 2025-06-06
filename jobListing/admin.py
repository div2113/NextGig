from django.contrib import admin
from .models import JobListing, JobViewLog


class JobListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "employer",
        "location",
        "education_requirements",
        "experience_level",
        "responsibilities",
        "job_type",
        "work_mode",
        "salary_range",
        "application_deadline",
        "created_at",
    )
    list_filter = (
        "education_requirements",
        "experience_level",
        "location",
        "job_type",
        "work_mode",
        "status",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "location",
        "employer__user__email",
        "job_type",
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


class JobViewLogAdmin(admin.ModelAdmin):
    list_display = ("job", "user", "viewed_at")
    search_fields = ("job__title", "user__email", "ip_address")
    ordering = ("-viewed_at",)
    readonly_fields = ("viewed_at",)


admin.site.register(JobListing, JobListingAdmin)
admin.site.register(JobViewLog, JobViewLogAdmin)
