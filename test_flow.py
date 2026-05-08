import requests

BASE_URL = 'http://127.0.0.1:5000'
session = requests.Session()

def test_flow():
    print("Starting e2e test...")
    
    # 1. Register Teacher
    res = session.post(f"{BASE_URL}/register", data={
        'name': 'Test Teacher',
        'email': 'teacher@test.com',
        'username': 'teacher1',
        'password': 'password',
        'role': 'teacher'
    })
    print("Teacher registered:", res.status_code)
    
    # 2. Login Teacher
    res = session.post(f"{BASE_URL}/login", data={
        'username': 'teacher1',
        'password': 'password'
    })
    print("Teacher logged in:", res.status_code)
    
    # Check Dashboard
    res = session.get(f"{BASE_URL}/teacher/dashboard")
    assert 'Dashboard' in res.text
    print("Teacher dashboard loaded.")
    
    # 3. Create Course
    res = session.post(f"{BASE_URL}/teacher/course/create", data={
        'title': 'Test Course 101',
        'description': 'A dummy course for testing.'
    })
    print("Course created:", res.status_code)
    
    # 4. Logout Teacher
    session.get(f"{BASE_URL}/logout")
    
    # 5. Register Student
    res = session.post(f"{BASE_URL}/register", data={
        'name': 'Test Student',
        'email': 'student@test.com',
        'username': 'student1',
        'password': 'password',
        'role': 'student'
    })
    print("Student registered:", res.status_code)
    
    # 6. Login Student
    res = session.post(f"{BASE_URL}/login", data={
        'username': 'student1',
        'password': 'password'
    })
    print("Student logged in:", res.status_code)
    
    # 7. Check Student Dashboard
    res = session.get(f"{BASE_URL}/student/dashboard")
    assert 'Dashboard' in res.text
    print("Student dashboard loaded.")
    
    # 8. Enroll in course
    # Course ID 1 since it's the first one created
    res = session.post(f"{BASE_URL}/student/course/1/enroll")
    print("Student enrolled in course:", res.status_code)
    
    # Verify course appears in student dashboard
    res = session.get(f"{BASE_URL}/student/dashboard")
    assert 'Test Course 101' in res.text
    print("Course verification passed.")
    print("All backend routes responding correctly!")

if __name__ == '__main__':
    try:
        test_flow()
    except Exception as e:
        print(f"Test failed with error: {e}")
