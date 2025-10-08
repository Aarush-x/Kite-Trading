"""
Script to get Kite Connect Access Token
Run this script to obtain your access token for the first time
"""

import webbrowser
from kiteconnect import KiteConnect
from config import config

def get_access_token():
    """Get access token using login flow"""
    
    print("🔑 Kite Connect Access Token Generator")
    print("=" * 50)
    
    # Validate API key and secret only (access token will be generated)
    if not config.API_KEY or config.API_KEY == "your_api_key_here":
        print("❌ Please update your API_KEY in config.py first")
        return
    if not config.API_SECRET or config.API_SECRET == "your_api_secret_here":
        print("❌ Please update your API_SECRET in config.py first")
        return
    
    # Initialize Kite Connect
    kite = KiteConnect(api_key=config.API_KEY)
    
    # Generate login URL
    login_url = kite.login_url()
    
    print(f"📱 Opening login URL in your browser...")
    print(f"URL: {login_url}")
    
    # Open browser
    webbrowser.open(login_url)
    
    print("\n📋 Instructions:")
    print("1. Login to your Zerodha account in the opened browser")
    print("2. After successful login, you'll be redirected to a URL")
    print("3. Copy the 'request_token' from the URL")
    print("4. Paste it below when prompted")
    
    # Get request token from user
    request_token = input("\n🔑 Enter the request_token from the URL: ").strip()
    
    if not request_token:
        print("❌ No request token provided")
        return
    
    try:
        # Generate access token
        data = kite.generate_session(request_token, api_secret=config.API_SECRET)
        access_token = data["access_token"]
        
        print(f"\n✅ Access token generated successfully!")
        print(f"🔑 Your access token: {access_token}")
        print(f"\n📝 Update your config.py file with this access token:")
        print(f"ACCESS_TOKEN = \"{access_token}\"")
        
        # Test the access token
        kite.set_access_token(access_token)
        profile = kite.profile()
        
        print(f"\n👤 Profile verification successful!")
        print(f"User: {profile.get('user_name', 'Unknown')}")
        print(f"Email: {profile.get('email', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        print("Please check your API credentials and try again")

if __name__ == "__main__":
    get_access_token()
