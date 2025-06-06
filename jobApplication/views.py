from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from .models import JobApplication
from .serializers import JobApplicationSerializer
from jobSeekerProfile.models import JobSeekerProfile
from jobListing.models import JobListing
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import JobApplicationSerializer
from rest_framework.permissions import BasePermission


class JobApplicationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class JobApplicationListAPIView(ListCreateAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(
            jobseekerprofile=self.request.user.jobseekerprofile
        )


class JobApplicationListCreateAPIView(ListCreateAPIView):
    serializer_class = JobApplicationSerializer
    pagination_class = JobApplicationPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(
            jobseekerprofile=self.request.user.jobseekerprofile
        )

    def perform_create(self, serializer):
        # automatically assign the jobseekerprofile and job from the request context
        jobseekerprofile = self.request.user.jobseekerprofile
        job = get_object_or_404(JobListing, id=self.kwargs["job_id"])

        # Save the application with the linked jobseeker and job
        serializer.save(jobseekerprofile=jobseekerprofile, job=job)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        job_id = self.kwargs.get("job_id")
        job = get_object_or_404(JobListing, id=job_id)

        jobseekerprofile = self.request.user.jobseekerprofile
        context.update({"job": job, "jobseekerprofile": jobseekerprofile})
        return context


class JobApplicationRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        application = self.get_object()

        # Check if the current user is the employer for the job
        if request.user != application.job.employer:
            return Response(
                {"detail": "You do not have permission to update this application."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Only allow updating the status field
        status = request.data.get("status")
        if status not in dict(JobApplication.STATUS_CHOICES):
            return Response(
                {"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST
            )

        application.status = status
        application.save()

        return Response(
            JobApplicationSerializer(application).data, status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        application = self.get_object()

        # Check if the current user is the employer for the job
        if request.user != application.job.employer:
            return Response(
                {"detail": "You do not have permission to delete this application."},
                status=status.HTTP_403_FORBIDDEN,
            )

        application.delete()

        return Response(
            {"detail": "Application deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has an employer profile
        return hasattr(request.user, "employer_profile")

    def has_object_permission(self, request, view, obj):
        # Check if the user is the employer for the job
        return obj.job.employer == request.user.employer_profile


class EmployerAllApplicationsAPIView(ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def get_queryset(self):
        # Get all applications for jobs owned by the logged-in employer
        employer_profile = self.request.user.employer_profile
        return JobApplication.objects.filter(job__employer=employer_profile)


class JobApplicationRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def partial_update(self, request, *args, **kwargs):
        application = self.get_object()
        if request.user.employer_profile != application.job.employer:
            return Response(
                {"detail": "You do not have permission to update this application."},
                status=status.HTTP_403_FORBIDDEN,
            )
        status_value = request.data.get("status")
        if status_value not in dict(JobApplication.STATUS_CHOICES):
            return Response(
                {"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST
            )
        application.status = status_value
        application.save()
        return Response(
            JobApplicationSerializer(application).data, status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        application = self.get_object()

        is_admin = request.user.is_staff or request.user.is_superuser
        is_employer = request.user.employer_profile == application.job.employer

        if not (is_admin or is_employer):
            return Response(
                {"detail": "You do not have permission to delete this application."},
                status=status.HTTP_403_FORBIDDEN,
            )
        application.delete()

        return Response(
            {"detail": "Application deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
