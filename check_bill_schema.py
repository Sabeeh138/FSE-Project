import sqlite3

# Create a connection to the database
conn = sqlite3.connect('instance/hospital.db')
cursor = conn.cursor()

# Get information about the bill table
cursor.execute('PRAGMA table_info(bill)')
columns = cursor.fetchall()

print('Bill table columns:')
for col in columns:
    # col structure: (cid, name, type, notnull, dflt_value, pk)
    col_id, name, type_, not_null, default_val, is_pk = col
    nullable = "NO" if not_null == 1 else "YES"
    print(f'{name}: type={type_}, nullable={nullable}, default={default_val}, primary_key={is_pk}')

# Close the connection
conn.close()