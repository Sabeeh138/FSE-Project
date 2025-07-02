from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager, bcrypt

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'doctor', 'nurse', 'receptionist', 'store_manager'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    nurse_profile = db.relationship('Nurse', backref='user', uselist=False, cascade='all, delete-orphan')
    receptionist_profile = db.relationship('Receptionist', backref='user', uselist=False, cascade='all, delete-orphan')
    store_manager_profile = db.relationship('StoreManager', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role = role
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_group = db.Column(db.String(5))
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))
    address = db.Column(db.String(200), nullable=False)
    emergency_contact = db.Column(db.String(15))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"Patient('{self.first_name}', '{self.last_name}', '{self.contact_number}')"

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(200), nullable=False)
    experience_years = db.Column(db.Integer)
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    office_room = db.Column(db.String(10))
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy=True, cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', backref='doctor', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"Doctor('{self.first_name}', '{self.last_name}', '{self.specialization}')"

class Nurse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    # Relationships
    patient_assignments = db.relationship('NurseAssignment', backref='nurse', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"Nurse('{self.first_name}', '{self.last_name}', '{self.department}')"

class Receptionist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    def __repr__(self):
        return f"Receptionist('{self.first_name}', '{self.last_name}')"

class StoreManager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    def __repr__(self):
        return f"StoreManager('{self.first_name}', '{self.last_name}')"

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    purpose = db.Column(db.String(200))
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_inpatient = db.Column(db.Boolean, default=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    nurse_id = db.Column(db.Integer, db.ForeignKey('nurse.id'), nullable=True)
    
    # Relationships for inpatient appointments
    room = db.relationship('Room', backref='appointments')
    nurse = db.relationship('Nurse', backref='appointments')
    
    def __repr__(self):
        return f"Appointment(Patient: {self.patient_id}, Doctor: {self.doctor_id}, Date: {self.appointment_date})"
    
    def assign_room(self, room_id, nurse_id):
        """Assign a room and nurse to an inpatient appointment"""
        from app.models import Room
        
        # Mark as inpatient
        self.is_inpatient = True
        self.room_id = room_id
        self.nurse_id = nurse_id
        
        # Update room status
        room = Room.query.get(room_id)
        if room:
            room.status = 'occupied'
        
        return True
    
    def discharge(self):
        """Discharge a patient from their room"""
        from app.models import Room
        
        if self.is_inpatient and self.room_id:
            # Free up the room
            room = Room.query.get(self.room_id)
            if room:
                room.status = 'available'
            
            return True
        return False

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    diagnosis = db.Column(db.String(200), nullable=False)
    treatment = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"MedicalRecord(Patient: {self.patient_id}, Date: {self.record_date})"

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    prescription_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    medications = db.relationship('PrescriptionMedication', backref='prescription', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"Prescription(Patient: {self.patient_id}, Doctor: {self.doctor_id}, Date: {self.prescription_date})"

class PrescriptionMedication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    dispensed = db.Column(db.Boolean, default=False)
    dispensed_at = db.Column(db.DateTime)
    
    def dispense(self):
        if not self.dispensed:
            medication = Medication.query.get(self.medication_id)
            if medication.stock_quantity >= self.quantity:
                medication.stock_quantity -= self.quantity
                self.dispensed = True
                self.dispensed_at = datetime.utcnow()
                db.session.commit()
                return True
            return False
        return False

    def __repr__(self):
        return f"PrescriptionMedication(Prescription: {self.prescription_id}, Medication: {self.medication_id})"

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    manufacturer = db.Column(db.String(100))
    unit_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    
    # Relationships
    prescription_medications = db.relationship('PrescriptionMedication', backref='medication', lazy=True)
    
    def __repr__(self):
        return f"Medication('{self.name}', Stock: {self.stock_quantity})"

class NurseAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nurse_id = db.Column(db.Integer, db.ForeignKey('nurse.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    assignment_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Relationship
    patient = db.relationship('Patient', backref='nurse_assignments')
    
    def __repr__(self):
        return f"NurseAssignment(Nurse: {self.nurse_id}, Patient: {self.patient_id})"

class PatientStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    nurse_id = db.Column(db.Integer, db.ForeignKey('nurse.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # stable, critical, improving, deteriorating, discharged
    blood_pressure = db.Column(db.String(20))
    temperature = db.Column(db.String(10))
    pulse = db.Column(db.String(10))
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='status_updates')
    nurse = db.relationship('Nurse', backref='patient_status_updates')
    
    def __repr__(self):
        return f"PatientStatus(Patient: {self.patient_id}, Status: {self.status}, Time: {self.timestamp})"

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # medication, equipment, supplies
    description = db.Column(db.Text)
    unit_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = db.relationship('Supplier', backref='inventory_items')
    
    def __repr__(self):
        return f"Inventory('{self.item_name}', Category: {self.category}, Stock: {self.stock_quantity})"

class MedicalProcedure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    procedure_name = db.Column(db.String(200), nullable=False)
    procedure_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    inventory_items = db.relationship('ProcedureInventoryItem', backref='procedure', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"MedicalProcedure(Patient: {self.patient_id}, Doctor: {self.doctor_id}, Procedure: {self.procedure_name})"

class ProcedureInventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    procedure_id = db.Column(db.Integer, db.ForeignKey('medical_procedure.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    quantity_used = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    
    # Relationships
    inventory = db.relationship('Inventory', backref='procedure_items')
    
    def use_items(self):
        inventory_item = Inventory.query.get(self.inventory_id)
        if inventory_item.stock_quantity >= self.quantity_used:
            inventory_item.stock_quantity -= self.quantity_used
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f"ProcedureInventoryItem(Procedure: {self.procedure_id}, Inventory: {self.inventory_id}, Quantity: {self.quantity_used})"

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f"Supplier('{self.name}', '{self.contact_person}')"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, delivered, cancelled
    total_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    
    # Relationships
    supplier = db.relationship('Supplier', backref='orders')
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"Order(Supplier: {self.supplier_id}, Date: {self.order_date}, Status: {self.status})"

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    
    # Relationship
    inventory = db.relationship('Inventory', backref='order_items')
    
    def __repr__(self):
        return f"OrderItem(Order: {self.order_id}, Item: {self.inventory_id}, Quantity: {self.quantity})"

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # private, semi-private, ward
    status = db.Column(db.String(20), default='available')  # available, occupied, maintenance
    daily_rate = db.Column(db.Float, nullable=False)
    
    # Relationships
    admissions = db.relationship('Admission', backref='room', lazy=True)
    
    def __repr__(self):
        return f"Room('{self.room_number}', Type: {self.room_type}, Status: {self.status})"
    
    def set_maintenance(self):
        """Set room status to maintenance"""
        # Only set to maintenance if not occupied
        if self.status != 'occupied':
            self.status = 'maintenance'
            return True
        return False
    
    def set_available(self):
        """Set room status to available"""
        # Only set to available if in maintenance
        if self.status == 'maintenance':
            self.status = 'available'
            return True
        return False
    
    def set_occupied(self):
        """Set room status to occupied"""
        # Only set to occupied if available
        if self.status == 'available':
            self.status = 'occupied'
            return True
        return False

class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    nurse_id = db.Column(db.Integer, db.ForeignKey('nurse.id'), nullable=False)
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)
    discharge_date = db.Column(db.DateTime)
    reason = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='admitted')  # admitted, discharged
    notes = db.Column(db.Text)
    
    # Relationships
    patient = db.relationship('Patient', backref='admissions')
    doctor = db.relationship('Doctor', backref='patient_admissions')
    nurse = db.relationship('Nurse', backref='patient_admissions')
    bills = db.relationship('Bill', backref='admission_record', lazy=True)
    
    def __repr__(self):
        return f"Admission(Patient: {self.patient_id}, Room: {self.room_id}, Status: {self.status})"

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.Integer, db.ForeignKey('admission.id'), nullable=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=True)
    bill_date = db.Column(db.DateTime, default=datetime.utcnow)
    room_charges = db.Column(db.Float, default=0.0)
    medical_charges = db.Column(db.Float, default=0.0)  # For procedures, tests etc
    medication_charges = db.Column(db.Float, default=0.0)
    other_charges = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, partially_paid
    payment_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Relationships
    appointment = db.relationship('Appointment', backref='bills', foreign_keys=[appointment_id])
    admission = db.relationship('Admission', foreign_keys=[admission_id])
    
    def calculate_total(self):
        self.total_amount = (
            self.room_charges +
            self.medical_charges +
            self.medication_charges +
            self.other_charges
        )
        return self.total_amount
    
    def __repr__(self):
        if self.admission_id:
            return f"Bill(Admission: {self.admission_id}, Total: {self.total_amount}, Status: {self.payment_status})"
        else:
            return f"Bill(Appointment: {self.appointment_id}, Total: {self.total_amount}, Status: {self.payment_status})"