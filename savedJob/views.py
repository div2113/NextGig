from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from .models import SavedJob
from .serializers import SavedJobSerializer
from user.pagination import BasePagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response


def is_valid_jobseeker(user):
    return hasattr(user, "is_employer") and not user.is_employer


class SavedJobListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SavedJobSerializer
    pagination_class = BasePagination

    def get_queryset(self):
        user = self.request.user
        if not is_valid_jobseeker(user):
            raise PermissionDenied("Only valid jobseekers can view saved jobs.")
        return SavedJob.objects.filter(user=user)


class SavedJobCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SavedJobSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if not is_valid_jobseeker(user):
            raise PermissionDenied("Only valid jobseekers with profile can save jobs.")
        serializer.save(user=self.request.user)


class SavedJobDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SavedJobSerializer

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if not is_valid_jobseeker(user):
            raise PermissionDenied("Only valid jobseekers can delete saved jobs.")
        if obj.user != user:
            raise PermissionDenied(
                "You do not have permission to delete this saved job."
            )
        return obj

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Job unsaved successfully."}, status=204)