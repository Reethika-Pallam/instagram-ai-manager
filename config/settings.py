"""Application settings and configuration."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Instagram API Configuration
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
INSTAGRAM_API_VERSION = os.getenv('INSTAGRAM_API_VERSION', 'v18.0')
INSTAGRAM_BASE_URL = f'https://graph.instagram.com/{INSTAGRAM_API_VERSION}'

# Anthropic Claude API Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')

# Microsoft Fabric Configuration
FABRIC_WORKSPACE_ID = os.getenv('FABRIC_WORKSPACE_ID')
FABRIC_DATASET_NAME = os.getenv('FABRIC_DATASET_NAME', 'instagram_performance')
FABRIC_TENANT_ID = os.getenv('FABRIC_TENANT_ID')
FABRIC_CLIENT_ID = os.getenv('FABRIC_CLIENT_ID')
FABRIC_CLIENT_SECRET = os.getenv('FABRIC_CLIENT_SECRET')
FABRIC_API_ENDPOINT = os.getenv('FABRIC_API_ENDPOINT', 'https://api.powerbi.com/v1.0/myorg')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

# Feature Toggles
ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
ENABLE_PREDICTIONS = os.getenv('ENABLE_PREDICTIONS', 'true').lower() == 'true'
ENABLE_RECOMMENDATIONS = os.getenv('ENABLE_RECOMMENDATIONS', 'true').lower() == 'true'
ENABLE_CAPTION_GENERATION = os.getenv('ENABLE_CAPTION_GENERATION', 'true').lower() == 'true'
ENABLE_FABRIC_INTEGRATION = os.getenv('ENABLE_FABRIC_INTEGRATION', 'true').lower() == 'true'

# API Settings
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
REST_PERIOD_SECONDS = int(os.getenv('REST_PERIOD_SECONDS', '60'))

# Caption Generation Settings
CAPTION_OPTIONS_COUNT = int(os.getenv('CAPTION_OPTIONS_COUNT', '3'))
DEFAULT_CAPTION_TONE = os.getenv('DEFAULT_CAPTION_TONE', 'casual')

# Knowledge Graph Settings
KNOWLEDGE_GRAPH_ENABLED = os.getenv('KNOWLEDGE_GRAPH_ENABLED', 'true').lower() == 'true'
KNOWLEDGE_GRAPH_MIN_EDGES = int(os.getenv('KNOWLEDGE_GRAPH_MIN_EDGES', '5'))

# API Fields to fetch
POST_FIELDS = 'id,caption,media_type,media_product_type,timestamp,like_count,comments_count,reach,impressions,saved,shares,plays,views'
REEL_FIELDS = 'id,caption,media_type,timestamp,like_count,comments_count,reach,impressions,saved,plays,shares,views'
INSIGHTS_FIELDS = 'impressions,reach,saved,like_count,comments_count,shares,video_views,play,total_interactions'

# Validation
if not INSTAGRAM_ACCESS_TOKEN:
    raise ValueError('INSTAGRAM_ACCESS_TOKEN environment variable is not set')
if not INSTAGRAM_BUSINESS_ACCOUNT_ID:
    raise ValueError('INSTAGRAM_BUSINESS_ACCOUNT_ID environment variable is not set')
if not ANTHROPIC_API_KEY:
    raise ValueError('ANTHROPIC_API_KEY environment variable is not set')
if ENABLE_FABRIC_INTEGRATION:
    if not FABRIC_WORKSPACE_ID:
        raise ValueError('FABRIC_WORKSPACE_ID environment variable is not set')
    if not FABRIC_TENANT_ID:
        raise ValueError('FABRIC_TENANT_ID environment variable is not set')
    if not FABRIC_CLIENT_ID:
        raise ValueError('FABRIC_CLIENT_ID environment variable is not set')
    if not FABRIC_CLIENT_SECRET:
        raise ValueError('FABRIC_CLIENT_SECRET environment variable is not set')
