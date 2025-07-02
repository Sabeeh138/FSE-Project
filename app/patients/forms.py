from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Doctor

class PatientRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[
        ('', 'Select Blood Group'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[Optional(), Email()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(max=200)])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(min=10, max=15)])
    medical_history = TextAreaField('Medical History', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Register Patient')

class MedicalRecordForm(FlaskForm):
    diagnosis = StringField('Diagnosis', validators=[DataRequired(), Length(max=200)])
    treatment = TextAreaField('Treatment', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Add Medical Record')

def get_doctors():
    return Doctor.query.all()

class AppointmentForm(FlaskForm):
    doctor = QuerySelectField('Doctor', query_factory=get_doctors, get_label=lambda d: f"{d.first_name} {d.last_name} ({d.specialization})", validators=[DataRequired()])
    appointment_date = DateField('Appointment Date', validators=[DataRequired()], format='%Y-%m-%d')
    purpose = StringField('Purpose', validators=[DataRequired(), Length(max=200)])
    notes = TextAreaField('Notes', validators=[Optional()])
    is_inpatient = BooleanField('Requires Hospitalization')
    submit = SubmitField('Schedule Appointment')

class PrescriptionForm(FlaskForm):
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Create Prescription')