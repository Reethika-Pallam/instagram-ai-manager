"""Helper functions and utilities."""

import logging
from typing import Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def format_timestamp(timestamp: str) -> datetime:
    """
    Parse Instagram API timestamp to datetime object.
    
    Args:
        timestamp: ISO 8601 timestamp string
        
    Returns:
        Parsed datetime object
    """
    try:
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except (ValueError, AttributeError) as e:
        logger.error(f'Failed to parse timestamp {timestamp}: {str(e)}')
        return datetime.now()


def get_time_period(days: int = 7) -> tuple:
    """
    Get start and end dates for a time period.
    
    Args:
        days: Number of days in the period
        
    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def calculate_percentage_change(
    old_value: float,
    new_value: float,
) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        old_value: Previous value
        new_value: Current value
        
    Returns:
        Percentage change
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def batch_list(items: list, batch_size: int = 100) -> list:
    """
    Split a list into batches.
    
    Args:
        items: List to batch
        batch_size: Size of each batch
        
    Returns:
        List of batches
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary with nested key support.
    
    Args:
        dictionary: Dictionary to get from
        key: Key (supports dot notation for nested keys)
        default: Default value if key not found
        
    Returns:
        Value from dictionary or default
    """
    keys = key.split('.')
    value = dictionary
    
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k, default)
        else:
            return default
    
    return value
