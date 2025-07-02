from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Patient

class NurseProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    department = StringField('Department', validators=[DataRequired(), Length(max=100)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Profile')

def get_patients():
    return Patient.query.all()

class NurseAssignmentForm(FlaskForm):
    patient = QuerySelectField('Patient', query_factory=get_patients, get_label=lambda p: f"{p.first_name} {p.last_name} (ID: {p.id})", validators=[DataRequired()])
    notes = TextAreaField('Assignment Notes', validators=[DataRequired()])
    submit = SubmitField('Assign Patient')

class PatientStatusForm(FlaskForm):
    status = SelectField('Patient Status', choices=[
        ('stable', 'Stable'),
        ('critical', 'Critical'),
        ('improving', 'Improving'),
        ('deteriorating', 'Deteriorating'),
        ('discharged', 'Discharged')
    ], validators=[DataRequired()])
    blood_pressure = StringField('Blood Pressure', validators=[Optional()])
    temperature = StringField('Temperature (°C)', validators=[Optional()])
    pulse = StringField('Pulse Rate (bpm)', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Update Status')