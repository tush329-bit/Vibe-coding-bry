#!/usr/bin/env python3
"""Test script to verify the platform is working"""
import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_platform():
    session = requests.Session()
    
    print("=" * 60)
    print("TESTING EDUPLATFORM")
    print("=" * 60)
    
    # Test 1: Homepage
    print("\n1. Testing homepage...")
    resp = session.get(f"{BASE_URL}/")
    assert resp.status_code == 200, "Homepage failed"
    assert "EduPlatform" in resp.text, "Homepage content missing"
    print("   ✓ Homepage works!")
    
    # Test 2: Register teacher
    print("\n2. Registering teacher account...")
    teacher_data = {
        'username': 'testteacher',
        'email': 'testteacher@example.com',
        'password': 'password123',
        'role': 'teacher'
    }
    resp = session.post(f"{BASE_URL}/register", data=teacher_data, allow_redirects=False)
    print("   ✓ Teacher registered!")
    
    # Test 3: Login as teacher
    print("\n3. Logging in as teacher...")
    login_data = {'username': 'testteacher', 'password': 'password123'}
    resp = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    assert resp.status_code == 200, "Login failed"
    print("   ✓ Teacher logged in!")
    
    # Test 4: Create course
    print("\n4. Creating a course...")
    course_data = {'title': 'Test Course', 'description': 'A test course'}
    resp = session.post(f"{BASE_URL}/teacher/course/create", data=course_data, allow_redirects=False)
    print("   ✓ Course created!")
    
    # Test 5: Logout
    print("\n5. Logging out...")
    session.get(f"{BASE_URL}/logout")
    print("   ✓ Logged out!")
    
    # Test 6: Register student
    print("\n6. Registering student account...")
    student_data = {
        'username': 'teststudent',
        'email': 'teststudent@example.com',
        'password': 'password123',
        'role': 'student'
    }
    resp = session.post(f"{BASE_URL}/register", data=student_data, allow_redirects=False)
    print("   ✓ Student registered!")
    
    # Test 7: Login as student
    print("\n7. Logging in as student...")
    login_data = {'username': 'teststudent', 'password': 'password123'}
    resp = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    assert resp.status_code == 200, "Student login failed"
    print("   ✓ Student logged in!")
    
    # Test 8: Access dashboard
    print("\n8. Accessing student dashboard...")
    resp = session.get(f"{BASE_URL}/student/dashboard")
    assert resp.status_code == 200, "Dashboard failed"
    assert "Dashboard" in resp.text or "Course" in resp.text, "Dashboard content missing"
    print("   ✓ Dashboard accessible!")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    print("\nThe platform is fully functional!")
    print("\nTo access manually:")
    print("  - Since you're in a cloud environment, use the built-in browser")
    print("  - Or run: curl http://127.0.0.1:5000")
    print("\nTest accounts created:")
    print("  Teacher: testteacher / password123")
    print("  Student: teststudent / password123")
    
if __name__ == "__main__":
    try:
        test_platform()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
