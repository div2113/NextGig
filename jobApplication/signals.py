from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import JobApplication
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=JobApplication)
def notify_job_application(sender, instance, created, **kwargs):
    try:
        if created:
            logger.info(
                f"New job application created for {instance.jobseekerprofile.user.username} on {instance.applied_at}."
            )
        else:
            logger.info(
                f"Job application updated for {instance.jobseekerprofile.user.username} on {instance.applied_at}."
            )
    except Exception as e:
        logger.error(f"Error in notifying job application signal:{e}")


# This signal will notify when a new job application is created or updated.

# It uses Django's built-in logging framework to log the information.
