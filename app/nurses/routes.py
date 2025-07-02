from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Nurse, Patient, NurseAssignment, Appointment, PatientStatus, Room
from app.nurses.forms import NurseProfileForm, NurseAssignmentForm, PatientStatusForm

nurses = Blueprint('nurses', __name__)

@nurses.route('/nurses/dashboard')
@login_required
def dashboard():
    # Check if user is a nurse
    if current_user.role != 'nurse':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Get the nurse profile
    nurse = Nurse.query.filter_by(user_id=current_user.id).first()
    
    # If nurse profile doesn't exist, redirect to create profile
    if not nurse:
        flash('Please complete your profile first', 'info')
        return redirect(url_for('nurses.create_profile'))
    
    # Get current patient assignments from NurseAssignment model
    assignments = NurseAssignment.query.filter_by(
        nurse_id=nurse.id,
        end_date=None
    ).all()
    
    # Get inpatient appointments assigned to this nurse
    inpatient_appointments = Appointment.query.filter_by(
        nurse_id=nurse.id,
        is_inpatient=True,
        status='scheduled'
    ).all()
    
    # Create assignment objects for appointments to maintain template compatibility
    for appointment in inpatient_appointments:
        # Check if there's already an assignment for this patient
        existing_assignment = next((a for a in assignments if a.patient_id == appointment.patient_id), None)
        if not existing_assignment:
            # Create a virtual assignment object
            assignment = NurseAssignment(
                nurse_id=nurse.id,
                patient_id=appointment.patient_id,
                assignment_date=appointment.appointment_date
            )
            assignment.patient = appointment.patient
            assignments.append(assignment)
    
    return render_template(
        'nurses/dashboard.html', 
        title='Nurse Dashboard',
        nurse=nurse,
        assignments=assignments
    )

@nurses.route('/nurses/profile', methods=['GET', 'POST'])
@login_required
def create_profile():
    # Check if user is a nurse
    if current_user.role != 'nurse':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Check if nurse profile already exists
    nurse = Nurse.query.filter_by(user_id=current_user.id).first()
    
    # If profile exists, redirect to edit profile
    if nurse:
        return redirect(url_for('nurses.edit_profile'))
    
    form = NurseProfileForm()
    if form.validate_on_submit():
        nurse = Nurse(
            user_id=current_user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            department=form.department.data,
            contact_number=form.contact_number.data,
            email=form.email.data
        )
        db.session.add(nurse)
        db.session.commit()
        flash('Your profile has been created!', 'success')
        return redirect(url_for('nurses.dashboard'))
    
    return render_template('nurses/create_profile.html', title='Create Nurse Profile', form=form)

@nurses.route('/nurses/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Check if user is a nurse
    if current_user.role != 'nurse':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    nurse = Nurse.query.filter_by(user_id=current_user.id).first_or_404()
    form = NurseProfileForm()
    
    if form.validate_on_submit():
        nurse.first_name = form.first_name.data
        nurse.last_name = form.last_name.data
        nurse.department = form.department.data
        nurse.contact_number = form.contact_number.data
        nurse.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('nurses.dashboard'))
    elif request.method == 'GET':
        form.first_name.data = nurse.first_name
        form.last_name.data = nurse.last_name
        form.department.data = nurse.department
        form.contact_number.data = nurse.contact_number
        form.email.data = nurse.email
    
    return render_template('nurses/edit_profile.html', title='Edit Nurse Profile', form=form)

@nurses.route('/nurses/patients')
@login_required
def assigned_patients():
    # Check if user is a nurse
    if current_user.role != 'nurse':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    nurse = Nurse.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get all assignments (current and past) from NurseAssignment model
    assignments = NurseAssignment.query.filter_by(nurse_id=nurse.id).all()
    
    # Get all inpatient appointments assigned to this nurse
    inpatient_appointments = Appointment.query.filter_by(
        nurse_id=nurse.id,
        is_inpatient=True
    ).all()
    
    # Create assignment objects for appointments to maintain template compatibility
    for appointment in inpatient_appointments:
        # Check if there's already an assignment for this patient
        existing_assignment = next((a for a in assignments if a.patient_id == appointment.patient_id), None)
        if not existing_assignment:
            # Create a virtual assignment object
            assignment = NurseAssignment(
                nurse_id=nurse.id,
                patient_id=appointment.patient_id,
                assignment_date=appointment.appointment_date
            )
            assignment.patient = appointment.patient
            assignments.append(assignment)
    
    return render_template(
        'nurses/assigned_patients.html', 
        title='My Assigned Patients',
        assignments=assignments
    )

@nurses.route('/nurses/patients/<int:patient_id>')
@login_required
def patient_details(patient_id):
    # Check if user is a nurse
    if current_user.role != 'nurse':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    nurse = Nurse.query.filter_by(user_id=current_user.id).first_or_404()
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if nurse is assigned to this patient via NurseAssignment
    assignment = NurseAssignment.query.filter_by(
        nurse_id=nurse.id,
        patient_id=patient_id,
        end_date=None
    ).first()
    
    # If no direct assignment, check if nurse is assigned via appointment
    if not assignment:
        # Check if there's an inpatient appointment with this nurse
        appointment = Appointment.query.filter_by(
            nurse_id=nurse.id,
            patient_id=patient_id,
            is_inpatient=True,
            status='scheduled'
        ).first()
        
        if appointment:
            # Create a virtual assignment object for template compatibility
            assignment = NurseAssignment(
                nurse_id=nurse.id,
                patient_id=patient_id,
                assignment_date=appointment.appointment_date
            )
            assignment.patient = patient
        else:
            flash('You are not currently assigned to this patient', 'warning')
            return redirect(url_for('nurses.assigned_patients'))
    
    return render_template(
        'nurses/patient_details.html',
        title=f'Patient: {patient.first_name} {patient.last_name}',
        patient=patient,
        assignment=assignment
    )

@nurses.route('/nurses/assignments/new', methods=['GET', 'POST'])
@login_required
def create_assignment():
    # Check if user is a nurse
    if current_user.role != 'nurse':
        flash('You do not have permission to create assignments', 'danger')
        return redirect(url_for('main.home'))
    
    nurse = Nurse.query.filter_by(user_id=current_user.id).first_or_404()
    form = NurseAssignmentForm()
    
    if form.validate_on_submit():
        assignment = NurseAssignment(
            nurse_id=nurse.id,
            patient_id=form.patient.data.id,
            notes=form.notes.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Patient assignment has been created!', 'success')
        return redirect(url_for('nurses.assigned_patients'))
    
    return render_template(
        'nurses/create_assignment.html',
        title='Create Patient Assignment',
        form=form
    )

@nurses.route('/nurses/assignments/<int:assignment_id>/end', methods=['POST'])
@login_required
def end_assignment(assignment_id):
    # Check if user is a nurse
    if current_user.role != 'nurse':
        flash('You do not have permission to end assignments', 'danger')
        return redirect(url_for('main.home'))
    
    nurse = Nurse.query.filter_by(user_id=current_user.id).first_or_404()
    assignment = NurseAssignment.query.filter_by(id=assignment_id, nurse_id=nurse.id).first_or_404()
    
    if assignment.end_date:
        flash('This assignment has already ended', 'warning')
    else:
        from datetime import datetime
        assignment.end_date = datetime.utcnow()
        db.session.commit()
        flash('Assignment has been ended successfully', 'success')
    
    return redirect(url_for('nurses.assigned_patients'))

@nurses.route('/nurses/patients/<int:patient_id>/update_status', methods=['GET', 'POST'])
@login_required
def update_patient_status(patient_id):
    # Check if user is a nurse
    if current_user.role != 'nurse':
        flash('You do not have permission to update patient status', 'danger')
        return redirect(url_for('main.home'))
    
    nurse = Nurse.query.filter_by(user_id=current_user.id).first_or_404()
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if nurse is assigned to this patient
    assignment = NurseAssignment.query.filter_by(
        nurse_id=nurse.id,
        patient_id=patient_id,
        end_date=None
    ).first()
    
    # If no direct assignment, check if nurse is assigned via appointment
    if not assignment:
        # Check if there's an inpatient appointment with this nurse
        appointment = Appointment.query.filter_by(
            nurse_id=nurse.id,
            patient_id=patient_id,
            is_inpatient=True,
            status='scheduled'
        ).first()
        
        if not appointment:
            flash('You are not currently assigned to this patient', 'warning')
            return redirect(url_for('nurses.assigned_patients'))
    
    form = PatientStatusForm()
    
    if form.validate_on_submit():
        # Create a new patient status record
        from datetime import datetime
        status = PatientStatus(
            patient_id=patient.id,
            nurse_id=nurse.id,
            status=form.status.data,
            blood_pressure=form.blood_pressure.data,
            temperature=form.temperature.data,
            pulse=form.pulse.data,
            notes=form.notes.data,
            timestamp=datetime.utcnow()
        )
        db.session.add(status)
        db.session.commit()
        
        flash('Patient status has been updated successfully', 'success')
        return redirect(url_for('nurses.patient_details', patient_id=patient.id))
    
    return render_template(
        'nurses/update_patient_status.html',
        title='Update Patient Status',
        form=form,
        patient=patient
    )

@nurses.route('/nurses/rooms')
@login_required
def rooms():
    # Check if user is a nurse
    if current_user.role != 'nurse':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Get all rooms
    rooms = Room.query.order_by(Room.room_number).all()
    return render_template('nurses/rooms.html', title='Hospital Rooms', rooms=rooms)
