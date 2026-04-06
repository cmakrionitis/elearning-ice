from .models import SiteFront
from django.core.cache import cache
from django.db.models import Count
from collections import defaultdict


def sitefront_context(request):
    # Κάνουμε cache για ταχύτητα (10 λεπτά)
    sitefront = cache.get('sitefront_instance')
    if not sitefront:
        sitefront = SiteFront.objects.first()
        cache.set('sitefront_instance', sitefront, 600)
    return {'sitefront': sitefront}