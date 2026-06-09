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

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

# Feature Toggles
ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
ENABLE_PREDICTIONS = os.getenv('ENABLE_PREDICTIONS', 'true').lower() == 'true'
ENABLE_RECOMMENDATIONS = os.getenv('ENABLE_RECOMMENDATIONS', 'true').lower() == 'true'
ENABLE_CAPTION_GENERATION = os.getenv('ENABLE_CAPTION_GENERATION', 'true').lower() == 'true'

# API Settings
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
REST_PERIOD_SECONDS = int(os.getenv('REST_PERIOD_SECONDS', '60'))

# Caption Generation Settings
CAPTION_OPTIONS_COUNT = int(os.getenv('CAPTION_OPTIONS_COUNT', '3'))
DEFAULT_CAPTION_TONE = os.getenv('DEFAULT_CAPTION_TONE', 'casual')

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
