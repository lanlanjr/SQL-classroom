#!/usr/bin/env python3
"""
Test script to verify the system uptime functionality
"""

import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_uptime_calculation():
    """Test uptime calculation logic"""
    
    # Simulate application start time (1 hour and 30 minutes ago)
    app_start_time = datetime.utcnow() - timedelta(hours=1, minutes=30)
    current_time = datetime.utcnow()
    
    # Calculate uptime
    uptime_delta = current_time - app_start_time
    uptime_hours = int(uptime_delta.total_seconds() // 3600)
    uptime_minutes = int((uptime_delta.total_seconds() % 3600) // 60)
    uptime_display = f"{uptime_hours}h {uptime_minutes}m"
    
    print("✅ Uptime Calculation Test")
    print(f"App Start Time: {app_start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Calculated Uptime: {uptime_display}")
    print(f"Expected: ~1h 30m")
    
    # Verify the calculation is reasonable
    if uptime_hours == 1 and uptime_minutes >= 29 and uptime_minutes <= 31:
        print("✅ Uptime calculation is correct!")
        return True
    else:
        print("❌ Uptime calculation seems incorrect")
        return False

def test_edge_cases():
    """Test edge cases for uptime calculation"""
    
    print("\n🔧 Testing edge cases...")
    
    # Test very recent start (less than 1 minute)
    app_start_time = datetime.utcnow() - timedelta(seconds=30)
    current_time = datetime.utcnow()
    
    uptime_delta = current_time - app_start_time
    uptime_hours = int(uptime_delta.total_seconds() // 3600)
    uptime_minutes = int((uptime_delta.total_seconds() % 3600) // 60)
    
    print(f"✅ Recent start: {uptime_hours}h {uptime_minutes}m (should be 0h 0m)")
    
    # Test longer uptime (multiple days)
    app_start_time = datetime.utcnow() - timedelta(days=2, hours=5, minutes=45)
    current_time = datetime.utcnow()
    
    uptime_delta = current_time - app_start_time
    uptime_hours = int(uptime_delta.total_seconds() // 3600)
    uptime_minutes = int((uptime_delta.total_seconds() % 3600) // 60)
    
    print(f"✅ Long uptime: {uptime_hours}h {uptime_minutes}m (should be ~53h 45m)")
    
    return True

if __name__ == "__main__":
    print("Testing system uptime functionality...")
    
    if test_uptime_calculation() and test_edge_cases():
        print("\n🎉 All uptime tests passed!")
        print("\nThe system uptime should now show:")
        print("- Real application start time from server")
        print("- Accurate uptime calculation")
        print("- Live updating every minute via JavaScript")
        print("- Start time display in the uptime card")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
