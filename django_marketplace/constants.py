from datetime import timedelta


CATEGORIES_CACHE_LIFETIME = timedelta(days=1).total_seconds()
SORT_OPTIONS_CACHE_LIFETIME = timedelta(days=2).total_seconds()
TAGS_CACHE_LIFETIME = timedelta(days=1).total_seconds()

