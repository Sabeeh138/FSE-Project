from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Receptionist, Patient, Appointment, Doctor, Room
from app.receptionists.forms import ReceptionistProfileForm, RoomAssignmentForm, AppointmentEditForm, DischargeForm, BillForm
from app.patients.forms import PatientRegistrationForm, AppointmentForm

receptionists = Blueprint('receptionists', __name__)

@receptionists.route('/receptionists/dashboard')
@login_required
def dashboard():
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Get the receptionist profile
    receptionist = Receptionist.query.filter_by(user_id=current_user.id).first()
    
    # If receptionist profile doesn't exist, redirect to create profile
    if not receptionist:
        flash('Please complete your profile first', 'info')
        return redirect(url_for('receptionists.create_profile'))
    
    # Get today's appointments
    from datetime import datetime, timedelta
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(tomorrow, datetime.min.time())
    
    today_appointments = Appointment.query.filter(
        Appointment.appointment_date >= today_start,
        Appointment.appointment_date < today_end
    ).order_by(Appointment.appointment_date).all()
    
    # Get recent patients
    recent_patients = Patient.query.order_by(Patient.registration_date.desc()).limit(5).all()
    
    return render_template(
        'receptionists/dashboard.html', 
        title='Receptionist Dashboard',
        receptionist=receptionist,
        today_appointments=today_appointments,
        recent_patients=recent_patients
    )

@receptionists.route('/receptionists/profile', methods=['GET', 'POST'])
@login_required
def create_profile():
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Check if receptionist profile already exists
    receptionist = Receptionist.query.filter_by(user_id=current_user.id).first()
    
    # If profile exists, redirect to edit profile
    if receptionist:
        return redirect(url_for('receptionists.edit_profile'))
    
    form = ReceptionistProfileForm()
    if form.validate_on_submit():
        receptionist = Receptionist(
            user_id=current_user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            contact_number=form.contact_number.data,
            email=form.email.data
        )
        db.session.add(receptionist)
        db.session.commit()
        flash('Your profile has been created!', 'success')
        return redirect(url_for('receptionists.dashboard'))
    
    return render_template('receptionists/create_profile.html', title='Create Receptionist Profile', form=form)

@receptionists.route('/receptionists/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    receptionist = Receptionist.query.filter_by(user_id=current_user.id).first_or_404()
    form = ReceptionistProfileForm()
    
    if form.validate_on_submit():
        receptionist.first_name = form.first_name.data
        receptionist.last_name = form.last_name.data
        receptionist.contact_number = form.contact_number.data
        receptionist.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('receptionists.dashboard'))
    elif request.method == 'GET':
        form.first_name.data = receptionist.first_name
        form.last_name.data = receptionist.last_name
        form.contact_number.data = receptionist.contact_number
        form.email.data = receptionist.email
    
    return render_template('receptionists/edit_profile.html', title='Edit Receptionist Profile', form=form)

@receptionists.route('/receptionists/patients')
@login_required
def patients():
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    patients = Patient.query.order_by(Patient.last_name).all()
    return render_template('receptionists/patients.html', title='Patients', patients=patients)

@receptionists.route('/receptionists/patients/<int:patient_id>')
@login_required
def patient_details(patient_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    # Get recent appointments for this patient
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.appointment_date.desc()).all()
    
    # Check if patient is an inpatient using the Appointment model
    current_inpatient = Appointment.query.filter_by(
        patient_id=patient_id,
        is_inpatient=True,
        status='scheduled'
    ).first()
    
    # For backward compatibility
    patient_type = 'inpatient' if current_inpatient else 'outpatient'
    admission = None
    if hasattr(Patient, 'admissions'):
        # If the patient has admissions, check the most recent one
        if patient.admissions and patient.admissions[-1].discharge_date is None:
            patient_type = 'inpatient'
            admission = patient.admissions[-1]
    
    return render_template(
        'receptionists/patient_details.html',
        title=f'Patient: {patient.first_name} {patient.last_name}',
        patient=patient,
        appointments=appointments,
        patient_type=patient_type,
        admission=admission,
        current_inpatient=current_inpatient
    )

@receptionists.route('/receptionists/patients/new', methods=['GET', 'POST'])
@login_required
def register_patient():
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to register patients', 'danger')
        return redirect(url_for('main.home'))
    
    form = PatientRegistrationForm()
    if form.validate_on_submit():
        patient = Patient(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            blood_group=form.blood_group.data,
            contact_number=form.contact_number.data,
            email=form.email.data,
            address=form.address.data,
            emergency_contact=form.emergency_contact.data
        )
        db.session.add(patient)
        db.session.commit()
        flash('Patient has been registered successfully!', 'success')
        return redirect(url_for('receptionists.patients'))
    
    return render_template('receptionists/register_patient.html', title='Register Patient', form=form)

@receptionists.route('/receptionists/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to edit patients', 'danger')
        return redirect(url_for('main.home'))
    
    patient = Patient.query.get_or_404(patient_id)
    form = PatientRegistrationForm()
    
    if form.validate_on_submit():
        patient.first_name = form.first_name.data
        patient.last_name = form.last_name.data
        patient.date_of_birth = form.date_of_birth.data
        patient.gender = form.gender.data
        patient.blood_group = form.blood_group.data
        patient.contact_number = form.contact_number.data
        patient.email = form.email.data
        patient.address = form.address.data
        patient.emergency_contact = form.emergency_contact.data
        
        db.session.commit()
        flash('Patient information has been updated successfully!', 'success')
        return redirect(url_for('receptionists.patients'))
    
    elif request.method == 'GET':
        form.first_name.data = patient.first_name
        form.last_name.data = patient.last_name
        form.date_of_birth.data = patient.date_of_birth
        form.gender.data = patient.gender
        form.blood_group.data = patient.blood_group
        form.contact_number.data = patient.contact_number
        form.email.data = patient.email
        form.address.data = patient.address
        form.emergency_contact.data = patient.emergency_contact
    
    return render_template('receptionists/edit_patient.html', title='Edit Patient', form=form, patient=patient)

@receptionists.route('/receptionists/appointments')
@login_required
def appointments():
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return render_template('receptionists/appointments.html', title='Appointments', appointments=appointments)

@receptionists.route('/receptionists/appointments/new', methods=['GET', 'POST'])
@login_required
def schedule_appointment():
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to schedule appointments', 'danger')
        return redirect(url_for('main.home'))
    
    form = AppointmentForm()
    if form.validate_on_submit():
        appointment = Appointment(
            patient_id=request.form.get('patient_id'),
            doctor_id=form.doctor.data.id,
            appointment_date=form.appointment_date.data,
            purpose=form.purpose.data,
            notes=form.notes.data,
            is_inpatient=form.is_inpatient.data
        )
        db.session.add(appointment)
        db.session.commit()
        
        # If this is an inpatient appointment, redirect to room assignment
        if form.is_inpatient.data:
            flash('Appointment scheduled. Please assign a room for this inpatient.', 'info')
            return redirect(url_for('receptionists.admit_patient', patient_id=request.form.get('patient_id')))
        else:
            flash('Appointment has been scheduled successfully!', 'success')
            return redirect(url_for('receptionists.appointments'))
    
    # Get patient ID from query parameter if available
    patient_id = request.args.get('patient_id')
    patient = None
    if patient_id:
        patient = Patient.query.get(patient_id)
    
    # Get all patients for the dropdown if no specific patient is selected
    patients = Patient.query.order_by(Patient.last_name).all() if not patient else None
    
    return render_template(
        'receptionists/schedule_appointment.html', 
        title='Schedule Appointment', 
        form=form,
        patient=patient,
        patients=patients
    )

@receptionists.route('/receptionists/appointments/<int:appointment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to edit appointments', 'danger')
        return redirect(url_for('main.home'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    form = AppointmentEditForm()
    
    if form.validate_on_submit():
        appointment.appointment_date = form.appointment_date.data
        appointment.status = form.status.data
        appointment.purpose = form.purpose.data
        appointment.notes = form.notes.data
        
        # Handle inpatient status change
        if form.is_inpatient.data != appointment.is_inpatient:
            # If changing from regular to inpatient
            if form.is_inpatient.data and not appointment.is_inpatient:
                appointment.is_inpatient = True
                flash('Appointment updated to inpatient. Please assign a room.', 'info')
                db.session.commit()
                return redirect(url_for('receptionists.admit_patient', patient_id=appointment.patient_id))
            # If changing from inpatient to regular
            elif not form.is_inpatient.data and appointment.is_inpatient:
                # If room is assigned, free it up
                if appointment.room_id:
                    appointment.discharge()
                appointment.is_inpatient = False
        
        db.session.commit()
        flash('Appointment has been updated successfully!', 'success')
        return redirect(url_for('receptionists.dashboard'))
    elif request.method == 'GET':
        form.appointment_date.data = appointment.appointment_date
        form.status.data = appointment.status
        form.purpose.data = appointment.purpose
        form.notes.data = appointment.notes
        form.is_inpatient.data = appointment.is_inpatient
    
    return render_template(
        'receptionists/edit_appointment.html',
        title='Edit Appointment',
        form=form,
        appointment=appointment
    )

@receptionists.route('/receptionists/doctors')
@login_required
def doctors():
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    doctors = Doctor.query.order_by(Doctor.last_name).all()
    return render_template('receptionists/doctors.html', title='Doctors', doctors=doctors)

@receptionists.route('/receptionists/doctors/<int:doctor_id>')
@login_required
def doctor_details(doctor_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Get doctor's schedule if available
    schedules = []
    if hasattr(Doctor, 'schedules'):
        schedules = doctor.schedules
    
    # Get upcoming appointments for this doctor
    from datetime import datetime
    today = datetime.now()
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date >= today
    ).order_by(Appointment.appointment_date).all()
    
    return render_template(
        'receptionists/doctor_details.html',
        title=f'Doctor: {doctor.first_name} {doctor.last_name}',
        doctor=doctor,
        schedules=schedules,
        appointments=appointments
    )

@receptionists.route('/receptionists/doctors/<int:doctor_id>/schedule')
@login_required
def doctor_schedule(doctor_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Get doctor's schedule if available
    schedules = []
    if hasattr(Doctor, 'schedules'):
        schedules = doctor.schedules
    
    # Get upcoming appointments for this doctor
    from datetime import datetime
    today = datetime.now()
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date >= today
    ).order_by(Appointment.appointment_date).all()
    
    return render_template(
        'receptionists/doctor_schedule.html',
        title=f'Doctor Schedule: {doctor.first_name} {doctor.last_name}',
        doctor=doctor,
        schedules=schedules,
        appointments=appointments
    )

@receptionists.route('/receptionists/doctor_schedules')
@login_required
def doctor_schedules():
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Get filter parameters
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date')
    
    # Base query
    schedules = []
    doctors = Doctor.query.order_by(Doctor.last_name).all()
    
    # Apply filters if available
    if hasattr(Doctor, 'schedules'):
        if doctor_id:
            doctor = Doctor.query.get_or_404(doctor_id)
            schedules = doctor.schedules
        else:
            # Get all schedules
            for doctor in doctors:
                if hasattr(doctor, 'schedules'):
                    schedules.extend(doctor.schedules)
    
    return render_template('receptionists/doctors.html', title='Doctor Schedules', doctors=doctors, schedules=schedules)

@receptionists.route('/receptionists/search', methods=['GET', 'POST'])
@login_required
def search():
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    query = request.args.get('query', '')
    results = []
    
    if query:
        # Search patients
        patients = Patient.query.filter(
            (Patient.first_name.ilike(f'%{query}%')) |
            (Patient.last_name.ilike(f'%{query}%')) |
            (Patient.contact_number.ilike(f'%{query}%'))
        ).all()
        
        # Search doctors
        doctors = Doctor.query.filter(
            (Doctor.first_name.ilike(f'%{query}%')) |
            (Doctor.last_name.ilike(f'%{query}%')) |
            (Doctor.specialization.ilike(f'%{query}%'))
        ).all()
        
        results = {
            'patients': patients,
            'doctors': doctors
        }
    
    return render_template('receptionists/search_results.html', title='Search Results', query=query, results=results)

@receptionists.route('/receptionists/appointments/<int:appointment_id>')
@login_required
def appointment_details(appointment_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    return render_template(
        'receptionists/appointment_details.html',
        title=f'Appointment Details',
        appointment=appointment
    )

@receptionists.route('/receptionists/rooms')
@login_required
def rooms():
    # Check if user is a receptionist or nurse
    if current_user.role != 'receptionist' and current_user.role != 'nurse':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    from app.models import Room
    rooms = Room.query.order_by(Room.room_number).all()
    return render_template('receptionists/rooms.html', title='Rooms', rooms=rooms)

@receptionists.route('/receptionists/rooms/<int:room_id>/maintenance')
@login_required
def set_room_maintenance(room_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to manage rooms', 'danger')
        return redirect(url_for('main.home'))
    
    room = Room.query.get_or_404(room_id)
    
    # Try to set room to maintenance
    if room.set_maintenance():
        db.session.commit()
        flash(f'Room {room.room_number} has been set to maintenance mode', 'success')
    else:
        flash(f'Cannot set room {room.room_number} to maintenance because it is currently occupied', 'warning')
    
    return redirect(url_for('receptionists.rooms'))

@receptionists.route('/receptionists/rooms/<int:room_id>/available')
@login_required
def set_room_available(room_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to manage rooms', 'danger')
        return redirect(url_for('main.home'))
    
    room = Room.query.get_or_404(room_id)
    
    # Try to set room to available
    if room.set_available():
        db.session.commit()
        flash(f'Room {room.room_number} has been set to available', 'success')
    else:
        flash(f'Cannot set room {room.room_number} to available because it is not in maintenance mode', 'warning')
    
    return redirect(url_for('receptionists.rooms'))

@receptionists.route('/receptionists/patients/<int:patient_id>/admit', methods=['GET', 'POST'])
@login_required
def admit_patient(patient_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to admit patients', 'danger')
        return redirect(url_for('main.home'))
    
    from app.models import Patient, Room, Appointment, Doctor
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if patient already has an active inpatient appointment
    current_inpatient = Appointment.query.filter_by(
        patient_id=patient_id,
        is_inpatient=True,
        status='scheduled'
    ).first()
    
    if current_inpatient and current_inpatient.room_id:
        flash('Patient is already admitted', 'warning')
        return redirect(url_for('receptionists.patient_details', patient_id=patient_id))
    
    form = RoomAssignmentForm()
    if form.validate_on_submit():
        # Get the selected room
        room = Room.query.get(form.room.data)
        
        # Find the most recent inpatient appointment without a room
        appointment = Appointment.query.filter_by(
            patient_id=patient_id,
            is_inpatient=True,
            status='scheduled',
            room_id=None
        ).order_by(Appointment.appointment_date.desc()).first()
        
        if not appointment:
            # Create a new inpatient appointment if none exists
            from datetime import datetime
            doctor = Doctor.query.get(form.doctor.data)
            appointment = Appointment(
                patient_id=patient_id,
                doctor_id=form.doctor.data,
                appointment_date=datetime.utcnow(),
                purpose=form.reason.data,
                notes=form.notes.data,
                is_inpatient=True
            )
            db.session.add(appointment)
        
        # Assign room and nurse to the appointment
        appointment.assign_room(room.id, form.nurse.data)
        
        db.session.commit()
        
        flash('Patient has been admitted successfully!', 'success')
        return redirect(url_for('receptionists.patient_details', patient_id=patient_id))
    
    return render_template(
        'receptionists/admit_patient.html',
        title=f'Admit Patient: {patient.first_name} {patient.last_name}',
        form=form,
        patient=patient
    )

@receptionists.route('/receptionists/patients/<int:patient_id>/discharge', methods=['GET', 'POST'])
@login_required
def discharge_patient(patient_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to discharge patients', 'danger')
        return redirect(url_for('main.home'))
    
    from app.models import Patient, Appointment
    patient = Patient.query.get_or_404(patient_id)
    
    # Get current inpatient appointment
    appointment = Appointment.query.filter_by(
        patient_id=patient_id,
        is_inpatient=True,
        status='scheduled'
    ).first_or_404()
    
    form = DischargeForm()
    if form.validate_on_submit():
        # Update appointment notes
        if form.notes.data:
            appointment.notes = appointment.notes + '\n\nDischarge notes: ' + form.notes.data if appointment.notes else 'Discharge notes: ' + form.notes.data
        
        # Mark appointment as completed
        appointment.status = 'completed'
        
        # Discharge patient from room
        appointment.discharge()
        
        # Generate bill
        from app.models import Bill
        from datetime import datetime
        
        # Calculate days admitted
        days_admitted = (datetime.utcnow() - appointment.appointment_date).days or 1
        room_charges = days_admitted * appointment.room.daily_rate
        
        # Create bill
        bill = Bill(
            appointment_id=appointment.id,  # Link bill to appointment
            room_charges=room_charges,
            medical_charges=0.0,  # These will be updated later
            medication_charges=0.0,
            other_charges=0.0,
            notes=f'Bill for inpatient stay from {appointment.appointment_date.strftime("%Y-%m-%d")} to {datetime.utcnow().strftime("%Y-%m-%d")}'
        )
        
        # Calculate total
        bill.calculate_total()
        
        db.session.add(bill)
        db.session.commit()
        
        flash('Patient has been discharged successfully!', 'success')
        return redirect(url_for('receptionists.patient_details', patient_id=patient_id))
    
    return render_template(
        'receptionists/discharge_patient.html',
        title=f'Discharge Patient: {patient.first_name} {patient.last_name}',
        form=form,
        patient=patient,
        appointment=appointment
    )

@receptionists.route('/receptionists/admissions/<int:admission_id>/bill', methods=['GET', 'POST'])
@login_required
def generate_admission_bill(admission_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to generate bills', 'danger')
        return redirect(url_for('main.home'))
    
    from app.models import Admission, Bill
    admission = Admission.query.get_or_404(admission_id)
    
    # Calculate room charges
    from datetime import datetime
    discharge_date = admission.discharge_date or datetime.utcnow()
    days_admitted = (discharge_date - admission.admission_date).days or 1
    room_charges = days_admitted * admission.room.daily_rate
    
    form = BillForm()
    if form.validate_on_submit():
        bill = Bill(
            admission_id=admission_id,
            room_charges=room_charges,
            medical_charges=float(form.medical_charges.data),
            medication_charges=float(form.medication_charges.data),
            other_charges=float(form.other_charges.data),
            notes=form.notes.data
        )
        
        # Calculate total
        bill.calculate_total()
        
        db.session.add(bill)
        db.session.commit()
        
        flash('Bill has been generated successfully!', 'success')
        return redirect(url_for('receptionists.patient_details', patient_id=admission.patient_id))
    
    return render_template(
        'receptionists/generate_bill.html',
        title='Generate Bill',
        form=form,
        admission=admission,
        room_charges=room_charges
    )

@receptionists.route('/receptionists/appointments/<int:appointment_id>/bill', methods=['GET', 'POST'])
@login_required
def generate_appointment_bill(appointment_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to generate bills', 'danger')
        return redirect(url_for('main.home'))
    
    from app.models import Appointment, Bill
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify this is an inpatient appointment
    if not appointment.is_inpatient or not appointment.room_id:
        flash('This appointment is not an inpatient stay', 'warning')
        return redirect(url_for('receptionists.appointments'))
    
    # Calculate room charges
    from datetime import datetime
    discharge_date = datetime.utcnow() if appointment.status == 'scheduled' else appointment.created_at
    days_admitted = (discharge_date - appointment.appointment_date).days or 1
    room_charges = days_admitted * appointment.room.daily_rate
    
    form = BillForm()
    if form.validate_on_submit():
        bill = Bill(
            appointment_id=appointment_id,
            room_charges=room_charges,
            medical_charges=float(form.medical_charges.data),
            medication_charges=float(form.medication_charges.data),
            other_charges=float(form.other_charges.data),
            notes=form.notes.data
        )
        
        # Calculate total
        bill.calculate_total()
        
        db.session.add(bill)
        db.session.commit()
        
        flash('Bill has been generated successfully!', 'success')
        return redirect(url_for('receptionists.patient_details', patient_id=appointment.patient_id))
    
    return render_template(
        'receptionists/generate_bill.html',
        title='Generate Bill for Inpatient Stay',
        form=form,
        appointment=appointment,
        room_charges=room_charges
    )