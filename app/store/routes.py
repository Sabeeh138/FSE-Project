from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import StoreManager, Inventory, Supplier, Order, OrderItem
from app.store.forms import StoreManagerProfileForm, InventoryForm, SupplierForm, OrderForm, OrderItemForm

store = Blueprint('store', __name__)

@store.route('/store/dashboard')
@login_required
def dashboard():
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Get the store manager profile
    store_manager = StoreManager.query.filter_by(user_id=current_user.id).first()
    
    # If store manager profile doesn't exist, redirect to create profile
    if not store_manager:
        flash('Please complete your profile first', 'info')
        return redirect(url_for('store.create_profile'))
    
    # Get low stock items
    low_stock_items = Inventory.query.filter(Inventory.stock_quantity <= Inventory.reorder_level).all()
    
    # Get recent orders
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    
    return render_template(
        'store/dashboard.html', 
        title='Store Manager Dashboard',
        store_manager=store_manager,
        low_stock_items=low_stock_items,
        recent_orders=recent_orders
    )

@store.route('/store/profile', methods=['GET', 'POST'])
@login_required
def create_profile():
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Check if store manager profile already exists
    store_manager = StoreManager.query.filter_by(user_id=current_user.id).first()
    
    # If profile exists, redirect to edit profile
    if store_manager:
        return redirect(url_for('store.edit_profile'))
    
    form = StoreManagerProfileForm()
    if form.validate_on_submit():
        store_manager = StoreManager(
            user_id=current_user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            contact_number=form.contact_number.data,
            email=form.email.data
        )
        db.session.add(store_manager)
        db.session.commit()
        flash('Your profile has been created!', 'success')
        return redirect(url_for('store.dashboard'))
    
    return render_template('store/create_profile.html', title='Create Store Manager Profile', form=form)

@store.route('/store/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    store_manager = StoreManager.query.filter_by(user_id=current_user.id).first_or_404()
    form = StoreManagerProfileForm()
    
    if form.validate_on_submit():
        store_manager.first_name = form.first_name.data
        store_manager.last_name = form.last_name.data
        store_manager.contact_number = form.contact_number.data
        store_manager.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('store.dashboard'))
    elif request.method == 'GET':
        form.first_name.data = store_manager.first_name
        form.last_name.data = store_manager.last_name
        form.contact_number.data = store_manager.contact_number
        form.email.data = store_manager.email
    
    return render_template('store/edit_profile.html', title='Edit Store Manager Profile', form=form)

@store.route('/store/inventory')
@login_required
def inventory():
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Get inventory items, optionally filtered by category
    category = request.args.get('category')
    if category and category != 'all':
        inventory_items = Inventory.query.filter_by(category=category).order_by(Inventory.item_name).all()
    else:
        inventory_items = Inventory.query.order_by(Inventory.item_name).all()
    
    return render_template('store/inventory.html', title='Inventory', inventory_items=inventory_items, selected_category=category)

@store.route('/store/inventory/new', methods=['GET', 'POST'])
@login_required
def add_inventory_item():
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to add inventory items', 'danger')
        return redirect(url_for('main.home'))
    
    form = InventoryForm()
    if form.validate_on_submit():
        inventory_item = Inventory(
            item_name=form.item_name.data,
            category=form.category.data,
            description=form.description.data,
            unit_price=form.unit_price.data,
            stock_quantity=form.stock_quantity.data,
            reorder_level=form.reorder_level.data,
            supplier_id=form.supplier.data.id if form.supplier.data else None
        )
        db.session.add(inventory_item)
        db.session.commit()
        flash('Inventory item has been added successfully!', 'success')
        return redirect(url_for('store.inventory'))
    
    return render_template('store/add_inventory_item.html', title='Add Inventory Item', form=form)

@store.route('/store/inventory/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_inventory_item(item_id):
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to edit inventory items', 'danger')
        return redirect(url_for('main.home'))
    
    inventory_item = Inventory.query.get_or_404(item_id)
    form = InventoryForm()
    
    if form.validate_on_submit():
        inventory_item.item_name = form.item_name.data
        inventory_item.category = form.category.data
        inventory_item.description = form.description.data
        inventory_item.unit_price = form.unit_price.data
        inventory_item.stock_quantity = form.stock_quantity.data
        inventory_item.reorder_level = form.reorder_level.data
        inventory_item.supplier_id = form.supplier.data.id if form.supplier.data else None
        db.session.commit()
        flash('Inventory item has been updated successfully!', 'success')
        return redirect(url_for('store.inventory'))
    elif request.method == 'GET':
        form.item_name.data = inventory_item.item_name
        form.category.data = inventory_item.category
        form.description.data = inventory_item.description
        form.unit_price.data = inventory_item.unit_price
        form.stock_quantity.data = inventory_item.stock_quantity
        form.reorder_level.data = inventory_item.reorder_level
        if inventory_item.supplier_id:
            form.supplier.data = inventory_item.supplier
    
    return render_template('store/edit_inventory_item.html', title='Edit Inventory Item', form=form, item=inventory_item)

@store.route('/store/suppliers')
@login_required
def suppliers():
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('store/suppliers.html', title='Suppliers', suppliers=suppliers)

@store.route('/store/suppliers/new', methods=['GET', 'POST'])
@login_required
def add_supplier():
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to add suppliers', 'danger')
        return redirect(url_for('main.home'))
    
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            contact_person=form.contact_person.data,
            contact_number=form.contact_number.data,
            email=form.email.data,
            address=form.address.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash('Supplier has been added successfully!', 'success')
        return redirect(url_for('store.suppliers'))
    
    return render_template('store/add_supplier.html', title='Add Supplier', form=form)

@store.route('/store/suppliers/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to edit suppliers', 'danger')
        return redirect(url_for('main.home'))
    
    supplier = Supplier.query.get_or_404(supplier_id)
    form = SupplierForm()
    
    if form.validate_on_submit():
        supplier.name = form.name.data
        supplier.contact_person = form.contact_person.data
        supplier.contact_number = form.contact_number.data
        supplier.email = form.email.data
        supplier.address = form.address.data
        db.session.commit()
        flash('Supplier has been updated successfully!', 'success')
        return redirect(url_for('store.suppliers'))
    elif request.method == 'GET':
        form.name.data = supplier.name
        form.contact_person.data = supplier.contact_person
        form.contact_number.data = supplier.contact_number
        form.email.data = supplier.email
        form.address.data = supplier.address
    
    return render_template('store/edit_supplier.html', title='Edit Supplier', form=form, supplier=supplier)

@store.route('/store/suppliers/<int:supplier_id>')
@login_required
def view_supplier(supplier_id):
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    supplier = Supplier.query.get_or_404(supplier_id)
    return render_template('store/supplier_details.html', title=f'Supplier: {supplier.name}', supplier=supplier)

@store.route('/store/orders')
@login_required
def orders():
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Get orders, optionally filtered by status
    status = request.args.get('status')
    if status and status != 'all':
        orders = Order.query.filter_by(status=status).order_by(Order.order_date.desc()).all()
    else:
        orders = Order.query.order_by(Order.order_date.desc()).all()
    
    return render_template('store/orders.html', title='Orders', orders=orders, selected_status=status)

@store.route('/store/orders/new', methods=['GET', 'POST'])
@login_required
def create_order():
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to create orders', 'danger')
        return redirect(url_for('main.home'))
    
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(
            supplier_id=form.supplier.data.id,
            notes=form.notes.data
        )
        db.session.add(order)
        db.session.commit()
        flash('Order has been created! Now add items to the order.', 'success')
        return redirect(url_for('store.add_order_item', order_id=order.id))
    
    return render_template('store/create_order.html', title='Create Order', form=form)

@store.route('/store/orders/<int:order_id>/items/add', methods=['GET', 'POST'])
@login_required
def add_order_item(order_id):
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to add order items', 'danger')
        return redirect(url_for('main.home'))
    
    order = Order.query.get_or_404(order_id)
    form = OrderItemForm()
    
    if form.validate_on_submit():
        order_item = OrderItem(
            order_id=order_id,
            inventory_id=form.inventory_item.data.id,
            quantity=form.quantity.data,
            unit_price=form.unit_price.data
        )
        db.session.add(order_item)
        
        # Update order total
        order.total_amount += (order_item.quantity * order_item.unit_price)
        
        db.session.commit()
        flash('Item has been added to the order!', 'success')
        
        if 'add_another' in request.form:
            return redirect(url_for('store.add_order_item', order_id=order_id))
        else:
            return redirect(url_for('store.order_details', order_id=order_id))
    
    return render_template('store/add_order_item.html', title='Add Order Item', form=form, order=order)

@store.route('/store/orders/<int:order_id>')
@login_required
def order_details(order_id):
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    order = Order.query.get_or_404(order_id)
    return render_template('store/order_details.html', title=f'Order #{order.id}', order=order)

@store.route('/store/orders/<int:order_id>/update-status', methods=['POST'])
@login_required
def update_order_status(order_id):
    # Check if user is a store manager
    if current_user.role != 'store_manager':
        flash('You do not have permission to update order status', 'danger')
        return redirect(url_for('main.home'))
    
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    
    if status in ['pending', 'delivered', 'cancelled']:
        order.status = status
        
        # If order is delivered, update inventory quantities
        if status == 'delivered':
            for item in order.order_items:
                inventory_item = item.inventory
                inventory_item.stock_quantity += item.quantity
        
        db.session.commit()
        flash(f'Order status has been updated to {status}!', 'success')
    else:
        flash('Invalid status value', 'danger')
    
    return redirect(url_for('store.order_details', order_id=order_id))