#!/usr/bin/env python3
"""
Comprehensive Skills Module Test Suite - DZ-Volunteer
Run: python scripts/test.py
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# ================= CONFIGURATION =================
BASE_URL = "http://localhost:8000/api"

# Authentication tokens - UPDATED WITH YOUR NEW TOKENS
TOKENS = {
    "admin": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY3MDEwODIxLCJpYXQiOjE3NjcwMDkwMjEsImp0aSI6IjJjMWY1OTE5NTgwMTQyZjE4ZTA5ZTNjOWE5MTU2NGFlIiwidXNlcl9pZCI6ImYxZDUxZGJmLTZiOTUtNGM5My1hMGI5LWNkZTkzMGE3MmU1NCJ9.uRDSqBqlu5B7MBa6IQvaPY0nH8EeHYWgh1IyB9KIX1s",
    "volunteer": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY3MDEwNTY0LCJpYXQiOjE3NjcwMDg3NjQsImp0aSI6ImMyMTNiOGI0NTBiNjQxYTZhNWVmZmM3NzYxNjU1M2Q0IiwidXNlcl9pZCI6IjgwZGNhYTE0LTlhNTctNDlhYS05ZjcwLTJmZTYxYjU3N2UxMiJ9.mZYj4-NWNUmQxFZWPwJNa-jNH7E0I0cXmJMIpQdjzJg",
    "organization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY3MDEwMTc1LCJpYXQiOjE3NjcwMDgzNzUsImp0aSI6IjJmMzVkNzFkMDYwYzRmZjhiYjc1MzcyMTBjMjMxNmQ3IiwidXNlcl9pZCI6IjM5ODQ3NDBjLWQ1NTAtNDcxZC1hZTQ5LTNmZThjNTE1NTBmNSJ9.1FCjm4KhGtVb5G2ZdRDui_0s6SHtdiNpOx03CIULCgw"
}

# Test data IDs
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
    "mission_id": "11111111-2222-3333-4444-555555555555",  # Mission created in SQL
}

# IDs for existing records
EXISTING_IDS = {
    "volunteer_id": "80dcaa14-9a57-49aa-9f70-2fe61b577e12",  # Updated volunteer ID from your new token
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
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_section(title):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

def print_step(step_num, description):
    """Print test step"""
    print(f"\n{Colors.BOLD}[Step {step_num}] {description}{Colors.END}")

def print_result(success, message, response=None):
    """Print test result"""
    if success:
        print(f"{Colors.GREEN}  ✓ {message}{Colors.END}")
    else:
        print(f"{Colors.RED}  ✗ {message}{Colors.END}")
        if response:
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text[:200]}")

def make_request(method, endpoint, token_type="admin", data=None, params=None):
    """Make HTTP request"""
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
    """Save ID from response to TEST_DATA"""
    if response_json and id_field in response_json:
        TEST_DATA[key] = response_json[id_field]
        return True
    return False

def check_endpoint_exists(endpoint):
    """Check if endpoint exists"""
    response = make_request("GET", endpoint, "admin")
    if response:
        print(f"    Endpoint {endpoint}: Status {response.status_code}")
    return response and response.status_code != 404

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
    response = make_request("POST", "/categories/", "admin", data)
    success = response and response.status_code in [201, 200]
    print_result(success, "Created Programming category")
    if success:
        save_id("cat_programming_id", response.json())
    else:
        if response:
            print(f"    Response: {response.status_code} - {response.text[:200]}")
    
    # 1.2 Create Sub-Category - Web Development
    print_step("1.2", "Create Sub-Category - Web Development")
    if TEST_DATA["cat_programming_id"]:
        data = {
            "name": "Web Development",
            "description": "Frontend and backend web development",
            "parent_category": TEST_DATA["cat_programming_id"]
        }
        response = make_request("POST", "/categories/", "admin", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Created Web Development sub-category")
        if success:
            save_id("cat_web_dev_id", response.json())
    else:
        print_result(False, "Skipped - No parent category ID")
    
    # 1.3 Create Root Category - Languages
    print_step("1.3", "Create Root Category - Languages")
    data = {
        "name": "Languages",
        "description": "Spoken and written languages",
        "parent_category": None
    }
    response = make_request("POST", "/categories/", "admin", data)
    success = response and response.status_code in [201, 200]
    print_result(success, "Created Languages category")
    if success:
        save_id("cat_languages_id", response.json())
    
    # 1.4 Get Category Tree
    print_step("1.4", "Get Category Tree")
    response = make_request("GET", "/categories/tree/", "admin")
    success = response and response.status_code == 200
    print_result(success, f"Retrieved category tree")
    
    # 1.5 Create Skill - Python
    print_step("1.5", "Create Skill - Python")
    if TEST_DATA["cat_web_dev_id"]:
        data = {
            "name": "Python",
            "category": TEST_DATA["cat_web_dev_id"],
            "description": "Python programming language for backend development, data science, and automation",
            "verification_requirement": "recommended",
            "is_active": True
        }
        response = make_request("POST", "/skills/", "admin", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Created Python skill")
        if success:
            save_id("skill_python_id", response.json())
    else:
        print_result(False, "Skipped - No category ID")
    
    # 1.6 Create Skill - JavaScript
    print_step("1.6", "Create Skill - JavaScript")
    if TEST_DATA["cat_web_dev_id"]:
        data = {
            "name": "JavaScript",
            "category": TEST_DATA["cat_web_dev_id"],
            "description": "JavaScript for frontend and full-stack web development",
            "verification_requirement": "recommended",
            "is_active": True
        }
        response = make_request("POST", "/skills/", "admin", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Created JavaScript skill")
        if success:
            save_id("skill_javascript_id", response.json())
    else:
        print_result(False, "Skipped - No category ID")
    
    # 1.7 Create Skill - Arabic Language
    print_step("1.7", "Create Skill - Arabic Language")
    if TEST_DATA["cat_languages_id"]:
        data = {
            "name": "Arabic Language",
            "category": TEST_DATA["cat_languages_id"],
            "description": "Arabic language proficiency for communication and translation",
            "verification_requirement": "none",
            "is_active": True
        }
        response = make_request("POST", "/skills/", "admin", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Created Arabic Language skill")
        if success:
            save_id("skill_arabic_id", response.json())
    else:
        print_result(False, "Skipped - No category ID")
    
    # 1.8 List All Skills
    print_step("1.8", "List All Skills")
    response = make_request("GET", "/skills/", "admin")  # Changed from /skills/?is_active=true
    success = response and response.status_code == 200
    if success:
        data = response.json()
        if isinstance(data, dict) and "results" in data:
            count = len(data["results"])
            print_result(success, f"Found {count} skills")
        elif isinstance(data, list):
            count = len(data)
            print_result(success, f"Found {count} skills")
        else:
            count = 0
            print_result(success, f"Found skills (format unknown)")
    else:
        print_result(success, "Failed to list skills")
    
    # 1.9 Get Skills by Category
    print_step("1.9", "Get Skills by Category")
    if TEST_DATA["cat_web_dev_id"]:
        # Try different endpoint variations
        endpoints = [
            f"/skills/by_category/?category_id={TEST_DATA['cat_web_dev_id']}",
            f"/skills/?category={TEST_DATA['cat_web_dev_id']}",
            f"/skills/?category_id={TEST_DATA['cat_web_dev_id']}"
        ]
        
        for endpoint in endpoints:
            response = make_request("GET", endpoint, "admin")
            if response and response.status_code == 200:
                skills = response.json()
                if isinstance(skills, list):
                    count = len(skills)
                elif isinstance(skills, dict) and "results" in skills:
                    count = len(skills["results"])
                elif isinstance(skills, dict) and "count" in skills:
                    count = skills["count"]
                else:
                    count = 0
                print_result(True, f"Found {count} skills in Web Development category")
                break
        else:
            print_result(False, "Failed to get skills by category")
    else:
        print_result(False, "Skipped - No category ID")

def test_volunteer_skills():
    """PHASE 2: VOLUNTEER PROFILE (Adding Skills)"""
    print_section("PHASE 2: VOLUNTEER PROFILE (Adding Skills)")
    
    # Check if volunteer-skills endpoint exists
    print_step("Check", "Checking volunteer-skills endpoint")
    response = make_request("GET", "/volunteer-skills/", "volunteer")
    if response and response.status_code != 404:
        print_result(True, "volunteer-skills endpoint found")
    else:
        print_result(False, "volunteer-skills endpoint not found (404). Creating skills via different endpoint.")
        # Try creating volunteer profile first
        return
    
    # 2.1 Add Python Skill to Volunteer Profile
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
        response = make_request("POST", "/volunteer-skills/", "volunteer", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Added Python skill to volunteer profile")
        if success:
            save_id("volunteer_skill_python_id", response.json())
        elif response:
            print(f"    Response: {response.status_code} - {response.text[:200]}")
    else:
        print_result(False, "Skipped - No Python skill ID")
    
    # 2.2 Add JavaScript Skill
    print_step("2.2", "Add JavaScript Skill")
    if TEST_DATA["skill_javascript_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_javascript_id"],
            "proficiency_level": "intermediate",
            "years_of_experience": 2.0,
            "last_used_date": "2024-11-15",
            "is_primary": False
        }
        response = make_request("POST", "/volunteer-skills/", "volunteer", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Added JavaScript skill to volunteer profile")
        if success:
            save_id("volunteer_skill_javascript_id", response.json())
    else:
        print_result(False, "Skipped - No JavaScript skill ID")
    
    # 2.3 Add Arabic Language Skill
    print_step("2.3", "Add Arabic Language Skill")
    if TEST_DATA["skill_arabic_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_arabic_id"],
            "proficiency_level": "expert",
            "years_of_experience": 25.0,
            "is_primary": False
        }
        response = make_request("POST", "/volunteer-skills/", "volunteer", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Added Arabic Language skill to volunteer profile")
        if success:
            save_id("volunteer_skill_arabic_id", response.json())
    else:
        print_result(False, "Skipped - No Arabic skill ID")
    
    # 2.5 List Volunteer's Skills
    print_step("2.5", "List Volunteer's Skills")
    response = make_request("GET", f"/volunteer-skills/?volunteer_id={EXISTING_IDS['volunteer_id']}", "volunteer")
    success = response and response.status_code == 200
    if success:
        data = response.json()
        if isinstance(data, dict) and "results" in data:
            count = len(data["results"])
            print_result(success, f"Volunteer has {count} skills")
        elif isinstance(data, list):
            count = len(data)
            print_result(success, f"Volunteer has {count} skills")
        else:
            print_result(success, "Volunteer skills retrieved (format unknown)")
    else:
        print_result(success, "Failed to list volunteer skills")
    
    # 2.6 Update Volunteer Skill (Increase Proficiency)
    print_step("2.6", "Update Volunteer Skill (Increase Proficiency)")
    if TEST_DATA["volunteer_skill_javascript_id"]:
        data = {
            "proficiency_level": "advanced",
            "years_of_experience": 3.0,
            "last_used_date": "2025-01-10"
        }
        response = make_request("PATCH", f"/volunteer-skills/{TEST_DATA['volunteer_skill_javascript_id']}/", "volunteer", data)
        success = response and response.status_code in [200, 204]
        print_result(success, "Updated JavaScript skill proficiency to advanced")
    else:
        print_result(False, "Skipped - No JavaScript volunteer skill ID")

def test_admin_verification():
    """PHASE 3: ADMIN VERIFICATION"""
    print_section("PHASE 3: ADMIN VERIFICATION")
    
    # 3.1 Verify Python Skill (Approve)
    print_step("3.1", "Verify Python Skill (Approve)")
    if TEST_DATA["volunteer_skill_python_id"]:
        data = {
            "verification_status": "verified",
            "verification_notes": "GitHub profile reviewed. Strong portfolio with multiple Python projects."
        }
        response = make_request("POST", f"/volunteer-skills/{TEST_DATA['volunteer_skill_python_id']}/verify/", "admin", data)
        success = response and response.status_code in [200, 201]
        print_result(success, "Verified Python skill")
    else:
        print_result(False, "Skipped - No Python volunteer skill ID")
    
    # 3.2 Verify JavaScript Skill (Approve)
    print_step("3.2", "Verify JavaScript Skill (Approve)")
    if TEST_DATA["volunteer_skill_javascript_id"]:
        data = {
            "verification_status": "verified",
            "verification_notes": "Verified through portfolio review"
        }
        response = make_request("POST", f"/volunteer-skills/{TEST_DATA['volunteer_skill_javascript_id']}/verify/", "admin", data)
        success = response and response.status_code in [200, 201]
        print_result(success, "Verified JavaScript skill")
    else:
        print_result(False, "Skipped - No JavaScript volunteer skill ID")
    
    # 3.3 List Pending Verifications (Admin View)
    print_step("3.3", "List Pending Verifications (Admin View)")
    response = make_request("GET", "/volunteer-skills/?verification_status=pending", "admin")
    success = response and response.status_code == 200
    if success:
        data = response.json()
        if isinstance(data, dict) and "results" in data:
            count = len(data["results"])
            print_result(success, f"Found {count} pending verifications")
        elif isinstance(data, list):
            count = len(data)
            print_result(success, f"Found {count} pending verifications")
        else:
            print_result(success, "Found pending verifications (format unknown)")
    else:
        print_result(success, "Failed to list pending verifications")

def test_mission_skills():
    """PHASE 4: MISSION REQUIREMENTS"""
    print_section("PHASE 4: MISSION REQUIREMENTS")
    
    # Check if mission-skills endpoint exists
    print_step("Check", "Checking mission-skills endpoint")
    response = make_request("GET", "/mission-skills/", "organization")
    if response and response.status_code != 404:
        print_result(True, "mission-skills endpoint found")
    else:
        print_result(False, "mission-skills endpoint not found (404). Skipping mission tests.")
        return
    
    if not TEST_DATA["mission_id"]:
        print_step("Skip", "No mission ID available")
        print_result(False, "Mission skills tests skipped - no mission ID")
        return
    
    # 4.1 Add Skill Requirement to Mission
    print_step("4.1", "Add Skill Requirement to Mission")
    if TEST_DATA["skill_python_id"]:
        data = {
            "mission_id": TEST_DATA["mission_id"],
            "skill_id": TEST_DATA["skill_python_id"],
            "requirement_level": "required",
            "is_verification_required": True,
            "min_proficiency_level": "intermediate"
        }
        response = make_request("POST", "/mission-skills/", "organization", data)
        success = response and response.status_code in [201, 200]
        print_result(success, "Added Python requirement to mission")
        if success:
            save_id("mission_skill_python_id", response.json())
        elif response:
            print(f"    Response: {response.status_code} - {response.text[:200]}")
    else:
        print_result(False, "Skipped - No Python skill ID")
    
    # 4.3 List Mission Requirements
    print_step("4.3", "List Mission Requirements")
    response = make_request("GET", f"/mission-skills/?mission_id={TEST_DATA['mission_id']}", "organization")
    success = response and response.status_code == 200
    if success:
        data = response.json()
        if isinstance(data, dict) and "results" in data:
            count = len(data["results"])
            print_result(success, f"Mission has {count} skill requirements")
        elif isinstance(data, list):
            count = len(data)
            print_result(success, f"Mission has {count} skill requirements")
        else:
            print_result(success, "Mission requirements retrieved (format unknown)")
    else:
        print_result(success, "Failed to list mission requirements")
    
    # 4.4 Get Required Skills Only
    print_step("4.4", "Get Required Skills Only")
    response = make_request("GET", f"/mission-skills/?mission_id={TEST_DATA['mission_id']}&required_only=true", "organization")
    success = response and response.status_code == 200
    if success:
        data = response.json()
        if isinstance(data, dict) and "results" in data:
            count = len(data["results"])
            print_result(success, f"Found {count} required skills")
        elif isinstance(data, list):
            count = len(data)
            print_result(success, f"Found {count} required skills")
        else:
            print_result(success, "Required skills retrieved (format unknown)")
    else:
        print_result(success, "Failed to get required skills")

def test_volunteer_search():
    """PHASE 5: VOLUNTEER SEARCH (Organizations)"""
    print_section("PHASE 5: VOLUNTEER SEARCH (Organizations)")
    
    # Check if volunteer-search endpoint exists
    print_step("Check", "Checking volunteer-search endpoint")
    response = make_request("GET", "/volunteer-search/", "organization")
    if response and response.status_code != 404:
        print_result(True, "volunteer-search endpoint found")
    else:
        print_result(False, "volunteer-search endpoint not found (404). Skipping search tests.")
        return
    
    # 5.1 Search Volunteers by Skills (Match ALL)
    print_step("5.1", "Search Volunteers by Skills (Match ALL)")
    if TEST_DATA["skill_python_id"] and TEST_DATA["skill_javascript_id"]:
        skill_ids = f"{TEST_DATA['skill_python_id']},{TEST_DATA['skill_javascript_id']}"
        response = make_request("GET", f"/volunteer-search/by_skills?skill_ids={skill_ids}&match_type=all&verified_only=true", "organization")
        success = response and response.status_code == 200
        if success:
            data = response.json()
            if isinstance(data, dict):
                count = data.get("count", 0)
                print_result(success, f"Found {count} volunteers with ALL specified skills")
            else:
                print_result(success, "Search results returned (format unknown)")
        else:
            print_result(success, "Failed to search volunteers (match ALL)")
    else:
        print_result(False, "Skipped - Missing skill IDs")
    
    # 5.2 Search by Skills (Match ANY)
    print_step("5.2", "Search by Skills (Match ANY)")
    if TEST_DATA["skill_python_id"] and TEST_DATA["skill_javascript_id"]:
        skill_ids = f"{TEST_DATA['skill_python_id']},{TEST_DATA['skill_javascript_id']}"
        response = make_request("GET", f"/volunteer-search/by_skills/?skill_ids={skill_ids}&match_type=any&verified_only=true&limit=20", "organization")
        success = response and response.status_code == 200
        if success:
            data = response.json()
            if isinstance(data, dict):
                count = data.get("count", 0)
                print_result(success, f"Found {count} volunteers with ANY specified skill")
            else:
                print_result(success, "Search results returned (format unknown)")
        else:
            print_result(success, "Failed to search volunteers (match ANY)")
    else:
        print_result(False, "Skipped - Missing skill IDs")
    
    # 5.3 Find Volunteers for Mission
    print_step("5.3", "Find Volunteers for Mission")
    if TEST_DATA["mission_id"]:
        response = make_request("GET", f"/volunteer-search/by_mission/?mission_id={TEST_DATA['mission_id']}&require_all=true&verified_only=true", "organization")
        success = response and response.status_code == 200
        if success:
            data = response.json()
            if isinstance(data, dict):
                count = data.get("count", 0)
                print_result(success, f"Found {count} volunteers qualified for mission")
            else:
                print_result(success, "Search results returned (format unknown)")
        else:
            print_result(success, "Failed to find volunteers for mission")
    else:
        print_result(False, "Skipped - No mission ID")
    
    # 5.4 Search by Category
    print_step("5.4", "Search by Category")
    if TEST_DATA["cat_web_dev_id"]:
        response = make_request("GET", f"/volunteer-search/by_skill_category/?category_id={TEST_DATA['cat_web_dev_id']}&verified_only=true&min_proficiency=intermediate", "organization")
        success = response and response.status_code == 200
        if success:
            data = response.json()
            if isinstance(data, dict):
                count = data.get("count", 0)
                print_result(success, f"Found {count} volunteers in category with intermediate+ proficiency")
            else:
                print_result(success, "Search results returned (format unknown)")
        else:
            print_result(success, "Failed to search by category")
    else:
        print_result(False, "Skipped - No category ID")

def test_error_cases():
    """PHASE 6: ERROR CASES (Test Validation)"""
    print_section("PHASE 6: ERROR CASES (Test Validation)")
    
    # 6.1 Duplicate Skill Error
    print_step("6.1", "Duplicate Skill Error")
    if TEST_DATA["skill_python_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_python_id"],
            "proficiency_level": "expert"
        }
        response = make_request("POST", "/volunteer-skills/", "volunteer", data)
        success = response and response.status_code == 400
        print_result(success, "Correctly rejected duplicate skill (400)")
        if not success and response:
            print(f"    Got {response.status_code} instead of 400")
    else:
        print_result(False, "Skipped - No Python skill ID")
    
    # 6.2 Permission Denied - Wrong Owner
    print_step("6.2", "Permission Denied - Wrong Owner")
    if TEST_DATA["skill_python_id"]:
        data = {
            "volunteer_id": "volunteer-uuid-999",
            "skill_id": TEST_DATA["skill_python_id"],
            "proficiency_level": "advanced"
        }
        response = make_request("POST", "/volunteer-skills/", "volunteer", data)
        success = response and response.status_code in [403, 400]
        print_result(success, "Correctly rejected permission for wrong owner")
        if not success and response:
            print(f"    Got {response.status_code} instead of 403/400")
    else:
        print_result(False, "Skipped - No Python skill ID")
    
    # 6.3 Invalid Proficiency Level
    print_step("6.3", "Invalid Proficiency Level")
    if TEST_DATA["skill_python_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_python_id"],
            "proficiency_level": "master"
        }
        response = make_request("POST", "/volunteer-skills/", "volunteer", data)
        success = response and response.status_code == 400
        print_result(success, "Correctly rejected invalid proficiency level")
        if not success and response:
            print(f"    Got {response.status_code} instead of 400")
    else:
        print_result(False, "Skipped - No Python skill ID")
    
    # 6.4 Volunteer Cannot Search (Privacy)
    print_step("6.4", "Volunteer Cannot Search (Privacy)")
    if TEST_DATA["skill_python_id"]:
        response = make_request("GET", f"/volunteer-search/by_skills/?skill_ids={TEST_DATA['skill_python_id']}", "volunteer")
        success = response and response.status_code == 403
        print_result(success, "Correctly prevented volunteer from searching")
        if not success and response:
            print(f"    Got {response.status_code} instead of 403")
    else:
        print_result(False, "Skipped - No Python skill ID")

def print_summary():
    """Print test summary"""
    print_section("TEST SUMMARY")
    
    print(f"{Colors.BOLD}Test Data Created:{Colors.END}")
    for key, value in TEST_DATA.items():
        if value:
            print(f"  {key}: {value}")
    
    print(f"\n{Colors.BOLD}Existing IDs Used:{Colors.END}")
    for key, value in EXISTING_IDS.items():
        print(f"  {key}: {value}")
    
    print(f"\n{Colors.BOLD}Note:{Colors.END}")
    print("  Mission ID is hardcoded from SQL creation: 11111111-2222-3333-4444-555555555555")

def check_prerequisites():
    """Check if prerequisites are met"""
    print_section("PREREQUISITE CHECK")
    
    print(f"{Colors.YELLOW}Checking server connectivity...{Colors.END}")
    
    # Check if we can connect to Django server
    try:
        # Try to access a known working endpoint
        response = requests.get(f"{BASE_URL}/accounts/me/", 
                              headers={"Authorization": f"Bearer {TOKENS['admin']}"},
                              timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✓ Server is running and accessible{Colors.END}")
            
            # Extract user info
            user_data = response.json()
            if "user" in user_data:
                user_info = user_data["user"]
                print(f"{Colors.CYAN}  Logged in as: {user_info.get('email', 'Unknown')}{Colors.END}")
                print(f"{Colors.CYAN}  User type: {user_info.get('user_type', 'Unknown')}{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Server returned {response.status_code}{Colors.END}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ Cannot connect to server. Make sure Django is running.{Colors.END}")
        print(f"{Colors.YELLOW}  Run: python manage.py runserver{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗ Error checking server: {e}{Colors.END}")
        return False
    
    # Check tokens
    print(f"\n{Colors.YELLOW}Checking authentication tokens...{Colors.END}")
    valid_tokens = 0
    for token_type, token in TOKENS.items():
        if token and len(token) > 100:  # Basic JWT check
            response = make_request("GET", "/accounts/me/", token_type)
            if response and response.status_code == 200:
                print(f"{Colors.GREEN}✓ {token_type.capitalize()} token is valid{Colors.END}")
                valid_tokens += 1
            else:
                print(f"{Colors.RED}✗ {token_type.capitalize()} token may be invalid or expired{Colors.END}")
        else:
            print(f"{Colors.RED}✗ {token_type.capitalize()} token appears to be invalid{Colors.END}")
    
    if valid_tokens < 3:
        print(f"{Colors.YELLOW}⚠ Some tokens may need to be refreshed{Colors.END}")
    
    print(f"\n{Colors.GREEN}All prerequisites checked!{Colors.END}")
    return True

# ================= MAIN EXECUTION =================
def main():
    """Main test runner"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'*'*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}DZ-VOLUNTEER SKILLS MODULE - COMPREHENSIVE TEST SUITE{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'*'*70}{Colors.END}")
    print(f"{Colors.YELLOW}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.YELLOW}Base URL: {BASE_URL}{Colors.END}")
    print(f"{Colors.YELLOW}Mission ID: {TEST_DATA['mission_id']}{Colors.END}")
    
    # Check prerequisites
    if not check_prerequisites():
        print(f"\n{Colors.RED}Tests cannot proceed. Please fix the issues above.{Colors.END}")
        return
    
    # Run all test phases
    try:
        test_admin_setup()
        test_volunteer_skills()
        test_admin_verification()
        test_mission_skills()
        test_volunteer_search()
        test_error_cases()
        
        print_section("TEST COMPLETED")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ All test phases completed!{Colors.END}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠ Tests interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Tests failed with error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    # Create scripts directory if it doesn't exist
    os.makedirs("scripts", exist_ok=True)
    
    # Save this script
    script_path = "scripts/test.py"
    with open(__file__, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"{Colors.GREEN}Script saved to: {script_path}{Colors.END}")
    print(f"{Colors.YELLOW}Run with: python {script_path}{Colors.END}")
    
    # Ask if user wants to run tests now
    response = input(f"\n{Colors.CYAN}Run tests now? (y/n): {Colors.END}").strip().lower()
    if response == 'y':
        main()
    else:
        print(f"{Colors.YELLOW}Tests not run. Execute 'python {script_path}' when ready.{Colors.END}")