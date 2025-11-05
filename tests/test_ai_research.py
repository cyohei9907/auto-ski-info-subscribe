"""
Tests for AI research module
"""
import pytest
from ai_research import DeepResearcher


def test_deep_researcher_init():
    """Test DeepResearcher initialization"""
    researcher = DeepResearcher()
    assert researcher.model is not None


def test_sentiment_analysis():
    """Test basic sentiment analysis"""
    researcher = DeepResearcher()
    
    # Test positive sentiment
    positive_text = "This is great and wonderful!"
    sentiment = researcher._analyze_sentiment(positive_text)
    assert sentiment == 'positive'
    
    # Test negative sentiment
    negative_text = "This is terrible and awful!"
    sentiment = researcher._analyze_sentiment(negative_text)
    assert sentiment == 'negative'
    
    # Test neutral sentiment
    neutral_text = "This is a post."
    sentiment = researcher._analyze_sentiment(neutral_text)
    assert sentiment == 'neutral'


def test_extract_key_points():
    """Test key points extraction"""
    researcher = DeepResearcher()
    
    analysis_text = """
    1. First key point
    2. Second key point
    - Third key point
    • Fourth key point
    """
    
    key_points = researcher._extract_key_points(analysis_text)
    assert len(key_points) > 0
    assert all(isinstance(point, str) for point in key_points)
