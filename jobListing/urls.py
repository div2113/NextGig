from django.urls import path
from .views import *

urlpatterns = [
    path("jobs/", JobListingApiView.as_view()),
    path("jobs/<int:pk>/", JobListingDetailView.as_view()),
    path("job-view-logs/", JobViewLogApiView.as_view()),
    path("public-jobs/", PublicJobListingApiView.as_view()),
]
