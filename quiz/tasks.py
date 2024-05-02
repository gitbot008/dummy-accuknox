from celery import shared_task
from django.core.cache import cache
from .models import SearchQuery
from collections import Counter

@shared_task
def update_top_search_results():
    # Get top 5 search queries from the database
    search_queries = SearchQuery.objects.values_list('query', flat=True)
    query_counts = Counter(search_queries)
    sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
    top_search_queries = [query[0] for query in sorted_queries[:5]]

    # Store top 5 search queries in the cache
    cache.set('top_search_queries', top_search_queries)