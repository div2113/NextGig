from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.http import HttpResponse

# define swagger schema view with JWT security

schema_view = get_schema_view(
    openapi.Info(
        title="NestGig API",
        default_version="v1",
        description="NextGig - Your Gateway to New Opportunities!",
        contact=openapi.Contact(email="support@NexttGig.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=(JWTAuthentication,),
)


urlpatterns = [
    path("", lambda request: HttpResponse("Welcome to NextGig API!"), name="home"),
    path("admin/", admin.site.urls),
    path("users/", include("user.urls")),
    path("employerProfiles/", include("employerProfile.urls")),
    path("jobApplications/", include("jobApplication.urls")),
    path("jobListings/", include("jobListing.urls")),
    path("jobSeekerProfiles/", include("jobSeekerProfile.urls")),
    # path("notifications/",include("notification.urls")),
    path("savedJobs/",include("savedJob.urls")),
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path("api/token/verify/", TokenVerifyView.as_view()),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
