"""
Test script to verify Kite Connect API credentials
"""

import requests
from config import config

def test_api_key():
    """Test if the API key is valid"""
    
    print("🔍 Testing Kite Connect API Key...")
    print("=" * 50)
    
    api_key = config.API_KEY
    print(f"API Key: {api_key}")
    
    # Test API key by making a simple request
    try:
        # Test with instruments endpoint (doesn't require authentication)
        url = f"https://api.kite.trade/instruments"
        
        headers = {
            'X-Kite-Version': '3',
            'Authorization': f'token {api_key}'
        }
        
        print("📡 Testing API key validity...")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Key is valid!")
            print("📊 API is responding correctly")
            return True
        elif response.status_code == 403:
            print("❌ API Key is invalid or not approved")
            print("💡 You need to create/approve a Kite Connect app")
            return False
        elif response.status_code == 401:
            print("❌ Unauthorized - API Key might be disabled")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_app_status():
    """Check if the app is properly configured"""
    
    print("\n🔍 Checking App Configuration...")
    print("=" * 50)
    
    print("📋 To check your app status:")
    print("1. Go to: https://kite.trade/apps/")
    print("2. Look for your app with API key:", config.API_KEY)
    print("3. Check if the status is 'Active' or 'Live'")
    print("4. If not active, you may need to:")
    print("   - Wait for approval")
    print("   - Complete verification")
    print("   - Create a new app")

if __name__ == "__main__":
    print("🚀 Kite Connect API Test")
    print("=" * 50)
    
    # Test API key
    is_valid = test_api_key()
    
    if not is_valid:
        check_app_status()
        
        print("\n💡 Next Steps:")
        print("1. Create a new Kite Connect app at: https://kite.trade/apps/")
        print("2. Use the new API credentials")
        print("3. Or use paper trading for testing")
    
    print("\n" + "=" * 50)
