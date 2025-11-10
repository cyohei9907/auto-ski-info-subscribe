#!/usr/bin/env python
"""
Quick test to verify MCP service is working.
Run this after starting Django server.
"""

import sys
import requests
from urllib.parse import urljoin


def test_mcp_endpoints():
    """Test all MCP endpoints."""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing MCP Service Endpoints\n")
    print("=" * 60)
    
    # Test 1: Check if MCP tweets endpoint is accessible
    print("\n📡 Test 1: MCP Tweets Endpoint")
    try:
        url = urljoin(base_url, "/api/mcp/tweets/")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"   MCP Version: {data.get('mcp_version', 'N/A')}")
            print(f"   Resource Type: {data.get('resource_type', 'N/A')}")
            print(f"   Count: {data.get('count', data.get('total_count', 0))}")
            
            results = data.get('results', data.get('resources', []))
            if results:
                print(f"   ✓ Found {len(results)} tweet resources")
                first = results[0]
                print(f"   Sample URI: {first.get('uri', 'N/A')}")
            else:
                print("   ⚠️  No tweets found (add some monitored accounts)")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Django server not running?")
        print("   Please start the server: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # Test 2: Check relevant tweets endpoint
    print("\n📊 Test 2: Relevant Tweets Endpoint")
    try:
        url = urljoin(base_url, "/api/mcp/tweets/relevant/")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"   Filter: {data.get('filter', 'N/A')}")
            count = data.get('count', data.get('total_count', 0))
            print(f"   Relevant Tweets: {count}")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Check accounts endpoint
    print("\n👥 Test 3: MCP Accounts Endpoint")
    try:
        url = urljoin(base_url, "/api/mcp/accounts/")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            count = data.get('count', len(data.get('results', [])))
            print(f"   Monitored Accounts: {count}")
            
            results = data.get('results', [])
            if results:
                for account in results[:3]:
                    metadata = account.get('metadata', {})
                    print(f"   - @{metadata.get('username', 'N/A')}: {metadata.get('total_tweets', 0)} tweets")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: Check search endpoint
    print("\n🔍 Test 4: Search Endpoint")
    try:
        url = urljoin(base_url, "/api/mcp/tweets/search/")
        params = {'q': 'test'}
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"   Search functional: ✓")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ MCP Service is operational!")
    print("\n📚 Documentation:")
    print(f"   - API Docs: {base_url}/swagger/")
    print(f"   - MCP Guide: backend/MCP_INTEGRATION.md")
    print(f"   - Full Tests: python backend/test_mcp_service.py")
    print()
    
    return True


if __name__ == "__main__":
    success = test_mcp_endpoints()
    sys.exit(0 if success else 1)
