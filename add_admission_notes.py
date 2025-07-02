from sqlalchemy import create_engine, text
import os

# Create a connection to the database
engine = create_engine('sqlite:///instance/hospital.db')

try:
    # Connect to the database
    with engine.connect() as conn:
        # Begin a transaction
        with conn.begin():
            # Add the missing notes column to the admission table
            print("Adding notes column to admission table...")
            conn.execute(text('ALTER TABLE admission ADD COLUMN notes TEXT'))
            
            # Commit the transaction automatically at the end of the with block
    
    print('Successfully added notes column to admission table')
    print('Database schema has been updated to match the model definition')
    
except Exception as e:
    print(f"Error: {e}")