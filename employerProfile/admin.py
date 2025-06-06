from django.contrib import admin
from .models import EmployerProfile
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class EmployerAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "company_name",
        "company_info",
        "email",
        "website",
        "contact_number",
        "location",
        "industry_type",
        "company_logo",
        "user",
    ]
    list_filter = ["location", "industry_type", "user"]
    search_fields = ("id", "user__username", "company_name")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user__is_employer=True)


admin.site.register(EmployerProfile, EmployerAdmin)
