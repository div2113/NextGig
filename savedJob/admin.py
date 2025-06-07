from django.contrib import admin
from .models import SavedJob
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class SavedJobAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "job", "saved_at"]
    list_filter = ["user", "job"]
    search_fields = ("id", "user__username", "job__title")


admin.site.register(SavedJob, SavedJobAdmin)
