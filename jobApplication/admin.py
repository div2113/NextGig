from django.contrib import admin
from .models import JobApplication


class JobApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "job",
        "jobseeker",
        "status",
        "applied_at",
    ]
    list_filter = ("status", "applied_at")
    search_fields = [
        "jobseekerprofile__user__username",
        "job__title",
        "jobseekerprofile__user__email",
    ]
    readonly_fields = ("applied_at",)
    ordering = ("-applied_at",)

    def jobseeker(self, obj):
        return obj.jobseekerprofile.user.username

    jobseeker.short_description = "Job Seeker"


admin.site.register(JobApplication, JobApplicationAdmin)
