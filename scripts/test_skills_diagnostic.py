#!/usr/bin/env python3
"""
Comprehensive Skills Module Test Suite
Tests all views, URLs, and permissions
File: scripts/test_skills_comprehensive.py
Run: python scripts/test_skills_comprehensive.py
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, List

# ================= CONFIGURATION =================
BASE_URL = "http://localhost:8000/api"

TOKENS = {
    "admin": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY3MDEwODIxLCJpYXQiOjE3NjcwMDkwMjEsImp0aSI6IjJjMWY1OTE5NTgwMTQyZjE4ZTA5ZTNjOWE5MTU2NGFlIiwidXNlcl9pZCI6ImYxZDUxZGJmLTZiOTUtNGM5My1hMGI5LWNkZTkzMGE3MmU1NCJ9.uRDSqBqlu5B7MBa6IQvaPY0nH8EeHYWgh1IyB9KIX1s",
    "volunteer": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY3MDEwNTY0LCJpYXQiOjE3NjcwMDg3NjQsImp0aSI6ImMyMTNiOGI0NTBiNjQxYTZhNWVmZmM3NzYxNjU1M2Q0IiwidXNlcl9pZCI6IjgwZGNhYTE0LTlhNTctNDlhYS05ZjcwLTJmZTYxYjU3N2UxMiJ9.mZYj4-NWNUmQxFZWPwJNa-jNH7E0I0cXmJMIpQdjzJg",
    "organization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY3MDEwMTc1LCJpYXQiOjE3NjcwMDgzNzUsImp0aSI6IjJmMzVkNzFkMDYwYzRmZjhiYjc1MzcyMTBjMjMxNmQ3IiwidXNlcl9pZCI6IjM5ODQ3NDBjLWQ1NTAtNDcxZC1hZTQ5LTNmZThjNTE1NTBmNSJ9.1FCjm4KhGtVb5G2ZdRDui_0s6SHtdiNpOx03CIULCgw"
}

TEST_DATA = {
    "cat_tech_id": "",
    "cat_web_id": "",
    "cat_lang_id": "",
    "skill_python_id": "",
    "skill_js_id": "",
    "skill_react_id": "",
    "skill_arabic_id": "",
    "skill_french_id": "",
    "volunteer_skill_python_id": "",
    "volunteer_skill_js_id": "",
    "volunteer_skill_arabic_id": "",
    "mission_skill_python_id": "",
    "mission_skill_js_id": "",
    "mission_id": "11111111-2222-3333-4444-555555555555",
}

EXISTING_IDS = {
    "volunteer_id": "80dcaa14-9a57-49aa-9f70-2fe61b577e12",
    "organization_id": "3984740c-d550-471d-ae49-3fe8c51550f5",
}

# Test statistics
stats = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
}

# ================= HELPER FUNCTIONS =================
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'-'*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'-'*70}{Colors.END}")

def print_test(test_name):
    stats["total"] += 1
    print(f"\n{Colors.BOLD}[Test {stats['total']}] {test_name}{Colors.END}")

def print_result(success, message, response=None):
    if success:
        stats["passed"] += 1
        print(f"{Colors.GREEN}  ✓ PASS: {message}{Colors.END}")
    else:
        stats["failed"] += 1
        print(f"{Colors.RED}  ✗ FAIL: {message}{Colors.END}")
        if response:
            print(f"    Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"    Error: {json.dumps(error_data, indent=6)}")
            except:
                print(f"    Response: {response.text[:300]}")

def print_skip(message):
    stats["skipped"] += 1
    print(f"{Colors.YELLOW}  ⊘ SKIP: {message}{Colors.END}")

def make_request(method, endpoint, token_type="admin", data=None, params=None, expect_success=True):
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
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}  ✗ Request failed: {e}{Colors.END}")
        return None

def save_id(key, response_json, id_field="id"):
    if response_json and id_field in response_json:
        TEST_DATA[key] = response_json[id_field]
        return True
    return False

# ================= TEST SUITES =================

def test_skill_categories():
    """Test SkillCategoryViewSet"""
    print_section("TESTING SKILL CATEGORIES")
    
    # Test 1: List categories (public access)
    print_test("List categories (public)")
    response = make_request("GET", "/skills/categories/", "admin")
    success = response and response.status_code == 200
    print_result(success, "Categories list accessible", response)
    
    # Test 2: Create root category - Technology
    print_test("Create root category - Technology [Admin]")
    data = {
        "name": "Technology",
        "description": "Technology and computer skills",
        "parent_category": None
    }
    response = make_request("POST", "/skills/categories/", "admin", data)
    success = response and response.status_code == 201
    print_result(success, "Created Technology category", response)
    if success:
        save_id("cat_tech_id", response.json())
    
    # Test 3: Create sub-category - Web Development
    print_test("Create sub-category - Web Development [Admin]")
    if TEST_DATA["cat_tech_id"]:
        data = {
            "name": "Web Development",
            "description": "Web development technologies",
            "parent_category": TEST_DATA["cat_tech_id"]
        }
        response = make_request("POST", "/skills/categories/", "admin", data)
        success = response and response.status_code == 201
        print_result(success, "Created Web Development sub-category", response)
        if success:
            save_id("cat_web_id", response.json())
    else:
        print_skip("No parent category ID")
    
    # Test 4: Create root category - Languages
    print_test("Create root category - Languages [Admin]")
    data = {
        "name": "Languages",
        "description": "Spoken and written languages",
        "parent_category": None
    }
    response = make_request("POST", "/skills/categories/", "admin", data)
    success = response and response.status_code == 201
    print_result(success, "Created Languages category", response)
    if success:
        save_id("cat_lang_id", response.json())
    
    # Test 5: Get category tree
    print_test("Get category tree")
    response = make_request("GET", "/skills/categories/tree/", "admin")
    success = response and response.status_code == 200
    print_result(success, "Retrieved category tree", response)
    
    # Test 6: Get category details
    print_test("Get category details")
    if TEST_DATA["cat_web_id"]:
        response = make_request("GET", f"/skills/categories/{TEST_DATA['cat_web_id']}/", "admin")
        success = response and response.status_code == 200
        print_result(success, "Retrieved category details", response)
    else:
        print_skip("No category ID")
    
    # Test 7: Update category
    print_test("Update category [Admin]")
    if TEST_DATA["cat_web_id"]:
        data = {"description": "Frontend and backend web development"}
        response = make_request("PATCH", f"/skills/categories/{TEST_DATA['cat_web_id']}/", "admin", data)
        success = response and response.status_code == 200
        print_result(success, "Updated category description", response)
    else:
        print_skip("No category ID")
    
    # Test 8: Non-admin cannot create category
    print_test("Non-admin cannot create category [Permission Test]")
    data = {"name": "Test Category", "description": "Test"}
    response = make_request("POST", "/skills/categories/", "volunteer", data)
    success = response and response.status_code == 403
    print_result(success, "Correctly blocked non-admin", response)
    
    # Test 9: Filter root categories
    print_test("Filter root categories only")
    response = make_request("GET", "/skills/categories/?root_only=true", "admin")
    success = response and response.status_code == 200
    print_result(success, "Filtered root categories", response)

def test_skills():
    """Test SkillViewSet"""
    print_section("TESTING SKILLS")
    
    # Test 1: List skills
    print_test("List all skills")
    response = make_request("GET", "/skills/skills/", "admin")
    success = response and response.status_code == 200
    print_result(success, "Skills list accessible", response)
    
    # Test 2: Create Python skill
    print_test("Create Python skill [Admin]")
    if TEST_DATA["cat_web_id"]:
        data = {
            "name": "Python Programming",
            "category": TEST_DATA["cat_web_id"],
            "description": "Python for backend development",
            "verification_requirement": "recommended",
            "is_active": True
        }
        response = make_request("POST", "/skills/skills/", "admin", data)
        success = response and response.status_code == 201
        print_result(success, "Created Python skill", response)
        if success:
            save_id("skill_python_id", response.json())
    else:
        print_skip("No category ID")
    
    # Test 3: Create JavaScript skill
    print_test("Create JavaScript skill [Admin]")
    if TEST_DATA["cat_web_id"]:
        data = {
            "name": "JavaScript",
            "category": TEST_DATA["cat_web_id"],
            "description": "JavaScript for web development",
            "verification_requirement": "recommended",
            "is_active": True
        }
        response = make_request("POST", "/skills/skills/", "admin", data)
        success = response and response.status_code == 201
        print_result(success, "Created JavaScript skill", response)
        if success:
            save_id("skill_js_id", response.json())
    else:
        print_skip("No category ID")
    
    # Test 4: Create React skill
    print_test("Create React skill [Admin]")
    if TEST_DATA["cat_web_id"]:
        data = {
            "name": "React",
            "category": TEST_DATA["cat_web_id"],
            "description": "React framework",
            "verification_requirement": "optional",
            "is_active": True
        }
        response = make_request("POST", "/skills/skills/", "admin", data)
        success = response and response.status_code == 201
        print_result(success, "Created React skill", response)
        if success:
            save_id("skill_react_id", response.json())
    else:
        print_skip("No category ID")
    
    # Test 5: Create Arabic language skill
    print_test("Create Arabic Language skill [Admin]")
    if TEST_DATA["cat_lang_id"]:
        data = {
            "name": "Arabic Language",
            "category": TEST_DATA["cat_lang_id"],
            "description": "Arabic language proficiency",
            "verification_requirement": "none",
            "is_active": True
        }
        response = make_request("POST", "/skills/skills/", "admin", data)
        success = response and response.status_code == 201
        print_result(success, "Created Arabic skill", response)
        if success:
            save_id("skill_arabic_id", response.json())
    else:
        print_skip("No category ID")
    
    # Test 6: Create French language skill
    print_test("Create French Language skill [Admin]")
    if TEST_DATA["cat_lang_id"]:
        data = {
            "name": "French Language",
            "category": TEST_DATA["cat_lang_id"],
            "description": "French language proficiency",
            "verification_requirement": "none",
            "is_active": True
        }
        response = make_request("POST", "/skills/skills/", "admin", data)
        success = response and response.status_code == 201
        print_result(success, "Created French skill", response)
        if success:
            save_id("skill_french_id", response.json())
    else:
        print_skip("No category ID")
    
    # Test 7: Get skill details
    print_test("Get skill details")
    if TEST_DATA["skill_python_id"]:
        response = make_request("GET", f"/skills/skills/{TEST_DATA['skill_python_id']}/", "admin")
        success = response and response.status_code == 200
        print_result(success, "Retrieved skill details", response)
    else:
        print_skip("No skill ID")
    
    # Test 8: Filter skills by category
    print_test("Filter skills by category")
    if TEST_DATA["cat_web_id"]:
        response = make_request("GET", f"/skills/skills/?category={TEST_DATA['cat_web_id']}", "admin")
        success = response and response.status_code == 200
        if success:
            data = response.json()
            count = len(data.get("results", data if isinstance(data, list) else []))
            print_result(success, f"Found {count} skills in category", response)
        else:
            print_result(success, "Filter failed", response)
    else:
        print_skip("No category ID")
    
    # Test 9: Get skills by category (custom action)
    print_test("Get skills by category (custom action)")
    if TEST_DATA["cat_web_id"]:
        response = make_request("GET", f"/skills/skills/by_category/?category_id={TEST_DATA['cat_web_id']}", "admin")
        success = response and response.status_code == 200
        print_result(success, "Retrieved skills by category", response)
    else:
        print_skip("No category ID")
    
    # Test 10: Update skill
    print_test("Update skill [Admin]")
    if TEST_DATA["skill_python_id"]:
        data = {"description": "Python for backend, ML, and data science"}
        response = make_request("PATCH", f"/skills/skills/{TEST_DATA['skill_python_id']}/", "admin", data)
        success = response and response.status_code == 200
        print_result(success, "Updated skill description", response)
    else:
        print_skip("No skill ID")
    
    # Test 11: Deactivate skill
    print_test("Deactivate skill [Admin]")
    if TEST_DATA["skill_react_id"]:
        data = {"is_active": False}
        response = make_request("PATCH", f"/skills/skills/{TEST_DATA['skill_react_id']}/", "admin", data)
        success = response and response.status_code == 200
        print_result(success, "Deactivated skill", response)
    else:
        print_skip("No skill ID")
    
    # Test 12: Non-admin cannot create skill
    print_test("Non-admin cannot create skill [Permission Test]")
    data = {"name": "Test Skill", "category": TEST_DATA["cat_web_id"]}
    response = make_request("POST", "/skills/skills/", "volunteer", data)
    success = response and response.status_code == 403
    print_result(success, "Correctly blocked non-admin", response)

def test_volunteer_skills():
    """Test VolunteerSkillViewSet"""
    print_section("TESTING VOLUNTEER SKILLS")
    
    # Test 1: List volunteer skills
    print_test("List volunteer skills [Volunteer]")
    response = make_request("GET", f"/skills/volunteer-skills/?volunteer_id={EXISTING_IDS['volunteer_id']}", "volunteer")
    success = response and response.status_code == 200
    print_result(success, "Volunteer skills list accessible", response)
    
    # Test 2: Add Python skill to volunteer profile
    print_test("Add Python skill to profile [Volunteer]")
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
        success = response and response.status_code == 201
        print_result(success, "Added Python skill", response)
        if success:
            save_id("volunteer_skill_python_id", response.json())
    else:
        print_skip("No skill ID")
    
    # Test 3: Add JavaScript skill
    print_test("Add JavaScript skill [Volunteer]")
    if TEST_DATA["skill_js_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_js_id"],
            "proficiency_level": "intermediate",
            "years_of_experience": 2.0,
            "is_primary": False
        }
        response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
        success = response and response.status_code == 201
        print_result(success, "Added JavaScript skill", response)
        if success:
            save_id("volunteer_skill_js_id", response.json())
    else:
        print_skip("No skill ID")
    
    # Test 4: Add Arabic language skill
    print_test("Add Arabic Language skill [Volunteer]")
    if TEST_DATA["skill_arabic_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_arabic_id"],
            "proficiency_level": "expert",
            "years_of_experience": 25.0,
            "is_primary": False
        }
        response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
        success = response and response.status_code == 201
        print_result(success, "Added Arabic skill", response)
        if success:
            save_id("volunteer_skill_arabic_id", response.json())
    else:
        print_skip("No skill ID")
    
    # Test 5: Update skill proficiency
    print_test("Update skill proficiency [Volunteer]")
    if TEST_DATA["volunteer_skill_js_id"]:
        data = {
            "proficiency_level": "advanced",
            "years_of_experience": 3.0
        }
        response = make_request("PATCH", f"/skills/volunteer-skills/{TEST_DATA['volunteer_skill_js_id']}/", "volunteer", data)
        success = response and response.status_code == 200
        print_result(success, "Updated JavaScript proficiency", response)
    else:
        print_skip("No volunteer skill ID")
    
    # Test 6: Get skill details
    print_test("Get volunteer skill details [Volunteer]")
    if TEST_DATA["volunteer_skill_python_id"]:
        response = make_request("GET", f"/skills/volunteer-skills/{TEST_DATA['volunteer_skill_python_id']}/", "volunteer")
        success = response and response.status_code == 200
        print_result(success, "Retrieved skill details", response)
    else:
        print_skip("No volunteer skill ID")
    
    # Test 7: Filter by verification status
    print_test("Filter by verification status")
    response = make_request("GET", f"/skills/volunteer-skills/?volunteer_id={EXISTING_IDS['volunteer_id']}&verification_status=pending", "volunteer")
    success = response and response.status_code == 200
    print_result(success, "Filtered by verification status", response)
    
    # Test 8: Verify skill (Admin)
    print_test("Verify skill [Admin]")
    if TEST_DATA["volunteer_skill_python_id"]:
        data = {
            "verification_status": "verified",
            "verification_notes": "Portfolio reviewed - excellent work"
        }
        response = make_request("POST", f"/skills/volunteer-skills/{TEST_DATA['volunteer_skill_python_id']}/verify/", "admin", data)
        success = response and response.status_code == 200
        print_result(success, "Verified Python skill", response)
    else:
        print_skip("No volunteer skill ID")
    
    # Test 9: Verify JavaScript skill
    print_test("Verify JavaScript skill [Admin]")
    if TEST_DATA["volunteer_skill_js_id"]:
        data = {
            "verification_status": "verified",
            "verification_notes": "Verified through code review"
        }
        response = make_request("POST", f"/skills/volunteer-skills/{TEST_DATA['volunteer_skill_js_id']}/verify/", "admin", data)
        success = response and response.status_code == 200
        print_result(success, "Verified JavaScript skill", response)
    else:
        print_skip("No volunteer skill ID")
    
    # Test 10: Volunteer cannot verify own skill
    print_test("Volunteer cannot verify own skill [Permission Test]")
    if TEST_DATA["volunteer_skill_arabic_id"]:
        data = {"verification_status": "verified"}
        response = make_request("POST", f"/skills/volunteer-skills/{TEST_DATA['volunteer_skill_arabic_id']}/verify/", "volunteer", data)
        success = response and response.status_code == 403
        print_result(success, "Correctly blocked volunteer verification", response)
    else:
        print_skip("No volunteer skill ID")
    
    # Test 11: Duplicate skill error
    print_test("Cannot add duplicate skill [Validation Test]")
    if TEST_DATA["skill_python_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_python_id"],
            "proficiency_level": "expert"
        }
        response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
        success = response and response.status_code == 400
        print_result(success, "Correctly rejected duplicate", response)
    else:
        print_skip("No skill ID")

def test_mission_skills():
    """Test MissionSkillViewSet"""
    print_section("TESTING MISSION SKILLS")
    
    # Test 1: List mission skills
    print_test("List mission skills")
    response = make_request("GET", f"/skills/mission-skills/?mission_id={TEST_DATA['mission_id']}", "organization")
    success = response and response.status_code == 200
    print_result(success, "Mission skills list accessible", response)
    
    # Test 2: Add Python requirement to mission
    print_test("Add Python requirement to mission [Organization]")
    if TEST_DATA["skill_python_id"]:
        data = {
            "mission_id": TEST_DATA["mission_id"],
            "skill_id": TEST_DATA["skill_python_id"],
            "requirement_level": "required",
            "is_verification_required": True,
            "min_proficiency_level": "intermediate"
        }
        response = make_request("POST", "/skills/mission-skills/", "organization", data)
        success = response and response.status_code == 201
        print_result(success, "Added Python requirement", response)
        if success:
            save_id("mission_skill_python_id", response.json())
    else:
        print_skip("No skill ID")
    
    # Test 3: Add JavaScript requirement
    print_test("Add JavaScript requirement [Organization]")
    if TEST_DATA["skill_js_id"]:
        data = {
            "mission_id": TEST_DATA["mission_id"],
            "skill_id": TEST_DATA["skill_js_id"],
            "requirement_level": "preferred",
            "is_verification_required": False,
            "min_proficiency_level": "beginner"
        }
        response = make_request("POST", "/skills/mission-skills/", "organization", data)
        success = response and response.status_code == 201
        print_result(success, "Added JavaScript requirement", response)
        if success:
            save_id("mission_skill_js_id", response.json())
    else:
        print_skip("No skill ID")
    
    # Test 4: Update requirement level
    print_test("Update requirement level [Organization]")
    if TEST_DATA["mission_skill_js_id"]:
        data = {
            "requirement_level": "required",
            "min_proficiency_level": "intermediate"
        }
        response = make_request("PATCH", f"/skills/mission-skills/{TEST_DATA['mission_skill_js_id']}/", "organization", data)
        success = response and response.status_code == 200
        print_result(success, "Updated requirement level", response)
    else:
        print_skip("No mission skill ID")
    
    # Test 5: Get mission skill details
    print_test("Get mission skill details")
    if TEST_DATA["mission_skill_python_id"]:
        response = make_request("GET", f"/skills/mission-skills/{TEST_DATA['mission_skill_python_id']}/", "organization")
        success = response and response.status_code == 200
        print_result(success, "Retrieved mission skill details", response)
    else:
        print_skip("No mission skill ID")
    
    # Test 6: Filter required skills only
    print_test("Filter required skills only")
    response = make_request("GET", f"/skills/mission-skills/?mission_id={TEST_DATA['mission_id']}&required_only=true", "organization")
    success = response and response.status_code == 200
    print_result(success, "Filtered required skills", response)
    
    # Test 7: Bulk add skills
    print_test("Bulk add skills to mission [Organization]")
    if TEST_DATA["skill_arabic_id"] and TEST_DATA["skill_french_id"]:
        data = {
            "mission_id": TEST_DATA["mission_id"],
            "skills": [
                {
                    "skill_id": TEST_DATA["skill_arabic_id"],
                    "requirement_level": "preferred",
                    "is_verification_required": False,
                    "min_proficiency_level": "beginner"
                },
                {
                    "skill_id": TEST_DATA["skill_french_id"],
                    "requirement_level": "optional",
                    "is_verification_required": False,
                    "min_proficiency_level": "beginner"
                }
            ]
        }
        response = make_request("POST", "/skills/mission-skills/bulk_add/", "organization", data)
        success = response and response.status_code == 201
        print_result(success, "Bulk added skills", response)
    else:
        print_skip("Missing skill IDs")
    
    # Test 8: Volunteer cannot add mission skills
    print_test("Volunteer cannot add mission skills [Permission Test]")
    data = {
        "mission_id": TEST_DATA["mission_id"],
        "skill_id": TEST_DATA["skill_python_id"]
    }
    response = make_request("POST", "/skills/mission-skills/", "volunteer", data)
    success = response and response.status_code == 403
    print_result(success, "Correctly blocked volunteer", response)

def test_volunteer_search():
    """Test VolunteerSearchViewSet"""
    print_section("TESTING VOLUNTEER SEARCH")
    
    # Test 1: Search by skills (match ALL)
    print_test("Search volunteers by skills (match ALL) [Organization]")
    if TEST_DATA["skill_python_id"] and TEST_DATA["skill_js_id"]:
        skill_ids = f"{TEST_DATA['skill_python_id']},{TEST_DATA['skill_js_id']}"
        response = make_request("GET", f"/skills/volunteer-search/by_skills/?skill_ids={skill_ids}&match_type=all&verified_only=true", "organization")
        success = response and response.status_code == 200
        if success:
            data = response.json()
            count = data.get("count", 0)
            print_result(success, f"Found {count} volunteers with ALL skills", response)
        else:
            print_result(success, "Search failed", response)
    else:
        print_skip("Missing skill IDs")
    
    # Test 2: Search by skills (match ANY)
    print_test("Search volunteers by skills (match ANY) [Organization]")
    if TEST_DATA["skill_python_id"] and TEST_DATA["skill_js_id"]:
        skill_ids = f"{TEST_DATA['skill_python_id']},{TEST_DATA['skill_js_id']}"
        response = make_request("GET", f"/skills/volunteer-search/by_skills/?skill_ids={skill_ids}&match_type=any&verified_only=true", "organization")
        success = response and response.status_code == 200
        if success:
            data = response.json()
            count = data.get("count", 0)
            print_result(success, f"Found {count} volunteers with ANY skill", response)
        else:
            print_result(success, "Search failed", response)
    else:
        print_skip("Missing skill IDs")
    
    # Test 3: Search by mission
    print_test("Search volunteers for mission [Organization]")
    response = make_request("GET", f"/skills/volunteer-search/by_mission/?mission_id={TEST_DATA['mission_id']}&require_all=true", "organization")
    success = response and response.status_code == 200
    if success:
        data = response.json()
        count = data.get("count", 0)
        print_result(success, f"Found {count} qualified volunteers", response)
    else:
        print_result(success, "Search failed", response)
    
    # Test 4: Search by category
    print_test("Search volunteers by category [Organization]")
    if TEST_DATA["cat_web_id"]:
        response = make_request("GET", f"/skills/volunteer-search/by_skill_category/?category_id={TEST_DATA['cat_web_id']}&verified_only=true", "organization")
        success = response and response.status_code == 200
        if success:
            data = response.json()
            count = data.get("count", 0)
            print_result(success, f"Found {count} volunteers in category", response)
        else:
            print_result(success, "Search failed", response)
    else:
        print_skip("No category ID")
    
    # Test 5: Volunteer cannot search (privacy)
    print_test("Volunteer cannot search [Permission Test]")
    if TEST_DATA["skill_python_id"]:
        response = make_request("GET", f"/skills/volunteer-search/by_skills/?skill_ids={TEST_DATA['skill_python_id']}", "volunteer")
        success = response and response.status_code == 403
        print_result(success, "Correctly blocked volunteer search", response)
    else:
        print_skip("No skill ID")
    
    # Test 6: Admin can search
    print_test("Admin can search volunteers [Admin]")
    if TEST_DATA["skill_python_id"]:
        response = make_request("GET", f"/skills/volunteer-search/by_skills/?skill_ids={TEST_DATA['skill_python_id']}", "admin")
        success = response and response.status_code == 200
        print_result(success, "Admin search successful", response)
    else:
        print_skip("No skill ID")

def test_permissions():
    """Test permission scenarios"""
    print_section("TESTING PERMISSIONS & AUTHORIZATION")
    
    # Test 1: Volunteer cannot create categories
    print_test("Volunteer denied category creation")
    data = {"name": "Test Category"}
    response = make_request("POST", "/skills/categories/", "volunteer", data)
    success = response and response.status_code == 403
    print_result(success, "Blocked volunteer category creation", response)
    
    # Test 2: Volunteer cannot create skills
    print_test("Volunteer denied skill creation")
    data = {"name": "Test Skill", "category": TEST_DATA["cat_web_id"]}
    response = make_request("POST", "/skills/skills/", "volunteer", data)
    success = response and response.status_code == 403
    print_result(success, "Blocked volunteer skill creation", response)
    
    # Test 3: Volunteer cannot verify skills
    print_test("Volunteer denied skill verification")
    if TEST_DATA["volunteer_skill_python_id"]:
        data = {"verification_status": "verified"}
        response = make_request("POST", f"/skills/volunteer-skills/{TEST_DATA['volunteer_skill_python_id']}/verify/", "volunteer", data)
        success = response and response.status_code == 403
        print_result(success, "Blocked volunteer verification", response)
    else:
        print_skip("No volunteer skill ID")
    
    # Test 4: Organization can create mission skills
    print_test("Organization allowed mission skill creation")
    if TEST_DATA["skill_python_id"]:
        data = {
            "mission_id": TEST_DATA["mission_id"],
            "skill_id": TEST_DATA["skill_python_id"],
            "requirement_level": "preferred"
        }
        # This will fail if skill already exists, which is OK
        response = make_request("POST", "/skills/mission-skills/", "organization", data)
        success = response and response.status_code in [201, 400]  # 400 if duplicate
        print_result(success, "Organization can create mission skills", response)
    else:
        print_skip("No skill ID")
    
    # Test 5: Organization cannot verify volunteer skills
    print_test("Organization denied volunteer skill verification")
    if TEST_DATA["volunteer_skill_python_id"]:
        data = {"verification_status": "verified"}
        response = make_request("POST", f"/skills/volunteer-skills/{TEST_DATA['volunteer_skill_python_id']}/verify/", "organization", data)
        success = response and response.status_code == 403
        print_result(success, "Blocked organization verification", response)
    else:
        print_skip("No volunteer skill ID")

def test_edge_cases():
    """Test edge cases and validation"""
    print_section("TESTING EDGE CASES & VALIDATION")
    
    # Test 1: Invalid proficiency level
    print_test("Invalid proficiency level rejected")
    if TEST_DATA["skill_python_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_python_id"],
            "proficiency_level": "master"  # Invalid
        }
        response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
        success = response and response.status_code == 400
        print_result(success, "Rejected invalid proficiency", response)
    else:
        print_skip("No skill ID")
    
    # Test 2: Negative years of experience
    print_test("Negative experience rejected")
    if TEST_DATA["skill_french_id"]:
        data = {
            "volunteer_id": EXISTING_IDS["volunteer_id"],
            "skill_id": TEST_DATA["skill_french_id"],
            "proficiency_level": "beginner",
            "years_of_experience": -5  # Invalid
        }
        response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
        success = response and response.status_code == 400
        print_result(success, "Rejected negative experience", response)
    else:
        print_skip("No skill ID")
    
    # Test 3: Invalid requirement level
    print_test("Invalid requirement level rejected")
    if TEST_DATA["skill_python_id"]:
        data = {
            "mission_id": TEST_DATA["mission_id"],
            "skill_id": TEST_DATA["skill_python_id"],
            "requirement_level": "mandatory"  # Invalid
        }
        response = make_request("POST", "/skills/mission-skills/", "organization", data)
        success = response and response.status_code == 400
        print_result(success, "Rejected invalid requirement level", response)
    else:
        print_skip("No skill ID")
    
    # Test 4: Non-existent skill ID
    print_test("Non-existent skill ID rejected")
    data = {
        "volunteer_id": EXISTING_IDS["volunteer_id"],
        "skill_id": "00000000-0000-0000-0000-000000000000",
        "proficiency_level": "beginner"
    }
    response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
    success = response and response.status_code in [400, 404]
    print_result(success, "Rejected non-existent skill", response)
    
    # Test 5: Missing required field
    print_test("Missing required field rejected")
    data = {
        "volunteer_id": EXISTING_IDS["volunteer_id"],
        # Missing skill_id
        "proficiency_level": "beginner"
    }
    response = make_request("POST", "/skills/volunteer-skills/", "volunteer", data)
    success = response and response.status_code == 400
    print_result(success, "Rejected missing field", response)

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = stats["total"]
    passed = stats["passed"]
    failed = stats["failed"]
    skipped = stats["skipped"]
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}Results:{Colors.END}")
    print(f"  Total Tests:   {total}")
    print(f"  {Colors.GREEN}Passed:        {passed}{Colors.END}")
    print(f"  {Colors.RED}Failed:        {failed}{Colors.END}")
    print(f"  {Colors.YELLOW}Skipped:       {skipped}{Colors.END}")
    print(f"  {Colors.CYAN}Pass Rate:     {pass_rate:.1f}%{Colors.END}")
    
    print(f"\n{Colors.BOLD}Created Test Data:{Colors.END}")
    for key, value in TEST_DATA.items():
        if value and key != "mission_id":
            print(f"  {key}: {value}")
    
    print(f"\n{Colors.BOLD}Status:{Colors.END}")
    if failed == 0:
        print(f"  {Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED!{Colors.END}")
    else:
        print(f"  {Colors.YELLOW}⚠️  Some tests failed - review output above{Colors.END}")

# ================= MAIN =================
def main():
    print_header("COMPREHENSIVE SKILLS MODULE TEST SUITE")
    print(f"{Colors.YELLOW}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.YELLOW}Base URL: {BASE_URL}{Colors.END}")
    
    try:
        # Run all test suites
        test_skill_categories()
        test_skills()
        test_volunteer_skills()
        test_mission_skills()
        test_volunteer_search()
        test_permissions()
        test_edge_cases()
        
        # Print summary
        print_summary()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Tests interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Tests failed with error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()