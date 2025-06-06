from django.urls import path
from .views import *

urlpatterns = [
    path("", EmployerProfileCreateApiView.as_view()),
    path("me/", EmployerProfileDetailView.as_view()),
    path("admin/employers/all/", EmployerProfileAdminListView.as_view()),
]
