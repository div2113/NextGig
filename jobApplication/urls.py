from django.urls import path
from .views import *

urlpatterns = [
    # Jobseeker: See all their applications
    path(
        "my-applications/",
        JobApplicationListAPIView.as_view(),
        name="jobseeker-application-list",
    ),
    path(
        "job/<int:job_id>/applications/",
        JobApplicationListCreateAPIView.as_view(),
        name="jobseeker-application-lis-create",
    ),
    # Retrieve, update, or delete a specific application (admin/employer can delete)
    path(
        "applications/<int:pk>/",
        JobApplicationRetrieveUpdateDestroyAPIView.as_view(),
        name="application-detail",
    ),
    # Employer: See all applications for all their jobs
    path(
        "employer/applications/",
        EmployerAllApplicationsAPIView.as_view(),
        name="employer-all-applications",
    ),
]
