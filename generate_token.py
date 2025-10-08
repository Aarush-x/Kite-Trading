"""
Simple script to generate access token from request token
Usage: python generate_token.py YOUR_REQUEST_TOKEN
"""

import sys
from kiteconnect import KiteConnect
from config import config

def generate_access_token(request_token):
    """Generate access token from request token"""
    
    print("🔑 Generating Access Token...")
    print("=" * 40)
    
    try:
        # Initialize Kite Connect
        kite = KiteConnect(api_key=config.API_KEY)
        
        # Generate access token
        data = kite.generate_session(request_token, api_secret=config.API_SECRET)
        access_token = data["access_token"]
        
        print(f"✅ Access token generated successfully!")
        print(f"🔑 Your access token: {access_token}")
        print(f"\n📝 Update your config.py file with this access token:")
        print(f"ACCESS_TOKEN = \"{access_token}\"")
        
        # Test the access token
        kite.set_access_token(access_token)
        profile = kite.profile()
        
        print(f"\n👤 Profile verification successful!")
        print(f"User: {profile.get('user_name', 'Unknown')}")
        print(f"Email: {profile.get('email', 'Unknown')}")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_token.py YOUR_REQUEST_TOKEN")
        print("Example: python generate_token.py ABC123XYZ")
        sys.exit(1)
    
    request_token = sys.argv[1].strip()
    generate_access_token(request_token)
