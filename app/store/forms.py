from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Supplier, Inventory

class StoreManagerProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Profile')

def get_suppliers():
    return Supplier.query.all()

class InventoryForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[
        ('medication', 'Medication'),
        ('equipment', 'Equipment'),
        ('supplies', 'Supplies')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    unit_price = FloatField('Unit Price', validators=[DataRequired(), NumberRange(min=0)])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    reorder_level = IntegerField('Reorder Level', validators=[DataRequired(), NumberRange(min=1)])
    supplier = QuerySelectField('Supplier', query_factory=get_suppliers, get_label=lambda s: s.name, allow_blank=True, blank_text='-- Select Supplier (Optional) --')
    submit = SubmitField('Save Item')

class SupplierForm(FlaskForm):
    name = StringField('Supplier Name', validators=[DataRequired(), Length(max=100)])
    contact_person = StringField('Contact Person', validators=[Optional(), Length(max=100)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Save Supplier')

class OrderForm(FlaskForm):
    supplier = QuerySelectField('Supplier', query_factory=get_suppliers, get_label=lambda s: s.name, validators=[DataRequired()])
    notes = TextAreaField('Order Notes', validators=[Optional()])
    submit = SubmitField('Create Order')

def get_inventory_items():
    return Inventory.query.all()

class OrderItemForm(FlaskForm):
    inventory_item = QuerySelectField('Inventory Item', query_factory=get_inventory_items, get_label=lambda i: f"{i.item_name} ({i.category})", validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    unit_price = FloatField('Unit Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Item')
    add_another = SubmitField('Add Item & Add Another')