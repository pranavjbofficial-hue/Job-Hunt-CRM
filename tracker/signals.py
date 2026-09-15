from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Application, StatusHistory


@receiver(pre_save, sender=Application)
def stash_old_status(sender, instance, **kwargs):
    """Before saving, remember what the status used to be (if this is an update)."""
    if not instance.pk:
        instance._old_status = None
        return
    try:
        instance._old_status = Application.objects.get(pk=instance.pk).status
    except Application.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Application)
def log_status_change(sender, instance, created, **kwargs):
    """After saving, write a StatusHistory row if the status changed (or this is brand new)."""
    old_status = getattr(instance, '_old_status', None)

    if created:
        StatusHistory.objects.create(
            application=instance,
            old_status=None,
            new_status=instance.status,
        )
    elif old_status is not None and old_status != instance.status:
        StatusHistory.objects.create(
            application=instance,
            old_status=old_status,
            new_status=instance.status,
        )
