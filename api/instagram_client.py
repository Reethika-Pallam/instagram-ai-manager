"""Instagram Graph API client for fetching Instagram data."""

import logging
import time
from typing import List, Dict, Any, Optional
import requests

from config.settings import (
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_BUSINESS_ACCOUNT_ID,
    INSTAGRAM_BASE_URL,
    INSTAGRAM_API_VERSION,
    API_TIMEOUT,
    MAX_RETRIES,
    POST_FIELDS,
    REEL_FIELDS,
    INSIGHTS_FIELDS,
)
from api.error_handler import (
    handle_api_response,
    retry_on_rate_limit,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class InstagramClient:
    """Client for interacting with Instagram Graph API."""
    
    def __init__(
        self,
        access_token: str = INSTAGRAM_ACCESS_TOKEN,
        business_account_id: str = INSTAGRAM_BUSINESS_ACCOUNT_ID,
        api_version: str = INSTAGRAM_API_VERSION,
    ):
        """
        Initialize Instagram API client.
        
        Args:
            access_token: Instagram Graph API access token
            business_account_id: Instagram Business Account ID
            api_version: Instagram API version
        """
        self.access_token = access_token
        self.business_account_id = business_account_id
        self.base_url = f'https://graph.instagram.com/{api_version}'
        self.timeout = API_TIMEOUT
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
    
    def _make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Instagram API.
        
        Args:
            endpoint: API endpoint (e.g., '/me/media')
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Request body data
            
        Returns:
            Parsed JSON response
        """
        url = f'{self.base_url}{endpoint}'
        
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=self.headers,
                timeout=self.timeout,
            )
            return handle_api_response(response)
        except requests.exceptions.Timeout:
            logger.error(f'Request timeout to {endpoint}')
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f'Request failed for {endpoint}: {str(e)}')
            raise
    
    @retry_on_rate_limit(max_retries=MAX_RETRIES)
    def get_recent_posts(
        self,
        limit: int = 10,
        fields: str = POST_FIELDS,
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent posts from Instagram Business Account.
        
        Args:
            limit: Number of posts to fetch
            fields: Comma-separated list of fields to retrieve
            
        Returns:
            List of recent posts with analytics
        """
        logger.info(f'Fetching {limit} recent posts')
        endpoint = f'/{self.business_account_id}/media'
        params = {
            'fields': fields,
            'limit': limit,
        }
        response = self._make_request(endpoint, params=params)
        return response.get('data', [])
    
    @retry_on_rate_limit(max_retries=MAX_RETRIES)
    def get_reel_insights(
        self,
        media_id: str,
        fields: str = INSIGHTS_FIELDS,
    ) -> Dict[str, Any]:
        """
        Fetch detailed insights for a specific reel.
        
        Args:
            media_id: Instagram media ID
            fields: Comma-separated list of insight fields
            
        Returns:
            Reel insights data
        """
        logger.info(f'Fetching insights for reel {media_id}')
        endpoint = f'/{media_id}/insights'
        params = {'metric': fields}
        response = self._make_request(endpoint, params=params)
        return response
    
    @retry_on_rate_limit(max_retries=MAX_RETRIES)
    def get_post_insights(
        self,
        media_id: str,
        fields: str = INSIGHTS_FIELDS,
    ) -> Dict[str, Any]:
        """
        Fetch detailed insights for a specific post.
        
        Args:
            media_id: Instagram media ID
            fields: Comma-separated list of insight fields
            
        Returns:
            Post insights data
        """
        logger.info(f'Fetching insights for post {media_id}')
        endpoint = f'/{media_id}/insights'
        params = {'metric': fields}
        response = self._make_request(endpoint, params=params)
        return response
    
    @retry_on_rate_limit(max_retries=MAX_RETRIES)
    def get_follower_count(self) -> int:
        """
        Get current follower count for the business account.
        
        Returns:
            Current follower count
        """
        logger.info('Fetching follower count')
        endpoint = f'/{self.business_account_id}'
        params = {'fields': 'followers_count'}
        response = self._make_request(endpoint, params=params)
        return response.get('followers_count', 0)
    
    @retry_on_rate_limit(max_retries=MAX_RETRIES)
    def get_audience_demographics(self) -> Dict[str, Any]:
        """
        Fetch audience demographics data.
        
        Returns:
            Audience demographics including age, gender, location
        """
        logger.info('Fetching audience demographics')
        endpoint = f'/{self.business_account_id}/insights'
        params = {
            'metric': 'audience_city,audience_country,audience_gender_age',
        }
        response = self._make_request(endpoint, params=params)
        return response
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get basic information about the business account.
        
        Returns:
            Account information (username, biography, website, etc.)
        """
        logger.info('Fetching account information')
        endpoint = f'/{self.business_account_id}'
        params = {
            'fields': 'id,username,biography,website,profile_picture_url,followers_count,ig_metadata_verification'
        }
        response = self._make_request(endpoint, params=params)
        return response
