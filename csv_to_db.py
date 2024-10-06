import os
from sqlalchemy import create_engine, inspect
import pandas as pd

# File contains code to convert the given patient CSV files into an RDB stored in local SQLite.

# Create SQLAlchemy engine
db_name = 'patient_data.db'
engine = create_engine(f'sqlite:///{db_name}')

# Directory containing CSV files
csv_directory = './patient_data'

# Function to clean column names
def clean_column_name(name):
    return name.lower().replace(' ', '_').replace('-', '_')

# Iterate through CSV files in the directory
for filename in os.listdir(csv_directory):
    if filename.endswith('.csv'):
        # Get the table name from the file name (without extension)
        table_name = os.path.splitext(filename)[0].lower()
        
        # Read CSV file
        df = pd.read_csv(os.path.join(csv_directory, filename))
        
        # Clean column names
        df.columns = [clean_column_name(col) for col in df.columns]
        
        # Create table and insert data
        df.to_sql(table_name, engine, if_exists='replace', index=False)

        print(f"Imported {filename} into {table_name} table")

print("All CSV files have been imported into the database.")

# Print table structures
inspector = inspect(engine)

for table_name in inspector.get_table_names():
    print(f"\nTable: {table_name}")
    for column in inspector.get_columns(table_name):
        print(f"  {column['name']}: {column['type']}")
