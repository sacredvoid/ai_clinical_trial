# This will help consolidate all information regarding a patient
from sqlalchemy import create_engine, text
from collections import defaultdict
from datetime import datetime

important_details_column_map = defaultdict()
important_details_column_map['allergies'] = ['description','type','category','reaction1','description1','severity1','reaction2','description2','severity2']
important_details_column_map['conditions'] = ['start','stop','description']
important_details_column_map['immunizations'] = ['description']
important_details_column_map['medications'] = ['start','stop','description','reasondescription']
important_details_column_map['observations'] = ['category','description','value','units','type']
important_details_column_map['procedures'] = ['start','stop','description','reasondescription']
important_details_column_map['patients'] = ['birthdate','gender']


def run_query(query):
    engine = create_engine('sqlite:///patient_data.db')
    connection = engine.connect()
    rows = []
    try:
        sql_query = text(query)
        result = connection.execute(sql_query)
        rows = result.fetchall()
        
    except Exception as e:
        print("Error: ", e)
    finally:
        connection.close()
        return rows

def get_patient_per_table_by_id(specific_table, p_id):
    specific_table_columns_to_select = important_details_column_map[specific_table]
    
    SELECT_TABLE_COLUMNS = ', '.join(map(lambda x: f'{"a."}{x}', specific_table_columns_to_select))
    query_to_run = f"""
            SELECT {SELECT_TABLE_COLUMNS}
            FROM patients p
            LEFT JOIN {specific_table} a ON p.id = a.patient
            WHERE p.id = '{p_id}';
            """
    
    query_result = run_query(query_to_run)
    return query_result

def get_patient_details(p_id):
    patients_table_columns_to_select = important_details_column_map['patients']
    SELECT_PATIENTS_COLUMNS = ', '.join(map(lambda x: f'{"p."}{x}', patients_table_columns_to_select))
    patient_query = f"""
            SELECT {SELECT_PATIENTS_COLUMNS}
            FROM patients p
            WHERE p.id = '{p_id}';
            """ 
    
    query_result = run_query(patient_query)
    return query_result

def get_all_patient_ids():
    patient_query = f"""
            SELECT id
            FROM patients;
            """ 
    
    query_result = run_query(patient_query)
    return query_result

def calculate_age(date_string):
    # Example birthdate (in standard Python date format)
    birthdate = datetime.strptime(date_string, "%Y-%m-%d")

    # Get the current date
    current_date = datetime.now()

    # Calculate the difference in years
    age = current_date.year - birthdate.year

    # Adjust if the birthday hasn't occurred yet this year
    if (current_date.month, current_date.day) < (birthdate.month, birthdate.day):
        age -= 1
    return age

def create_patient_profile(p_id):
    patient_profile = defaultdict()
    patient_details = get_patient_details(p_id)
    patient_bday = patient_details[0][0]
    age = calculate_age(patient_bday)

    for key in important_details_column_map.keys():
        if key != 'patients': 
            patient_profile[key] = get_patient_per_table_by_id(key, p_id)
    
    return {f"{p_id}":{
                        "age": age,
                        "gender": patient_details[0][1],
                        "profile":patient_profile
                    }
            }

def main():
    print(create_patient_profile('b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85'))

if __name__ == "__main__":
    main()
