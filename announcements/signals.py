from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from announcements.models import Announcement
from django.core.cache import cache


@receiver([post_save, post_delete], sender=Announcement)
def announcement_cache_delete(sender, instance, **kwargs):
    print("announcement_cache_delete")
    cache.delete(f"*announcements_detail*")
    cache.delete(f"*announcements_list*")
