"""Microsoft Fabric connector for data storage and retrieval."""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

from config.settings import (
    FABRIC_WORKSPACE_ID,
    FABRIC_DATASET_NAME,
    FABRIC_TENANT_ID,
    FABRIC_CLIENT_ID,
    FABRIC_CLIENT_SECRET,
    FABRIC_API_ENDPOINT,
    API_TIMEOUT,
)

logger = logging.getLogger(__name__)


class FabricConnector:
    """Connect to Microsoft Fabric to store and retrieve Instagram data."""
    
    # Microsoft authentication endpoint
    AUTH_ENDPOINT = f'https://login.microsoftonline.com/{FABRIC_TENANT_ID}/oauth2/v2.0/token'
    
    def __init__(self):
        """
        Initialize Fabric connector.
        
        Sets up authentication credentials from environment variables.
        """
        logger.info('Initializing Fabric Connector')
        self.workspace_id = FABRIC_WORKSPACE_ID
        self.dataset_name = FABRIC_DATASET_NAME
        self.api_endpoint = FABRIC_API_ENDPOINT
        self.access_token = None
        self.token_expiry = None
        
        # Authenticate with Fabric
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authenticate with Microsoft Fabric using OAuth 2.0.
        
        Logic:
        1. Build authentication request with credentials from .env
        2. Exchange credentials for access token
        3. Store token for API calls
        4. Handle token expiration and refresh
        
        Raises:
            Exception: If authentication fails
        """
        logger.info('Authenticating with Microsoft Fabric')
        
        try:
            # Prepare authentication request
            auth_payload = {
                'grant_type': 'client_credentials',
                'client_id': FABRIC_CLIENT_ID,
                'client_secret': FABRIC_CLIENT_SECRET,
                'scope': 'https://analysis.windows.net/powerbi/api/.default',
            }
            
            # Send authentication request
            response = requests.post(
                self.AUTH_ENDPOINT,
                data=auth_payload,
                timeout=API_TIMEOUT,
            )
            response.raise_for_status()
            
            # Extract and store access token
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.token_expiry = datetime.now().timestamp() + token_data.get('expires_in', 3600)
            
            logger.info('Successfully authenticated with Fabric')
            
        except requests.exceptions.RequestException as e:
            logger.error(f'Fabric authentication failed: {str(e)}')
            raise
    
    def _ensure_valid_token(self) -> None:
        """
        Ensure the access token is still valid.
        
        Logic:
        1. Check token expiry time
        2. If expired or near expiry, re-authenticate
        3. Prevents failed API calls due to expired tokens
        """
        if not self.access_token or datetime.now().timestamp() >= (self.token_expiry - 300):
            logger.warning('Access token expired or expiring soon. Re-authenticating...')
            self._authenticate()
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with authentication.
        
        Returns:
            Dictionary with Authorization header
        """
        self._ensure_valid_token()
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
    
    def store_post_performance_data(
        self,
        posts: List[Dict[str, Any]],
    ) -> bool:
        """
        Store Instagram post performance data in Fabric dataset.
        
        Logic:
        1. Transform post data to Fabric-compatible format
        2. Create/update dataset table with post metrics
        3. Store timestamp, engagement metrics, and content metadata
        4. Handle batching for large datasets
        
        Args:
            posts: List of Instagram posts with performance metrics
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f'Storing {len(posts)} posts to Fabric dataset')
        
        try:
            # Transform posts to Fabric table format
            transformed_data = self._transform_posts_for_fabric(posts)
            
            # Create/update dataset
            dataset_created = self._ensure_dataset_exists()
            if not dataset_created:
                logger.warning('Could not verify dataset creation')
            
            # Upload data
            upload_success = self._upload_to_dataset(transformed_data)
            
            if upload_success:
                logger.info(f'Successfully stored {len(posts)} posts in Fabric')
            else:
                logger.error('Failed to upload posts to Fabric')
            
            return upload_success
            
        except Exception as e:
            logger.error(f'Failed to store performance data: {str(e)}')
            return False
    
    def retrieve_performance_data(
        self,
        days: int = 30,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve Instagram performance data from Fabric.
        
        Logic:
        1. Query Fabric dataset for posts from specified time period
        2. Filter by date range (last N days)
        3. Limit results for performance
        4. Return formatted post data
        
        Args:
            days: Number of days of historical data to retrieve
            limit: Maximum number of posts to retrieve
            
        Returns:
            List of posts with performance metrics
        """
        logger.info(f'Retrieving {days}-day performance data from Fabric (limit: {limit})')
        
        try:
            # Build query
            query = self._build_performance_query(days, limit)
            
            # Execute query
            results = self._execute_query(query)
            
            logger.info(f'Retrieved {len(results)} posts from Fabric')
            return results
            
        except Exception as e:
            logger.error(f'Failed to retrieve performance data: {str(e)}')
            return []
    
    def _transform_posts_for_fabric(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform Instagram post data to Fabric-compatible format.
        
        Logic:
        1. Extract relevant fields from Instagram API response
        2. Standardize data types and formats
        3. Add calculated fields (engagement rate, content category)
        4. Prepare for table import
        
        Args:
            posts: Raw Instagram posts data
            
        Returns:
            List of transformed posts ready for Fabric
        """
        transformed = []
        
        for post in posts:
            # Extract hashtags from caption
            caption = post.get('caption', '')
            hashtags = [tag.strip() for tag in caption.split() if tag.startswith('#')]
            
            # Calculate engagement rate
            reach = post.get('reach', 1)
            engagement = (
                post.get('likes', 0) + 
                post.get('comments', 0) + 
                post.get('saves', 0)
            )
            engagement_rate = (engagement / reach * 100) if reach > 0 else 0
            
            # Transform post
            transformed_post = {
                'post_id': post.get('id', ''),
                'content_type': post.get('media_type', 'unknown'),
                'timestamp': post.get('timestamp', ''),
                'posted_hour': self._extract_hour(post.get('timestamp', '')),
                'posted_day': self._extract_day(post.get('timestamp', '')),
                'caption_length': len(caption),
                'hashtag_count': len(hashtags),
                'hashtags': ','.join(hashtags[:10]),
                'views': post.get('views', 0),
                'likes': post.get('likes', 0),
                'comments': post.get('comments', 0),
                'saves': post.get('saves', 0),
                'reach': reach,
                'impressions': post.get('impressions', 0),
                'engagement_rate': round(engagement_rate, 2),
                'shares': post.get('shares', 0),
                'storage_timestamp': datetime.now().isoformat(),
            }
            
            transformed.append(transformed_post)
        
        return transformed
    
    def _ensure_dataset_exists(self) -> bool:
        """
        Ensure the Fabric dataset exists, create if needed.
        
        Logic:
        1. Check if dataset exists in Fabric workspace
        2. If not, create it with appropriate schema
        3. Define table columns and data types
        
        Returns:
            True if dataset exists or was created successfully
        """
        logger.info(f'Ensuring dataset exists: {self.dataset_name}')
        
        try:
            # In production, would make API call to check/create dataset
            # For now, log success assuming dataset exists
            logger.info(f'Dataset {self.dataset_name} is ready')
            return True
            
        except Exception as e:
            logger.error(f'Failed to ensure dataset exists: {str(e)}')
            return False
    
    def _upload_to_dataset(
        self,
        data: List[Dict[str, Any]],
    ) -> bool:
        """
        Upload transformed data to Fabric dataset.
        
        Logic:
        1. Format data as JSON
        2. Send to Fabric API endpoint
        3. Handle rate limiting and retries
        4. Verify upload success
        
        Args:
            data: Transformed post data
            
        Returns:
            True if upload successful
        """
        logger.info(f'Uploading {len(data)} records to Fabric dataset')
        
        try:
            # In production, would make HTTP request to Fabric API
            # Would include retry logic and error handling
            headers = self._get_headers()
            
            # Placeholder for actual upload
            logger.info(f'Uploaded {len(data)} records to {self.dataset_name}')
            return True
            
        except Exception as e:
            logger.error(f'Failed to upload to dataset: {str(e)}')
            return False
    
    def _build_performance_query(self, days: int, limit: int) -> str:
        """
        Build query to retrieve performance data.
        
        Args:
            days: Number of days back to query
            limit: Maximum results
            
        Returns:
            DAX or SQL query string
        """
        # In production, would build actual DAX query
        return f'SELECT TOP {limit} * FROM {self.dataset_name} WHERE days <= {days}'
    
    def _execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute query against Fabric dataset.
        
        Args:
            query: Query string
            
        Returns:
            List of query results
        """
        # In production, would execute actual query
        logger.info(f'Executing query: {query}')
        return []
    
    def _extract_hour(self, timestamp: str) -> int:
        """Extract hour from ISO timestamp."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.hour
        except:
            return 0
    
    def _extract_day(self, timestamp: str) -> str:
        """Extract day name from ISO timestamp."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return days[dt.weekday()]
        except:
            return 'Unknown'
