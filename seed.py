import sys
from datetime import datetime, timedelta
from app import create_app
from database import db
from models import User, Patient, Doctor, Appointment, MedicalRecord, Billing

def seed_database():
    app = create_app()
    with app.app_context():
        print("[*] Creating all database tables if not exist...")
        try:
            db.create_all()
            print("[+] Database tables verified/created successfully.")
        except Exception as e:
            print(f"[-] Error connecting/creating tables: {e}")
            print("[!] Please ensure MySQL in XAMPP is started or check config.py settings.")
            return False

        # Check if users already exist
        if User.query.first():
            print("[!] Database already contains user data. Skipping seed to prevent duplication.")
            return True

        print("[*] Seeding sample users and data...")

        # 1. Users
        admin = User(username='admin', role='admin', email='admin@medicare.com')
        admin.set_password('admin123')

        dr_sarah_user = User(username='dr_sarah', role='doctor', email='sarah.jenkins@medicare.com')
        dr_sarah_user.set_password('doctor123')

        dr_james_user = User(username='dr_james', role='doctor', email='james.wilson@medicare.com')
        dr_james_user.set_password('doctor123')

        rec_user = User(username='receptionist1', role='receptionist', email='frontdesk@medicare.com')
        rec_user.set_password('rec123')

        pat_john_user = User(username='patient_john', role='patient', email='john.doe@gmail.com')
        pat_john_user.set_password('patient123')

        pat_emily_user = User(username='patient_emily', role='patient', email='emily.rose@gmail.com')
        pat_emily_user.set_password('patient123')

        db.session.add_all([admin, dr_sarah_user, dr_james_user, rec_user, pat_john_user, pat_emily_user])
        db.session.flush()

        # 2. Doctors
        doc1 = Doctor(
            user_id=dr_sarah_user.id,
            full_name='Dr. Sarah Jenkins, MD',
            specialization='Cardiology',
            phone='+1 (555) 234-5678',
            room_number='Room 302-A'
        )
        doc2 = Doctor(
            user_id=dr_james_user.id,
            full_name='Dr. James Wilson, MD',
            specialization='General Medicine & Pediatrics',
            phone='+1 (555) 345-6789',
            room_number='Room 105-B'
        )
        db.session.add_all([doc1, doc2])
        db.session.flush()

        # 3. Patients
        p1 = Patient(
            user_id=pat_john_user.id,
            full_name='John Doe',
            dob=datetime.strptime('1988-05-14', '%Y-%m-%d').date(),
            gender='Male',
            phone='+1 (555) 019-2834',
            address='742 Evergreen Terrace, Springfield',
            emergency_contact='Jane Doe (+1 555-019-2835)'
        )
        p2 = Patient(
            user_id=pat_emily_user.id,
            full_name='Emily Rose',
            dob=datetime.strptime('1995-11-22', '%Y-%m-%d').date(),
            gender='Female',
            phone='+1 (555) 829-1144',
            address='124 Conch Street, Pacific City',
            emergency_contact='Robert Rose (+1 555-829-9988)'
        )
        p3 = Patient(
            user_id=None,
            full_name='Michael Chang',
            dob=datetime.strptime('1976-03-30', '%Y-%m-%d').date(),
            gender='Male',
            phone='+1 (555) 431-7720',
            address='88 Maple Ave, Metroville',
            emergency_contact='Grace Chang (+1 555-431-7721)'
        )
        db.session.add_all([p1, p2, p3])
        db.session.flush()

        # 4. Appointments
        now = datetime.now()
        app1 = Appointment(
            patient_id=p1.id,
            doctor_id=doc1.id,
            appointment_date=now + timedelta(hours=2),
            status='Confirmed',
            reason='Routine cardiology checkup and follow-up on ECG results.'
        )
        app2 = Appointment(
            patient_id=p2.id,
            doctor_id=doc2.id,
            appointment_date=now + timedelta(hours=5),
            status='Confirmed',
            reason='Seasonal allergy symptoms and mild throat irritation.'
        )
        app3 = Appointment(
            patient_id=p3.id,
            doctor_id=doc1.id,
            appointment_date=now - timedelta(days=1),
            status='Completed',
            reason='Hypertension consultation and prescription renewal.'
        )
        app4 = Appointment(
            patient_id=p1.id,
            doctor_id=doc2.id,
            appointment_date=now + timedelta(days=2),
            status='Pending',
            reason='General wellness assessment.'
        )
        db.session.add_all([app1, app2, app3, app4])
        db.session.flush()

        # 5. Medical Records
        rec1 = MedicalRecord(
            patient_id=p3.id,
            doctor_id=doc1.id,
            diagnosis='Stage 1 Hypertension. Elevated systolic pressure observed during examination.',
            prescription='Amlodipine 5mg once daily every morning. Low sodium diet and 30 mins daily walking.',
            record_date=now - timedelta(days=1)
        )
        rec2 = MedicalRecord(
            patient_id=p1.id,
            doctor_id=doc1.id,
            diagnosis='Mild sinus tachycardia. Heart sounds normal with regular rhythm.',
            prescription='Metoprolol 25mg as advised. Avoid excessive caffeine intake. Follow up in 6 months.',
            record_date=now - timedelta(days=20)
        )
        db.session.add_all([rec1, rec2])

        # 6. Billings
        b1 = Billing(patient_id=p3.id, appointment_id=app3.id, amount=150.00, status='Paid', billing_date=now - timedelta(days=1))
        b2 = Billing(patient_id=p1.id, appointment_id=app1.id, amount=180.00, status='Pending', billing_date=now)
        b3 = Billing(patient_id=p2.id, appointment_id=app2.id, amount=95.00, status='Pending', billing_date=now)
        db.session.add_all([b1, b2, b3])

        db.session.commit()
        print("[+] Database successfully seeded with sample users, doctors, patients, appointments, and records!")
        return True

if __name__ == '__main__':
    seed_database()
