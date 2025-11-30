# Hospital Management System

A comprehensive web-based Hospital Management System built with Flask, SQLite, and Bootstrap.

## Features

### Admin Features
- Dashboard with statistics (total doctors, patients, appointments)
- Add, update, and delete doctor profiles
- Manage patient records
- View and manage all appointments
- Search functionality for doctors and patients

### Doctor Features
- Dashboard showing today's and week's appointments
- View assigned patients
- Mark appointments as completed or cancelled
- Add diagnosis, prescriptions, and treatment notes
- View patient treatment history
- Set availability for next 7 days

### Patient Features
- Register and login
- Search doctors by name, specialization, or department
- View doctor profiles and availability
- Book, reschedule, and cancel appointments
- View appointment history
- View treatment history with prescriptions
- Update profile information

## Technology Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLite
- **Authentication**: Flask-Login
- **Frontend**: Jinja2, HTML5, CSS3, Bootstrap 5.3
- **ORM**: Flask-SQLAlchemy

## Project Structure

```
Hospital Management System/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models.py            # Database models
│   ├── routes.py            # All application routes
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html        # Base template
│   │   ├── auth/            # Authentication templates
│   │   ├── admin/           # Admin templates
│   │   ├── doctor/          # Doctor templates
│   │   └── patient/         # Patient templates
│   └── static/              # Static files (CSS, JS, images)
├── instance/                # Instance folder (database)
├── venv/                    # Virtual environment
├── config.py                # Configuration settings
├── run.py                   # Application entry point
└── requirements.txt         # Python dependencies
```

## Installation & Setup

1. **Clone or extract the project**

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python run.py
```

5. **Access the application**
Open your browser and navigate to: `http://127.0.0.1:5000`

## Default Admin Credentials

- **Username**: admin
- **Password**: admin123

## Database

The database is created automatically when you first run the application. It includes:

- Users table (for authentication)
- Patients table
- Doctors table
- Departments table (pre-populated with 6 departments)
- Appointments table
- Treatments table
- Doctor Availability table

## Key Functionalities

### Appointment Management
- Prevent double-booking (same doctor, date, time)
- Three status types: Booked, Completed, Cancelled
- Dynamic status updates
- Treatment records linked to completed appointments

### Search Features
- Search doctors by name or specialization
- Filter doctors by department
- Search patients by name or phone

### Availability System
- Doctors set availability for next 7 days
- Patients can only book when doctors are available
- Shows available time slots when booking

### Treatment History
- Doctors can view complete patient history
- Patients can view their own treatment records
- Includes diagnosis, prescriptions, and notes

## Validation

- **Frontend**: HTML5 form validation, required fields
- **Backend**: 
  - Unique username and email validation
  - Password minimum length
  - Duplicate appointment prevention
  - Role-based access control

## Security Features

- Password hashing using Werkzeug
- Role-based access control (Admin, Doctor, Patient)
- Login required decorators
- Session management with Flask-Login
- User account activation/deactivation

## Usage Guide

### For Patients
1. Register a new account
2. Login with credentials
3. Search for doctors by specialization or department
4. View doctor availability
5. Book appointments
6. View upcoming appointments and treatment history

### For Doctors
1. Login with credentials (created by admin)
2. Set availability for next 7 days
3. View today's and week's appointments
4. Complete appointments with diagnosis and prescriptions
5. View patient treatment history

### For Admin
1. Login with default credentials
2. Add new doctors with department assignment
3. Manage doctor and patient records
4. View all appointments
5. Search and filter doctors/patients

## Development Notes

- Database is created programmatically (no manual DB creation required)
- Admin user is auto-created on first run
- Six default departments are pre-populated
- All forms include proper validation
- Responsive design using Bootstrap 5

## Future Enhancements (Optional)

- REST API endpoints
- Charts and analytics (Chart.js)
- Email notifications
- Appointment reminders
- PDF prescription generation
- Multi-language support

## License

Educational project for learning purposes.
