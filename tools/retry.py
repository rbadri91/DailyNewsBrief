import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Reusable decorator for all outbound HTTP calls.
# Retries up to 3 times with exponential backoff (2s, 4s, 8s) on transient errors.
http_retry = retry(
    retry=retry_if_exception_type(
        (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError)
    ),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
