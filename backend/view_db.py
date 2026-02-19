import sqlite3
import os

# Path to your database file
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

def view_users():
    if not os.path.exists(db_path):
        print("Error: database.db not found. Have you logged in at least once?")
        return

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query all users from the user table
        cursor.execute("SELECT * FROM user")
        rows = cursor.fetchall()

        if not rows:
            print("Database is empty. Try logging in on the website first!")
        else:
            print("\n--- REGISTERED USERS IN SQLITE ---")
            print(f"{'ID':<5} | {'UID':<30} | {'Username':<15} | {'Email'}")
            print("-" * 70)
            for row in rows:
                print(f"{row[0]:<5} | {row[1]:<30} | {row[2]:<15} | {row[3]}")
        
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    view_users()