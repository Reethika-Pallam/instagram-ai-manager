"""Error handling and rate limiting utilities."""

import time
import logging
from typing import Callable, Any, TypeVar
from functools import wraps
import requests

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class InstagramAPIError(Exception):
    """Base exception for Instagram API errors."""
    pass


class RateLimitError(InstagramAPIError):
    """Exception raised when rate limit is exceeded."""
    pass


class AuthenticationError(InstagramAPIError):
    """Exception raised for authentication failures."""
    pass


class ResourceNotFoundError(InstagramAPIError):
    """Exception raised when a resource is not found."""
    pass


def handle_api_response(response: requests.Response) -> dict:
    """
    Handle API response and raise appropriate exceptions.
    
    Args:
        response: The requests Response object
        
    Returns:
        Parsed JSON response
        
    Raises:
        AuthenticationError: For 401/403 status codes
        RateLimitError: For 429 status code
        ResourceNotFoundError: For 404 status code
        InstagramAPIError: For other 4xx/5xx errors
    """
    try:
        data = response.json()
    except ValueError:
        data = {'error': 'Failed to parse response'}
    
    if response.status_code == 200:
        return data
    elif response.status_code == 401 or response.status_code == 403:
        error_msg = data.get('error', {}).get('message', 'Authentication failed')
        logger.error(f'Authentication error: {error_msg}')
        raise AuthenticationError(f'Authentication failed: {error_msg}')
    elif response.status_code == 429:
        logger.warning('Rate limit exceeded')
        raise RateLimitError('Instagram API rate limit exceeded')
    elif response.status_code == 404:
        error_msg = data.get('error', {}).get('message', 'Resource not found')
        logger.error(f'Resource not found: {error_msg}')
        raise ResourceNotFoundError(f'Resource not found: {error_msg}')
    else:
        error_msg = data.get('error', {}).get('message', 'Unknown error')
        logger.error(f'API error (status {response.status_code}): {error_msg}')
        raise InstagramAPIError(f'API error: {error_msg}')


def retry_on_rate_limit(max_retries: int = 3, base_wait: int = 60) -> Callable:
    """
    Decorator to retry API calls on rate limit with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_wait: Base wait time in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retry_count = 0
            while retry_count < max_retries:
                try:
                    return func(*args, **kwargs)
                except RateLimitError:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise
                    wait_time = base_wait * (2 ** (retry_count - 1))
                    logger.warning(
                        f'Rate limited. Retrying in {wait_time} seconds '
                        f'(attempt {retry_count}/{max_retries})'
                    )
                    time.sleep(wait_time)
            return func(*args, **kwargs)
        return wrapper
    return decorator
