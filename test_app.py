import os
os.environ['USE_SQLITE'] = '1'

from app import create_app
from database import db
from models import User, Patient, Doctor, Appointment, MedicalRecord

def run_tests():
    app = create_app()
    app.config['TESTING'] = True
    client = app.test_client()

    print("\n--- Running HMS Automated Test Suite ---")

    # 1. Test Login with Admin
    res = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert res.status_code == 200, f"Admin login failed: {res.status_code}"
    assert b"System Overview" in res.data, "Admin dashboard failed to load"
    print("[PASS] Admin login and dashboard verification")

    # 2. Test Admin API metrics
    res = client.get('/api/metrics')
    assert res.status_code == 200
    metrics = res.get_json()
    print(f"[PASS] /api/metrics returned: {metrics}")
    assert metrics['total_patients'] >= 3
    assert metrics['total_doctors'] >= 2

    # 3. Test Doctor Login & Schedule
    client.get('/logout')
    res = client.post('/login', data={'username': 'dr_sarah', 'password': 'doctor123'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Clinical Schedule" in res.data, "Doctor dashboard failed to load"
    print("[PASS] Doctor login and clinical dashboard verification")

    # 4. Test Doctor creating an EHR Medical Record
    res = client.post('/api/medical-records', data={
        'patient_id': 1,
        'diagnosis': 'Seasonal allergic rhinitis with mild congestion.',
        'prescription': 'Cetirizine 10mg once daily at bedtime. Saline nasal rinse.'
    }, follow_redirects=True)
    assert res.status_code in [200, 201], f"Create medical record failed: {res.status_code}"
    print("[PASS] Doctor diagnosis and prescription logging")

    # 5. Test Receptionist Login & Patient Registration
    client.get('/logout')
    res = client.post('/login', data={'username': 'receptionist1', 'password': 'rec123'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Front Desk Intake" in res.data, "Receptionist dashboard failed"
    print("[PASS] Receptionist login and front desk dashboard verification")

    res = client.post('/api/patients', data={
        'full_name': 'Samantha Miller',
        'dob': '1992-08-15',
        'gender': 'Female',
        'phone': '+1 (555) 678-9900',
        'address': '456 Blossom Lane',
        'emergency_contact': 'David Miller'
    }, follow_redirects=True)
    assert res.status_code in [200, 201]
    print("[PASS] Receptionist patient intake registration")

    # 6. Test Patient Login & Portal
    client.get('/logout')
    res = client.post('/login', data={'username': 'patient_john', 'password': 'patient123'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Your Personal Health Record" in res.data, "Patient portal failed"
    print("[PASS] Patient login and personal health portal verification")

    # 7. Test RBAC protection (Patient attempting to access /users should get 403 or redirect)
    res = client.get('/users', follow_redirects=True)
    assert b"Access Denied" in res.data or res.status_code == 403
    print("[PASS] Role-Based Access Control (RBAC) enforced against unauthorized role")

    print("\n[SUCCESS] All 7 test suites passed perfectly!\n")

if __name__ == '__main__':
    run_tests()
