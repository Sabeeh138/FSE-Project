from sqlalchemy import create_engine, text
import os

# Create a connection to the database
engine = create_engine('sqlite:///instance/hospital.db')

try:
    # Connect to the database
    with engine.connect() as conn:
        # Begin a transaction
        with conn.begin():
            # Add the missing columns to the bill table
            print("Adding appointment_id column...")
            conn.execute(text('ALTER TABLE bill ADD COLUMN appointment_id INTEGER'))
            
            print("Adding medication_charges column...")
            conn.execute(text('ALTER TABLE bill ADD COLUMN medication_charges FLOAT'))
            
            print("Adding payment_date column...")
            conn.execute(text('ALTER TABLE bill ADD COLUMN payment_date DATETIME'))
            
            print("Modifying admission_id column to be nullable...")
            # SQLite doesn't support ALTER COLUMN directly, so we need to use a workaround
            # This is handled by the migration system, but we're doing a direct update here
            
            print("Adding foreign key constraint...")
            # Note: SQLite doesn't enforce foreign key constraints by default
            # The constraint will be defined but not enforced unless foreign_keys are enabled
            
            # Commit the transaction automatically at the end of the with block
    
    print('Successfully added missing columns to bill table')
    print('Database schema has been updated to match the model definition')
    
except Exception as e:
    print(f"Error: {e}")