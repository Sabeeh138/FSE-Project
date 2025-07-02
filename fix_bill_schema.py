from sqlalchemy import create_engine, text
import os

# Create a connection to the database
engine = create_engine('sqlite:///instance/hospital.db')

try:
    # Connect to the database
    with engine.connect() as conn:
        # Begin a transaction
        with conn.begin():
            print("Fixing bill table schema...")
            
            # SQLite doesn't support ALTER COLUMN directly, so we need to use a workaround
            # 1. Create a new table with the correct schema
            conn.execute(text("""
                CREATE TABLE bill_new (
                    id INTEGER NOT NULL, 
                    admission_id INTEGER, 
                    appointment_id INTEGER,
                    bill_date DATETIME, 
                    room_charges FLOAT, 
                    medical_charges FLOAT, 
                    medication_charges FLOAT,
                    other_charges FLOAT, 
                    total_amount FLOAT, 
                    payment_status VARCHAR(20), 
                    payment_date DATETIME,
                    notes TEXT,
                    PRIMARY KEY (id),
                    FOREIGN KEY(admission_id) REFERENCES admission (id),
                    FOREIGN KEY(appointment_id) REFERENCES appointment (id)
                )
            """))
            
            # 2. Copy data from the old table to the new table
            conn.execute(text("""
                INSERT INTO bill_new 
                SELECT id, admission_id, appointment_id, bill_date, room_charges, 
                       medical_charges, medication_charges, other_charges, total_amount, 
                       payment_status, payment_date, notes 
                FROM bill
            """))
            
            # 3. Drop the old table
            conn.execute(text("DROP TABLE bill"))
            
            # 4. Rename the new table to the original name
            conn.execute(text("ALTER TABLE bill_new RENAME TO bill"))
            
            print("Successfully updated bill table schema")
    
    print('Database schema has been updated to match the model definition')
    print('The admission_id column in the bill table is now nullable')
    
except Exception as e:
    print(f"Error: {e}")