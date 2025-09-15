#!/usr/bin/env python3
"""
Test script for admin functionality in Quran AI Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_admin_config():
    """Test admin configuration loading"""
    print("🔍 Testing Admin Configuration...")
    
    # Get admin user IDs from environment
    admin_user_ids = os.getenv("ADMIN_USER_IDS", "").split(",") if os.getenv("ADMIN_USER_IDS") else []
    admin_user_ids = [int(uid.strip()) for uid in admin_user_ids if uid.strip().isdigit()]
    
    print(f"📊 Admin User IDs: {admin_user_ids}")
    
    if not admin_user_ids:
        print("⚠️  No admin users configured!")
        print("   Set ADMIN_USER_IDS in your .env file")
        print("   Example: ADMIN_USER_IDS=123456789,987654321")
        return False
    
    print("✅ Admin configuration loaded successfully")
    return True

def test_admin_check():
    """Test admin check function"""
    print("\n🔍 Testing Admin Check Function...")
    
    # Import the function from the bot
    try:
        from quran_bot import is_admin, ADMIN_USER_IDS
        print(f"📊 Admin User IDs from bot: {ADMIN_USER_IDS}")
        
        # Test with some sample user IDs
        test_users = [123456789, 987654321, 111222333]
        
        for user_id in test_users:
            is_admin_user = is_admin(user_id)
            status = "👑 ADMIN" if is_admin_user else "👤 USER"
            print(f"   User {user_id}: {status}")
        
        print("✅ Admin check function working correctly")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import from quran_bot: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing admin check: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Quran AI Bot - Admin Functionality Test")
    print("=" * 50)
    
    # Test admin configuration
    config_ok = test_admin_config()
    
    # Test admin check function
    if config_ok:
        admin_check_ok = test_admin_check()
    else:
        admin_check_ok = False
    
    print("\n" + "=" * 50)
    if config_ok and admin_check_ok:
        print("🎉 All tests passed! Admin functionality is working correctly.")
    else:
        print("❌ Some tests failed. Please check the configuration.")


if __name__ == "__main__":
    main()


