from sqlalchemy import create_engine, text
import os

# Create a connection to the database
engine = create_engine('sqlite:///instance/hospital.db')

try:
    # Connect to the database
    with engine.connect() as conn:
        # Begin a transaction
        with conn.begin():
            # Add the missing columns to the appointment table
            print("Adding is_inpatient column...")
            conn.execute(text('ALTER TABLE appointment ADD COLUMN is_inpatient BOOLEAN DEFAULT 0'))
            
            print("Adding room_id column...")
            conn.execute(text('ALTER TABLE appointment ADD COLUMN room_id INTEGER'))
            
            print("Adding nurse_id column...")
            conn.execute(text('ALTER TABLE appointment ADD COLUMN nurse_id INTEGER'))
            
            # Commit the transaction automatically at the end of the with block
    
    print('Successfully added missing columns to appointment table')
    print('Database schema has been updated to match the model definition')
    
except Exception as e:
    print(f"Error: {e}")