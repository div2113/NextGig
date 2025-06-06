from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
    ListAPIView,
)
from .serializers import JobListingSerializer, JobViewLogSerializer
from .models import JobListing, JobViewLog
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from employerProfile.models import EmployerProfile
from rest_framework.response import Response


class IsEmployer(BasePermission):
    """
    Allow access only to logged-in users with the 'employer'profile.
    """

    def has_permission(self, request, view):
        print("is_authenticated:", request.user.is_authenticated)
        print("has employer_profile:", hasattr(request.user, "employer_profile"))
        return (
            hasattr(request.user, "employer_profile") and request.user.is_authenticated
        ) or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return (
            hasattr(request.user, "employer_profile")
            and obj.employer == request.user.employer_profile
        ) or request.user.is_staff


class JobListingPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class JobListingApiView(ListCreateAPIView):
    serializer_class = JobListingSerializer
    permission_classes = [IsEmployer, IsAuthenticated]
    pagination_class = JobListingPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return JobListing.objects.all()
        if hasattr(user, "employer_profile"):
            return JobListing.objects.filter(employer=user.employer_profile)
        return JobListing.objects.none()

    def perform_create(self, serializer):
        employer_profile = EmployerProfile.objects.get(user=self.request.user)
        serializer.save(employer=self.request.user.employer_profile)


class JobListingDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = JobListingSerializer
    permission_classes = [IsEmployer]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return JobListing.objects.all()
        if hasattr(user, "employer_profile"):
            return JobListing.objects.filter(employer=user.employer_profile)
        return JobListing.objects.none()

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Job listing deleted successfully."}, status=response.status_code
        )


class PublicJobListingApiView(ListAPIView):
    serializer_class = JobListingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return JobListing.objects.filter(status="active").order_by("-created_at")


class JobViewLogPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class JobViewLogApiView(ListCreateAPIView):
    serializer_class = JobViewLogSerializer
    permission_classes = [IsEmployer]
    pagination_class = JobViewLogPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return JobViewLog.objects.all()
        if hasattr(user, "employer_profile"):
            return JobViewLog.objects.select_related("job", "job__employer").filter(
                job__employer=user.employer_profile
            )
        return JobViewLog.objects.none()
