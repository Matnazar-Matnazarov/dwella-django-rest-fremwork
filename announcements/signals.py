from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from announcements.models import Announcement

@receiver([post_save, post_delete], sender=Announcement)
def announcements_cache_delete(sender, instance, **kwargs):
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern("*announcements_list*")
        cache.delete_pattern("*announcements_detail*")
    else:
        cache.delete("announcements_list")
        cache.delete("announcements_detail")
    