from datetime import timedelta


CATEGORIES_CACHE_LIFETIME = timedelta(days=1).total_seconds()
TAGS_CACHE_LIFETIME = timedelta(days=1).total_seconds()
SALES_CACHE_LIFETIME = timedelta(days=1).total_seconds()
SHOPS_CACHE_LIFETIME = timedelta(days=1).total_seconds()
PRODUCTS_TOP_CACHE_LIFETIME = timedelta(hours=1).total_seconds()
ORDER_AMOUNT_WHICH_DELIVERY_FREE = 2000