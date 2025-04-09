from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from industry.models import Industry
from accounts.models import CustomUser, Like
from django.core.cache import cache

@receiver(post_save, sender=CustomUser)
def clear_cache_on_user_save(sender, instance, **kwargs):
    print(f"Clearing cache for CustomUser: {instance.id}")
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern("*masters_list*")
    else:
        cache.delete("masters_list")

@receiver(post_delete, sender=CustomUser)
def clear_cache_on_user_delete(sender, instance, **kwargs):
    print(f"Clearing cache for CustomUser delete: {instance.id}")
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern("*masters_list*")
    else:
        cache.delete("masters_list")

@receiver(post_save, sender=Industry)
def clear_cache_on_industry_save(sender, instance, **kwargs):
    print(f"Clearing cache for Industry: {instance.id}")
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern("*masters_list*")
    else:
        cache.delete("masters_list")

@receiver(post_delete, sender=Industry)
def clear_cache_on_industry_delete(sender, instance, **kwargs):
    print(f"Clearing cache for Industry delete: {instance.id}")
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern("*masters_list*")
    else:
        cache.delete("masters_list")

@receiver(post_save, sender=Like)
def clear_cache_on_like_save(sender, instance, **kwargs):
    print(f"Clearing cache for Like: {instance.id}")
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern("*masters_list*")
    else:
        cache.delete("masters_list")

@receiver(post_delete, sender=Like)
def clear_cache_on_like_delete(sender, instance, **kwargs):
    print(f"Clearing cache for Like delete: {instance.id}")
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern("*masters_list*")
    else:
        cache.delete("masters_list")
