#!/usr/bin/env python3
"""
Updated Skills Module Test Suite - DZ-Volunteer
Matches actual implementation in the codebase
Run: python scripts/test_skills.py
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# ================= CONFIGURATION =================
BASE_URL = "http://localhost:8000/api"

# Authentication tokens
TOKENS = {
    "admin": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY3MDEwODIxLCJpYXQiOjE3NjcwMDkwMjEsImp0aSI6IjJjMWY1OTE5NTgwMTQyZjE4ZTA5ZTNjOWE5MTU2NGFlIiwidXNlcl9pZCI6ImYxZDUxZGJmLTZiOTUtNGM5My1hMGI5LWNkZTkzMGE3MmU1NCJ9.uRDSqBqlu5B7MBa6IQvaPY0nH8EeHYWgh1IyB9KIX1s",
    "volunteer": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY3MDEwNTY0LCJpYXQiOjE3NjcwMDg3NjQsImp0aSI6ImMyMTNiOGI0NTBiNjQxYTZhNWVmZmM3NzYxNjU1M2Q0IiwidXNlcl9pZCI6IjgwZGNhYTE0LTlhNTctNDlhYS05ZjcwLTJmZTYxYjU3N2UxMiJ9.mZYj4-NWNUmQxFZWPwJNa-jNH7E0I0cXmJMIpQdjzJg",
    "organization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY3MDEwMTc1LCJpYXQiOjE3NjcwMDgzNzUsImp0aSI6IjJmMzVkNzFkMDYwYzRmZjhiYjc1MzcyMTBjMjMxNmQ3IiwidXNlcl9pZCI6IjM5ODQ3NDBjLWQ1NTAtNDcxZC1hZTQ5LTNmZThjNTE1NTBmNSJ9.1FCjm4KhGtVb5G2ZdRDui_0s6SHtdiNpOx03CIULCgw"
}

# Test data storage
TEST_DATA = {
    "cat_programming_id": "",
    "cat_web_dev_id": "",
    "cat_languages_id": "",
    "skill_python_id": "",
    "skill_javascript_id": "",
    "skill_arabic_id": "",
    "volunteer_skill_python_id": "",
    "volunteer_skill_javascript_id": "",
    "volunteer_skill_arabic_id": "",
    "mission_skill_python_id": "",
    "mission_id": "11111111-2222-3333-4444-555555555555",
}

EXISTING_IDS = {
    "volunteer_id": "80dcaa14-9a57-49aa-9f70-2fe61b577e12",
    "organization_id": "3984740c-d550-471d-ae49-3fe8c51550f5",
}

# ================= HELPER FUNCTIONS =================
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

def print_step(step_num, description):
    print(f"\n{Colors.BOLD}[Step {step_num}] {description}{Colors.END}")

def print_result(success, message, response=None):
    if success:
        print(f"{Colors.GREEN}  ✓ {message}{Colors.END}")
    else:
        print(f"{Colors.RED}  ✗ {message}{Colors.END}")
        if response:
            print(f"    Status: {response.status_code}")
            try:
                print(f"    Response: {response.json()}")
            except:
                print(f"    Response: {response.text[:200]}")

def make_request(method, endpoint, token_type="admin", data=None, params=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {TOKENS[token_type]}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params,
            timeout=10
        )
        return response
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}  ✗ Cannot connect to {url}. Is the server running?{Colors.END}")
        return None
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}  ✗ Request timed out for {url}{Colors.END}")
        return None

def save_id(key, response_json, id_field="id"):
    if response_json and id_field in response_json:
        TEST_DATA[key] = response_json[id_field]
        return True
    return False

# ================= TEST FUNCTIONS =================

def test_admin_setup():
    """PHASE 1: ADMIN SETUP (Master Data)"""
    print_section("PHASE 1: ADMIN SETUP (Master Data)")
    
    # 1.1 Create Root Category - Programming
    print_step("1.1", "Create Root Category - Programming")
    data = {
        "name": "Programming",
        "description": "Programming and software development skills",
        "parent_category": None
    }
    response = make_request("POST", "/skills/categories/", "admin", data)
    success = response and response.status_code in [201, 200]
    print_result(success, "Created Programming category", response)
    if success:
        save_id("cat_programming_id", response.json())
    
    # 1.2 Create Sub-Category - Web Development
    print_step("1.2", "Create Sub-Category - Web Development")
    if TEST_DATA["cat_programming_id"]:
        data = {
            "name": "Web Development",
            "description": "Frontend and backend web development",
            "parent_category": TEST_DATA["cat_programming_id"]
        }
        response = make_request("POST", "/skills/categories/", "admin", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Created Web Development sub-category", response)
        if success:
            save_id("cat_web_dev_id", response.json())
    
    # 1.3 Create Root Category - Languages
    print_step("1.3", "Create Root Category - Languages")
    data = {
        "name": "Languages",
        "description": "Spoken and written languages",
        "parent_category": None
    }
    response = make_request("POST", "/skills/categories/", "admin", data)
    success = response and response.status_code in [201, 200]
    print_result(success, "Created Languages category", response)
    if success:
        save_id("cat_languages_id", response.json())
    
    # 1.4 Get Category Tree
    print_step("1.4", "Get Category Tree")
    response = make_request("GET", "/skills/categories/tree/", "admin")
    success = response and response.status_code == 200
    print_result(success, "Retrieved category tree", response)
    
    # 1.5 Create Skill - Python
    print_step("1.5", "Create Skill - Python")
    if TEST_DATA["cat_web_dev_id"]:
        data = {
            "name": "Python",
            "category": TEST_DATA["cat_web_dev_id"],
            "description": "Python programming language",
            "verification_requirement": "recommended",
            "is_active": True
        }
        response = make_request("POST", "/skills/skills/", "admin", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Created Python skill", response)
        if success:
            save_id("skill_python_id", response.json())
    
    # 1.6 Create Skill - JavaScript
    print_step("1.6", "Create Skill - JavaScript")
    if TEST_DATA["cat_web_dev_id"]:
        data = {
            "name": "JavaScript",
            "category": TEST_DATA["cat_web_dev_id"],
            "description": "JavaScript for web development",
            "verification_requirement": "recommended",
            "is_active": True
        }
        response = make_request("POST", "/skills/skills/", "admin", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Created JavaScript skill", response)
        if success:
            save_id("skill_javascript_id", response.json())
    
    # 1.7 Create Skill - Arabic Language
    print_step("1.7", "Create Skill - Arabic Language")
    if TEST_DATA["cat_languages_id"]:
        data = {
            "name": "Arabic Language",
            "category": TEST_DATA["cat_languages_id"],
            "description": "Arabic language proficiency",
            "verification_requirement": "none",
            "is_active": True
        }
        response = make_request("POST", "/skills/skills/", "admin", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Created Arabic Language skill", response)
        if success:
            save_id("skill_arabic_id", response.json())
    
    # 1.8 List All Skills
    print_step("1.8", "List All Skills")
    response = make_request("GET", "/skills/skills/", "admin")
    success = response and response.status_code == 200
    if success:
        data = response.json()
        count = len(data.get("results", data if isinstance(data, list) else []))
        print_result(success, f"Found {count} skills", response)
    else:
        print_result(success, "Failed to list skills", response)
    
    # 1.9 Get Skills by Category (using filter)
    print_step("1.9", "Get Skills by Category")
    if TEST_DATA["cat_web_dev_id"]:
        response = make_request("GET", f"/skills/skills/?category={TEST_DATA['cat_web_dev_id']}", "admin")
        success = response and response.status_code == 200
        if success:
            data = response.json()
            count = len(data.get("results", data if isinstance(data, list) else []))
            print_result(success, f"Found {count} skills in Web Development", response)
        else:
            print_result(success, "Failed to get skills by category", response)

def test_volunteer_skills():
    """PHASE 2: VOLUNTEER PROFILE (Adding Skills)"""
    print_section("PHASE 2: VOLUNTEER PROFILE (Adding Skills)")
    
    # 2.1 Add Python Skill
    print_step("2.1", "Add Python Skill to Volunteer Profile")
    if TEST_DATA["skill_python_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_python_id"],
            "proficiency_level": "advanced",
            "years_of_experience": 3.5,
            "last_used_date": "2024-12-01",
            "is_primary": True
        }
        response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Added Python skill", response)
        if success:
            save_id("volunteer_skill_python_id", response.json())
    
    # 2.2 Add JavaScript Skill
    print_step("2.2", "Add JavaScript Skill")
    if TEST_DATA["skill_javascript_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_javascript_id"],
            "proficiency_level": "intermediate",
            "years_of_experience": 2.0,
            "is_primary": False
        }
        response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Added JavaScript skill", response)
        if success:
            save_id("volunteer_skill_javascript_id", response.json())
    
    # 2.3 Add Arabic Language
    print_step("2.3", "Add Arabic Language Skill")
    if TEST_DATA["skill_arabic_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_arabic_id"],
            "proficiency_level": "expert",
            "years_of_experience": 25.0,
            "is_primary": False
        }
        response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Added Arabic skill", response)
        if success:
            save_id("volunteer_skill_arabic_id", response.json())
    
    # 2.4 List Volunteer's Skills
    print_step("2.4", "List Volunteer's Skills")
    response = make_request("GET", f"/skills/volunteer-skills/?volunteer_id={EXISTING_IDS['volunteer_id']}", "volunteer")
    success = response and response.status_code == 200
    if success:
        data = response.json()
        count = len(data.get("results", data if isinstance(data, list) else []))
        print_result(success, f"Volunteer has {count} skills", response)
    else:
        print_result(success, "Failed to list skills", response)
    
    # 2.5 Update Skill
    print_step("2.5", "Update JavaScript Skill Proficiency")
    if TEST_DATA["volunteer_skill_javascript_id"]:
        data = {
            "proficiency_level": "advanced",
            "years_of_experience": 3.0
        }
        response = make_request("PATCH", f"/skills/volunteer-skills/{TEST_DATA['volunteer_skill_javascript_id']}/", "volunteer", data)
        success = response and response.status_code in [200, 204]
        print_result(success, "Updated JavaScript proficiency", response)

def test_admin_verification():
    """PHASE 3: ADMIN VERIFICATION"""
    print_section("PHASE 3: ADMIN VERIFICATION")
    
    # 3.1 Verify Python Skill
    print_step("3.1", "Verify Python Skill")
    if TEST_DATA["volunteer_skill_python_id"]:
        data = {
            "verification_status": "verified",
            "verification_notes": "Portfolio reviewed"
        }
        response = make_request("POST", f"/skills/volunteer-skills/{TEST_DATA['volunteer_skill_python_id']}/verify/", "admin", data)
        success = response and response.status_code in [200, 201]
        print_result(success, "Verified Python skill", response)
    
    # 3.2 Verify JavaScript Skill
    print_step("3.2", "Verify JavaScript Skill")
    if TEST_DATA["volunteer_skill_javascript_id"]:
        data = {
            "verification_status": "verified",
            "verification_notes": "Verified through portfolio"
        }
        response = make_request("POST", f"/skills/volunteer-skills/{TEST_DATA['volunteer_skill_javascript_id']}/verify/", "admin", data)
        success = response and response.status_code in [200, 201]
        print_result(success, "Verified JavaScript skill", response)
    
    # 3.3 List Pending Verifications
    print_step("3.3", "List Pending Verifications")
    response = make_request("GET", "/skills/volunteer-skills/?verification_status=pending", "admin")
    success = response and response.status_code == 200
    if success:
        data = response.json()
        count = len(data.get("results", data if isinstance(data, list) else []))
        print_result(success, f"Found {count} pending verifications", response)
    else:
        print_result(success, "Failed to list pending", response)

def test_mission_skills():
    """PHASE 4: MISSION REQUIREMENTS"""
    print_section("PHASE 4: MISSION REQUIREMENTS")
    
    # 4.1 Add Python Requirement to Mission
    print_step("4.1", "Add Python Requirement to Mission")
    if TEST_DATA["skill_python_id"]:
        data = {
            "mission_id": TEST_DATA["mission_id"],
            "skill_id": TEST_DATA["skill_python_id"],
            "requirement_level": "required",
            "is_verification_required": True,
            "min_proficiency_level": "intermediate"
        }
        response = make_request("POST", "/skills/mission-skills/", "organization", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Added Python requirement", response)
        if success:
            save_id("mission_skill_python_id", response.json())
    
    # 4.2 List Mission Requirements
    print_step("4.2", "List Mission Requirements")
    response = make_request("GET", f"/skills/mission-skills/?mission_id={TEST_DATA['mission_id']}", "organization")
    success = response and response.status_code == 200
    if success:
        data = response.json()
        count = len(data.get("results", data if isinstance(data, list) else []))
        print_result(success, f"Mission has {count} requirements", response)
    else:
        print_result(success, "Failed to list requirements", response)

def test_volunteer_search():
    """PHASE 5: VOLUNTEER SEARCH"""
    print_section("PHASE 5: VOLUNTEER SEARCH")
    
    # 5.1 Search by Skills (Match ALL)
    print_step("5.1", "Search Volunteers by Skills (Match ALL)")
    if TEST_DATA["skill_python_id"] and TEST_DATA["skill_javascript_id"]:
        skill_ids = f"{TEST_DATA['skill_python_id']},{TEST_DATA['skill_javascript_id']}"
        response = make_request("GET", f"/skills/volunteer-search/by_skills/?skill_ids={skill_ids}&match_type=all", "organization")
        success = response and response.status_code == 200
        if success:
            data = response.json()
            count = data.get("count", 0)
            print_result(success, f"Found {count} volunteers with ALL skills", response)
        else:
            print_result(success, "Failed to search", response)
    
    # 5.2 Search by Mission
    print_step("5.2", "Find Volunteers for Mission")
    response = make_request("GET", f"/skills/volunteer-search/by_mission/?mission_id={TEST_DATA['mission_id']}", "organization")
    success = response and response.status_code == 200
    if success:
        data = response.json()
        count = data.get("count", 0)
        print_result(success, f"Found {count} qualified volunteers", response)
    else:
        print_result(success, "Failed to find volunteers", response)
    
    # 5.3 Search by Category
    print_step("5.3", "Search by Skill Category")
    if TEST_DATA["cat_web_dev_id"]:
        response = make_request("GET", f"/skills/volunteer-search/by_skill_category/?category_id={TEST_DATA['cat_web_dev_id']}", "organization")
        success = response and response.status_code == 200
        if success:
            data = response.json()
            count = data.get("count", 0)
            print_result(success, f"Found {count} volunteers in category", response)
        else:
            print_result(success, "Failed to search by category", response)

def test_error_cases():
    """PHASE 6: ERROR CASES"""
    print_section("PHASE 6: ERROR CASES")
    
    # 6.1 Duplicate Skill
    print_step("6.1", "Test Duplicate Skill Error")
    if TEST_DATA["skill_python_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_python_id"],
            "proficiency_level": "expert"
        }
        response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
        success = response and response.status_code == 400
        print_result(success, "Correctly rejected duplicate" if success else f"Got {response.status_code if response else 'None'}", response)
    
    # 6.2 Invalid Proficiency
    print_step("6.2", "Test Invalid Proficiency Level")
    if TEST_DATA["skill_python_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": "00000000-0000-0000-0000-000000000000",
            "proficiency_level": "master"
        }
        response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
        success = response and response.status_code in [400, 404]
        print_result(success, "Correctly rejected invalid data", response)
    
    # 6.3 Volunteer Cannot Search
    print_step("6.3", "Test Volunteer Cannot Search (Privacy)")
    if TEST_DATA["skill_python_id"]:
        response = make_request("GET", f"/skills/volunteer-search/by_skills/?skill_ids={TEST_DATA['skill_python_id']}", "volunteer")
        success = response and response.status_code == 403
        print_result(success, "Correctly prevented volunteer search" if success else f"Got {response.status_code if response else 'None'}", response)

def print_summary():
    """Print test summary"""
    print_section("TEST SUMMARY")
    
    print(f"{Colors.BOLD}Created IDs:{Colors.END}")
    for key, value in TEST_DATA.items():
        if value:
            print(f"  {key}: {value}")

# ================= MAIN =================
def main():
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'*'*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}DZ-VOLUNTEER SKILLS MODULE - TEST SUITE{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'*'*70}{Colors.END}")
    print(f"{Colors.YELLOW}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.YELLOW}Base URL: {BASE_URL}{Colors.END}")
    
    try:
        test_admin_setup()
        test_volunteer_skills()
        test_admin_verification()
        test_mission_skills()
        test_volunteer_search()
        test_error_cases()
        
        print_section("TESTS COMPLETED")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ All test phases completed!{Colors.END}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠ Tests interrupted{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Tests failed: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
    
    print_summary()

if __name__ == "__main__":
    main()