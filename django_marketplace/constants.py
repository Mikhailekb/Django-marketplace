from datetime import timedelta


CATEGORIES_CACHE_LIFETIME = timedelta(days=1).total_seconds()
TAGS_CACHE_LIFETIME = timedelta(days=1).total_seconds()
SALES_CACHE_LIFETIME = timedelta(days=1).total_seconds()
