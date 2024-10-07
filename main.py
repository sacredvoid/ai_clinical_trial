# In sub.py
import subprocess


def main():
    # Run this to convert the CSV files of patients to SQLite RDB
    print("Converting Patient CSV Files to SQLite DB")
    subprocess.call(['python', 'csv_to_db.py'])
    print("Saved CSV data to SQLite DB here: ./patient_data.db")
    # Run this to fetch latest recruiting trials, can be modified to fetch n number of pages and trials
    print("Fetching latest recruiting trials: ")
    subprocess.call(['python', 'web_scraper_trials.py'])
    print("Stored all trials in chromaDB here: ./chromadb_clinicaltrial")
    # Run this to then start the matching process. It will save jsons to /patient_trials_matched.
    print("Finding matched trials per patient ID:")
    subprocess.call(['python', 'find_matching_trial.py'])
    print("Results stored in: ./patient_trials_matched")
    

if __name__ == "__main__":
    main()