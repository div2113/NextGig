from django.contrib import admin
from .models import JobSeekerProfile
from django.utils.translation import gettext_lazy as _


class JobSeekerAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user_username",
        "contact_num",
        "resume",
        "location",
        "experience_years",
        "education",
    ]
    list_filter = ["location", "experience_years", "education"]
    search_fields = ["user__username", "contact_num"]
    readonly_fields = ["user"]

    def user_username(self, obj):
        return obj.user.username

    user_username.short_description = "Username"


admin.site.register(JobSeekerProfile, JobSeekerAdmin)
