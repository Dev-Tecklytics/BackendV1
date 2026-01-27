"""
Test script for AI Code Review Analysis endpoints
Run this after starting the server to verify the implementation
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials (update with actual test user)
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}


def login() -> str:
    """Login and get JWT token"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        json=TEST_USER
    )
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None


def test_ai_analysis_endpoints(token: str):
    """Test AI analysis endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n" + "="*60)
    print("Testing AI Code Review Analysis Endpoints")
    print("="*60)
    
    # Step 1: Get a code review ID (you'll need to replace this with an actual review ID)
    print("\n1. Fetching existing code reviews...")
    # This is a placeholder - you'll need to get an actual review_id from your database
    # For now, we'll use a dummy UUID
    review_id = "REPLACE_WITH_ACTUAL_REVIEW_ID"
    
    print(f"   Using review_id: {review_id}")
    
    # Step 2: Test POST /api/v1/code-review/{review_id}/ai-analysis
    print("\n2. Running AI analysis (POST)...")
    response = requests.post(
        f"{API_BASE}/code-review/{review_id}/ai-analysis",
        headers=headers
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ AI Analysis completed successfully!")
        print(f"   Message: {data.get('message')}")
        print(f"   Summary: {data.get('summary')}")
        print(f"   Cached: {data.get('cached')}")
        
        analysis = data.get('analysis', {})
        print(f"\n   Analysis Details:")
        print(f"   - Overall Assessment: {analysis.get('overallAssessment')[:100]}...")
        print(f"   - Insights Count: {len(analysis.get('insights', []))}")
        print(f"   - Patterns Identified: {len(analysis.get('patterns', {}).get('identified', []))}")
        print(f"   - Anti-Patterns: {len(analysis.get('patterns', {}).get('antiPatterns', []))}")
        print(f"   - Optimization Opportunities: {len(analysis.get('optimizationOpps', []))}")
        print(f"   - Migration Risks: {len(analysis.get('migrationRisks', []))}")
        
        # Print first insight as sample
        insights = analysis.get('insights', [])
        if insights:
            print(f"\n   Sample Insight:")
            insight = insights[0]
            print(f"   - Category: {insight.get('category')}")
            print(f"   - Severity: {insight.get('severity')}")
            print(f"   - Title: {insight.get('title')}")
            print(f"   - Confidence: {insight.get('confidence')}")
    
    elif response.status_code == 404:
        print(f"   ❌ Code review not found")
        print(f"   {response.json()}")
    else:
        print(f"   ❌ Request failed")
        print(f"   {response.text}")
    
    # Step 3: Test GET /api/v1/code-review/{review_id}/ai-analysis
    print("\n3. Retrieving AI analysis (GET)...")
    response = requests.get(
        f"{API_BASE}/code-review/{review_id}/ai-analysis",
        headers=headers
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ AI Analysis retrieved successfully!")
        print(f"   - Analysis ID: {data.get('id')}")
        print(f"   - Review ID: {data.get('reviewId')}")
        print(f"   - Created At: {data.get('createdAt')}")
        print(f"   - Insights Count: {len(data.get('insights', []))}")
    elif response.status_code == 404:
        print(f"   ℹ️  No AI analysis found (expected if not run yet)")
        print(f"   {response.json()}")
    else:
        print(f"   ❌ Request failed")
        print(f"   {response.text}")
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)


def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"⚠️  API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        return False


def main():
    """Main test function"""
    print("="*60)
    print("AI Code Review Analysis - Integration Test")
    print("="*60)
    
    # Test API health
    print("\nChecking API health...")
    if not test_api_health():
        print("\n⚠️  Please start the server first:")
        print("   uv run uvicorn app.main:app --reload")
        return
    
    # Login
    print("\nAttempting login...")
    token = login()
    
    if not token:
        print("\n⚠️  Please update TEST_USER credentials in this script")
        return
    
    # Test AI analysis endpoints
    test_ai_analysis_endpoints(token)
    
    print("\n📝 Note: To fully test this feature:")
    print("   1. Create a workflow by uploading a .xaml file")
    print("   2. Run code review on that workflow")
    print("   3. Use the review_id from step 2 in this test")
    print("   4. Update the review_id variable in this script")


if __name__ == "__main__":
    main()
