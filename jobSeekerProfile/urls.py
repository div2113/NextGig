from django.urls import path
from .views import *

urlpatterns = [
    path("", JobSeekerCreateApiView.as_view()),
    path("me/", JobseekerProfileDetailView.as_view()),
    path("admin/jobseeker/all/", JobSeekerProfileAdminListView.as_view()),
]
