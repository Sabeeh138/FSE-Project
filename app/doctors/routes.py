from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Doctor, Patient, Appointment, Prescription, MedicalRecord
from app.doctors.forms import DoctorProfileForm, PrescriptionForm

doctors = Blueprint('doctors', __name__)

@doctors.route('/doctors/dashboard')
@login_required
def dashboard():
    # Check if user is a doctor
    if current_user.role != 'doctor':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Get the doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # If doctor profile doesn't exist, redirect to create profile
    if not doctor:
        flash('Please complete your profile first', 'info')
        return redirect(url_for('doctors.create_profile'))
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter_by(
        doctor_id=doctor.id, 
        status='scheduled'
    ).order_by(Appointment.appointment_date).limit(5).all()
    
    return render_template(
        'doctors/dashboard.html', 
        title='Doctor Dashboard',
        doctor=doctor,
        upcoming_appointments=upcoming_appointments
    )

@doctors.route('/doctors/profile', methods=['GET', 'POST'])
@login_required
def create_profile():
    # Check if user is a doctor
    if current_user.role != 'doctor':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Check if doctor profile already exists
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # If profile exists, redirect to edit profile
    if doctor:
        return redirect(url_for('doctors.edit_profile'))
    
    form = DoctorProfileForm()
    if form.validate_on_submit():
        doctor = Doctor(
            user_id=current_user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            specialization=form.specialization.data,
            qualification=form.qualification.data,
            experience_years=form.experience_years.data,
            contact_number=form.contact_number.data,
            email=form.email.data,
            office_room=form.office_room.data
        )
        db.session.add(doctor)
        db.session.commit()
        flash('Your profile has been created!', 'success')
        return redirect(url_for('doctors.dashboard'))
    
    return render_template('doctors/create_profile.html', title='Create Doctor Profile', form=form)

@doctors.route('/doctors/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Check if user is a doctor
    if current_user.role != 'doctor':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
    form = DoctorProfileForm()
    
    if form.validate_on_submit():
        doctor.first_name = form.first_name.data
        doctor.last_name = form.last_name.data
        doctor.specialization = form.specialization.data
        doctor.qualification = form.qualification.data
        doctor.experience_years = form.experience_years.data
        doctor.contact_number = form.contact_number.data
        doctor.email = form.email.data
        doctor.office_room = form.office_room.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('doctors.dashboard'))
    elif request.method == 'GET':
        form.first_name.data = doctor.first_name
        form.last_name.data = doctor.last_name
        form.specialization.data = doctor.specialization
        form.qualification.data = doctor.qualification
        form.experience_years.data = doctor.experience_years
        form.contact_number.data = doctor.contact_number
        form.email.data = doctor.email
        form.office_room.data = doctor.office_room
    
    return render_template('doctors/edit_profile.html', title='Edit Doctor Profile', form=form)

@doctors.route('/doctors/appointments')
@login_required
def appointments():
    # Check if user is a doctor
    if current_user.role != 'doctor':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template(
        'doctors/appointments.html', 
        title='My Appointments',
        appointments=appointments
    )

@doctors.route('/doctors/appointments/<int:appointment_id>/update', methods=['POST'])
@login_required
def update_appointment_status(appointment_id):
    # Check if user is a doctor
    if current_user.role != 'doctor':
        flash('You do not have permission to perform this action', 'danger')
        return redirect(url_for('main.home'))
    
    doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor.id).first_or_404()
    
    status = request.form.get('status')
    if status in ['scheduled', 'completed', 'cancelled']:
        appointment.status = status
        
        # If appointment is marked as completed and it's an inpatient appointment with a room,
        # update the room status to available (discharge the patient)
        if status == 'completed' and appointment.is_inpatient and appointment.room_id:
            # Free up the room
            from app.models import Room
            room = Room.query.get(appointment.room_id)
            if room:
                room.status = 'available'
                flash(f'Room {room.room_number} has been marked as available.', 'info')
        
        db.session.commit()
        flash('Appointment status has been updated!', 'success')
    else:
        flash('Invalid status value', 'danger')
    
    return redirect(url_for('doctors.appointments'))

@doctors.route('/doctors/patients')
@login_required
def patients():
    # Check if user is a doctor
    if current_user.role != 'doctor':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get patients who have appointments with this doctor
    patient_ids = db.session.query(Appointment.patient_id).filter_by(doctor_id=doctor.id).distinct().all()
    patient_ids = [pid[0] for pid in patient_ids]  # Extract IDs from result tuples
    
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
    
    return render_template('doctors/patients.html', title='My Patients', patients=patients)

@doctors.route('/doctors/prescriptions/new/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def create_prescription(patient_id):
    # Check if user is a doctor
    if current_user.role != 'doctor':
        flash('You do not have permission to create prescriptions', 'danger')
        return redirect(url_for('main.home'))
    
    doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
    patient = Patient.query.get_or_404(patient_id)
    
    form = PrescriptionForm()
    if form.validate_on_submit():
        prescription = Prescription(
            patient_id=patient_id,
            doctor_id=doctor.id,
            notes=form.notes.data
        )
        db.session.add(prescription)
        db.session.commit()
        
        flash('Prescription has been created!', 'success')
        return redirect(url_for('doctors.patient_details', patient_id=patient_id))
    
    return render_template(
        'doctors/create_prescription.html',
        title='Create Prescription',
        form=form,
        patient=patient
    )

@doctors.route('/doctors/patients/<int:patient_id>')
@login_required
def patient_details(patient_id):
    # Check if user is a doctor
    if current_user.role != 'doctor':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
    patient = Patient.query.get_or_404(patient_id)
    
    # Get medical records
    medical_records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.record_date.desc()).all()
    
    # Get prescriptions by this doctor
    prescriptions = Prescription.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).order_by(Prescription.prescription_date.desc()).all()
    
    # Get appointments with this doctor
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template(
        'doctors/patient_details.html',
        title=f'Patient: {patient.first_name} {patient.last_name}',
        patient=patient,
        medical_records=medical_records,
        prescriptions=prescriptions,
        appointments=appointments
    )