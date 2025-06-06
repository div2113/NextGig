from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from .serializers import JobSeekerProfileSerializer
from .models import JobSeekerProfile
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from user.models import ActivityLog
from rest_framework.response import Response
from rest_framework import status
from user.pagination import BasePagination


class JobSeekerCreateApiView(CreateAPIView):
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePagination

    def get_queryset(self):
        return JobSeekerProfile.objects.filter(is_deleted=False).order_by("id")

    def perform_create(self, serializer):
        user = self.request.user
        soft_deleted_profile = JobSeekerProfile.objects.filter(
            user=user, is_deleted=True
        ).first()

        if soft_deleted_profile:
            # If a soft-deleted profile exists, reuse it through the serializer
            serializer.instance = soft_deleted_profile
            soft_deleted_profile.is_deleted = False
            soft_deleted_profile.is_active = True
            serializer.save(user=user)

            ActivityLog.objects.create(
                user=user,
                action="Jobseeker Profile Restored",
                details=f"{user.username} restored their soft-deleted jobseeker profile.",
            )
        elif JobSeekerProfile.objects.filter(user=user, is_deleted=False).exists():
            raise ValidationError("You already have a jobseeker profile.")
        else:
            serializer.save(user=user)
            ActivityLog.objects.create(
                user=user,
                action="Jobseeker Profile Created",
                details=f"{user.username} created their jobseeker profile.",
            )


class JobseekerProfileDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_employer:
            raise PermissionDenied("Employers cannot access jobseeker profiles.")
        return JobSeekerProfile.objects.filter(user=self.request.user, is_deleted=False)

    def get_object(self):
        return self.get_queryset().first()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"message": "Jobseeker profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer):
        # Check that the jobseeker can only update their own profile
        instance = self.get_object()
        if self.request.user != instance.user:
            raise PermissionDenied("You can only update your own profile")

        serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="Jobseeker Profile Updated",
            details=f"Jobseeker profile for {self.request.user.username} updated by {self.request.user.username}.",
        )

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.is_active = False
        instance.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="Jobseeker Profile Deleted",
            details=f"Jobseeker profile was deleted by {self.request.user.username}.",
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Jobseeker profile deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class JobSeekerProfileAdminListView(ListAPIView):
    queryset = JobSeekerProfile.objects.all().order_by("id")
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [IsAdminUser]
    pagination_class = PageNumberPagination
