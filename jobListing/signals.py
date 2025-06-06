from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import JobListing, JobViewLog
from jobApplication.models import JobApplication
from django.db.models import F
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=JobApplication)
def update_applications_count(sender, instance, created, **kwargs):
    try:
        if created and instance.job:
            # Increase the applications_count safely
            JobListing.objects.filter(id=instance.job.id).update(
                applications_count=F("applications_count") + 1
            )
            logger.info(
                f"📥 JobApplication: {instance.user} applied to '{instance.job.title}'"
            )
    except Exception as e:
        logger.error(f"Error updating applications count: {e}")


@receiver(post_save, sender=JobViewLog)
def update_views_count(sender, instance, created, **kwargs):
    try:
        if created and instance.job:
            # Only increase count on new unique view
            JobListing.objects.filter(id=instance.job.id).update(
                views_count=F("views_count") + 1
            )
            if instance.user:
                logger.info(
                    f"👁️ JobViewLog: {instance.user} viewed '{instance.job.title}' at {now()}"
                )
            else:
                logger.info(
                    f"👁️ Anonymous user viewed '{instance.job.title}' at {now()}"
                )
    except Exception as e:
        logger.error(f"Error updating views count: {e}")
