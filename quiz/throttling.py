from rest_framework.throttling import SimpleRateThrottle
from rest_framework.throttling import UserRateThrottle


class CustomRateThrottle(SimpleRateThrottle):
    rate = '1/minute'

class CustomThrottle(UserRateThrottle):
    scope = 'custom_throttle'
    rate = '3/minute'

    def allow_request(self, request, view):
        # Check if request should be throttled
        if self.rate is None:
            return True

        # Get the unique cache key for the current request
        cache_key = self.get_cache_key(request, view)

        # Get the current request count from cache
        request_count = self.cache.get(cache_key, 0)

        # Increment the request count
        request_count += 1

        # Save the updated request count back to cache
        self.cache.set(cache_key, request_count, self.duration)

        # Check if the request count exceeds the limit
        if request_count > self.num_requests:
            return False

        return True

