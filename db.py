import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('db.sqlite3')

# Create a cursor object
cursor = conn.cursor()

# Specify the table name to drop
table_name = 'delivery_cartitem'

# Drop the table if it exists
cursor.execute(f'DROP TABLE IF EXISTS {table_name}')

# Commit the changes and close the connection
conn.commit()
conn.close()
