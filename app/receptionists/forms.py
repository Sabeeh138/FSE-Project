from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateTimeField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length
from datetime import datetime

class ReceptionistProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Profile')

class AppointmentEditForm(FlaskForm):
    appointment_date = DateTimeField('Appointment Date and Time', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    status = SelectField('Status', choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    purpose = StringField('Purpose', validators=[DataRequired(), Length(max=200)])
    notes = TextAreaField('Notes', validators=[Length(max=500)])
    is_inpatient = BooleanField('Requires Hospitalization')
    submit = SubmitField('Update Appointment')

class RoomAssignmentForm(FlaskForm):
    room = SelectField('Room', coerce=int, validators=[DataRequired()])
    doctor = SelectField('Assigned Doctor', coerce=int, validators=[DataRequired()])
    nurse = SelectField('Assigned Nurse', coerce=int, validators=[DataRequired()])
    reason = StringField('Reason for Admission', validators=[DataRequired(), Length(max=200)])
    notes = TextAreaField('Additional Notes', validators=[Length(max=500)])
    submit = SubmitField('Assign Room')

    def __init__(self, *args, **kwargs):
        super(RoomAssignmentForm, self).__init__(*args, **kwargs)
        from app.models import Room, Doctor, Nurse
        # Only show available rooms
        self.room.choices = [(r.id, f'Room {r.room_number} - {r.room_type}') 
                            for r in Room.query.filter_by(status='available').all()]
        # Get all doctors
        self.doctor.choices = [(d.id, f'Dr. {d.first_name} {d.last_name} - {d.specialization}') 
                              for d in Doctor.query.order_by(Doctor.last_name).all()]
        # Get all nurses
        self.nurse.choices = [(n.id, f'{n.first_name} {n.last_name} - {n.department}') 
                             for n in Nurse.query.order_by(Nurse.last_name).all()]

class DischargeForm(FlaskForm):
    notes = TextAreaField('Discharge Notes', validators=[Length(max=500)])
    submit = SubmitField('Discharge Patient')

class BillForm(FlaskForm):
    medical_charges = StringField('Medical Charges', validators=[DataRequired()])
    medication_charges = StringField('Medication Charges', validators=[DataRequired()])
    other_charges = StringField('Other Charges', validators=[DataRequired()])
    notes = TextAreaField('Billing Notes', validators=[Length(max=500)])
    submit = SubmitField('Generate Bill')