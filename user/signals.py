from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ActivityLog
from employerProfile.models import (
    EmployerProfile,
)  # For employer-specific profile actions
from jobSeekerProfile.models import JobSeekerProfile

User = get_user_model()


# Log when a user is created or updated
@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    if created:
        action = "User Created"
        details = f"New user registered: {instance.username}"
    else:
        action = "User Updated"
        details = f"User {instance.username} profile updated."

    # Create the activity log entry
    ActivityLog.objects.create(user=instance, action=action, details=details)


# Log when an EmployerProfile is created or deleted (specific to employer actions)
@receiver(post_save, sender=EmployerProfile)
def log_employer_profile_save(sender, instance, created, **kwargs):
    if created:
        action = "Employer Profile Created"
        details = f"Employer profile for {instance.company_name} created by {instance.user.username}."
    else:
        action = "Employer Profile Updated"
        details = f"Employer profile for {instance.company_name} updated by {instance.user.username}."

    # Create the activity log entry
    ActivityLog.objects.create(user=instance.user, action=action, details=details)


@receiver(post_delete, sender=EmployerProfile)
def log_employer_profile_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance.user,
        action="Employer Profile Deleted",
        details=f"Employer profile for {instance.company_name} was deleted by {instance.user.username}.",
    )


# Log when an JobseekerProfile is created or deleted (specific to employer actions)
@receiver(post_save, sender=JobSeekerProfile)
def log_jobseeker_profile_save(sender, instance, created, **kwargs):
    if created:
        action = "Jobseeker Profile Created"
        details = f"Jobseeker profile created by {instance.user.username}."
    else:
        action = "Jobseeker Profile Updated"
        details = f"Jobseeker profile updated by {instance.user.username}."

    # Create the activity log entry
    ActivityLog.objects.create(user=instance.user, action=action, details=details)


@receiver(post_delete, sender=JobSeekerProfile)
def log_jobseeker_profile_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance.user,
        action="Jobseeker Profile Deleted",
        details=f"Jobseeker profile was successfully deleted by {instance.user.username}.",
    )
