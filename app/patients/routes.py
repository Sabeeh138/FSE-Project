from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Patient, MedicalRecord, Appointment, Prescription
from app.patients.forms import PatientRegistrationForm, MedicalRecordForm, AppointmentForm

patients = Blueprint('patients', __name__)

@patients.route('/patients')
@login_required
def patient_list():
    # Check if user has permission to view patients
    if current_user.role not in ['doctor', 'nurse', 'receptionist']:
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    patients = Patient.query.all()
    return render_template('patients/patient_list.html', title='Patients', patients=patients)

@patients.route('/patients/new', methods=['GET', 'POST'])
@login_required
def register_patient():
    # Check if user has permission to register patients
    if current_user.role not in ['receptionist']:
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
        return redirect(url_for('patients.patient_list'))
    
    return render_template('patients/register_patient.html', title='Register Patient', form=form)

@patients.route('/patients/<int:patient_id>')
@login_required
def patient_profile(patient_id):
    # Check if user has permission to view patient profiles
    if current_user.role not in ['doctor', 'nurse', 'receptionist']:
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    patient = Patient.query.get_or_404(patient_id)
    return render_template('patients/patient_profile.html', title=f'Patient - {patient.first_name} {patient.last_name}', patient=patient)

@patients.route('/patients/<int:patient_id>/medical_records')
@login_required
def medical_records(patient_id):
    # Check if user has permission to view medical records
    if current_user.role not in ['doctor', 'nurse']:
        flash('You do not have permission to view medical records', 'danger')
        return redirect(url_for('main.home'))
    
    patient = Patient.query.get_or_404(patient_id)
    medical_records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.record_date.desc()).all()
    return render_template('patients/medical_records.html', title='Medical Records', patient=patient, medical_records=medical_records)

@patients.route('/patients/<int:patient_id>/medical_records/new', methods=['GET', 'POST'])
@login_required
def add_medical_record(patient_id):
    # Check if user has permission to add medical records
    if current_user.role != 'doctor':
        flash('Only doctors can add medical records', 'danger')
        return redirect(url_for('main.home'))
    
    patient = Patient.query.get_or_404(patient_id)
    form = MedicalRecordForm()
    if form.validate_on_submit():
        medical_record = MedicalRecord(
            patient_id=patient_id,
            diagnosis=form.diagnosis.data,
            treatment=form.treatment.data,
            notes=form.notes.data
        )
        db.session.add(medical_record)
        db.session.commit()
        flash('Medical record has been added successfully!', 'success')
        return redirect(url_for('patients.medical_records', patient_id=patient_id))
    
    return render_template('patients/add_medical_record.html', title='Add Medical Record', form=form, patient=patient)

@patients.route('/patients/<int:patient_id>/appointments')
@login_required
def appointments(patient_id):
    # Check if user has permission to view appointments
    if current_user.role not in ['doctor', 'nurse', 'receptionist']:
        flash('You do not have permission to view appointments', 'danger')
        return redirect(url_for('main.home'))
    
    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.appointment_date.desc()).all()
    return render_template('patients/appointments.html', title='Appointments', patient=patient, appointments=appointments)

@patients.route('/patients/<int:patient_id>/appointments/new', methods=['GET', 'POST'])
@login_required
def schedule_appointment(patient_id):
    # Check if user has permission to schedule appointments
    if current_user.role not in ['receptionist']:
        flash('Only receptionists can schedule appointments', 'danger')
        return redirect(url_for('main.home'))
    
    patient = Patient.query.get_or_404(patient_id)
    form = AppointmentForm()
    if form.validate_on_submit():
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=form.doctor.data,
            appointment_date=form.appointment_date.data,
            purpose=form.purpose.data,
            notes=form.notes.data
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment has been scheduled successfully!', 'success')
        return redirect(url_for('patients.appointments', patient_id=patient_id))
    
    return render_template('patients/schedule_appointment.html', title='Schedule Appointment', form=form, patient=patient)

@patients.route('/patients/<int:patient_id>/prescriptions')
@login_required
def prescriptions(patient_id):
    # Check if user has permission to view prescriptions
    if current_user.role not in ['doctor', 'nurse', 'receptionist']:
        flash('You do not have permission to view prescriptions', 'danger')
        return redirect(url_for('main.home'))
    
    patient = Patient.query.get_or_404(patient_id)
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).order_by(Prescription.prescription_date.desc()).all()
    return render_template('patients/prescriptions.html', title='Prescriptions', patient=patient, prescriptions=prescriptions)