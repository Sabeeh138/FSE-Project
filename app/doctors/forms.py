from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange

class DoctorProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    specialization = StringField('Specialization', validators=[DataRequired(), Length(max=100)])
    qualification = StringField('Qualification', validators=[DataRequired(), Length(max=200)])
    experience_years = IntegerField('Years of Experience', validators=[Optional(), NumberRange(min=0, max=70)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    office_room = StringField('Office/Room Number', validators=[Optional(), Length(max=10)])
    submit = SubmitField('Save Profile')

class PrescriptionForm(FlaskForm):
    notes = TextAreaField('Prescription Notes', validators=[DataRequired()])
    submit = SubmitField('Create Prescription')