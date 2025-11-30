from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Patient, Doctor, Department, Appointment, Treatment, DoctorAvailability
from datetime import datetime, timedelta, date, time
from functools import wraps

# Create blueprints
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')
patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)

# Role-based access control decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'doctor':
            flash('You need doctor privileges to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'patient':
            flash('You need patient privileges to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# ============== AUTH ROUTES ==============

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        elif current_user.role == 'patient':
            return redirect(url_for('patient.dashboard'))
    return render_template('auth/index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact admin.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor.dashboard'))
            elif user.role == 'patient':
                return redirect(url_for('patient.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        address = request.form.get('address')
        blood_group = request.form.get('blood_group')
        emergency_contact = request.form.get('emergency_contact')
        
        # Validation
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create user
        user = User(username=username, email=email, role='patient')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        # Create patient profile
        patient = Patient(
            user_id=user.id,
            full_name=full_name,
            phone=phone,
            date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date() if date_of_birth else None,
            gender=gender,
            address=address,
            blood_group=blood_group,
            emergency_contact=emergency_contact
        )
        db.session.add(patient)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

# ============== ADMIN ROUTES ==============

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    today_appointments = Appointment.query.filter_by(appointment_date=date.today()).count()

    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_appointments=total_appointments,
                         today_appointments=today_appointments,
                         recent_appointments=recent_appointments,
                         current_date=datetime.now())

@admin_bp.route('/departments')
@login_required
@admin_required
def departments():
    departments = Department.query.all()
    return render_template('admin/departments.html', departments=departments)

@admin_bp.route('/departments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if Department.query.filter_by(name=name).first():
            flash('Department already exists', 'danger')
            return redirect(url_for('admin.add_department'))
        
        dept = Department(name=name, description=description)
        db.session.add(dept)
        db.session.commit()
        flash('Department added successfully', 'success')
        return redirect(url_for('admin.departments'))
        
    return render_template('admin/manage_department.html', title='Add Department')

@admin_bp.route('/departments/edit/<int:dept_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    
    if request.method == 'POST':
        dept.name = request.form.get('name')
        dept.description = request.form.get('description')
        
        db.session.commit()
        flash('Department updated successfully', 'success')
        return redirect(url_for('admin.departments'))
        
    return render_template('admin/manage_department.html', title='Edit Department', department=dept)

@admin_bp.route('/departments/delete/<int:dept_id>')
@login_required
@admin_required
def delete_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    
    # Check if doctors are assigned
    if dept.doctors:
        flash('Cannot delete department with assigned doctors.', 'warning')
        return redirect(url_for('admin.departments'))
        
    db.session.delete(dept)
    db.session.commit()
    flash('Department deleted successfully', 'success')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/doctors')
@login_required
@admin_required
def doctors():
    search_query = request.args.get('search', '')
    if search_query:
        doctors = Doctor.query.filter(
            (Doctor.full_name.ilike(f'%{search_query}%')) |
            (Doctor.specialization.ilike(f'%{search_query}%'))
        ).all()
    else:
        doctors = Doctor.query.all()
    
    return render_template('admin/doctors.html', doctors=doctors, search_query=search_query)

@admin_bp.route('/doctors/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_doctor():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        department_id = request.form.get('department_id')
        specialization = request.form.get('specialization')
        phone = request.form.get('phone')
        qualification = request.form.get('qualification')
        experience_years = request.form.get('experience_years')
        
        # Validation
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('admin.add_doctor'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('admin.add_doctor'))
        
        # Create user
        user = User(username=username, email=email, role='doctor')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            full_name=full_name,
            department_id=department_id,
            specialization=specialization,
            phone=phone,
            qualification=qualification,
            experience_years=int(experience_years) if experience_years else 0
        )
        db.session.add(doctor)
        db.session.commit()
        
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('admin.doctors'))
    
    departments = Department.query.all()
    return render_template('admin/add_doctor.html', departments=departments)

@admin_bp.route('/doctors/edit/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        doctor.full_name = request.form.get('full_name')
        doctor.department_id = request.form.get('department_id')
        doctor.specialization = request.form.get('specialization')
        doctor.phone = request.form.get('phone')
        doctor.qualification = request.form.get('qualification')
        doctor.experience_years = int(request.form.get('experience_years', 0))
        
        db.session.commit()
        flash('Doctor updated successfully!', 'success')
        return redirect(url_for('admin.doctors'))
    
    departments = Department.query.all()
    return render_template('admin/edit_doctor.html', doctor=doctor, departments=departments)

@admin_bp.route('/doctors/delete/<int:doctor_id>')
@login_required
@admin_required
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    user = User.query.get(doctor.user_id)
    
    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()
    
    flash('Doctor deleted successfully!', 'success')
    return redirect(url_for('admin.doctors'))

@admin_bp.route('/patients')
@login_required
@admin_required
def patients():
    search_query = request.args.get('search', '')
    if search_query:
        # Search by name, ID, or phone
        patients = Patient.query.filter(
            (Patient.full_name.ilike(f'%{search_query}%')) |
            (Patient.phone.ilike(f'%{search_query}%')) |
            (Patient.id == int(search_query) if search_query.isdigit() else False)
        ).all()
    else:
        patients = Patient.query.all()

    return render_template('admin/patients.html', patients=patients, search_query=search_query)

@admin_bp.route('/patients/edit/<int:patient_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        patient.full_name = request.form.get('full_name')
        patient.phone = request.form.get('phone')
        patient.address = request.form.get('address')
        patient.blood_group = request.form.get('blood_group')
        patient.emergency_contact = request.form.get('emergency_contact')
        
        db.session.commit()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('admin.patients'))
    
    return render_template('admin/edit_patient.html', patient=patient)

@admin_bp.route('/patients/delete/<int:patient_id>')
@login_required
@admin_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    user = User.query.get(patient.user_id)
    
    db.session.delete(patient)
    db.session.delete(user)
    db.session.commit()
    
    flash('Patient deleted successfully!', 'success')
    return redirect(url_for('admin.patients'))

@admin_bp.route('/appointments')
@login_required
@admin_required
def appointments():
    # Get filter parameters
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    date_from = request.args.get('date_from', '')

    # Base query
    query = Appointment.query

    # Apply search filter
    if search_query:
        query = query.join(Patient).join(Doctor).filter(
            (Patient.full_name.ilike(f'%{search_query}%')) |
            (Doctor.full_name.ilike(f'%{search_query}%'))
        )

    # Apply status filter
    if status_filter:
        query = query.filter(Appointment.status == status_filter)

    # Apply date filter
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Appointment.appointment_date >= from_date)
        except ValueError:
            pass

    # Get appointments
    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()

    return render_template('admin/appointments.html',
                         appointments=appointments,
                         search_query=search_query,
                         status_filter=status_filter,
                         date_from=date_from)

@admin_bp.route('/appointments/<int:appointment_id>/cancel')
@login_required
@admin_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'Cancelled'
    db.session.commit()
    flash('Appointment cancelled successfully!', 'success')
    return redirect(url_for('admin.appointments'))

# ============== DOCTOR ROUTES ==============

@doctor_bp.route('/dashboard')
@login_required
@doctor_required
def dashboard():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # Get today's appointments
    today = date.today()
    today_appointments = Appointment.query.filter_by(
        doctor_id=doctor.id,
        appointment_date=today
    ).all()
    
    # Get week's appointments
    week_end = today + timedelta(days=7)
    week_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= today,
        Appointment.appointment_date <= week_end
    ).order_by(Appointment.appointment_date).all()
    
    # Get all patients assigned
    patient_ids = [apt.patient_id for apt in Appointment.query.filter_by(doctor_id=doctor.id).all()]
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all() if patient_ids else []
    
    return render_template('doctor/dashboard.html',
                         doctor=doctor,
                         today_appointments=today_appointments,
                         week_appointments=week_appointments,
                         patients=patients)

@doctor_bp.route('/appointments/<int:appointment_id>/complete', methods=['GET', 'POST'])
@login_required
@doctor_required
def complete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if appointment.doctor_id != doctor.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('doctor.dashboard'))
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        notes = request.form.get('notes')
        
        # Update appointment status
        appointment.status = 'Completed'
        
        # Create or update treatment
        if appointment.treatment:
            appointment.treatment.diagnosis = diagnosis
            appointment.treatment.prescription = prescription
            appointment.treatment.notes = notes
        else:
            treatment = Treatment(
                appointment_id=appointment.id,
                diagnosis=diagnosis,
                prescription=prescription,
                notes=notes
            )
            db.session.add(treatment)
        
        db.session.commit()
        flash('Appointment marked as completed!', 'success')
        return redirect(url_for('doctor.dashboard'))
    
    # Fetch patient history (completed appointments, excluding current)
    history = Appointment.query.filter(
        Appointment.patient_id == appointment.patient_id,
        Appointment.status == 'Completed',
        Appointment.id != appointment.id
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('doctor/complete_appointment.html', appointment=appointment, history=history)

@doctor_bp.route('/appointments/<int:appointment_id>/cancel')
@login_required
@doctor_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if appointment.doctor_id != doctor.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('doctor.dashboard'))
    
    appointment.status = 'Cancelled'
    db.session.commit()
    
    flash('Appointment cancelled!', 'info')
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/patients/<int:patient_id>/history')
@login_required
@doctor_required
def patient_history(patient_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    patient = Patient.query.get_or_404(patient_id)
    
    # Get all appointments for this patient (visible to any doctor)
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        status='Completed'
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('doctor/patient_history.html', patient=patient, appointments=appointments)

@doctor_bp.route('/availability', methods=['GET', 'POST'])
@login_required
@doctor_required
def availability():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # Delete existing availability for next 7 days
        today = date.today()
        week_end = today + timedelta(days=7)
        DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.date >= today,
            DoctorAvailability.date <= week_end
        ).delete()
        
        # Add new availability
        for i in range(7):
            availability_date = today + timedelta(days=i)
            is_available = request.form.get(f'available_{i}') == 'on'
            
            if is_available:
                start_time_str = request.form.get(f'start_time_{i}', '09:00')
                end_time_str = request.form.get(f'end_time_{i}', '17:00')
                
                availability = DoctorAvailability(
                    doctor_id=doctor.id,
                    date=availability_date,
                    start_time=datetime.strptime(start_time_str, '%H:%M').time(),
                    end_time=datetime.strptime(end_time_str, '%H:%M').time(),
                    is_available=True
                )
                db.session.add(availability)
        
        db.session.commit()
        flash('Availability updated successfully!', 'success')
        return redirect(url_for('doctor.dashboard'))
    
    # Get current availability
    today = date.today()
    week_end = today + timedelta(days=7)
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_end
    ).all()
    
    availability_dict = {av.date: av for av in availabilities}

    # Create list of dates for the next 7 days
    date_list = [(today + timedelta(days=i)) for i in range(7)]

    return render_template('doctor/availability.html',
                         doctor=doctor,
                         availability_dict=availability_dict,
                         today=today,
                         date_list=date_list)

# ============== PATIENT ROUTES ==============

@patient_bp.route('/dashboard')
@login_required
@patient_required
def dashboard():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    # Get all departments
    departments = Department.query.all()
    
    # Get upcoming appointments
    today = date.today()
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date >= today,
        Appointment.status == 'Booked'
    ).order_by(Appointment.appointment_date).all()
    
    # Get past appointments with treatments
    past_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'Completed'
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('patient/dashboard.html',
                         patient=patient,
                         departments=departments,
                         upcoming_appointments=upcoming_appointments,
                         past_appointments=past_appointments)

@patient_bp.route('/doctors')
@login_required
@patient_required
def doctors():
    search_query = request.args.get('search', '')
    department_id = request.args.get('department', '')
    
    query = Doctor.query.join(User).filter(User.is_active == True)
    
    if search_query:
        query = query.filter(
            (Doctor.full_name.ilike(f'%{search_query}%')) |
            (Doctor.specialization.ilike(f'%{search_query}%'))
        )
    
    if department_id:
        query = query.filter(Doctor.department_id == department_id)
    
    doctors = query.all()
    departments = Department.query.all()
    
    # Get availability for next 7 days
    today = date.today()
    week_end = today + timedelta(days=7)
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_end,
        DoctorAvailability.is_available == True
    ).all()
    
    availability_dict = {}
    for av in availabilities:
        if av.doctor_id not in availability_dict:
            availability_dict[av.doctor_id] = []
        availability_dict[av.doctor_id].append(av)
    
    return render_template('patient/doctors.html',
                         doctors=doctors,
                         departments=departments,
                         availability_dict=availability_dict,
                         search_query=search_query,
                         selected_department=department_id)

@patient_bp.route('/book-appointment/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@patient_required
def book_appointment(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        appointment_date_str = request.form.get('appointment_date')
        appointment_time_str = request.form.get('appointment_time')
        reason = request.form.get('reason')
        
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        appointment_time = datetime.strptime(appointment_time_str, '%H:%M').time()
        
        # Check if slot is already booked (excluding cancelled appointments)
        existing = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status.in_(['Booked', 'Completed'])
        ).first()

        if existing:
            flash('This time slot is already booked. Please choose another time.', 'danger')
            return redirect(url_for('patient.book_appointment', doctor_id=doctor_id))
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason,
            status='Booked'
        )
        db.session.add(appointment)
        db.session.commit()
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('patient.dashboard'))
    
    # Get doctor's availability
    today = date.today()
    week_end = today + timedelta(days=7)
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_end,
        DoctorAvailability.is_available == True
    ).all()
    
    return render_template('patient/book_appointment.html',
                         doctor=doctor,
                         availabilities=availabilities)

@patient_bp.route('/appointments/<int:appointment_id>/cancel')
@login_required
@patient_required
def cancel_appointment(appointment_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.patient_id != patient.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('patient.dashboard'))
    
    appointment.status = 'Cancelled'
    db.session.commit()
    
    flash('Appointment cancelled!', 'info')
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@patient_required
def profile():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        patient.full_name = request.form.get('full_name')
        patient.phone = request.form.get('phone')
        patient.address = request.form.get('address')
        patient.blood_group = request.form.get('blood_group')
        patient.emergency_contact = request.form.get('emergency_contact')
        
        dob_str = request.form.get('date_of_birth')
        if dob_str:
            patient.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
        patient.gender = request.form.get('gender')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('patient.profile'))
    
    return render_template('patient/profile.html', patient=patient)

# ============== COMMON ROUTES ==============

@auth_bp.route('/prescription/<int:appointment_id>/print')
@login_required
def print_prescription(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Authorization Check
    is_authorized = False
    
    if current_user.role == 'admin':
        is_authorized = True
    elif current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if doctor and appointment.doctor_id == doctor.id:
            is_authorized = True
    elif current_user.role == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient and appointment.patient_id == patient.id:
            is_authorized = True
            
    if not is_authorized or appointment.status != 'Completed' or not appointment.treatment:
        flash('You are not authorized to view this prescription or it is not ready.', 'danger')
        return redirect(url_for('auth.index'))
    
    return render_template('common/prescription_print.html', appointment=appointment, today=date.today())

