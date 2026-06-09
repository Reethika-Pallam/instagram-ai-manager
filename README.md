# Instagram AI Manager

An AI-powered Python application to manage Instagram accounts with analytics, content recommendations, and predictions.

## Features

- **Instagram Graph API Integration**: Connect and authenticate with Instagram Graph API
- **Analytics Fetching**: Retrieve post/reel analytics (views, likes, comments, reach)
- **Content Analysis**: Analyze content and generate caption suggestions
- **View Prediction**: Predict estimated views based on historical data
- **Posting Optimization**: Suggest best posting times and content recommendations

## Project Structure

```
instagram-ai-manager/
├── main.py                 # Entry point
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration and constants
├── api/
│   ├── __init__.py
│   ├── instagram_client.py # Instagram Graph API client
│   └── error_handler.py    # API error handling
├── analytics/
│   ├── __init__.py
│   ├── data_analyzer.py    # Analytics processing
│   └── predictions.py      # View prediction models
├── content/
│   ├── __init__.py
│   ├── caption_generator.py # AI caption suggestions
│   └── recommendations.py   # Content recommendations
└── utils/
    ├── __init__.py
    ├── logger.py           # Logging utility
    └── helpers.py          # Helper functions
```

## Installation

1. Clone the repository
```bash
git clone https://github.com/Reethika-Pallam/instagram-ai-manager.git
cd instagram-ai-manager
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your Instagram Graph API credentials
```

## Usage

```python
from main import InstagramAIManager

manager = InstagramAIManager()
manager.run()
```

## Configuration

Set the following environment variables in `.env`:

- `INSTAGRAM_ACCESS_TOKEN`: Your Instagram Graph API access token
- `INSTAGRAM_BUSINESS_ACCOUNT_ID`: Your Instagram Business Account ID
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Requirements

- Python 3.8+
- requests library for API calls
- python-dotenv for environment variables
- Additional ML/AI libraries as needed

## License

MIT
