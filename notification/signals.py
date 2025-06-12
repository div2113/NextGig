from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from notification.models import Notification
from jobListing.models import JobListing

User=get_user_model()

@receiver(post_save,sender=JobListing)
def notify_users_on_new_job(sender,instance,created,**kwargs):
    if created:
        try:
            users=User.objects.filter(is_employer=False)

            notifications=[
                Notification(user=user,message=f"New Job Posted:{instance.title}")
                for user in users
            ]
            Notification.objects.bulk_create(notifications)

        except Exception as e:
            print(f"Error creating notifications: {e}")