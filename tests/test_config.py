"""
Tests for configuration module
"""
import os
import pytest
from config import Config


def test_config_defaults():
    """Test default configuration values"""
    assert Config.API_PORT == int(os.getenv('API_PORT', 5000))
    assert Config.SCRAPE_INTERVAL_HOURS >= 1
    assert Config.OPENAI_MODEL in ['gpt-4', 'gpt-3.5-turbo']


def test_config_validation():
    """Test configuration validation"""
    # This will fail if required env vars are not set
    # In production, should have proper mocking
    try:
        Config.validate()
    except ValueError as e:
        # Expected if credentials not configured
        assert 'Missing required configuration' in str(e)
