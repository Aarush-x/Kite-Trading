"""
Improved access token generation script
Handles session management better
"""

import webbrowser
import time
from kiteconnect import KiteConnect
from config import config

def get_access_token_v2():
    """Get access token with better session handling"""
    
    print("🔑 Kite Connect Access Token Generator v2")
    print("=" * 50)
    
    # Initialize Kite Connect
    kite = KiteConnect(api_key=config.API_KEY)
    
    # Generate fresh login URL
    login_url = kite.login_url()
    
    print(f"📱 Opening fresh login URL...")
    print(f"URL: {login_url}")
    print("\n📋 Instructions:")
    print("1. Complete the login in the browser")
    print("2. After login, you'll be redirected")
    print("3. Copy the ENTIRE redirected URL")
    print("4. Paste it below")
    
    # Open browser
    webbrowser.open(login_url)
    
    # Wait a moment for browser to open
    time.sleep(2)
    
    print("\n⏳ Waiting for you to complete login...")
    print("💡 Tip: Make sure to complete the login process fully")
    
    # Get the full redirected URL from user
    redirected_url = input("\n🔗 Paste the FULL redirected URL here: ").strip()
    
    if not redirected_url:
        print("❌ No URL provided")
        return None
    
    try:
        # Extract request token from URL
        if "request_token=" in redirected_url:
            request_token = redirected_url.split("request_token=")[1].split("&")[0]
        else:
            print("❌ Could not find request_token in the URL")
            print("💡 Make sure you copied the complete redirected URL")
            return None
        
        print(f"🔍 Found request token: {request_token}")
        
        # Generate access token
        print("🔄 Generating access token...")
        data = kite.generate_session(request_token, api_secret=config.API_SECRET)
        access_token = data["access_token"]
        
        print(f"\n✅ SUCCESS! Access token generated!")
        print(f"🔑 Your access token: {access_token}")
        
        # Test the access token
        print("🧪 Testing access token...")
        kite.set_access_token(access_token)
        profile = kite.profile()
        
        print(f"\n👤 Profile verification successful!")
        print(f"User: {profile.get('user_name', 'Unknown')}")
        print(f"Email: {profile.get('email', 'Unknown')}")
        
        print(f"\n📝 Update your config.py file:")
        print(f"ACCESS_TOKEN = \"{access_token}\"")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Common issues:")
        print("- Make sure you completed the full login process")
        print("- Copy the complete redirected URL")
        print("- The request_token should be in the URL")
        return None

if __name__ == "__main__":
    get_access_token_v2()
