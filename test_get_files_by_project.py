"""
Test script for the new GET /api/v1/workflows/files/{project_id} endpoint

This script demonstrates how to:
1. Authenticate and get a token
2. Retrieve all files for a specific project
3. Display file and workflow information
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_VERSION = "v1"


def login(email: str, password: str) -> Optional[str]:
    """Login and get access token"""
    url = f"{BASE_URL}/api/{API_VERSION}/auth/login"
    
    response = requests.post(url, json={
        "email": email,
        "password": password
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful for {email}")
        return data["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None


def get_files_by_project(project_id: str, token: str):
    """Get all files for a specific project"""
    url = f"{BASE_URL}/api/{API_VERSION}/workflows/files/{project_id}"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Retrieved files for project: {data['project_name']}")
        print(f"📊 Platform: {data['platform']}")
        print(f"📁 Total Files: {data['total_files']}")
        print("\n" + "="*80)
        
        for idx, file in enumerate(data['files'], 1):
            print(f"\n📄 File #{idx}: {file['file_name']}")
            print(f"   File ID: {file['file_id']}")
            print(f"   Size: {file['file_size']:,} bytes")
            print(f"   Uploaded: {file['uploaded_at']}")
            
            if file['workflow']:
                workflow = file['workflow']
                print(f"\n   ✅ ANALYZED")
                print(f"   Workflow ID: {workflow['workflow_id']}")
                print(f"   Complexity: {workflow['complexity_level']} (Score: {workflow['complexity_score']})")
                print(f"   Activities: {workflow['activity_count']}")
                print(f"   Nesting Depth: {workflow['nesting_depth']}")
                print(f"   Variables: {workflow['variable_count']}")
                print(f"   Estimated Effort: {workflow['estimated_effort_hours']} hours")
                print(f"   Compatibility: {workflow['compatibility_score']}%")
                
                if workflow['risk_indicators']:
                    print(f"\n   ⚠️  Risk Indicators:")
                    for risk in workflow['risk_indicators']:
                        print(f"      - {risk}")
                
                if workflow['activity_breakdown']:
                    print(f"\n   📊 Activity Breakdown:")
                    for category, count in workflow['activity_breakdown'].items():
                        print(f"      - {category}: {count}")
                
                if workflow['suggestions']:
                    print(f"\n   💡 Suggestions ({len(workflow['suggestions'])}):")
                    for suggestion in workflow['suggestions'][:3]:  # Show first 3
                        print(f"      - [{suggestion['priority'].upper()}] {suggestion['title']}")
                
                if workflow['ai_summary']:
                    print(f"\n   🤖 AI Summary:")
                    print(f"      {workflow['ai_summary'][:100]}...")
            else:
                print(f"\n   ⏳ NOT ANALYZED YET")
            
            print("\n" + "-"*80)
        
        return data
    
    elif response.status_code == 404:
        print(f"❌ Project not found: {project_id}")
        return None
    
    elif response.status_code == 401:
        print(f"❌ Unauthorized - invalid token")
        return None
    
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None


def get_all_projects(token: str):
    """Get all projects for the user"""
    url = f"{BASE_URL}/api/{API_VERSION}/projects"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        projects = response.json()
        print(f"\n📋 Found {len(projects)} project(s):")
        for idx, project in enumerate(projects, 1):
            print(f"   {idx}. {project['name']} ({project['platform']}) - ID: {project['project_id']}")
        return projects
    else:
        print(f"❌ Failed to get projects: {response.text}")
        return []


def main():
    """Main test function"""
    print("="*80)
    print("Testing GET /api/v1/workflows/files/{project_id} Endpoint")
    print("="*80)
    
    # Step 1: Login
    print("\n📝 Step 1: Login")
    email = input("Enter email (or press Enter for test@example.com): ").strip()
    if not email:
        email = "test@example.com"
    
    password = input("Enter password (or press Enter for 'password'): ").strip()
    if not password:
        password = "password"
    
    token = login(email, password)
    
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Step 2: Get all projects
    print("\n📝 Step 2: Get Projects")
    projects = get_all_projects(token)
    
    if not projects:
        print("\n⚠️  No projects found. Please create a project first.")
        return
    
    # Step 3: Select project
    print("\n📝 Step 3: Select Project")
    project_id = input(f"Enter project ID (or press Enter for first project): ").strip()
    
    if not project_id:
        project_id = projects[0]['project_id']
        print(f"Using first project: {projects[0]['name']} ({project_id})")
    
    # Step 4: Get files for project
    print("\n📝 Step 4: Get Files for Project")
    files_data = get_files_by_project(project_id, token)
    
    if files_data:
        # Summary statistics
        analyzed_count = sum(1 for f in files_data['files'] if f['workflow'])
        total_count = files_data['total_files']
        
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        print(f"Project: {files_data['project_name']}")
        print(f"Platform: {files_data['platform']}")
        print(f"Total Files: {total_count}")
        print(f"Analyzed Files: {analyzed_count}")
        print(f"Pending Analysis: {total_count - analyzed_count}")
        
        if analyzed_count > 0:
            total_complexity = sum(
                f['workflow']['complexity_score'] 
                for f in files_data['files'] 
                if f['workflow']
            )
            avg_complexity = total_complexity / analyzed_count
            
            total_effort = sum(
                f['workflow']['estimated_effort_hours'] or 0
                for f in files_data['files'] 
                if f['workflow']
            )
            
            print(f"Average Complexity Score: {avg_complexity:.1f}")
            print(f"Total Estimated Effort: {total_effort} hours")
        
        print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
