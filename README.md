# MediCare - Hospital Management System (HMS)

An enterprise-grade, full-stack Hospital Management System (HMS) developed with **Python (Flask)**, **MySQL (XAMPP / phpMyAdmin)**, and a modern, responsive **Bootstrap 5 & JavaScript** frontend.

---

## 🏥 System Overview & Roles

MediCare HMS provides tailored clinical and administrative portals with strict Role-Based Access Control (RBAC):

1. **Administrator (`admin`)**
   - System-wide dashboard metrics: Total Registered Patients, Active Medical Doctors, Scheduled Appointments, and Financial Revenue Summary (Paid vs. Pending).
   - User administration portal to create/remove doctors, front-desk receptionists, and administrators.
   - Global view and control over all appointments and clinical logs.

2. **Doctor (`doctor`)**
   - Personalized clinical dashboard with today's real-time consultation schedule.
   - Quick **Diagnose & Prescribe** clinical interface to log Electronic Health Records (EHR) and prescriptions directly into the patient's chart.
   - View assigned patients and historical diagnostic logs.

3. **Receptionist / Front Desk (`receptionist`)**
   - Patient intake and directory management (instant registration).
   - Appointment booking, rescheduling, and cancellation.
   - Triage queue to review and confirm pending patient booking requests.

4. **Patient Portal (`patient`)**
   - View upcoming consultation appointments with doctor name, room number, and time.
   - Review past medical diagnoses, prescriptions, and dosage instructions.
   - Request new consultations online.

---

## 📁 Project Folder Structure

```
Hospital/
├── config.py                 # Application configuration & MySQL/XAMPP connection resolver
├── database.py               # SQLAlchemy ORM instance initialization
├── models.py                 # Relational models: User, Patient, Doctor, Appointment, MedicalRecord, Billing
├── app.py                    # Main Flask application with RBAC, session auth, views & REST APIs
├── seed.py                   # Automated database initialization & seed script
├── test_app.py               # Automated test suite covering auth, RBAC, and REST endpoints
├── requirements.txt          # Python dependencies
├── README.md                 # Complete documentation & setup instructions
├── schema/
│   └── hospital_db.sql       # Pure MySQL script with database schema & seed accounts
├── static/
│   ├── css/
│   │   └── style.css         # Modern healthcare theme, glassmorphism, responsive styles
│   └── js/
│       └── app.js            # Client-side validation, AJAX actions, demo autofill & modals
└── templates/
    ├── base.html             # Master responsive layout (role-aware sidebar & topbar)
    ├── login.html            # Sign-in page with 1-click quick-fill demo buttons
    ├── register.html         # Self-service patient registration page
    ├── dashboard.html        # Adaptive dashboard (Admin, Doctor, Receptionist, Patient)
    ├── patients.html         # Patient directory & registration interface
    ├── appointments.html     # Appointment scheduling & status management interface
    ├── medical_records.html  # Electronic Health Records (EHR) & prescription logs
    └── users.html            # Admin user management portal
```

---

## 🗄️ Database Setup in XAMPP / phpMyAdmin

Follow these step-by-step instructions to set up the MySQL database using XAMPP:

### Step 1: Start XAMPP Services
1. Open the **XAMPP Control Panel**.
2. Click **Start** next to **Apache**.
3. Click **Start** next to **MySQL**.

### Step 2: Open phpMyAdmin
1. Open your web browser and navigate to:
   ```
   http://localhost/phpmyadmin/
   ```

### Step 3: Import the Database Script
1. In the top navigation bar of phpMyAdmin, click the **Import** tab.
2. Under **File to import**, click **Choose File** (or **Browse**).
3. Navigate to your project directory and select:
   ```
   Hospital/schema/hospital_db.sql
   ```
4. Scroll to the bottom and click the **Import** (or **Go**) button.
5. phpMyAdmin will execute the script, creating the database `hospital_db` and its 6 normalized tables populated with sample records.

> **Default Connection Settings**:
> - **Host**: `localhost` (port `3306`)
> - **User**: `root`
> - **Password**: `""` (empty by default in XAMPP)
> - **Database**: `hospital_db`
>
> *Note:* If your MySQL server uses a custom password or port, you can set the environment variables `DB_PASSWORD` or `DB_PORT`, or customize `config.py`. If MySQL is offline, the application will automatically activate its local fallback (`hospital_dev.db`) so development never halts.

---

## 🚀 Running the Flask Application Locally

### 1. Install Dependencies
Open PowerShell or your command prompt in the `Hospital` folder and run:
```bash
pip install -r requirements.txt
```

### 2. (Optional) Run Initial Seeder via CLI
If you prefer initializing and populating the database via Python instead of phpMyAdmin, run:
```bash
python seed.py
```

### 3. Run the Automated Test Suite
To verify all routes, API endpoints, and RBAC rules:
```bash
python test_app.py
```

### 4. Start the Application Server
Run the Flask server:
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Demo Login Credentials

The login screen includes **1-click quick-fill buttons** for each role, or you can log in manually:

| Role | Username | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | System analytics, user administration, global schedules, billing |
| **Doctor** | `dr_sarah` | `doctor123` | Daily schedule, consultation notes, write diagnoses & prescriptions |
| **Doctor** | `dr_james` | `doctor123` | Pediatric/General medicine daily schedule and medical records |
| **Receptionist** | `receptionist1` | `rec123` | Register patients, book appointments, approve triage queue |
| **Patient** | `patient_john` | `patient123` | View personal health record, active prescriptions, book visits |
| **Patient** | `patient_emily`| `patient123` | View personal appointments, prescriptions, and billing statements |

---

## 🌐 RESTful API Reference

All endpoints return structured JSON and enforce session-based Role-Based Access Control:

| Method | Endpoint | Allowed Roles | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/metrics` | `admin` | Real-time KPI counts and financial billing summary |
| `GET` | `/api/patients` | `admin`, `doctor`, `receptionist` | List all patient records |
| `POST` | `/api/patients` | `admin`, `receptionist` | Register a new patient record |
| `PUT` | `/api/patients/<id>` | `admin`, `receptionist` | Update patient demographic info |
| `DELETE` | `/api/patients/<id>` | `admin`, `receptionist` | Delete a patient profile |
| `GET` | `/api/appointments` | All (filtered by role) | List appointments |
| `POST` | `/api/appointments` | All | Schedule a new appointment |
| `PATCH`| `/api/appointments/<id>/status`| `admin`, `doctor`, `receptionist`| Update status (`Confirmed`, `Completed`, `Cancelled`)|
| `DELETE`| `/api/appointments/<id>` | `admin` | Cancel and delete an appointment |
| `GET` | `/api/medical-records` | All (filtered by role) | Retrieve EHR diagnostic logs |
| `POST`| `/api/medical-records` | `admin`, `doctor` | Record diagnosis and prescribe medication |
| `GET` | `/api/doctors` | All authenticated | List active doctors and specializations |
| `GET` | `/api/users` | `admin` | List all system user accounts |
| `POST`| `/api/users` | `admin` | Create new staff or user login |
| `DELETE`| `/api/users/<id>` | `admin` | Deactivate/delete a user account |
