from datetime import datetime
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'doctor', 'receptionist', 'patient', name='user_roles'), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    patient_profile = db.relationship('Patient', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    full_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other', name='patient_gender'), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointments = db.relationship('Appointment', backref='patient', cascade='all, delete-orphan', lazy='dynamic')
    medical_records = db.relationship('MedicalRecord', backref='patient', cascade='all, delete-orphan', lazy='dynamic')
    billings = db.relationship('Billing', backref='patient', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'dob': self.dob.strftime('%Y-%m-%d') if self.dob else None,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    room_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', cascade='all, delete-orphan', lazy='dynamic')
    medical_records = db.relationship('MedicalRecord', backref='doctor', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'specialization': self.specialization,
            'phone': self.phone,
            'room_number': self.room_number,
            'email': self.user.email if self.user else None
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        db.Enum('Pending', 'Confirmed', 'Completed', 'Cancelled', name='appointment_status'),
        default='Pending'
    )
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    billing = db.relationship('Billing', backref='appointment', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else 'Unknown',
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.full_name if self.doctor else 'Unknown',
            'specialization': self.doctor.specialization if self.doctor else '',
            'appointment_date': self.appointment_date.strftime('%Y-%m-%d %H:%M') if self.appointment_date else None,
            'status': self.status,
            'reason': self.reason,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=False)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else 'Unknown',
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.full_name if self.doctor else 'Unknown',
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'record_date': self.record_date.strftime('%Y-%m-%d %H:%M') if self.record_date else None
        }

class Billing(db.Model):
    __tablename__ = 'billings'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id', ondelete='SET NULL'), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    status = db.Column(db.Enum('Paid', 'Unpaid', 'Pending', name='billing_status'), default='Pending')
    billing_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else 'Unknown',
            'appointment_id': self.appointment_id,
            'amount': float(self.amount) if self.amount else 0.0,
            'status': self.status,
            'billing_date': self.billing_date.strftime('%Y-%m-%d %H:%M') if self.billing_date else None
        }
