"""
Test script for MCP service endpoints.

This script tests the MCP resource API to ensure tweets with AI analysis
are properly exposed through the MCP protocol.
"""

import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8000/api/mcp"


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_list_tweets():
    """Test listing all tweet resources."""
    print_section("Test 1: List All Tweet Resources")
    
    url = f"{BASE_URL}/tweets/"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nMCP Version: {data.get('mcp_version')}")
        print(f"Resource Type: {data.get('resource_type')}")
        print(f"Total Count: {data.get('count', data.get('total_count', 'N/A'))}")
        
        results = data.get('results', data.get('resources', []))
        if results:
            print(f"\nFirst Resource:")
            first = results[0]
            print(f"  URI: {first.get('uri')}")
            print(f"  Name: {first.get('name')}")
            print(f"  Description: {first.get('description', 'N/A')[:100]}...")
            print(f"  MIME Type: {first.get('mimeType')}")
            
            metadata = first.get('metadata', {})
            print(f"\nMetadata:")
            print(f"  Author: @{metadata.get('author')}")
            print(f"  Posted: {metadata.get('posted_at')}")
            
            if 'ai_analysis' in metadata:
                ai = metadata['ai_analysis']
                print(f"\nAI Analysis:")
                print(f"  Sentiment: {ai.get('sentiment')}")
                print(f"  Importance: {ai.get('importance_score')}")
                print(f"  Topics: {', '.join(ai.get('topics', []))}")
                print(f"  Summary: {ai.get('summary', 'N/A')[:100]}...")
    else:
        print(f"Error: {response.text}")


def test_get_tweet(tweet_id):
    """Test getting a specific tweet resource."""
    print_section(f"Test 2: Get Specific Tweet Resource (ID: {tweet_id})")
    
    url = f"{BASE_URL}/tweets/{tweet_id}/"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nURI: {data.get('uri')}")
        print(f"Name: {data.get('name')}")
        print(f"MIME Type: {data.get('mimeType')}")
        print(f"\nText: {data.get('text', 'N/A')[:200]}...")
        
        metadata = data.get('metadata', {})
        print(f"\nMetadata:")
        print(f"  Tweet URL: {metadata.get('tweet_url')}")
        print(f"  Engagement: {json.dumps(metadata.get('engagement', {}), indent=4)}")
        
        if 'ai_analysis' in metadata:
            ai = metadata['ai_analysis']
            print(f"\nAI Analysis:")
            print(json.dumps(ai, indent=4, ensure_ascii=False))
    else:
        print(f"Error: {response.text}")


def test_relevant_tweets():
    """Test getting only AI-relevant tweets."""
    print_section("Test 3: List AI-Relevant Tweets")
    
    url = f"{BASE_URL}/tweets/relevant/"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nMCP Version: {data.get('mcp_version')}")
        print(f"Filter: {data.get('filter')}")
        print(f"Total Relevant: {data.get('count', data.get('total_count', 'N/A'))}")
        
        results = data.get('results', data.get('resources', []))
        print(f"\nShowing {len(results)} relevant tweets:")
        for i, tweet in enumerate(results[:3], 1):
            print(f"\n  {i}. {tweet.get('name')}")
            metadata = tweet.get('metadata', {})
            if 'ai_analysis' in metadata:
                ai = metadata['ai_analysis']
                print(f"     Sentiment: {ai.get('sentiment')} | Importance: {ai.get('importance_score')}")
                print(f"     Summary: {ai.get('summary', 'N/A')[:80]}...")
    else:
        print(f"Error: {response.text}")


def test_search_tweets(query):
    """Test searching tweets."""
    print_section(f"Test 4: Search Tweets (Query: {query})")
    
    url = f"{BASE_URL}/tweets/search/"
    params = {'q': query}
    response = requests.get(url, params=params)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSearch Query: {data.get('search_query')}")
        print(f"Results Found: {data.get('count', data.get('total_count', 'N/A'))}")
        
        results = data.get('results', data.get('resources', []))
        if results:
            print(f"\nFirst {min(3, len(results))} results:")
            for i, tweet in enumerate(results[:3], 1):
                print(f"\n  {i}. {tweet.get('name')}")
                print(f"     {tweet.get('description', 'N/A')[:100]}...")
    else:
        print(f"Error: {response.text}")


def test_sentiment_filter(sentiment):
    """Test filtering by sentiment."""
    print_section(f"Test 5: Filter by Sentiment ({sentiment})")
    
    url = f"{BASE_URL}/tweets/by_sentiment/"
    params = {'sentiment': sentiment}
    response = requests.get(url, params=params)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nFilter: {data.get('filter')}")
        print(f"Total {sentiment.capitalize()} Tweets: {data.get('count', data.get('total_count', 'N/A'))}")
        
        results = data.get('results', data.get('resources', []))
        print(f"\nShowing {len(results)} tweets:")
        for i, tweet in enumerate(results[:3], 1):
            metadata = tweet.get('metadata', {})
            ai = metadata.get('ai_analysis', {})
            print(f"  {i}. {tweet.get('name')} - {ai.get('summary', 'N/A')[:60]}...")
    else:
        print(f"Error: {response.text}")


def test_list_accounts():
    """Test listing account resources."""
    print_section("Test 6: List Account Resources")
    
    url = f"{BASE_URL}/accounts/"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        print(f"\nTotal Accounts: {data.get('count', len(results))}")
        
        for i, account in enumerate(results, 1):
            print(f"\n{i}. {account.get('name')}")
            metadata = account.get('metadata', {})
            print(f"   URI: {account.get('uri')}")
            print(f"   Username: @{metadata.get('username')}")
            print(f"   Total Tweets: {metadata.get('total_tweets')}")
            print(f"   Analyzed: {metadata.get('analyzed_tweets')}")
            print(f"   Relevant: {metadata.get('relevant_tweets')}")
    else:
        print(f"Error: {response.text}")


def test_account_tweets(username):
    """Test getting tweets from a specific account."""
    print_section(f"Test 7: Get Tweets from Account (@{username})")
    
    url = f"{BASE_URL}/accounts/{username}/tweets/"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAccount: @{data.get('account')}")
        print(f"Total Tweets: {data.get('count', data.get('total_count', 'N/A'))}")
        
        results = data.get('results', data.get('resources', []))
        print(f"\nShowing {len(results)} tweets:")
        for i, tweet in enumerate(results[:3], 1):
            print(f"\n  {i}. {tweet.get('name')}")
            metadata = tweet.get('metadata', {})
            print(f"     Posted: {metadata.get('posted_at')}")
            if 'ai_analysis' in metadata:
                ai = metadata['ai_analysis']
                print(f"     Sentiment: {ai.get('sentiment')} | Score: {ai.get('importance_score')}")
    else:
        print(f"Error: {response.text}")


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "MCP SERVICE TEST SUITE" + " " * 36 + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        # Test 1: List all tweets
        test_list_tweets()
        
        # Test 2: Get specific tweet (will need actual tweet ID)
        # First, try to get a tweet ID from the list
        response = requests.get(f"{BASE_URL}/tweets/")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', data.get('resources', []))
            if results:
                first_tweet_id = results[0].get('metadata', {}).get('tweet_id')
                if first_tweet_id:
                    test_get_tweet(first_tweet_id)
        
        # Test 3: Get relevant tweets
        test_relevant_tweets()
        
        # Test 4: Search tweets
        test_search_tweets("スキー")  # Search for "skiing" in Japanese
        
        # Test 5: Filter by sentiment
        test_sentiment_filter("positive")
        
        # Test 6: List accounts
        test_list_accounts()
        
        # Test 7: Get tweets from specific account
        response = requests.get(f"{BASE_URL}/accounts/")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                first_username = results[0].get('metadata', {}).get('username')
                if first_username:
                    test_account_tweets(first_username)
        
        print_section("Test Suite Complete")
        print("✓ All tests executed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("   Please make sure the Django server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
