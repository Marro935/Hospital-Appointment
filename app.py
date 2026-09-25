import os
from functools import wraps
from datetime import datetime, date
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort
)
from sqlalchemy import func
from config import Config
from database import db
from models import User, Patient, Doctor, Appointment, MedicalRecord, Billing

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Context processor to inject auth state into all Jinja templates
    @app.context_processor
    def inject_user_context():
        current_user = None
        if 'user_id' in session:
            current_user = User.query.get(session['user_id'])
        return {
            'current_user': current_user,
            'now': datetime.now()
        }

    # -------------------------------------------------------------
    # Authentication & Access Control Decorators
    # -------------------------------------------------------------
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function

    def role_required(*allowed_roles):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    flash('Please log in to access this page.', 'warning')
                    return redirect(url_for('login'))
                user_role = session.get('user_role')
                if user_role not in allowed_roles:
                    if request.is_json:
                        return jsonify({'error': 'Unauthorized access: insufficient privileges'}), 403
                    flash('Access Denied: You do not have permission to view this section.', 'danger')
                    return redirect(url_for('dashboard'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    # -------------------------------------------------------------
    # Authentication Routes
    # -------------------------------------------------------------
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session.clear()
                session['user_id'] = user.id
                session['username'] = user.username
                session['user_role'] = user.role
                session['user_email'] = user.email

                flash(f'Welcome back, {user.username}! You are logged in as {user.role.capitalize()}.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid username or password. Please try again.', 'danger')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been successfully logged out.', 'info')
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            gender = request.form.get('gender', 'Other')
            dob_str = request.form.get('dob', '')

            # Validation
            if not username or not email or not password or not full_name:
                flash('Please fill in all required fields.', 'danger')
                return render_template('register.html')

            if User.query.filter_by(username=username).first():
                flash('Username is already taken. Please choose another.', 'warning')
                return render_template('register.html')

            if User.query.filter_by(email=email).first():
                flash('Email is already registered. Please log in.', 'warning')
                return render_template('register.html')

            try:
                # Create patient user by default
                new_user = User(username=username, email=email, role='patient')
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.flush()

                dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else date(1990, 1, 1)
                new_patient = Patient(
                    user_id=new_user.id,
                    full_name=full_name,
                    phone=phone,
                    gender=gender,
                    dob=dob,
                    address=request.form.get('address', ''),
                    emergency_contact=request.form.get('emergency_contact', '')
                )
                db.session.add(new_patient)
                db.session.commit()

                flash('Registration successful! Please log in with your credentials.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred during registration: {str(e)}', 'danger')

        return render_template('register.html')

    # -------------------------------------------------------------
    # Core Dashboard & Views
    # -------------------------------------------------------------
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        role = session.get('user_role')
        user_id = session.get('user_id')
        user = User.query.get(user_id)

        # Base collections needed for forms across dashboards
        doctors_list = Doctor.query.all()
        patients_list = Patient.query.order_by(Patient.full_name).all()

        metrics = {}
        role_data = {}

        if role == 'admin':
            total_patients = Patient.query.count()
            total_doctors = Doctor.query.count()
            total_appointments = Appointment.query.count()
            pending_appointments = Appointment.query.filter_by(status='Pending').count()
            
            # Revenue calculation
            paid_revenue = db.session.query(func.coalesce(func.sum(Billing.amount), 0))\
                .filter(Billing.status == 'Paid').scalar()
            pending_revenue = db.session.query(func.coalesce(func.sum(Billing.amount), 0))\
                .filter(Billing.status == 'Pending').scalar()

            recent_appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).limit(6).all()
            recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
            recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

            metrics = {
                'total_patients': total_patients,
                'total_doctors': total_doctors,
                'total_appointments': total_appointments,
                'pending_appointments': pending_appointments,
                'paid_revenue': float(paid_revenue or 0),
                'pending_revenue': float(pending_revenue or 0)
            }
            role_data = {
                'recent_appointments': recent_appointments,
                'recent_patients': recent_patients,
                'recent_users': recent_users
            }

        elif role == 'doctor':
            doctor_profile = Doctor.query.filter_by(user_id=user_id).first()
            if doctor_profile:
                today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = datetime.now().replace(hour=23, minute=59, end=59) if hasattr(datetime.now(), 'end') else datetime.now().replace(hour=23, minute=59, second=59)

                today_appointments = Appointment.query.filter(
                    Appointment.doctor_id == doctor_profile.id,
                    Appointment.appointment_date >= today_start,
                    Appointment.appointment_date <= today_end
                ).order_by(Appointment.appointment_date).all()

                all_doc_appointments = Appointment.query.filter_by(doctor_id=doctor_profile.id)\
                    .order_by(Appointment.appointment_date.desc()).limit(10).all()

                recent_records = MedicalRecord.query.filter_by(doctor_id=doctor_profile.id)\
                    .order_by(MedicalRecord.record_date.desc()).limit(8).all()

                role_data = {
                    'doctor': doctor_profile,
                    'today_appointments': today_appointments,
                    'all_appointments': all_doc_appointments,
                    'recent_records': recent_records
                }
                metrics = {
                    'today_count': len(today_appointments),
                    'total_assigned': Appointment.query.filter_by(doctor_id=doctor_profile.id).count(),
                    'records_written': MedicalRecord.query.filter_by(doctor_id=doctor_profile.id).count()
                }

        elif role == 'receptionist':
            total_patients = Patient.query.count()
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = datetime.now().replace(hour=23, minute=59, second=59)

            today_appointments = Appointment.query.filter(
                Appointment.appointment_date >= today_start,
                Appointment.appointment_date <= today_end
            ).order_by(Appointment.appointment_date).all()

            pending_appointments = Appointment.query.filter_by(status='Pending')\
                .order_by(Appointment.appointment_date).all()

            metrics = {
                'total_patients': total_patients,
                'today_appointments_count': len(today_appointments),
                'pending_count': len(pending_appointments)
            }
            role_data = {
                'today_appointments': today_appointments,
                'pending_appointments': pending_appointments,
                'doctors': doctors_list
            }

        elif role == 'patient':
            patient_profile = Patient.query.filter_by(user_id=user_id).first()
            upcoming_appointments = []
            past_records = []
            billings = []

            if patient_profile:
                now = datetime.now()
                upcoming_appointments = Appointment.query.filter(
                    Appointment.patient_id == patient_profile.id,
                    Appointment.appointment_date >= now
                ).order_by(Appointment.appointment_date).all()

                past_records = MedicalRecord.query.filter_by(patient_id=patient_profile.id)\
                    .order_by(MedicalRecord.record_date.desc()).all()

                billings = Billing.query.filter_by(patient_id=patient_profile.id)\
                    .order_by(Billing.billing_date.desc()).all()

            role_data = {
                'patient': patient_profile,
                'upcoming_appointments': upcoming_appointments,
                'past_records': past_records,
                'billings': billings
            }
            metrics = {
                'upcoming_count': len(upcoming_appointments),
                'prescriptions_count': len(past_records)
            }

        return render_template(
            'dashboard.html',
            role=role,
            metrics=metrics,
            role_data=role_data,
            doctors=doctors_list,
            patients=patients_list
        )

    # -------------------------------------------------------------
    # Patients Management Views & APIs
    # -------------------------------------------------------------
    @app.route('/patients')
    @login_required
    @role_required('admin', 'receptionist', 'doctor')
    def patients_view():
        patients_list = Patient.query.order_by(Patient.created_at.desc()).all()
        return render_template('patients.html', patients=patients_list)

    @app.route('/api/patients', methods=['GET', 'POST'])
    @login_required
    def api_patients():
        if request.method == 'GET':
            patients = Patient.query.order_by(Patient.full_name).all()
            return jsonify([p.to_dict() for p in patients])

        if request.method == 'POST':
            # Role check: only admin and receptionist can add
            if session.get('user_role') not in ['admin', 'receptionist']:
                return jsonify({'error': 'Unauthorized to register new patients'}), 403

            data = request.get_json() if request.is_json else request.form
            full_name = data.get('full_name', '').strip()
            phone = data.get('phone', '').strip()
            dob_str = data.get('dob', '')
            gender = data.get('gender', 'Other')

            if not full_name or not phone or not dob_str:
                return jsonify({'error': 'Full name, phone, and date of birth are required.'}), 400

            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                new_patient = Patient(
                    full_name=full_name,
                    phone=phone,
                    gender=gender,
                    dob=dob,
                    address=data.get('address', ''),
                    emergency_contact=data.get('emergency_contact', '')
                )
                db.session.add(new_patient)
                db.session.commit()

                if not request.is_json:
                    flash(f'Patient {new_patient.full_name} added successfully!', 'success')
                    return redirect(url_for('patients_view'))
                return jsonify({'message': 'Patient created successfully', 'patient': new_patient.to_dict()}), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500

    @app.route('/api/patients/<int:patient_id>', methods=['PUT', 'DELETE'])
    @login_required
    @role_required('admin', 'receptionist')
    def api_patient_detail(patient_id):
        patient = Patient.query.get_or_404(patient_id)

        if request.method == 'DELETE':
            try:
                db.session.delete(patient)
                db.session.commit()
                return jsonify({'message': 'Patient deleted successfully'})
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500

        if request.method == 'PUT':
            data = request.get_json() or {}
            if 'full_name' in data:
                patient.full_name = data['full_name']
            if 'phone' in data:
                patient.phone = data['phone']
            if 'gender' in data:
                patient.gender = data['gender']
            if 'address' in data:
                patient.address = data['address']
            if 'emergency_contact' in data:
                patient.emergency_contact = data['emergency_contact']
            if 'dob' in data and data['dob']:
                patient.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()

            try:
                db.session.commit()
                return jsonify({'message': 'Patient updated successfully', 'patient': patient.to_dict()})
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500

    # -------------------------------------------------------------
    # Appointments Management Views & APIs
    # -------------------------------------------------------------
    @app.route('/appointments')
    @login_required
    def appointments_view():
        role = session.get('user_role')
        user_id = session.get('user_id')

        if role == 'doctor':
            doc = Doctor.query.filter_by(user_id=user_id).first()
            appointments = Appointment.query.filter_by(doctor_id=doc.id).order_by(Appointment.appointment_date.desc()).all() if doc else []
        elif role == 'patient':
            pat = Patient.query.filter_by(user_id=user_id).first()
            appointments = Appointment.query.filter_by(patient_id=pat.id).order_by(Appointment.appointment_date.desc()).all() if pat else []
        else:
            appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()

        doctors = Doctor.query.all()
        patients = Patient.query.order_by(Patient.full_name).all()
        return render_template('appointments.html', appointments=appointments, doctors=doctors, patients=patients)

    @app.route('/api/appointments', methods=['GET', 'POST'])
    @login_required
    def api_appointments():
        if request.method == 'GET':
            role = session.get('user_role')
            user_id = session.get('user_id')

            if role == 'doctor':
                doc = Doctor.query.filter_by(user_id=user_id).first()
                appointments = Appointment.query.filter_by(doctor_id=doc.id).all() if doc else []
            elif role == 'patient':
                pat = Patient.query.filter_by(user_id=user_id).first()
                appointments = Appointment.query.filter_by(patient_id=pat.id).all() if pat else []
            else:
                appointments = Appointment.query.all()
            return jsonify([a.to_dict() for a in appointments])

        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            role = session.get('user_role')
            user_id = session.get('user_id')

            # Identify patient
            if role == 'patient':
                patient = Patient.query.filter_by(user_id=user_id).first()
                if not patient:
                    return jsonify({'error': 'Patient profile not found'}), 400
                patient_id = patient.id
            else:
                patient_id = data.get('patient_id')

            doctor_id = data.get('doctor_id')
            date_str = data.get('appointment_date')
            reason = data.get('reason', '').strip()

            if not patient_id or not doctor_id or not date_str or not reason:
                if not request.is_json:
                    flash('All appointment fields are required.', 'danger')
                    return redirect(url_for('appointments_view'))
                return jsonify({'error': 'Patient, doctor, date/time, and reason are required.'}), 400

            try:
                # Parse date string (supports standard datetime-local format: YYYY-MM-DDTHH:MM)
                dt_str = date_str.replace('T', ' ')
                if len(dt_str) == 16:
                    dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
                else:
                    dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

                new_app = Appointment(
                    patient_id=int(patient_id),
                    doctor_id=int(doctor_id),
                    appointment_date=dt,
                    status='Pending' if role == 'patient' else data.get('status', 'Confirmed'),
                    reason=reason
                )
                db.session.add(new_app)
                db.session.flush()

                # Generate initial billing statement
                billing = Billing(
                    patient_id=new_app.patient_id,
                    appointment_id=new_app.id,
                    amount=120.00,
                    status='Pending'
                )
                db.session.add(billing)
                db.session.commit()

                if not request.is_json:
                    flash('Appointment scheduled successfully!', 'success')
                    return redirect(url_for('appointments_view'))
                return jsonify({'message': 'Appointment scheduled successfully', 'appointment': new_app.to_dict()}), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500

    @app.route('/api/appointments/<int:appointment_id>/status', methods=['PATCH', 'POST'])
    @login_required
    @role_required('admin', 'doctor', 'receptionist')
    def api_appointment_status(appointment_id):
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.get_json() if request.is_json else request.form
        new_status = data.get('status')

        if new_status not in ['Pending', 'Confirmed', 'Completed', 'Cancelled']:
            return jsonify({'error': 'Invalid appointment status'}), 400

        try:
            appointment.status = new_status
            db.session.commit()
            if not request.is_json:
                flash(f'Appointment status updated to {new_status}.', 'success')
                return redirect(url_for('appointments_view'))
            return jsonify({'message': 'Status updated successfully', 'appointment': appointment.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
    @login_required
    @role_required('admin', 'receptionist')
    def api_delete_appointment(appointment_id):
        appointment = Appointment.query.get_or_404(appointment_id)
        try:
            db.session.delete(appointment)
            db.session.commit()
            return jsonify({'message': 'Appointment cancelled/deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # -------------------------------------------------------------
    # Medical Records & Prescriptions
    # -------------------------------------------------------------
    @app.route('/medical-records')
    @login_required
    def medical_records_view():
        role = session.get('user_role')
        user_id = session.get('user_id')

        if role == 'doctor':
            doc = Doctor.query.filter_by(user_id=user_id).first()
            records = MedicalRecord.query.filter_by(doctor_id=doc.id).order_by(MedicalRecord.record_date.desc()).all() if doc else []
        elif role == 'patient':
            pat = Patient.query.filter_by(user_id=user_id).first()
            records = MedicalRecord.query.filter_by(patient_id=pat.id).order_by(MedicalRecord.record_date.desc()).all() if pat else []
        else:
            records = MedicalRecord.query.order_by(MedicalRecord.record_date.desc()).all()

        patients = Patient.query.order_by(Patient.full_name).all()
        doctors = Doctor.query.all()
        return render_template('medical_records.html', records=records, patients=patients, doctors=doctors)

    @app.route('/api/medical-records', methods=['GET', 'POST'])
    @login_required
    def api_medical_records():
        if request.method == 'GET':
            role = session.get('user_role')
            user_id = session.get('user_id')

            if role == 'doctor':
                doc = Doctor.query.filter_by(user_id=user_id).first()
                records = MedicalRecord.query.filter_by(doctor_id=doc.id).all() if doc else []
            elif role == 'patient':
                pat = Patient.query.filter_by(user_id=user_id).first()
                records = MedicalRecord.query.filter_by(patient_id=pat.id).all() if pat else []
            else:
                records = MedicalRecord.query.all()
            return jsonify([r.to_dict() for r in records])

        if request.method == 'POST':
            # Role check: only doctors and admins can write medical records
            role = session.get('user_role')
            if role not in ['doctor', 'admin']:
                return jsonify({'error': 'Only medical doctors or administrators can create diagnostic records.'}), 403

            data = request.get_json() if request.is_json else request.form
            patient_id = data.get('patient_id')
            diagnosis = data.get('diagnosis', '').strip()
            prescription = data.get('prescription', '').strip()

            # Determine doctor_id
            if role == 'doctor':
                doc = Doctor.query.filter_by(user_id=session.get('user_id')).first()
                if not doc:
                    return jsonify({'error': 'Doctor profile not found'}), 400
                doctor_id = doc.id
            else:
                doctor_id = data.get('doctor_id')

            if not patient_id or not doctor_id or not diagnosis or not prescription:
                if not request.is_json:
                    flash('Patient, doctor, diagnosis, and prescription are all required.', 'danger')
                    return redirect(url_for('medical_records_view'))
                return jsonify({'error': 'Missing required medical record fields'}), 400

            try:
                record = MedicalRecord(
                    patient_id=int(patient_id),
                    doctor_id=int(doctor_id),
                    diagnosis=diagnosis,
                    prescription=prescription,
                    record_date=datetime.now()
                )
                db.session.add(record)
                db.session.commit()

                if not request.is_json:
                    flash('Medical record and prescription logged successfully!', 'success')
                    return redirect(url_for('medical_records_view'))
                return jsonify({'message': 'Record logged successfully', 'record': record.to_dict()}), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500

    # -------------------------------------------------------------
    # User Management (Admin Only)
    # -------------------------------------------------------------
    @app.route('/users')
    @login_required
    @role_required('admin')
    def users_view():
        users = User.query.order_by(User.created_at.desc()).all()
        return render_template('users.html', users=users)

    @app.route('/api/users', methods=['GET', 'POST'])
    @login_required
    @role_required('admin')
    def api_users():
        if request.method == 'GET':
            users = User.query.order_by(User.created_at.desc()).all()
            return jsonify([u.to_dict() for u in users])

        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
            role = data.get('role', 'patient')

            if not username or not email or not password or not role:
                if not request.is_json:
                    flash('All user fields are required.', 'danger')
                    return redirect(url_for('users_view'))
                return jsonify({'error': 'All fields are required.'}), 400

            if User.query.filter_by(username=username).first():
                return jsonify({'error': 'Username already exists.'}), 400

            try:
                new_user = User(username=username, email=email, role=role)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.flush()

                # If creating a doctor, add doctor record
                if role == 'doctor':
                    doc = Doctor(
                        user_id=new_user.id,
                        full_name=data.get('full_name', f'Dr. {username}'),
                        specialization=data.get('specialization', 'General Practice'),
                        phone=data.get('phone', 'N/A'),
                        room_number=data.get('room_number', 'Room 101')
                    )
                    db.session.add(doc)

                db.session.commit()
                if not request.is_json:
                    flash(f'User {username} ({role}) created successfully.', 'success')
                    return redirect(url_for('users_view'))
                return jsonify({'message': 'User created successfully', 'user': new_user.to_dict()}), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500

    @app.route('/api/users/<int:user_id>', methods=['DELETE'])
    @login_required
    @role_required('admin')
    def api_delete_user(user_id):
        if user_id == session.get('user_id'):
            return jsonify({'error': 'You cannot delete your own administrative account.'}), 400

        user = User.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': f'User {user.username} deleted.'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # -------------------------------------------------------------
    # Auxiliary APIs: Doctors listing & Metrics
    # -------------------------------------------------------------
    @app.route('/api/doctors', methods=['GET'])
    @login_required
    def api_doctors():
        doctors = Doctor.query.all()
        return jsonify([d.to_dict() for d in doctors])

    @app.route('/api/metrics', methods=['GET'])
    @login_required
    @role_required('admin')
    def api_metrics():
        total_patients = Patient.query.count()
        total_doctors = Doctor.query.count()
        total_appointments = Appointment.query.count()
        pending_appointments = Appointment.query.filter_by(status='Pending').count()
        paid_rev = db.session.query(func.coalesce(func.sum(Billing.amount), 0))\
            .filter(Billing.status == 'Paid').scalar()
        pending_rev = db.session.query(func.coalesce(func.sum(Billing.amount), 0))\
            .filter(Billing.status == 'Pending').scalar()

        return jsonify({
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'total_appointments': total_appointments,
            'pending_appointments': pending_appointments,
            'paid_revenue': float(paid_rev or 0),
            'pending_revenue': float(pending_rev or 0)
        })

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', not_found=True), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('base.html', forbidden=True), 403

    return app

# Instantiate app for direct running or WSGI servers
app = create_app()

if __name__ == '__main__':
    # Initialize tables if MySQL is running
    with app.app_context():
        try:
            db.create_all()
        except Exception as ex:
            print(f"[!] Notice: Database connection check: {ex}")
            print("[!] Please start MySQL in XAMPP or run 'python seed.py' when ready.")

    print("\n" + "="*60)
    print("  Hospital Management System (HMS) Server Starting")
    print("  URL: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
